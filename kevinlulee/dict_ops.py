def find_in_json(json_data, validator_func, find_all=False):
    """
    Recursively traverse a JSON structure (dict or list) to find a dictionary 
    or all dictionaries that satisfy the validator function.
    
    Args:
        json_data: A JSON structure (dict or list)
        validator_func: A callback function that takes a dict and returns True if it meets criteria
        find_all: If True, find all matching dictionaries, if False, return on first match
    
    Returns:
        If find_all is False: The first dict that meets the validator criteria, or None if no match found
        If find_all is True: A list of all dicts that meet the validator criteria, or empty list if no matches
    """
    results = [] if find_all else None
    
    def finder(data):
        # Base case: if data is None
        if data is None:
            return None
        
        # If the current item is a dictionary
        if isinstance(data, dict):
            # Check if this dictionary meets the criteria
            if validator_func(data):
                if find_all:
                    results.append(data)
                else:
                    return data
            
            # If not, search in each value of the dictionary
            for value in data.values():
                result = finder(value)
                if result is not None and not find_all:
                    return result
        
        # If the current item is a list
        elif isinstance(data, list):
            # Search in each item of the list
            for item in data:
                result = finder(item)
                if result is not None and not find_all:
                    return result
        
        # If we've checked everything and found nothing
        return None
    
    if find_all:
        finder(json_data)
        return results
    else:
        return finder(json_data)



# Example usage with your specific validator case:
def has_fields_and_children(d):
    """
    Validator function to check if a dict has both 'fields' and 'children' keys
    with non-empty values.
    """
    return (isinstance(d, dict) and 
            'fields' in d and d['fields'] and 
            'children' in d and d['children'])


# Sample JSON data for testing
sample_data = {
    "name": "root",
    "level1": {
        "info": "some info",
        "items": [
            {"name": "item1"},
            {"name": "item2", 
             "nested": {
                 "fields": [1, 2, 3],
                 "children": ["a", "b", "c"]
             }
            },
            {"name": "item3"}
        ]
    }
}

# Find a dict with fields and children
# result = find_in_json(kx.readfile(python_node_types_json), has_fields_and_children, find_all=True)


# class ItemCoder:
#     system = ''
#     def map_func(self, item):
#         prompt = 'write a '

# kx.clip(result)  # Should print the nested dict with fields


