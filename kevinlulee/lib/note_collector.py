import kevinlulee as kx


class NoteCollectorMixin:
    collection_pattern = "^-{3,}"

    def collect(self, s):
        return kx.split(s, self.collection_pattern, flags=kx.re.M)

    def run(self, s):
        return kx.mapfilter(self.collect(s), self.parse)

    def parse(self, s):
        raise Exception("abstract")


class SimpleNoteCollector(NoteCollectorMixin):
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
        if fm.get("ignore"):
            return
        if kx.exists(text):
            fm["text"] = text
        return fm

    def to_dict(self):
        return {
            el.get("name") or el.get("key"): el.get("text")
            for el in self.run(self.src_text)
        }


def to_dict(s) -> dict:
    s = kx.text_getter(s)
    return SimpleNoteCollector(s).to_dict()


def collect_dict(s) -> dict:
    s = kx.text_getter(s)
    return SimpleNoteCollector(s).to_dict()


# kx.pprint(to_dict('/home/kdog3682/projects/python/maelstrom/lib/aicmp/prompts.txt'))


class BraceNoteCollector:
    collection_pattern = "^-{3,}"

    def collect(self, s):
        return kx.split(
            kx.text_getter(s), self.collection_pattern, flags=kx.re.M
        )

    def run(self, s):
        return kx.mapfilter(self.collect(s), self.parse)

    def parse(self, s):
        args = kx.split(s, "^\[([a-zA-Z].*?)\]", flags=kx.re.M)
        return dict(kx.partition(args))

    def get_value(self, el):
        return el

    def get_key(self, el):
        return el.get("key")

    def to_dict(self, s):
        return {self.get_key(el): self.get_value(el) for el in self.run(s)}


class AbstractNoteCollection:
    collection_pattern = "^-{3,}"

    def __init__(self, text):
        parts = kx.split(
            kx.text_getter(text), self.collection_pattern, flags=kx.re.M
        )
        data = kx.mapfilter(parts, self.parse)
        self.data = {self.get_key(el): self.get_value(el) for el in data}

    def get_value(self, el):
        return el

    def get_key(self, el):
        return el.get("key") or el.get("name")

    def get(self, key):
        return self.data.get(key)

    def to_dict(self):
        return self.data

class PromptLibCollection(AbstractNoteCollection):
    text_key = "text"

    def parse(self, s):
        text, fm = kx.extract_frontmatter(s)
        assert fm, "frontmatter must exist for PromptLibCollection"
        if not fm:
            return
        if fm.get("ignore"):
            return
        if kx.exists(text):
            fm[self.text_key] = text
        return fm


if __name__ == "__main__":
    # kx.pprint(
    #     BraceNoteCollector().to_dict(
    #         "/home/kdog3682/projects/python/maelstrom/lib/aicmp/templates.txt"
    #     )
    # )
    kx.pprint(
        PromptLibCollection(
            "/home/kdog3682/projects/python/maelstrom/lib/aicmp/templates/coder.txt"
        ).to_dict()
    )
