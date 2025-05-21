def get_structure(obj):
    """
    Returns:
        The structure representation of an object:
        
    Purpose:
        For instructing AI
        For generating dataclasses and typed dicts

    Example:
        {
          "name": "str",
          "description": "str",
          "items": [{
            "methods": [{
              "description": "str",
              "skip?": "bool",
              "signature?": "str",
              "name": "str"
            }]
          }]
        }
    """
    if isinstance(obj, dict):
        structure = {}
        for key, value in obj.items():
            structure[key] = get_structure(value)
        return structure
    elif isinstance(obj, (list, tuple)):
        if not obj:
            return []

        if all(isinstance(item, dict) for item in obj):
            # Collect all possible keys from all dictionaries
            all_keys = set()
            for item in obj:
                all_keys.update(item.keys())

            # Create a merged structure with all possible keys
            merged_structure = {}
            for key in all_keys:
                key_exists_in_all = all(key in item for item in obj)
                suffix = "" if key_exists_in_all else "?"

                # Get structure for this key from items that have it
                structures = [get_structure(item[key]) for item in obj if key in item]
                if structures:
                    merged_structure[f"{key}{suffix}"] = structures[0]

            return [merged_structure]
        elif all(isinstance(item, (tuple, list)) for item in obj):
            # For lists of lists, check the first non-empty list
            for item in obj:
                if item:
                    return [get_structure(item)]
            return [[]]
        else:
            # If items are primitive or have different structures
            type_set = set(type(item).__name__ for item in obj)
            if len(type_set) == 1:
                return [list(type_set)[0]]
            else:
                return ["any"]
    else:
        return type(obj).__name__
