import kevinlulee as kx


class NoteCollector:
    collection_pattern = "^-{3,}"

    def collect(self, s):
        return kx.split(s, self.collection_pattern, flags=kx.re.M)

    def run(self, s):
        return kx.mapfilter(self.collect(s), self.parse)

    def parse(self, s):
        raise Exception("abstract")
class SimpleNoteCollector(NoteCollector):
    """

    Text looks like the following:

    items are separated by dashbreaks.
    frontmatter exists at the top.

    the rest of the text, if it exists, is placed into field: text.

    ---------------------------------------
    name: succinct

    be succinct and detailed.
    consider words carefully.
    especially find creative ways to avoid redundancy.

    ---------------------------------------
    name: present

    reference only code that is present.
    do not make things up or assume anything
    do not implement new code
    """

    collection_pattern = "^-{3,45}"
    # when the dash pattern is longer than 45, it is usually associated with ascii tables
    # hence, by stopping at 45, the whole of the table can be collected
    # this is hacky and unreliable ... but can be made more robust in the future


    def __init__(self, src_text):
        super().__init__()
        self.src_text = src_text

    def parse(self, s):
        text, fm = kx.extract_frontmatter(s)
        if not fm:
            return
        if fm.get('ignore'):
            return 
        if kx.exists(text):
            fm["text"] = text
        return fm

    def to_dict(self):
        return {
            el.get("name"): el.get("text") for el in self.run(self.src_text)
        }


def to_dict(s) -> dict:
    s = kx.text_getter(s)
    return SimpleNoteCollector(s).to_dict()


# kx.pprint(to_dict('/home/kdog3682/projects/python/maelstrom/lib/aicmp/prompts.txt'))
