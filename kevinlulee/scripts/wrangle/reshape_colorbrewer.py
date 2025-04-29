def rgb_to_hex(rgb: list[int, int, int]):
  if not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
    raise Exception('invalid rgb')
  for val in rgb:
    if not isinstance(val, int) or not 0 <= val <= 255:
        raise Exception('invalid rgb')

  return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def reshape_colorbrewer_data(data: dict):
    """
        source: /mnt/chromeos/MyFiles/Downloads/colorbrewer.json
        desc: 
            creates a more readable colorbrewer dataset from the above source
            (a flat array of objects)
    """
    store = []
    for category, contents in data.items():
        for theme, entries in contents.items():
            colors = {}
            last_amount = None
            for amount, color_set in entries.items():
                rgbs = [rgb_to_hex(c) for c in  color_set]
                colors[amount] = rgbs
                last_amount = amount

            payload = {
                'category': category,
                'theme': theme,
                'amount': last_amount,
                'colors': colors,
            }
            store.append(payload)
    return store

