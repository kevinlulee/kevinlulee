# active
from kevinlulee import *
from pprint import pprint

# to ascii
# also need to do the thing where it becomes 

def parse_diagram(diagram):
    lines = trimdent(diagram).split('\n')
    result = []
    
    for y, line in enumerate(lines):
        x = 0
        while x < len(line):
            char = line[x]
            if char.isdigit() or char.isalpha():
                value = char
                x += 1
                result.append({"value": value, "pos": (x-1, y)})
            elif char == "(":
                props_start = x
                props_content = ""
                paren_count = 1
                x += 1
                while x < len(line) and paren_count > 0:
                    if line[x] == "(":
                        paren_count += 1
                    elif line[x] == ")":
                        paren_count -= 1
                    
                    if paren_count > 0 or line[x] != ")":
                        props_content += line[x]
                    x += 1
                
                # Parse the properties
                properties = {}
                if props_content:
                    prop_pairs = props_content.split(',')
                    for pair in prop_pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            properties[key] = value
                
                # Find the element this property belongs to
                if result and 'properties' not in result[-1]:
                    result[-1]['properties'] = properties
            elif char == "-":
                # Check if it's a line of dashes
                line_length = 1
                x += 1
                while x < len(line) and line[x] == "-":
                    line_length += 1
                    x += 1
                
                if line_length >= 2:
                    result.append({
                        "value": "line", 
                        "pos": (x - line_length, y), 
                        "length": line_length
                    })
                else:
                    # It's a minus sign
                    result.append({"value": "-", "pos": (x - 1, y)})
            elif char in "+-/*":
                value = char
                x += 1
                result.append({"value": value, "pos": (x-1, y)})
            else:
                # Skip whitespace or other characters
                x += 1
    
    return result


diagram = '''


3451
 121
+ 11
----


'''



pprint(parse_diagram(diagram))
