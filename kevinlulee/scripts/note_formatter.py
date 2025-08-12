import kevinlulee as kx
from codefmt.yaml import yamlfmt
import re

from typing import TypedDict, NotRequired, Literal, Any


class Formatter(TypedDict):
    # lock to the formatter you showed; change to `str` if you want to allow others
    name: Literal["NoteFormatterV1"]


class Frontmatter(TypedDict, total=False):
    debug: bool
    # bucket for any additional frontmatter options
    options: NotRequired[dict[str, Any]]


class Meta(TypedDict):
    author: str
    created_at: str      # ISO date, e.g. "2025-08-11"
    date_range: str      # e.g. "August 2025 to August 2025"
    debug: bool
    formatter: Formatter
    frontmatter: Frontmatter


class ContentItemBase(TypedDict):
    date: str                    # ISO date for the entry
    type: str
    text: str


class ContentItem(ContentItemBase, total=False):
    # optional, known fields
    title: NotRequired[str]
    tags: NotRequired[list[str]]
    id: NotRequired[str]
    # catch-all bag for any other per-item attributes
    attrs: NotRequired[dict[str, Any]]


class NotesDoc(TypedDict):
    contents: list[ContentItem]
    meta: Meta


def error_wrapper(func, handler = None):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if handler:
                return handler(*args, **kwargs)
            print('ERROR')
            if args:
                print('first arg')
                print('___')
                print(args[0])
                print('___')

            raise e

    return wrapper

def fix_bullets_with_extra_spaces(s):
    s = re.sub("^- +", "- ", s, flags=re.M)
    return s


def parser_v1(s):
    s, date = kx.mget(s, "^\d\d\d\d-\d\d-\d\d")
    initial_text = s
    if not s.strip():
        return
    as_title = s.startswith(' ') and not kx.matchstr(s, '^ *\n')
    s = s.strip()
    first_line = None
    if date:
        t, fm = kx.extract_frontmatter(s)
        if fm:
            return {"date": date, **fm, "text": t}

        if as_title:
            s, first_line = kx.mget(s, ".*")
        if not s.strip():
            return {"date": date, "type": "singleton", "text": first_line}
        else:
            s, fm = kx.extract_frontmatter(s)
            s = s.strip()
            if fm and first_line:
                fm["title"] = first_line
            if fm:
                return {"date": date, **fm, "text": s}
            if first_line:
                if kx.is_word(first_line):
                    return {
                        "type": first_line,
                        "text": s,
                        "date": date,
                    }
                else:
                    return {
                        "title": first_line,
                        "text": s,
                        "date": date,
                    }

            return {
                "type": "uncategorized",
                "date": date,
                "text": s,
            }
    else:
        # no date is present here ...
        # will eventually be backfilled
        # split by dash lines
        # in the future ... this should be avoided.
        # to prevent word fillins
        s, fm = kx.extract_frontmatter(s)
        if s:
            fm["text"] = s
        if fm:
            return {
                **fm,
            }
        else:
            if not s:
                return
            return {
                "type": "uncategorized",
                "text": s,
            }


class NoteFormatterV1:
    """
    ----------------------------------------
    this formatter was written on 2025-05-10
    ----------------------------------------

    items are split by isodate: 2025-05-10
    sometimes items are split by
    "--------------------" or  "----------------------------------------"

    - items have optional title and frontmatter.
      frontmatter must be enclosed in --- and --- delimiteres
    - items are allowed to be single lines.
      they are categorized as "singleton"

    this is a complicated parser with many twists and turns
    but it works
    """

    parsers = dict(v1=parser_v1)
    text_formatters = [
        fix_bullets_with_extra_spaces,
    ]
    default_opts = dict(archive_original_file=True)

    def __init__(self, parser_key="v1", frontmatter={}, opts={}):
        self.opts = {**self.default_opts, **opts}
        self.parser_key = parser_key
        self.frontmatter = frontmatter

    def pre_process(self, s):
        for formatter in self.text_formatters:
            s = formatter(s)
        s, fm = kx.extract_frontmatter(s)
        self.frontmatter.update(fm)
        return s

    def collect(self, s):
        r = "^(?=\d\d\d\d-\d\d-\d\d|-{3,})"
        items = kx.split(s, r, flags=re.M)
        return kx.filtered(items)

    def format(self, text):
        def error_handler(s):
            return None
        items = self.collect(self.pre_process(text))
        data = self.post_process(
            kx.mapfilter(items, error_wrapper(self.parsers.get(self.parser_key), error_handler))
        )
        return data

    def post_process(self, contents):
        def search_backwards(i, contents):
            while i > 0:
                i -= 1
                c = contents[i]
                if "date" in c:
                    return c["date"]

        for i, content in enumerate(contents):
            type = content.get('type')
            title = content.get('title')
            text = content.get('text')
            if not title and kx.linecount(text) > 15:
                content['deleted'] = True
                continue

            if not "date" in content:
                content["date"] = search_backwards(i, contents)

        contents = [c for c in contents if c.get('date')]
        contents.sort(key=kx.to_timestamp)

        dt1 = kx.DateAccess(contents[0])
        dt2 = kx.DateAccess(contents[-1])
        month1, year1 = dt1.month_name, dt1.year
        month2, year2 = dt2.month_name, dt2.year

        date_range = f"{month1} {year1} to {month2} {year2}"
        data = {
            "contents": contents,
            "meta": {
                "author": "Kevin Lee",
                "created_at": kx.strftime(),
                "date_range": date_range,
                "formatter": {
                    "name": kx.nameof(self),
                },
                "frontmatter": self.frontmatter,
            },
        }
        return data

    def load(self) -> KevNote:
        path = kx.get_most_recent_file('~/data/kevnotes/compiled')
        return kx.readfile(path)
    def dump(self, data):
        frontmatter = data['meta']['frontmatter']
        sb = kx.StringBuilder()
        if frontmatter:
            sb.add_text(yamlfmt.to_frontmatter(frontmatter))

        def parse(content):
            
            text = content.pop('text', None)
            date = content.pop('date', None)
            title = content.pop('title', None)
            type = content.pop('type', None)
            s = date  + "\n" +  yamlfmt.format(content) + "\n\n" + text
            return s

        contents = data['contents']
        for content in contents:
            sb.add_text(parse(content))

        return str(sb)

    def run(self, src_path):
        data = self.format(kx.readfile(src_path))

        date_range = data["meta"]["date_range"]
        debug = data["meta"]["debug"]
        contents = data["contents"]

        if debug:
            return mod.pathman.save(data, open=True)
        dst_path = f"~/data/kevnotes/compiled/{date_range}.json"
        cp_path = f"~/data/kevnotes/raw/{date_range}.txt"
        kx.cpfile(src_path, cp_path)
        kx.writefile(dst_path, data)

        print(kx.fancy_file_tree('~/data/kevnotes'))


s = """
    
2025-04-14

https://chatgpt.com/c/67fd6106-ded8-8001-ba49-4f6f2387d1bd
this url is ....
"""
activate = False
if __name__ == "__main__" and activate:
    formatter = NoteFormatterV1()
    formatter.run("/home/kdog3682/documents/notes/notes.txt")
    # '~/data/kevnotes/compiled/February 2025 to August 2025.json'
else:
    formatter = NoteFormatterV1()
    kx.pprint(formatter.format(s))
        

