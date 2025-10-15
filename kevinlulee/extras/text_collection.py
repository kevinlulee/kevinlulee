import kevinlulee as kx
from kevinlulee.extras.colon_dict import colon_dict


class AbstractNoteCollection:
    def setup(self):
        pass

    def __init__(self, input):
        self.setup()
        self.text, self.file = (
            (kx.readfile(input), input) if kx.is_file(input)
            else (kx.readdir(input, delimiter='-' * 50), input) if kx.is_dir(input)
            else (kx.trimdent(input), None)
        )
        self.update()

    def get_delimiter(self):
        
        delimiters = kx.re.findall('^-{3,}', self.text, flags=kx.re.M)
        if not delimiters:
            return '---'
        most_common = kx.Counter(delimiters).most_common(1)[0][0]

        if most_common == "---":
            long_dels = [d for d in delimiters if len(d) >= 10]
            if long_dels:
                most_common = kx.Counter(long_dels).most_common(1)[0][0]

        a = f'^-{{{len(most_common)},}}'
        return a

    def update(self):
        a = self.get_delimiter()
        pattern = kx.re.compile(a, flags=kx.re.M)
        parts = kx.split(
            self.text, pattern
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
        args = kx.split(s, "^\[([a-zA-Z].*?)\]", flags=kx.re.M)
        items = kx.partition(args)
        return dict(items)


class PromptLibCollection(AbstractNoteCollection):

    def parse(self, s):
        keys = [
            'prompt',
            'system',
            'schema',
            'role',
            'query',
            'desc',
            'key',
            'name',
        ]
        return colon_dict(s, keys=keys)


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


class YamlSnippetCollection(AbstractNoteCollection):
    """
    first used for snippeteer plugin (collecting wphandles)
    """
    
    def parse(self, s):
        return kx.colon_dict(s, keys = ['prefix', 'body'])
        
    def get_value(self, s):
        body = s['body']
        return dict(template = body, nargs = kx.infer_nargs(body))
    # def to_dict(self):
        
if __name__ == '__main__':
    spec_path = "~/projects/python/maelstrom/lib/aicmp/instructions"
    kx.pretty_print(PromptLibCollection(spec_path).to_dict())

    # spec_path = "/home/kdog3682/data/plugins/snippeteer/omni_handle"
    # kx.pretty_print(YamlSnippetCollection(spec_path).to_dict())
