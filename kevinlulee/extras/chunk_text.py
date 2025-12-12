import re
from typing import List
import kevinlulee as kx


def chunk_text(text: str) -> List[str]:
    """
    Chunk text based on explicit section breaks or newlines.
    
    Explicit section breaks are paired lines matching ^(-+|_+) *$
    Between paired boundaries, text stays together.
    Outside boundaries, text is chunked by empty lines.
    
    Args:
        text: The input text to chunk
        
    Returns:
        List of text chunks
    """
    lines = text.split('\n')
    break_pattern = re.compile(r'^(-+|_+) *$')
    
    chunks = []
    current_chunk = []
    inside_boundaries = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if break_pattern.match(line):
            # Found a boundary marker
            if not inside_boundaries:
                # Starting a bounded section
                # First, save any accumulated chunk
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                inside_boundaries = True
            else:
                # Ending a bounded section
                # Save the bounded chunk
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                inside_boundaries = False
        else:
            # Regular line
            if inside_boundaries:
                # Inside boundaries - accumulate everything
                current_chunk.append(line)
            else:
                # Outside boundaries - split by empty lines
                if line.strip():  # Non-empty line
                    current_chunk.append(line)
                else:  # Empty line
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                        current_chunk = []
        
        i += 1
    
    # Add any remaining chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


# Test with your example
if __name__ == "__main__":
    # Your exact example - checking if there's an empty line between c and d
    test_text = """
a

b
_
c_a

d_asd

asd


ill show you.
it starts like this:

short = d.get_short_form_question()
long = d.get_long_form_question()

g = Flex(short, long)


a
_
e

f
"""
    result = chunk_text(test_text)
    print(kx.ascii.side_by_side(test_text, "\n---\n".join(result)))
