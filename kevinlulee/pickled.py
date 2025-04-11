import pickle
import hashlib
from functools import wraps
from pathlib import Path
import inspect
from kevinlulee.module_utils import get_modname_from_file
from kevinlulee import clear_directory

 
 

DEFAULT_PICKLED = True
BASE_DIR = Path.home() / '.cache' / 'kdog3682' / 'pickles'



def pickled(func):
    """
    Decorator that caches a function's result based on its input arguments by pickling the output.

    When the decorated function is called with pickled=True, it will:
    - Serialize the input arguments (module, func, args and kwargs)
    - Generate a hash filepath from the serialized data
    - Look for a file in ~/.cache/kdog3682/pickles
        - If the file exists, return the cached result
        - If not, run the function, save the result, and return it

    If pickled=False, the function runs normally without caching.
    the default pickled value is DEFAULT_PICKLED. (default = True)

    This is useful for avoiding recomputation in deterministic functions, especially
    for expensive operations with consistent inputs.
    """

    name = func.__name__
    module = get_modname_from_file(inspect.getfile(func))
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    @wraps(func)
    def wrapper(*args, pickled=DEFAULT_PICKLED, **kwargs):
        if not pickled:
            return func(*args, **kwargs)

        argdata = {
            'func': name,
            'module': module,
            'args': args,
            'kwargs': kwargs,
        }
        data = pickle.dumps(argdata)
        hash_digest = hashlib.md5(data).hexdigest()
        file_path = BASE_DIR / f'{hash_digest}.pkl'

        if file_path.exists():
            print(f'returning pickle {hash_digest} @ {module}.{name}')
            return pickle.loads(file_path.read_bytes())

        result = func(*args, **kwargs)
        print(f'creating pickle {hash_digest} @ {module}.{name}')
        file_path.write_bytes(pickle.dumps(result))

        return result

    return wrapper



if __name__ == '__main__':
    if False:
        clear_directory(BASE_DIR)
