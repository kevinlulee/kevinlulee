
import nvim
from pprint import pprint
import vim
#
#
# repo = GitRepo('~/github/benlubas-vim-cmp/')
# print(repo.url)
# git_dirs = 
#
# git_dirs = fdfind(
#     dirs=['~/github'],
#     query=".git",
#     only_directories=True,
#     include_dirs=[".git"],
# )
# 
# 

import difflib

def highlight_diff_in_region(vim, original_text, new_text):
    """
    Highlights diff between two text blocks in the current buffer.
    - Deletions are highlighted in red
    - Additions are highlighted in green
    
    Args:
        vim: Neovim instance
        original_text: Original text in the region (list of lines)
        new_text: New text to compare against (list of lines)
    """
    # Get current buffer
    buffer = vim.current.buffer
    
    # Get current cursor position
    cursor_row, cursor_col = vim.current.window.cursor
    
    # Get selected region (start and end lines)
    # Assuming region is defined by marks '< and '> (visual selection)
    start_row = cursor_row - 1
    end_row = cursor_row - 1
    
    # Compute the diff
    differ = difflib.Differ()
    diff = list(differ.compare(original_text, new_text))
    
    # Process the diff to create highlighted lines
    highlighted_lines = []
    for line in diff:
        if line.startswith('  '):  # Unchanged line
            highlighted_lines.append(line[2:])
        elif line.startswith('- '):  # Deleted line
            highlighted_lines.append(f"[DEL]{line[2:]}[/DEL]")
        elif line.startswith('+ '):  # Added line
            highlighted_lines.append(f"[ADD]{line[2:]}[/ADD]")


    pprint(highlighted_lines)
    return 
    # Create highlight groups for additions and deletions
    if nvim.g.highlighted:
        print('already highlighted')
    else:
        nvim.g.highlighting = True
        vim.command('highlight DiffAddHighlight ctermfg=green guifg=#00FF00')
        vim.command('highlight DiffDeleteHighlight ctermfg=red guifg=#FF0000')
    
    # Create a namespace for our highlights
    namespace = vim.api.create_namespace('diff_highlights')
    
    
    # Replace the region with the highlighted diff
    buffer[start_row - 1:end_row] = highlighted_lines
    
    # Apply syntax highlighting by scanning for [ADD] and [DEL] markers
    for i, line in enumerate(buffer[start_row:start_row+len(highlighted_lines)], start=start_row):
        # Find all [ADD] and [DEL] markers and their content
        j = 0
        while j < len(line):
            if line[j:j+5] == "[ADD]":
                start_col = j
                end_marker = line.find("[/ADD]", start_col)
                if end_marker != -1:
                    buffer.add_highlight("DiffAddHighlight", i, start_col+5, end_marker, namespace)
                    # Skip ahead
                    j = end_marker + 6
                    continue
            elif line[j:j+5] == "[DEL]":
                start_col = j
                end_marker = line.find("[/DEL]", start_col)
                if end_marker != -1:
                    buffer.add_highlight("DiffDeleteHighlight", i, start_col+5, end_marker, namespace)
                    # Skip ahead
                    j = end_marker + 6
                    continue
            j += 1
    
    # Now remove the markers from the text
    for i, line in enumerate(buffer[start_row:start_row+len(highlighted_lines)], start=start_row):
        clean_line = (line.replace("[ADD]", "").replace("[/ADD]", "")
                         .replace("[DEL]", "").replace("[/DEL]", ""))
        buffer[i] = clean_line

def main():
    # Example usage
    # Get selected text
    try:
        start_row = vim.funcs.line('.')
        end_row = start_row + 1
        
        # Get original text from the selected region
        buffer = vim.current.buffer
        original_text = buffer[start_row - 1:end_row]
        
        # For demonstration purposes - replace with actual new text
        # In practice, this would come from another file or user input
        new_text = original_text.copy()
        if len(new_text) > 0:
            new_text[0] = "This is a modified line"
        if len(new_text) > 2:
            new_text.insert(2, "This is a new line added")
            
        # Apply diff highlighting
        print(original_text)
        print()
        print(new_text)
        print()
        highlight_diff_in_region(vim, original_text, new_text)
        
    except Exception as e:
        vim.command(f'echo "Error: {str(e)}"')

if __name__ == "__main__":
    main()


# abc
# abc
# line 131
# line 132
# line 133
# line 134




import pynvim
import difflib
from typing import List, Tuple

