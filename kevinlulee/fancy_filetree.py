def fancy_filetree(root_dir):
    """
    Generates a string representation of the file tree for a given directory,
    expanding the directory path using os.path.expanduser().

    Args:
        root_dir (str): The path to the root directory (will be expanded).

    Returns:
        str: A string representing the fancy file tree. Returns an error message
             if the provided path is not a valid directory after expansion.
    """
    if isinstance(root_dir, (list, tuple)):
        return fancy_filetree_from_list(root_dir)
    # Expand the root directory path
    expanded_root = os.path.expanduser(root_dir)
    
    # Check if the expanded path is a valid directory
    if not os.path.isdir(expanded_root):
        return ''
    
    # Initialize the result string with the root directory
    result = os.path.basename(expanded_root) + "/\n"
    ignore = create_gitignore_matcher(expanded_root)
    
    # Recursively build the tree
    def build_tree(directory, prefix=""):
        entries = sorted(os.listdir(directory))
        count = len(entries)
        
        tree_str = ""
        for i, entry in enumerate(entries):
            full_path = os.path.join(directory, entry)
            if ignore(full_path):
                continue
            is_last = i == count - 1
            
            # Select the appropriate connector
            connector = "└── " if is_last else "├── "
            
            # Determine if entry is a directory
            if os.path.isdir(full_path):
                tree_str += f"{prefix}{connector}{entry}/\n"
                # Determine the new prefix for the next level
                next_prefix = prefix + ("    " if is_last else "│   ")
                tree_str += build_tree(full_path, next_prefix)
            else:
                tree_str += f"{prefix}{connector}{entry}\n"
        
        return tree_str
    
    # Start building the tree from the root
    result += build_tree(expanded_root)
    return result



import os
from collections import defaultdict

class FileTreeNode:
    def __init__(self, name, is_file=False):
        self.name = name
        self.is_file = is_file
        self.children = {}
        
    def add_child(self, name, is_file=False):
        if name not in self.children:
            self.children[name] = FileTreeNode(name, is_file)
        return self.children[name]

def build_file_tree(file_paths):
    """
    Build a file tree from a list of file paths.
    
    Args:
        file_paths: List of file paths (strings)
    
    Returns:
        FileTreeNode: Root node of the file tree
    """
    root = FileTreeNode("root")
    
    for path in file_paths:
        # Normalize path separators and split into parts
        path = path.replace('/home/kdog3682/projects', '')
        parts = path.replace('\\', '/').strip('/').split('/')
        current_node = root
        
        # Traverse/create the path
        for i, part in enumerate(parts):
            if not part:  # Skip empty parts
                continue
            
            # Check if this is the last part (file)
            is_file = (i == len(parts) - 1)
            current_node = current_node.add_child(part, is_file)
    
    return root

def print_tree(node, prefix="", is_last=True):
    """
    Generate a string representation of the file tree in a visual format.
    
    Args:
        node: FileTreeNode to print
        prefix: Current indentation prefix
        is_last: Whether this is the last child at current level
    
    Returns:
        str: String representation of the tree
    """
    lines = []
    
    if node.name != "root":
        # Choose the appropriate tree symbol
        symbol = "└── " if is_last else "├── "
        lines.append(f"{prefix}{symbol}{node.name}")
        
        # Update prefix for children
        new_prefix = prefix + ("    " if is_last else "│   ")
    else:
        new_prefix = prefix
    
    # Sort children: directories first, then files
    children = sorted(node.children.items(), key=lambda x: (x[1].is_file, x[0]))
    
    for i, (name, child_node) in enumerate(children):
        is_last_child = (i == len(children) - 1)
        lines.extend(print_tree(child_node, new_prefix, is_last_child))
    
    return lines

def get_tree_string(node):
    """
    Get the file tree as a single string.
    
    Args:
        node: FileTreeNode (root of the tree)
    
    Returns:
        str: Complete tree as a formatted string
    """
    lines = print_tree(node)
    return '\n'.join(lines)
    """
    Convert the tree to a nested dictionary structure.
    
    Args:
        node: FileTreeNode to convert
    
    Returns:
        dict: Nested dictionary representation of the tree
    """
    if node.is_file:
        return node.name
    
    result = {}
    for name, child in node.children.items():
        result[name] = get_tree_dict(child)
    
    return result

# Example usage

def fancy_filetree_from_list(custom_files):
    custom_tree = build_file_tree(custom_files)
    custom_tree_string = get_tree_string(custom_tree)[2:]
    return custom_tree_string
