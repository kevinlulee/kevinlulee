import kevinlulee as kx
from kevinlulee.extras.line_edit import LineEdit

import re
import yaml


def extract_frontmatter(text: str) -> tuple[str, dict]:
    """
    Extract frontmatter from text.
    
    Frontmatter can appear in several formats:
    - Delimited by --- lines
    - Without delimiters (YAML-like at start)
    - Commented with // or # (JS/Python-style comments)
    
    Returns:
        tuple of (remaining_text, frontmatter_dict)
    """
    text = text.strip()
    le = LineEdit(text)
    
    line = le.get_line(1)
    if not line:
        return text, {}
    
    # Case 1: Dash-delimited frontmatter (---)
    if line.match(r"^---\s*$"):
        start_line = line
        end_line = line.seek_below(r"^---\s*$")
        
        if end_line:
            frontmatter_lines = []
            current = start_line.next()
            while current and current != end_line:
                frontmatter_lines.append(current.text)
                current = current.next()
            
            current = start_line
            while current:
                next_line = current.next()
                current.delete()
                if current == end_line:
                    break
                current = next_line
            
            frontmatter = yaml.safe_load('\n'.join(frontmatter_lines)) or {}
            return str(le).strip(), frontmatter
    
    # Case 2: JS-style comment frontmatter (// key: value)
    if line.match(r"^//\s*[\w-]+:"):
        frontmatter_lines = []
        current = line
        
        while current and current.match(r"^//"):
            content = re.sub(r"^//\s?", "", current.text)
            frontmatter_lines.append(content)
            next_line = current.next()
            current.delete()
            current = next_line
        
        frontmatter = yaml.safe_load('\n'.join(frontmatter_lines)) or {}
        return str(le).strip(), frontmatter
    
    # Case 3: Python-style comment frontmatter (# key: value)
    if line.match(r"^#\s*[\w-]+:"):
        frontmatter_lines = []
        current = line
        
        while current and current.match(r"^#"):
            content = re.sub(r"^#\s?", "", current.text)
            frontmatter_lines.append(content)
            next_line = current.next()
            current.delete()
            current = next_line
        
        frontmatter = yaml.safe_load('\n'.join(frontmatter_lines)) or {}
        return str(le).strip(), frontmatter
    
    # Case 4: YAML-like frontmatter without delimiters (key: value at start)
    if line.match(r"^\w[\w\-]*:"):
        frontmatter_lines = []
        current = line
        
        while current:
            if not current.has_text():
                frontmatter_lines.append(current.text)
                next_line = current.next()
                current.delete()
                current = next_line
            elif current.match(r"^\w[\w\-]*:") or current.match(r"^\s+\S"):
                frontmatter_lines.append(current.text)
                next_line = current.next()
                current.delete()
                current = next_line
            elif not current.has_text():
                break
            else:
                break
        
        frontmatter = yaml.safe_load('\n'.join(frontmatter_lines)) or {}
        return str(le).strip(), frontmatter
    
    return text, {}


if __name__ == "__main__":
    
    # Dash-delimited
    text1 = """
    ---
    title: My Post
    tags:
    
      - python
    
      - yaml
    
    ---
    This is the content.
    """
    kx.pretty_print(extract_frontmatter(text1))
    # ('This is the content.', {'title': 'My Post', 'tags': ['python', 'yaml']})
    
    # JS-style comments
    text2 = """
    // title: My Script
    // version: 1.0
    console.log("hello");
    """
    kx.pretty_print(extract_frontmatter(text2))
    # ('console.log("hello");', {'title': 'My Script', 'version': 1.0})
    
    # Python-style comments
    text3 = """
    # author: Alice
    # debug: true
    def main():
        pass
    """
    kx.pretty_print(extract_frontmatter(text3))
    # ('def main():\n    pass', {'author': 'Alice', 'debug': True})
    
    # YAML without delimiters
    text4 = """
    name: config
    count: 42
    
    The rest of the document.
    """
    kx.pretty_print(extract_frontmatter(text4))
    # ('The rest of the document.', {'name': 'config', 'count': 42})
    
    # No frontmatter
    text5 = "Just plain text."
    kx.pretty_print(extract_frontmatter(text5))
    # ('Just plain text.', {})
