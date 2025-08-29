import kevinlulee as kx


from typing import List, Dict, Any, Callable, Optional, Union
import re
def extract_table_from_str(text: str, coerce: Optional[Dict[str, Callable]] = None, 
                           default_coerce: Optional[Callable] = kx.smart_coerce) -> List[Dict[str, Any]]:
    """
    Extract table data from text snippets, intelligently skipping prose text.
    
    Args:
        text (str): The text containing the table (may include prose)
        coerce (dict, optional): Dictionary mapping column names to coercion functions
        default_coerce (callable, optional): Default coercion function for unspecified columns
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries representing table rows
    """
    lines = [line.rstrip() for line in text.split('\n')]
    
    # Find table boundaries by detecting aligned pipes
    table_start, table_end = find_table_boundaries(lines)
    
    if table_start == -1:
        # No table found, try fallback methods
        return extract_fallback_table(lines, coerce, default_coerce)
    
    # Extract table lines
    table_lines = lines[table_start:table_end + 1]
    
    # Remove separator lines (lines with only dashes, pipes, spaces)
    content_lines = []
    for line in table_lines:
        stripped = line.strip()
        if stripped and not re.match(r'^[-|\s+=]+$', stripped):
            content_lines.append(line)
    
    if len(content_lines) < 2:  # Need at least header + 1 data row
        return []
    
    return parse_pipe_delimited_table(content_lines, coerce, default_coerce)

def find_table_boundaries(lines: List[str]) -> tuple[int, int]:
    """
    Find the start and end of a table by detecting aligned pipes.
    
    Args:
        lines (List[str]): All lines of text
        
    Returns:
        tuple[int, int]: (start_line_index, end_line_index) or (-1, -1) if no table found
    """
    pipe_positions = {}  # line_index -> list of pipe positions
    
    # Find all pipe positions in each line
    for i, line in enumerate(lines):
        pipes = [m.start() for m in re.finditer(r'\|', line)]
        if len(pipes) >= 1:  # At least one pipe
            pipe_positions[i] = pipes
    
    if len(pipe_positions) < 2:
        return -1, -1
    
    # Group consecutive lines with similar pipe positions
    table_groups = []
    current_group = []
    
    sorted_lines = sorted(pipe_positions.keys())
    
    for line_idx in sorted_lines:
        if not current_group:
            current_group = [line_idx]
        else:
            # Check if this line's pipes align with the previous lines
            prev_line = current_group[-1]
            if (line_idx - prev_line <= 2 and  # Lines are close together
                pipes_are_aligned(pipe_positions[prev_line], pipe_positions[line_idx])):
                current_group.append(line_idx)
            else:
                # Start a new group
                if len(current_group) >= 2:  # Valid table needs at least 2 lines
                    table_groups.append(current_group)
                current_group = [line_idx]
    
    # Don't forget the last group
    if len(current_group) >= 2:
        table_groups.append(current_group)
    
    # Find the largest table group
    if not table_groups:
        return -1, -1
    
    largest_group = max(table_groups, key=len)
    return min(largest_group), max(largest_group)

def pipes_are_aligned(pipes1: List[int], pipes2: List[int], tolerance: int = 3) -> bool:
    """
    Check if pipe positions between two lines are roughly aligned.
    
    Args:
        pipes1, pipes2: Lists of pipe positions
        tolerance: Maximum deviation allowed for alignment
        
    Returns:
        bool: True if pipes are aligned
    """
    if len(pipes1) != len(pipes2):
        return False
    
    for p1, p2 in zip(pipes1, pipes2):
        if abs(p1 - p2) > tolerance:
            return False
    
    return True

