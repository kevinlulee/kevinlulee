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


def mgetall(s, regex, flags = 0):
    # string_utils
    matches = []
    
    def replacer(match):
        matches.append(match.group(1))
        return ''
        
    result = re.sub(regex, replacer, s.strip(), flags=flags).strip()
    return result, matches
