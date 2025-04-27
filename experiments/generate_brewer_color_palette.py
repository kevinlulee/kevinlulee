# todo: get the colorbrewer palletes



def generate_palette(size, palette_type="RdYlBu"):
    """
    Generate a color palette of the specified size using the established index mapping pattern.
    
    Args:
        size (int): The size of the palette (3-11)
        palette_type (str): The type of palette to generate ("RdYlBu" or "RdBu")
        
    Returns:
        list: A list of RGB color values as strings
    """

    index_mappings = {
        3: [1, 5, 8],  # Center indices for small palette
        4: [0, 3, 7, 10],  # Distributed without center point
        5: [0, 3, 5, 7, 10],  # Includes center point
        6: [0, 1, 3, 7, 8, 10],  # More granular without center
        7: [0, 1, 3, 5, 7, 8, 10],  # Includes center point
        8: [0, 1, 2, 3, 7, 8, 9, 10],  # Further granularity without center
        9: [0, 1, 2, 3, 5, 7, 8, 9, 10],  # Includes center point
        10: [0, 1, 2, 3, 4, 6, 7, 8, 9, 10],  # Almost complete
        11: list(range(11))  # Complete palette
    }
    
    # Validate input
    if size < 3 or size > 11:
        raise ValueError("Palette size must be between 3 and 11")
    
    if palette_type not in palettes:
        raise ValueError(f"Unknown palette type: {palette_type}")
    
    full_palette = palettes[palette_type]
    indices = index_mappings.get(size)
    result = [full_palette[idx] for idx in indices]
    return result
