import threading
import queue
import logging
from typing import Callable, Any


class PerKeyExecutor:
    """
    Executes tasks with per-key serialization.
    Tasks with the same key are processed sequentially (FIFO).
    Tasks with different keys are processed in parallel.
    """

    def __init__(self, worker_idle_timeout: float = 60.0, max_queue_size: int = 0):
        """
        Args:
            worker_idle_timeout: Seconds a worker waits for new work before exiting
            max_queue_size: Max items per queue (0 = unlimited)
        """
        self._queues: dict[str, queue.Queue] = {}
        self._workers: dict[str, threading.Thread] = {}
        self._lock = threading.Lock()
        self._shutdown = False
        self._worker_idle_timeout = worker_idle_timeout
        self._max_queue_size = max_queue_size

    def submit(self, key: str, fn: Callable, *args, **kwargs) -> bool:
        """
        Submit a task to be executed for the given key.

        Args:
            key: The key to serialize on (e.g., ISIN)
            fn: The function to execute
            *args, **kwargs: Arguments to pass to fn

        Returns:
            True if submitted, False if rejected (queue full or shutdown)
        """
        with self._lock:
            if self._shutdown:
                return False

            if key not in self._queues:
                logging.info("Add new queue for isin %s", key)
                self._queues[key] = queue.Queue(maxsize=self._max_queue_size)

            q = self._queues[key]

            if 0 < self._max_queue_size <= q.qsize():
                return False

            q.put((fn, args, kwargs))

            if key not in self._workers or not self._workers[key].is_alive():
                logging.info("Add new worker for isin %s", key)
                worker = threading.Thread(target=self._worker, args=(key,), daemon=True)
                self._workers[key] = worker
                worker.start()

            return True

    def _worker(self, key: str) -> None:
        """Worker thread that processes tasks for a specific key."""
        q = self._queues[key]

        while True:
            try:
                item = q.get(timeout=self._worker_idle_timeout)
                fn, args, kwargs = item
                logging.info("Start new task for isin %s", key)
                try:
                    fn(*args, **kwargs)
                except Exception as e:
                    logging.exception(f"Error processing task for key {key}: {e}")
                finally:
                    q.task_done()
            except queue.Empty:
                with self._lock:
                    if q.empty():
                        if key in self._workers:
                            del self._workers[key]
                        return

            if self._shutdown and q.empty():
                with self._lock:
                    if key in self._workers:
                        del self._workers[key]
                return

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.

        Args:
            wait: If True, wait for all workers to complete their queues
        """
        self._shutdown = True

        if wait:
            logging.info("Shut down process executor gracefully.")
            with self._lock:
                workers = list(self._workers.values())
            for worker in workers:
                worker.join()

    def pending_count(self, key: str) -> int:
        """Returns number of pending tasks for a specific key."""
        with self._lock:
            if key in self._queues:
                return self._queues[key].qsize()
            return 0

    def total_pending(self) -> int:
        """Returns total pending tasks across all keys."""
        with self._lock:
            return sum(q.qsize() for q in self._queues.values())

    def active_workers(self) -> int:
        """Returns count of currently active worker threads."""
        with self._lock:
            return sum(1 for w in self._workers.values() if w.is_alive())