def parse_pipe_delimited_table(lines: List[str], coerce: Optional[Dict[str, Callable]] = None,
                              default_coerce: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    Parse pipe-delimited table lines into list of dictionaries.
    
    Args:
        lines: Table lines with pipe delimiters
        coerce: Column-specific coercion functions
        default_coerce: Default coercion function
        
    Returns:
        List of dictionaries representing rows
    """
    if not lines:
        return []
    
    # Extract header and data
    header_line = lines[0]
    data_lines = lines[1:]
    
    # Parse header
    headers = [col.strip() for col in header_line.split('|')]
    headers = [h for h in headers if h]  # Remove empty headers
    
    if not headers:
        return []
    
    # Parse data rows
    rows = []
    for line in data_lines:
        cols = [col.strip() for col in line.split('|')]
        cols = [c for c in cols if c or len([c for c in cols if c]) == 1]  # Keep empty if it's the only non-empty
        
        # Skip lines that don't have the right number of columns (roughly)
        if len(cols) < len(headers) - 1:  # Allow some flexibility
            continue
        
        # Pad with empty strings if needed
        while len(cols) < len(headers):
            cols.append('')
        
        # Truncate if too many columns
        cols = cols[:len(headers)]
        
        # Create row dictionary with coercion
        row_dict = {}
        for i, header in enumerate(headers):
            value = cols[i] if i < len(cols) else ''
            
            # Apply coercion
            coerced_value = apply_coercion(value, header, coerce, default_coerce)
            row_dict[header] = coerced_value
        
        rows.append(row_dict)
    
    return rows

def extract_fallback_table(lines: List[str], coerce: Optional[Dict[str, Callable]] = None,
                          default_coerce: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    Fallback method to extract tables when pipes aren't found.
    Looks for consistent spacing patterns.
    
    Args:
        lines: All text lines
        coerce: Column-specific coercion functions
        default_coerce: Default coercion function
        
    Returns:
        List of dictionaries representing rows
    """
    # Look for lines that might be table rows (contain multiple words with consistent spacing)
    potential_table_lines = []
    
    for line in lines:
        stripped = line.strip()
        if (stripped and 
            not re.match(r'^[-=\s]+$', stripped) and  # Not just separators
            len(stripped.split()) >= 2 and  # At least 2 words
            not stripped.endswith('.') and  # Probably not prose
            not stripped.endswith(',') and
            not stripped.endswith(';')):
            potential_table_lines.append(line)
    
    if len(potential_table_lines) < 2:
        return []
    
    return extract_table_by_spacing(potential_table_lines, coerce, default_coerce)

def extract_table_by_spacing(lines: List[str], coerce: Optional[Dict[str, Callable]] = None,
                            default_coerce: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    Extract table data by analyzing column spacing patterns.
    """
    if not lines:
        return []
    
    # Find column boundaries by analyzing spacing
    max_length = max(len(line) for line in lines)
    padded_lines = [line.ljust(max_length) for line in lines]
    
    # Find positions where most lines have spaces (potential column boundaries)
    column_boundaries = []
    for pos in range(1, max_length - 1):
        space_count = 0
        char_count = 0
        
        for line in padded_lines:
            if pos < len(line):
                if line[pos].isspace():
                    space_count += 1
                else:
                    char_count += 1
        
        # If most lines have a space here, and there are characters before/after
        if (space_count >= len(lines) * 0.6 and char_count > 0 and
            any(not line[pos-1].isspace() for line in padded_lines if pos-1 < len(line)) and
            any(not line[pos+1].isspace() for line in padded_lines if pos+1 < len(line))):
            column_boundaries.append(pos)
    
    # Clean up boundaries (remove those too close together)
    cleaned_boundaries = []
    for boundary in column_boundaries:
        if not cleaned_boundaries or boundary - cleaned_boundaries[-1] > 3:
            cleaned_boundaries.append(boundary)
    
    if not cleaned_boundaries:
        # Fallback: look for sequences of multiple spaces
        for line in lines[:3]:  # Check first few lines
            matches = list(re.finditer(r'\s{2,}', line))
            if matches:
                cleaned_boundaries = [match.start() for match in matches]
                break
    
    if not cleaned_boundaries:
        return []
    
    # Extract columns using boundaries
    boundaries = [0] + cleaned_boundaries + [max_length]
    
    rows = []
    headers = []
    
    for i, line in enumerate(lines):
        row_data = []
        for j in range(len(boundaries) - 1):
            start = boundaries[j]
            end = boundaries[j + 1]
            cell = line[start:end].strip()
            row_data.append(cell)
        
        if i == 0:
            # First row becomes headers
            headers = [cell if cell else f"column_{j+1}" for j, cell in enumerate(row_data)]
        else:
            # Create row dictionary with coercion
            row_dict = {}
            for k, header in enumerate(headers):
                value = row_data[k] if k < len(row_data) else ''
                coerced_value = apply_coercion(value, header, coerce, default_coerce)
                row_dict[header] = coerced_value
            
            rows.append(row_dict)
    
    return rows

def apply_coercion(value: str, column_name: str, coerce: Optional[Dict[str, Callable]] = None,
                  default_coerce: Optional[Callable] = None) -> Any:
    """
    Apply coercion function to a value.
    
    Args:
        value: The string value to coerce
        column_name: Name of the column
        coerce: Column-specific coercion functions
        default_coerce: Default coercion function
        
    Returns:
        Coerced value or original value if coercion fails
    """
    # Try column-specific coercion first
    if coerce and column_name in coerce:
        try:
            return coerce[column_name](value)
        except (ValueError, TypeError, AttributeError):
            pass
    
    # Try default coercion
    if default_coerce:
        try:
            return default_coerce(value)
        except (ValueError, TypeError, AttributeError):
            pass
    
    # Return original value if no coercion works
    return value
