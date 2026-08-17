import unittest
import threading
import time
import config_logging
from per_key_executor import PerKeyExecutor


class TestPerKeyExecutor(unittest.TestCase):

    def test_sequential_processing_same_key(self):
        """Tasks with the same key should be processed sequentially in FIFO order."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)
        results = []
        lock = threading.Lock()

        def task(value, delay=0.1):
            time.sleep(delay)
            with lock:
                results.append(value)

        executor.submit("key1", task, 1)
        executor.submit("key1", task, 2)
        executor.submit("key1", task, 3)

        executor.shutdown(wait=True)

        self.assertEqual(results, [1, 2, 3])

    def test_parallel_processing_different_keys(self):
        """Tasks with different keys should be processed in parallel."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)
        start_times = {}
        lock = threading.Lock()

        def task(key, delay=0.2):
            with lock:
                start_times[key] = time.time()
            time.sleep(delay)

        start = time.time()
        executor.submit("key1", task, "key1")
        executor.submit("key2", task, "key2")
        executor.submit("key3", task, "key3")

        executor.shutdown(wait=True)
        elapsed = time.time() - start

        # If parallel, should complete in ~0.2s; if sequential, ~0.6s
        self.assertLess(elapsed, 0.5)
        self.assertEqual(len(start_times), 3)

    def test_active_workers_count(self):
        """active_workers() should return correct count of running workers."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)
        event = threading.Event()

        def blocking_task():
            event.wait()

        executor.submit("key1", blocking_task)
        executor.submit("key2", blocking_task)
        time.sleep(0.1)  # Let workers start

        self.assertEqual(executor.active_workers(), 2)

        event.set()
        executor.shutdown(wait=True)

    def test_pending_count(self):
        """pending_count() should return correct count for a key."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)
        event = threading.Event()

        def blocking_task():
            event.wait()

        executor.submit("key1", blocking_task)
        executor.submit("key1", lambda: None)
        executor.submit("key1", lambda: None)
        time.sleep(0.1)  # Let first task start

        # First task is being processed, two are pending
        self.assertEqual(executor.pending_count("key1"), 2)

        # Release task
        event.set()
        executor.shutdown(wait=True)

    def test_total_pending(self):
        """total_pending() should return sum across all keys."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)
        event = threading.Event()

        def blocking_task():
            event.wait()

        executor.submit("key1", blocking_task)
        executor.submit("key1", lambda: None)
        executor.submit("key2", blocking_task)
        executor.submit("key2", lambda: None)
        time.sleep(0.1)

        self.assertEqual(executor.total_pending(), 2)

        # Release blocking tasks
        event.set()
        executor.shutdown(wait=True)

    def test_worker_idle_timeout(self):
        """Worker should exit after idle timeout when queue is empty."""
        executor = PerKeyExecutor(worker_idle_timeout=0.3)

        executor.submit("key1", lambda: None)
        time.sleep(0.1)

        # Worker should still be active or just finished the task
        time.sleep(0.5)  # Wait longer than idle timeout

        # Worker should have exited
        self.assertEqual(executor.active_workers(), 0)

        executor.shutdown(wait=True)

    def test_shutdown_prevents_new_submissions(self):
        """After shutdown, submit() should return False."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)

        executor.shutdown(wait=True)

        result = executor.submit("key1", lambda: None)
        self.assertFalse(result)

    def test_max_queue_size(self):
        """submit() should return False when queue is full."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0, max_queue_size=2)
        event = threading.Event()

        def blocking_task():
            event.wait()

        # First task starts processing
        self.assertTrue(executor.submit("key1", blocking_task))
        time.sleep(0.1)

        # These two fill the queue
        self.assertTrue(executor.submit("key1", lambda: None))
        self.assertTrue(executor.submit("key1", lambda: None))

        # This one should be rejected
        self.assertFalse(executor.submit("key1", lambda: None))

        event.set()
        executor.shutdown(wait=True)

    def test_exception_in_task_does_not_stop_worker(self):
        """Worker should continue processing after a task raises an exception."""
        executor = PerKeyExecutor(worker_idle_timeout=5.0)
        results = []

        def failing_task():
            raise ValueError("test error")

        def success_task(value):
            results.append(value)

        executor.submit("key1", success_task, 1)
        executor.submit("key1", failing_task)
        executor.submit("key1", success_task, 2)

        executor.shutdown(wait=True)

        self.assertEqual(results, [1, 2])

    def test_new_worker_spawns_after_previous_exits(self):
        """A new worker should spawn if previous one exited due to idle timeout."""
        executor = PerKeyExecutor(worker_idle_timeout=0.2)
        results = []

        executor.submit("key1", lambda: results.append(1))
        time.sleep(0.5)  # Wait for worker to exit

        self.assertEqual(executor.active_workers(), 0)

        executor.submit("key1", lambda: results.append(2))
        executor.shutdown(wait=True)

        self.assertEqual(results, [1, 2])


if __name__ == "__main__":
    unittest.main()
