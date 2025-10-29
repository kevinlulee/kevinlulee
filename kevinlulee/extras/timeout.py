import time
import signal
from functools import wraps
from kevinlulee.extras.log_file import log_file

def timeout(max_seconds: float = 5):
    """Decorator to time function execution and kill if it exceeds max_seconds."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"{func.__name__} exceeded {max_seconds}s")
            
            start = time.perf_counter()
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(max_seconds))
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                return result
            finally:
                signal.alarm(0)
        
        return wrapper
    return decorator


if __name__ == '__main__':
    @timeout(max_seconds=1)
    def slow_function(sleep_time):
        """Function that sleeps for specified time."""
        time.sleep(sleep_time)
        return "Completed"


    try:
        result = slow_function(5)
        print(f"slow_function with 5s: {result}")
    except TimeoutError as e:
        print(f"Error: {e}")

