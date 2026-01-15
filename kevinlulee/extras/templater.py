import re
import kevinlulee as kx
from kevinlulee.extras.line_edit import LineEdit

import re
EMPTY = "<EMPTY>"

def wrap_triple_quotes_with_display(text: str, func = 'display') -> str:
    pattern = r"((\"\"\"|''').*?\2)"
    return re.sub(pattern, rf"{func}(\1)", text, flags=re.DOTALL)

def execute(code: str, globals_dict=None, locals_dict=None):
    code = kx.trimdent(code)
    try:
        exec(code, globals_dict, locals_dict)
    except Exception as e:
        print("Error while executing code. Original code:\n")
        print('---')
        print(code)
        print('---')
        raise e

        # exec(kx.trimdent(code), exec_scope)
def remove_empty_placeholders(s):
    if EMPTY not in s:
        return s

    le = LineEdit(s)
    lines = le.findall("<EMPTY>")

    for line in lines:
        if line.prev().match(":$"):
            line.prev().delete()
            line.delete()
            line.prev().prev().delete()
        elif line.prev().match("---") and line.next().match("---"):
            if line.prev().prev().has_text():
                line.prev().prev().delete()
            line.prev().delete()
            line.next().delete()
            line.delete()
        else:
            line.delete()

    return str(le)


class Templater:
    COMBINED = re.compile(
        r"""
            (?:(\n)([ \t]+))?             # group 1,2: optional newline + indentation
            ([-*][ \t]+|\d+\.[ \t]*|[A-Za-z]\.[ \t]*)?  # group 3: marker with its trailing space
            (?:
                {(.*?)}               # group 4: single brace content
                |
                {{([\w\W]+?)}}            # group 5: double brace content
            )
        """,
        flags=re.VERBOSE,
    )

    def __init__(self, ref=None, recursive=False, max_depth=3):
        self.ref = self._build_scope(ref)
        self.recursive = recursive
        self.max_depth = max_depth
        self._depth = 0
        self._display_store = []

    def _build_scope(self, ref):
        if ref is None:
            scope = {}
        elif kx.is_array(ref):
            scope = kx.array_to_dict(ref)
        elif not kx.is_dict(ref):
            scope = {"1": ref, "arg": ref}
        else:
            scope = dict(ref)
        
        scope["kx"] = kx
        scope["xml"] = kx.to_xml
        
        return scope

    def _get_value(self, expr):
        expr = expr.strip()
        if not expr:
            return None
        
        if expr in self.ref:
            return self.ref[expr]
        
        try:
            return eval(expr, self.ref)
        except Exception as e:
            print('ERROR @ ttemplater')
            print('expr')
            print(expr)
            print('---')
            print(e)
            return None

    def _format_list(self, items, marker):
        marker = marker.rstrip()
        lines = []
        for i, item in enumerate(items):
            item_str = self._serialize_value(item)
            # Handle multiline items
            item_lines = item_str.split("\n")
            
            if marker in ("-", "*"):
                prefix = f"{marker} "
            elif marker[-1] == ".":
                if marker[0].isdigit():
                    prefix = f"{i + 1}. "
                else:
                    prefix = f"{chr(ord(marker[0].upper()) + i)}. "
            else:
                prefix = ""
            
            # First line gets the marker, rest get indented
            lines.append(f"{prefix}{item_lines[0]}")
            indent = " " * len(prefix)
            for sub_line in item_lines[1:]:
                lines.append(f"{indent}{sub_line}")
        
        return lines

    def _serialize_value(self, v, marker=None):
        if isinstance(v, str):
            return kx.trimdent(v)
        
        if kx.is_array(v):
            if isinstance(v, set):
                v = list(v)
            if marker:
                return "\n".join(self._format_list(v, marker))
            if v and isinstance(v[0], str):
                return kx.json.dumps(v)
        
        return kx.serialize_data(v)

    def _exec_double_brace(self, code):
        self._display_store = []
        
        def display(s):
            if s is not None:
                self._display_store.append(self._serialize_value(s))
        
        exec_scope = dict(self.ref)
        exec_scope["display"] = display
        

        code = wrap_triple_quotes_with_display(code)
        # print(code)
        # raise Exception()
        execute(code, exec_scope)
        
        return kx.join_text(self._display_store)

    def _apply_indent(self, payload, newline, ind):
        if not newline:
            return payload
        
        lines = payload.split("\n")
        first = lines[0]
        rest = "".join(f"\n{ind}{line}" for line in lines[1:])
        return "\n" + ind + first + rest

    def _replacer(self, match):
        newline, ind, marker, single_expr, double_code = match.groups()
        ind = ind or ""
        
        # Only treat as marker if it's at line start (after newline+indent)
        if marker and not newline:
            marker = None
        
        if double_code is not None:
            payload = self._exec_double_brace(double_code)
        elif single_expr is not None:
            v = self._get_value(single_expr)
            
            if v is None:
                return EMPTY
            
            if self.recursive and isinstance(v, str) and "{" in v:
                if self._depth >= self.max_depth:
                    raise RecursionError(f"templater exceeded max depth of {self.max_depth}")
                self._depth += 1
                v = re.sub(self.COMBINED, self._replacer, v)
                self._depth -= 1
            
            is_array = kx.is_array(v)
            
            # Handle empty arrays
            if is_array and len(v) == 0:
                return ""
            
            payload = self._serialize_value(v, marker)
            
            if marker and not is_array:
                payload = f"{marker.rstrip()} {payload}"
        else:
            return match.group(0)
        
        return self._apply_indent(payload, newline, ind)

    def render(self, template):
        assert template, "empty template was provided"
        template = kx.trimdent(template)
        s = re.sub(self.COMBINED, self._replacer, template)
        s = remove_empty_placeholders(s)
        s = re.sub("\n{3,}", '\n\n', s)
        s = s.strip()
        return s

