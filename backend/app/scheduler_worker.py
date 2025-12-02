import time
import logging
from app.core.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    sched = start_scheduler()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        pass
