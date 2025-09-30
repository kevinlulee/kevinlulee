import kevinlulee as kx
from typing import Dict, List, Literal

# Optional formatting helpers (assumed available)

# -------------------------
# Types
# -------------------------

TailWindScaleNumber = Literal[
    "50",
    "100",
    "200",
    "300",
    "400",
    "500",
    "600",
    "700",
    "800",
    "900",
]

PaletteTheme = Literal[
    "deep-ocean",
    "seafoam",
    "twilight",
    "glacier",
    "forest",
    "fog",
    "ember",
    "citrus",
    "dusk-bay",
    "aurora",
    "orchid",
    "amethyst",
    "rose-dusk",
    "crimson",
    "spring-meadow",
    "shoreline",
    "desert-canyon",
    "sunset",
]

# -------------------------
# Paths
# -------------------------

COLORS_DIR = "~/data/colors"

PATHS = {
    # JSON sources (consolidated)
    "palette_map": f"{COLORS_DIR}/colorbrewer-palette-map.json",
    "colorbrewer_tailwind": f"{COLORS_DIR}/colorbrewer-tailwind.json",
    "colorbrewer_sequential": f"{COLORS_DIR}/colorbrewer-sequential.json",
    # Generated Typst outputs
    "typ_nested": f"{COLORS_DIR}/colorbrewer-themes-nested.typ",
    "typ_flat": f"{COLORS_DIR}/colorbrewer-themes-flat.typ",
}

# Legacy locations -> new locations (for migration)
LEGACY_TO_NEW = {
    "~/data/pallete-map.json": PATHS["palette_map"],  # legacy misspelling
    "~/data/sequential-colorbrewer.tailwind.json": PATHS[
        "colorbrewer_tailwind"
    ],
    "~/data/sequential-colorbrewer.json": PATHS["colorbrewer_sequential"],
}

# -------------------------
# Migration
# -------------------------


def migrate_color_files() -> Dict[str, str]:
    """
    Move legacy color data files into the consolidated colors directory with improved names.

    Returns
    -------
    Dict[str, str]
        A mapping of source -> destination for all moves attempted.

    Notes
    -----
    - Uses `kx.mvfile`, which auto-creates missing directories and asserts as needed.
    - Idempotent intent: if you've already moved files, calling again should be a no-op if `kx.mvfile`
      respects identical src/dst semantics.
    """
    moved = {}
    for src, dst in LEGACY_TO_NEW.items():
        kx.mvfile(src, dst)
        moved[src] = dst
    return moved


# -------------------------
# Data loading
# -------------------------


def records_to_mapping(
    data: List[dict],
    key_field: str | None = None,
    value_field: str | None = None,
) -> Dict[str, dict | list | str]:
    """
    Convert a list of records (dicts) into a mapping.

    Parameters
    ----------
    data : List[dict]
        Records that include fields for keys and values.
    key_field : str | None
        Field name to use as the dictionary key. If `None`, prefers "name", then "key".
    value_field : str | None
        Field name to use as the dictionary value. If `None`, tries "value", then "colors", then "text", then "scale".

    Returns
    -------
    Dict[str, dict | list | str]
        Mapping from `key_field` value to `value_field` value.

    Raises
    ------
    AssertionError
        If a suitable key or value field cannot be determined.
    """
    keys = data[0].keys()

    if not key_field:
        if "name" in keys:
            key_field = "name"
        elif "key" in keys:
            key_field = "key"

    if not value_field:
        if "value" in keys:
            value_field = "value"
        elif "colors" in keys:
            value_field = "colors"
        elif "text" in keys:
            value_field = "text"
        elif "scale" in keys:
            value_field = "scale"

    assert key_field, "no key_field"
    assert value_field, "no value_field"

    return {d[key_field]: d[value_field] for d in data}


# -------------------------
# Color accessors
# -------------------------


def get_palette_scale(theme: PaletteTheme, size: int) -> List[str]:
    """
    Return a sequential ColorBrewer palette (list of hex colors) for a theme and size.

    Parameters
    ----------
    theme : PaletteTheme
        Name of the base palette (e.g., "deep-ocean").
    size : int
        Number of colors in the sequential scale (e.g., 3..9 for ColorBrewer sequential).

    Returns
    -------
    List[str]
        List of color hex strings for the requested scale.
    """
    return COLORBREWER_SEQUENTIAL[theme][str(size)]