def templater(template, ref=None, recursive=False, max_depth=10):
    if not template:
        return template
    return Templater(ref=ref, recursive=recursive, max_depth=max_depth).render(template)


if __name__ == "__main__":
    # Basic usage

    file_name = 'abc'
    content = templater('''
        #import "@local/typkit:0.3.0" as tk
        #let {file_name}() = {
          return
        }
    ''', dict(file_name = file_name))
    print(content)
    result = templater(
        """
        Hello {name}!
        
        Items:
            - {items}
        
        Numbered:
            1. {items}
        
        Lettered:
            A. {items}
        """,
        ref=dict(name="World", items={"apple", "banana", "cherry"})
    )
    print("=== Basic ===")
    print(result)
    
    # Edge case 2: Marker false positives - "3." mid-sentence should NOT be a marker
    result = templater(
        "I have 3. {count} items and Grade A. {grade} score",
        ref=dict(count=5, grade="excellent")
    )
    print("\n=== Marker false positive (should be inline) ===")
    print(result)
    
    # Edge case 3: Empty arrays
    result = templater(
        """
        Header:
            - {empty_list}
        
        After empty
        """,
        ref=dict(empty_list=[])
    )
    print("\n=== Empty array ===")
    print(result)
    
    # Edge case 5: Recursive infinite loop protection
    try:
        result = templater(
            "{a}",
            ref=dict(a="{a}"),
            recursive=True,
            max_depth=5
        )
    except RecursionError as e:
        print(f"\n=== Recursion protection ===\n{e}")
    
    # Edge case 6: Multiline items in arrays
    result = templater(
        """
        Notes:
            - {notes}
        """,
        ref=dict(notes={
            "First note",
            "Second note\nwith multiple\nlines",
            "Third note"
        })
    )
    print("\n=== Multiline items ===")
    print(result)
    
    # Double brace code execution
    result = templater(
        """
        Generated:
            {{
                for i in range(3):
                    display(f"Item {i + 1}")

                ''' hi '''
                '''
                hidisplaydisplay
                    hidisplaydisplay
                '''
            }}

        {1 if nvim.g.debug else 4}
        """,
        ref={}
    )
    print("\n=== Double brace ===")
    print(result)
