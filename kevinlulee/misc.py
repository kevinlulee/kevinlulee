import re
import kevinlulee as kx

def yaml_indentation_fix(s, keys = ["code", "diagram", "description", "notes", "note"]):
    """
    this will be used for the hammy math class frame creations.
    this adds pipes when entries are multiline.

    """
    keys = "|".join(keys)

    def replacer_empty(x):
        spaces = x.group(1)
        key = x.group(2)
        return f"{spaces}{key}: none"

    # s = re.sub(
    #     "^( +)([\w-]+): *$", replacer_empty, s, flags=re.M
    # )  # this removes indented blank fields

    def replacer(x):
        key = x.group(1)
        assert key in keys, f"{key} does not exist in {keys}. invalid block group."
        return key + ": |" + kx.newline_indent(x.group(2)) + "\n"

    s = re.sub(
        f"^(@?[\w-]+): *\n+(\S[\w\W]+?)(?=\Z|\n[\w-]+:)", replacer, s, flags=kx.re.M
    )

    s = kx.yamload(s)
    return s

