from .date_utils import *
from .assertion import *
from .file_utils import *
from .string_utils import *
from .text_tools import *
from .base import *
from .validation import *
from .ao import *
from .constants import *
from .extended import *
from .array import *
from .templater import *
from .module_utils import *
from .bash import *
from .ripgrep import *
from .file_ops import *
from .components.string_builders import *
from .git import GitRepo
from .pythonfmt import pythonfmt
from .typstfmt import typstfmt
import kevinlulee.ascii as ascii
import kevinlulee.introspect as introspect


def mgetall(s, regex, flags = 0):
    # string_utils
    matches = []
    
    def replacer(match):
        matches.append(match.group(1))
        return ''
        
    result = re.sub(regex, replacer, s.strip(), flags=flags).strip()
    return result, matches


def bring_to_life(code, scope=None) -> Callable:
    """
    Evaluates Python function code and returns the callable.
    
    Args:
        code (str): Python function code as a string
        scope (dict, optional): Dictionary to use as the global scope for exec.
                               If None, uses an empty dictionary.
                               
    Returns:
        callable: The function defined in the code
    """
    scope = scope or globals()
    # Create a local namespace for execution
    local_namespace = {}
    # Execute the code in the provided scope
    exec(code, scope, local_namespace)
    
    # Find the function name by parsing the code
    lines = code.strip().split('\n')
    first_line = lines[0].strip()
    
    # Extract function name from the def statement
    import re
    match = re.match(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', first_line)
    
    if not match:
        raise ValueError("Could not find function definition in the provided code")
    
    function_name = match.group(1)
    
    # Return the function from the local namespace
    if function_name not in local_namespace:
        raise ValueError(f"Function '{function_name}' was not defined in the provided code")
    
    return local_namespace[function_name]


def is_class_instance(s):
    return (hasattr(s, '__class__') and 
            not isinstance(s, type) and 
            not isinstance(s, (list, dict, tuple, set, str, int, float, bool)) and 
            type(s) != type)
def modify_array(items, func, key = None):
    # kx.ao
    for i, item in enumerate(items):
        value = func(item)
        if value is not None:
            if key:
                items[i][key] = value
            else:
                items[i] = valuee
    return items
