import kevinlulee as kx

pat = kx.re.compile("\$(\w+(?:\.\w+)*)(?:\((.*?)\))?")
import nvim

def strfmt(template, ref):
    
    # kx.pretty_print(ref.current_file)
    # env = ref.__dict__
    # kx.pretty_print(env.keys())

    def replacer(x):
        base = x.group(0)
        prefix = 'self.state.'
        expr = prefix + base[1:]
        kx.pretty_print(expr)
        return eval(expr, dict(self = ref))
        
    return kx.re.sub(pat, replacer, template)

print(strfmt('$current_file', nvim))
