from __future__ import annotations
import kevinlulee as kx

def expand_dot_notation(config: dict) -> dict:
    """
    Expand dot notation keys into nested dicts.

    Example:
        {'body.row_groups.0': VISIBLE} -> {'body': {'row_groups': {0: VISIBLE}}}
    """
    result = {}
    if not config:
        return result

    for key, value in config.items():
        if isinstance(key, str) and "." in key:
            parts = key.split(".")
            current = result

            for part in parts[:-1]:
                if part.isdigit():
                    part = int(part)
                if part not in current:
                    current[part] = {}
                current = current[part]

            final_key = parts[-1]
            if final_key.isdigit():
                final_key = int(final_key)
            current[final_key] = value
        else:
            if isinstance(value, dict):
                value = expand_dot_notation(value)
            result[key] = value

    return result
