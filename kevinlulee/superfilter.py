
from typing import Callable, Dict, List, Literal, Optional, TypedDict, Union

from kevinlulee.validation import exists

class TimeOption(TypedDict):
    hours: int
    seconds: int
    minute: int
    days: int

class TimeSpec(TypedDict):
    recent: TimeOption
    distant: TimeOption

class FilterOpts(TypedDict, total=False):
    key: str
    time: TimeSpec
    filetypes: List[str]
    fields: Dict[str, Callable[[object], bool]]

from kevinlulee.base import testf
from kevinlulee.typing import Selector
from kevinlulee.date_utils import resolve_timedelta

def filterf(opts: FilterOpts):
    key = opts.get('key')
    time_opts = opts.get('time', {})
    field_opts = opts.get('fields', {})
    if field_opts:
        # field_opts = [
        #     (k, testf(v)) for k,v in field_opts.items()
        # ]
        # field_opts = [
        #     (k, v) for k,v in field_opts.items()
        # ]
        field_opts = field_opts.items()
    timestamp = None
    if time_opts:
        recent = time_opts.get('recent')
        distant = time_opts.get('distant')
        t = recent or distant
        target_time = resolve_timedelta(**t)

    def callback(el):

        if time_opts:
            time_opt_key = time_opts.get('key')
            value = el.get(time_opt_key) if time_opt_key else el
            
            if recent and value < target_time:
                return False
            if distant and value > target_time:
                return False

        if field_opts:
            for k,v in field_opts:
                if v and not el[k]:
                    return False

                if not v and el[k]:
                    return False
        return True

    return callback

def superfilter(items, selector: Selector = exists):
    fn = filterf(selector) if isinstance(selector, dict) else testf(selector)
    return [ item for item in items if fn(item) ] 



# a = {
#     'hidden': 0
# }
# print(superfilter([a], {'fields': {'hidden': False}}))
