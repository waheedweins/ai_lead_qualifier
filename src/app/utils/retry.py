import time
import logging

logger = logging.getLogger("retry")

def retry(fn, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            if attempt == retries - 1:
                raise
            time.sleep(delay)
