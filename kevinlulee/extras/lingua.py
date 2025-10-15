
from pypinyin import lazy_pinyin, Style

def get_pinyin(s):
    return "".join(lazy_pinyin(s, style=Style.TONE))
