import time
import signal
from functools import wraps
from kevinlulee.extras.log_file import log_file

def timeout(max_seconds: float = 20.0):
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

