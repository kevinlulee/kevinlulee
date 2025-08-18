import kevinlulee as kx
from codefmt.typst import typstfmt
from codefmt.python import pythonfmt

data = {
    "name": "arrow-flex",
    "params": {
        "elude": "sink",
        "named": {
            "spacing": {"type": "number", "value": "5in"},
            "arrow-length": {"type": "number", "value": "10pt"},
            "adjust": {"type": "none", "value": "none"},
        },
        "pos": ["asdfasdf-sdfsdf"],
    },
    "doc": "dsfsdf\nsdfsdf",
}


def to_python(data):
    name = data["name"]
    params = data["params"]
    named = params["named"]
    pos = params["pos"]
    elude = params["elude"]
    doc = data.get("doc")
    args = kx.map(pos, kx.snake_case)

    kwargs = {}
    bridge_kwargs = {}

    for k, v in named.items():
        k = kx.snake_case(k)

        type = v["type"]
        value = v["value"]

        bridge_kwargs[k] = k

        val = None
        match type:
            case "group":
                val = {}
            case "bool":
                val = "True" if value == "true" else "False"
            case "auto":
                val = value
            case "ident":
                val = "None"
            case "none":
                val = "None"
            case "string":
                val = value
            case "sign":
                d, u = kx.matchstr(value, "(-\d+(?:\.\d+)?)(.*)")
                aliases = {"in": "inches"}
                u = aliases.get(u, u)
                val = (u, d)
            case "number":
                d, u = kx.matchstr(value, "(\d+(?:\.\d+)?)(.*)")
                # d = float(d)
                aliases = {"in": "inches"}
                if u:
                    u = aliases.get(u, u)
                    if u == "pt":
                        val = d
                    else:
                        val = pythonfmt.call(
                            u, [kx.possibly_normalize_number(d)]
                        )
                else:
                    val = d
            case _:
                panic("not handled yet ... only none string and numbers")

        kwargs[k] = val

    args = kx.real(args)
    cargs = [kx.snake_case(name)] + args
    main = pythonfmt.decl(
        "return",
        kx.real(pythonfmt.call("bridge", cargs, kx.real(bridge_kwargs))),
    )
    docstr = kx.parens(doc, '"""\n\n"""') if doc else None
    body = kx.join_text(docstr, main)
    return pythonfmt.func(kx.snake_case(name), args, kx.real(kwargs), body)


def to_typst(data):
    name = data["name"]
    params = data["params"]
    named = params["named"]
    pos = params["pos"]
    elude = params["elude"]
    doc = data.get("doc")
    args = kx.map(pos, kx.dash_case)

    kwargs = kx.reduce(named, lambda x: x["value"])
    docstr = kx.comment(doc, "typst", as_documentation=True)
    body = kx.join_text(docstr, "return")
    return typstfmt.func(name, args, kwargs, body, top_level=True)


if __name__ == "__main__":
    mod.commander.run(to_typst, data)
    # mod.commander.run(to_python, data)