def highlight_diff_in_region(nvim):
    """
    Highlights diff between original text and new text in a selected region.
    - Deletions are highlighted in red
    - Additions are highlighted in green
    
    Args:
        nvim: Neovim instance
    """
    # Create highlight groups for additions and deletions
    nvim.command('highlight DiffAddHighlight ctermbg=green guibg=#CCFFCC')
    nvim.command('highlight DiffDeleteHighlight ctermbg=red guibg=#FFCCCC')
    
    # Create a namespace for our highlights
    namespace = nvim.api.create_namespace('diff_highlights')
    
    # Get current buffer
    buffer = nvim.current.buffer
    
    # Get selected region (start and end lines)
    try:
        start_row = nvim.funcs.getpos("'<")[1] - 1  # Convert to 0-indexed
        end_row = nvim.funcs.getpos("'>")[1] - 1    # Convert to 0-indexed
    except:
        # Fallback - use current cursor position
        cursor_row, _ = nvim.current.window.cursor
        start_row = cursor_row - 1
        end_row = cursor_row - 1
    
    # Get original text from the selected region
    original_text = get_buffer_range(buffer, start_row, end_row)
    
    # In a real plugin, we'd get new_text from somewhere (another buffer, file, etc.)
    # For example purposes, let's prompt the user
    nvim.command('let g:new_text = input("Enter new text (use \\n for newlines): ")')
    new_text_raw = nvim.vars['new_text']
    new_text = new_text_raw.split('\\n')
    
    # Generate the diff
    diff = list(difflib.unified_diff(original_text, new_text, n=0, lineterm=''))
    
    # Process the diff output
    diff_lines = []
    add_ranges = []  # Store (line_index, end_line_index) for additions
    del_ranges = []  # Store (line_index, end_line_index) for deletions
    
    line_idx = 0
    in_addition = False
    in_deletion = False
    add_start = 0
    del_start = 0
    
    # Skip headers (first 2 lines)
    for line in diff[2:]:
        if line.startswith('+'):
            if not in_addition:
                in_addition = True
                add_start = line_idx
            diff_lines.append(line[1:])
            line_idx += 1
        elif line.startswith('-'):
            if not in_deletion:
                in_deletion = True
                del_start = line_idx
            diff_lines.append(line[1:])
            line_idx += 1
        else:
            # End of an addition or deletion block
            if in_addition:
                add_ranges.append((add_start, line_idx - 1))
                in_addition = False
            if in_deletion:
                del_ranges.append((del_start, line_idx - 1))
                in_deletion = False
            
            # Normal line (might start with a space)
            if line.startswith(' '):
                line = line[1:]
            diff_lines.append(line)
            line_idx += 1
    
    # Handle ranges that extend to the end
    if in_addition:
        add_ranges.append((add_start, line_idx - 1))
    if in_deletion:
        del_ranges.append((del_start, line_idx - 1))
    
    # Replace the region with the diff lines
    set_buffer_range(buffer, start_row, end_row, diff_lines)
    
    # Apply highlighting to the ranges
    for start, end in add_ranges:
        for i in range(start, end + 1):
            abs_line_idx = start_row + i
            if abs_line_idx < len(buffer):  # Make sure we're within buffer bounds
                buffer.add_highlight("DiffAddHighlight", abs_line_idx, 0, -1, namespace)
    
    for start, end in del_ranges:
        for i in range(start, end + 1):
            abs_line_idx = start_row + i
            if abs_line_idx < len(buffer):  # Make sure we're within buffer bounds
                buffer.add_highlight("DiffDeleteHighlight", abs_line_idx, 0, -1, namespace)

def get_buffer_range(buffer, start_row, end_row):
    """
    Get a range of lines from a buffer
    
    Args:
        buffer: Neovim buffer object
        start_row: Starting line (0-indexed)
        end_row: Ending line (0-indexed)
    
    Returns:
        List of lines
    """
    return buffer[start_row:end_row+1]
    buffer[start_row:end_row+1] = lines

def set_buffer_range(buffer, start_row, end_row, lines):
    """
    Replace a range of lines in a buffer
    
    Args:
        buffer: Neovim buffer object
        start_row: Starting line (0-indexed)
        end_row: Ending line (0-indexed)
        lines: New lines to insert
    """

def plugin_command(nvim):
    """
    Main plugin command function that can be called from Neovim
    
    Args:
        nvim: Neovim instance
    """
    try:
        highlight_diff_in_region(nvim)
    except Exception as e:
        nvim.command(f'echo "Error: {str(e)}"')

# Example setup for a plugin
def setup_plugin(nvim):
    """
    Register the plugin command with Neovim
    
    Args:
        nvim: Neovim instance
    """
    nvim.command(
        '''
        command! HighlightDiff lua require('diff_highlighter').highlight_diff()
        '''
    )