def get_theme_scale(theme: PaletteTheme) -> Dict[TailWindScaleNumber, str]:
    """
    Return the Tailwind-like scale mapping for a theme.

    Parameters
    ----------
    theme : PaletteTheme
        Name of the base palette (e.g., "deep-ocean").

    Returns
    -------
    Dict[TailWindScaleNumber, str]
        Mapping from Tailwind scale step to a hex color (e.g., {"50": "#...", "100": "#...", ...}).
    """
    return COLORBREWER_TAILWIND[theme]


def get_theme_color(theme: PaletteTheme, token: str) -> str:
    """
    Resolve a color value for a theme using a token syntax.

    Token formats
    -------------
    - "primary.100"     -> color from the theme's scale at step 100
    - "secondary.200"   -> color from the complement theme's scale at step 200
    - "<primary.500>"   -> same as above; XML-like brackets are stripped if present
    - "twilight.300"    -> explicit theme override: use that theme's scale at step 300

    Parameters
    ----------
    theme : PaletteTheme
        The current theme context.
    token : str
        Dot-separated selector as above.

    Returns
    -------
    str
        Hex color string (e.g., "#AABBCC").
    """
    if kx.is_xml(token):
        token = token[1:-1]

    parts = token.split(".")
    match len(parts):
        case 1:
            raise Exception("requires 2 parts: '<namespace>.<step>'")
        case 2:
            ns, step = parts
            match ns:
                case "primary":
                    return COLORBREWER_TAILWIND[theme][step]
                case "secondary":
                    return COLORBREWER_TAILWIND[
                        PALETTE_MAP[theme]["complement"]
                    ][step]
                case _:
                    # Treat the namespace as an explicit theme name
                    return COLORBREWER_TAILWIND[ns][step]
        case _:
            raise Exception("unsupported token format")


# -------------------------
# Typst exports
# -------------------------


def export_typst_themes_nested() -> str:
    """
    Export a Typst file with nested theme records:
        theme -> { primary: {50:#..,100:#..,...}, secondary: {50:#..,100:#..,...} }

    Returns
    -------
    str
        The path to the generated Typst file.
    """
    from codefmt.typst import typstfmt

    store = {}
    for theme, scale in COLORBREWER_TAILWIND.items():
        comp_theme = PALETTE_MAP[theme]["complement"]
        store[theme] = dict(
            primary=scale,
            secondary=COLORBREWER_TAILWIND[comp_theme],
        )

    decls = []
    for name, value in store.items():
        decls.append(typstfmt.decl(name, value, coerce=False, top_level=True))

    text = kx.join_text(decls)
    kx.writefile(PATHS["typ_nested"], text)
    return PATHS["typ_nested"]


def export_typst_themes_flat() -> str:
    """
    Export a Typst file with flattened theme keys:
        theme -> {
          primary-50: rgb("#..."), ... primary-900: rgb("#..."),
          secondary-50: rgb("#..."), ... secondary-900: rgb("#...")
        }

    Returns
    -------
    str
        The path to the generated Typst file.
    """

    def rgb_expr(hex_color: str):
        return kx.real(f'rgb("{hex_color}")')

    from codefmt.typst import typstfmt

    store: Dict[str, Dict[str, str]] = {}

    for theme, scale in COLORBREWER_TAILWIND.items():
        comp_theme = PALETTE_MAP[theme]["complement"]
        comp_scale = COLORBREWER_TAILWIND[comp_theme]

        flat: Dict[str, str] = {}
        for step, hex_color in scale.items():
            flat[f"primary-{step}"] = rgb_expr(hex_color)
        for step, hex_color in comp_scale.items():
            flat[f"secondary-{step}"] = rgb_expr(hex_color)

        store[theme] = flat

    decls = []
    for name, value in store.items():
        decls.append(typstfmt.decl(name, value, coerce=False, top_level=True))

    text = kx.join_text(decls)
    kx.writefile(PATHS["typ_flat"], text)
    return PATHS["typ_flat"]


# -------------------------
# Sample usage (no CLI)
# -------------------------

# if __name__ == "__main__":
    # Ensure files are in the new locations before loading.
    # (Sample call; comment out if you prefer a manual migration trigger.)
    # migrate_color_files()

    # Load consolidated data
PALETTE_MAP = kx.readfile(
    PATHS["palette_map"]
)  # theme -> { complement: <theme>, ... }
COLORBREWER_TAILWIND = records_to_mapping(
    kx.readfile(PATHS["colorbrewer_tailwind"]), value_field="scale"
)  # theme -> { "50": "#...", "100": "#...", ... }
COLORBREWER_SEQUENTIAL = records_to_mapping(
    kx.readfile(PATHS["colorbrewer_sequential"]), value_field="colors"
)  # theme -> { "3": [#..,#..,#..], "4": [...], ... }
