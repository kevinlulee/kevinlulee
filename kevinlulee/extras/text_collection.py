import kevinlulee as kx
from kevinlulee.extras.colon_dict import colon_dict


class AbstractNoteCollection:
    collection_pattern = "^-{3,}"

    def setup(self):
        pass

    def __init__(self, input):
        self.setup()
        self.text, self.file = (
            (kx.readfile(input), input) if kx.is_file(input) else (kx.trimdent(input), None)
        )

        self.update()

    def update(self):
        parts = kx.split(
            kx.text_getter(self.text), self.collection_pattern, flags=kx.re.M
        )
        self.create(parts)

    def create(self, parts):
        self.items = kx.mapfilter(parts, self.parse)
        self.data = {self.get_key(el): self.get_value(el) for el in self.items}

    def get_value(self, el):
        return el

    def get_key(self, el):
        return el.get("key") or el.get("name") or el.get('prefix')

    def get(self, key):
        return self.data.get(key)

    def to_list(self):
        return self.items

    def to_dict(self) -> dict:
        return self.data


class BraceNoteCollection(AbstractNoteCollection):

    def parse(self, s):
        colons
        args = kx.split(s, "^\[([a-zA-Z].*?)\]", flags=kx.re.M)
        items = kx.partition(args)
        return dict(items)


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


class TreeSitterNoteCollection(AbstractNoteCollection):
    collection_pattern = "^={60}"

    def create(self, parts):
        items = kx.partition(parts)
        store = []
        for a, b in items:
            before, after = kx.split(b, super().collection_pattern)
            ref = kx.colon_split(a)
            ref["before"] = before
            ref["after"] = after
            store.append(ref)

        self.data = store


def example():
    s = """
        key: asdfadsf
        
        asdfasdf
        asdf

        ---

        key: asdf

        text: adfasd
        adsfadf
    """

    a = PromptLibCollection(kx.trimdent(s))
    kx.pprint(a.to_list())


def example():
    s = """
    
    [key]
    
    [system]
    
    [prompt]
    
    
    ---
    
    
    [key]
    
    [system]
    
    [prompt]
    
    
    ---
    
    [key]
    
    [system]
    
    [prompt]
    
    
    ---
    
    """
    print(BraceNoteCollection(s).to_dict())
if __name__ == '__main__':
    example()
