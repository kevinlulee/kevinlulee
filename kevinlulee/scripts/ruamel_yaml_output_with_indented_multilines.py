from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
import copy


def merge_dicts(*dicts):
    return {k: v for d in dicts for k, v in d.items()}

class NoChompingLiteralString(LiteralScalarString):
    def __new__(cls, value):
        # Ensure value ends with a newline to avoid chomping
        if not value.endswith('\n'):
            value += '\n\n'
        return super().__new__(cls, value)

def format_multiline_strings(obj):
    """
    Walks through an object and converts any strings with newlines
    to YAML literal block scalars (|).
    
    Args:
        obj: The object to process (dict, list, or scalar value)
        
    Returns:
        A copy of the object with multiline strings converted to LiteralScalarString
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            result[key] = format_multiline_strings(value)
        return result
    elif isinstance(obj, list):
        return [format_multiline_strings(item) for item in obj]
    elif isinstance(obj, str) and '\n' in obj:
        # Convert strings with newlines to LiteralScalarString
        return NoChompingLiteralString(obj)
    else:
        return obj

def dump_yaml_with_multiline_blocks(data, stream=None, **kwargs):
    """
    Dumps data to YAML with proper handling of multiline strings.
    
    Args:
        data: The data to dump to YAML
        stream: Optional stream to write to
        **kwargs: Additional arguments to pass to YAML.dump
        
    Returns:
        If stream is None, returns the YAML string, otherwise returns None
    """
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True
    
    # Process the data to handle multiline strings
    processed_data = format_multiline_strings(data)
    
    # Dump the processed data
    if stream is None:
        from io import StringIO
        string_stream = StringIO()
        yaml.dump(processed_data, string_stream, **kwargs)
        return string_stream.getvalue()
    else:
        yaml.dump(processed_data, stream, **kwargs)

# Example usage
if __name__ == "__main__":
    test_data = {
        "name": "Test Document",
        "description": "This is a\nmultiline string\nthat should be formatted",
        "single_line": "This is a single line string",
        "nested": {
            "multiline_code": "def hello():\n    print('Hello, world!')\n    return True",
            "normal_text": "No newlines here"
        },
        "items": [
            "Item 1",
            "Item 2",
            "This is item 3\nwith multiple lines",
            {"nested_item": "This also has\nmultiple lines"}
        ]
    }
    
    # yaml_output = dump_yaml_with_multiline_blocks(test_data)
    # print(yaml_output)



s = """

 top:
    amount: 10
    sort_by_diffculty: true
 apply:
    num_carries: 0
    operation: addition
    unique_numbers: true
    unique_digits: true
    shared_digits_between_numbers: true
    rules: 
        answer:
            validator: "lambda x: x % 5 == 0"
 xx amount: 3
  x instruct: true

 xxx amount: 2
  xx

 xxx amount: 1
  xx
   x

 xxx amount: 1
 xxx

   x masks: 1
   x 
   x

  xx masks: 2
  xx masking_allowed_in_answer: false
     mask_shared_number: true

"""


def parse_input(input_str):
    """
    Parse input string by separating x markers from content.
    
    Args:
        input_str (str): The input string to parse
        
    Returns:
        str: Formatted output with x markers at top followed by content
    """
    lines = trimdent(input_str).split('\n')
    
    x_markers = []
    content_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check if this line starts with an 'x' marker
        import re
        x_match = re.search(r'^(\s*x+)', line)
        
        if x_match:
            marker = x_match.group(1)
            # print([marker])
            x_markers.append(marker)
            
            # Find the actual content part after the marker
            key_value_match = re.search(r'^\s*x+\s+(.+)', line)
            if key_value_match:
                content = key_value_match.group(1)
                content_lines.append(content)
        else:
            # This is a line without an x marker
            content_lines.append(stripped)
    
    s = trimdent('\n'.join(x_markers))
    o = yamload('\n'.join(content_lines))
    o['template'] = s
    return o

def foo(s):
    s = trimdent(s)
    s, fm = extract_frontmatter(s)
    chunks = filtered(re.split('\n\n+', s))
    chunks = each(chunks, parse_input)
    apply = fm.get('apply')
    if apply:
        store = []
        for chunk in chunks:
            store.append(merge_dicts(apply, chunk))
        
    # return store 
    fm['contents'] = chunks
    return fm


print(dump_yaml_with_multiline_blocks(foo(s)))
