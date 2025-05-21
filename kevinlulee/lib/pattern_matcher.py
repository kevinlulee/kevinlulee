import kevinlulee as kx
class PatternMatcher:
    """
    hacky as heck ... but it works for now and we will fix it later
    """
    def match(self, items: list, schema: list):
        def replacer(x):
            key = x.group(0)
            return group(key, space = True)
            
        def group(s, start = False, end = False, space = False):
            space = ' ?' if space else ''
            a = '^' if start else ''
            b = '$' if start else ''
            return f'{a}(?:{s}{space}){b}'

        s = ' '.join(items)
        schema = ' '.join(schema)
        schema = kx.re.sub('[a-zA-Z]+', replacer, schema)
        schema = kx.re.sub(' +(?![*?])', '', schema)
        schema = group(schema, True, True)
        m = kx.re.match(schema, s)
        return bool(m)
