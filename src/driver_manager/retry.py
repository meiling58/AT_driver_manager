# driver_manager/retry.py

import time

def retry(times=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"[Retry {attempt+1}/{times}] {func.__name__} failed:", e)
                    time.sleep(delay)
            raise RuntimeError(f"{func.__name__} failed after {times} retries")
        return wrapper
    return decorator
