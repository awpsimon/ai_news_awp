import logging

# Logging konfigurieren
logging.basicConfig(encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(processName)s %(threadName)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logging.info("Starting News API")
