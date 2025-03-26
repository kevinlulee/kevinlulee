def dotaccess(val, key):
    parts = key.split(".")
    for part in parts:
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return None
    return val


def smallify(arr):
    return arr[0] if len(arr) == 1 else arr
