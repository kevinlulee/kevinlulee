import kevinlulee as kx
from string import ascii_lowercase
from typing import Dict, List, Union
from codefmt.python import pythonfmt
from typing import Literal
PaletteValue = Literal[
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

PALLETE_MAP = {
  "spring-meadow": {
    "complement": "shoreline",
    "companions": [
      "desert-canyon",
      "ember",
      "forest",
      "glacier"
    ]
  },
  "forest": {
    "complement": "deep-ocean",
    "companions": [
      "spring-meadow",
      "desert-canyon",
      "glacier",
      "seafoam"
    ]
  },
  "glacier": {
    "complement": "fog",
    "companions": [
      "forest",
      "spring-meadow",
      "seafoam",
      "aurora"
    ]
  },
  "seafoam": {
    "complement": "rose-dusk",
    "companions": [
      "glacier",
      "forest",
      "aurora",
      "dusk-bay"
    ]
  },
  "aurora": {
    "complement": "crimson",
    "companions": [
      "seafoam",
      "glacier",
      "dusk-bay",
      "twilight"
    ]
  },
  "dusk-bay": {
    "complement": "sunset",
    "companions": [
      "aurora",
      "seafoam",
      "twilight",
      "amethyst"
    ]
  },
  "twilight": {
    "complement": "citrus",
    "companions": [
      "dusk-bay",
      "aurora",
      "amethyst",
      "orchid"
    ]
  },
  "amethyst": {
    "complement": "ember",
    "companions": [
      "twilight",
      "dusk-bay",
      "orchid",
      "shoreline"
    ]
  },
  "orchid": {
    "complement": "desert-canyon",
    "companions": [
      "amethyst",
      "twilight",
      "shoreline",
      "deep-ocean"
    ]
  },
  "shoreline": {
    "complement": "spring-meadow",
    "companions": [
      "orchid",
      "amethyst",
      "deep-ocean",
      "fog"
    ]
  },
  "deep-ocean": {
    "complement": "forest",
    "companions": [
      "shoreline",
      "orchid",
      "fog",
      "rose-dusk"
    ]
  },
  "fog": {
    "complement": "glacier",
    "companions": [
      "deep-ocean",
      "shoreline",
      "rose-dusk",
      "crimson"
    ]
  },
  "rose-dusk": {
    "complement": "seafoam",
    "companions": [
      "fog",
      "deep-ocean",
      "crimson",
      "sunset"
    ]
  },
  "crimson": {
    "complement": "aurora",
    "companions": [
      "rose-dusk",
      "fog",
      "sunset",
      "citrus"
    ]
  },
  "sunset": {
    "complement": "dusk-bay",
    "companions": [
      "crimson",
      "rose-dusk",
      "citrus",
      "ember"
    ]
  },
  "citrus": {
    "complement": "twilight",
    "companions": [
      "sunset",
      "crimson",
      "ember",
      "desert-canyon"
    ]
  },
  "ember": {
    "complement": "amethyst",
    "companions": [
      "citrus",
      "sunset",
      "desert-canyon",
      "spring-meadow"
    ]
  },
  "desert-canyon": {
    "complement": "orchid",
    "companions": [
      "ember",
      "citrus",
      "spring-meadow",
      "forest"
    ]
  }
}

class ColorBrewer:
    def __init__(self):
        self.data = kx.readfile("~/data/sequential-colorbrewer.json")

    def get(self, x: str) -> "ColorBrewerSlice":
        def foobar(entry):
            key = entry["key"]
            return all(el in key for el in x)

        validator = kx.testf(x, key="name") if kx.is_string(x) else foobar
        entry = kx.find(self.data, validator)
        return ColorBrewerSlice(entry)

    def get_theme(self, key: PaletteValue):
        return ColorBrewerTheme(key)
        


from typing import Dict, List, Union, overload, Literal
from string import ascii_lowercase
from codefmt.python import pythonfmt

class ColorBrewerSlice:
    TONE_NAMES = ("lightest", "lighter", "light", "dark", "darker", "darkest", "normal")
    _TONE_OFFSETS = {
        "lightest": 0,  # leftmost (light end)
        "lighter": 1,
        "light": 2,
        "normal": 3,
        "dark": -3,
        "darker": -2,
        "darkest": -1,  # rightmost (dark end)
    }

    def __init__(self, entry, size: int = 7):
        self.colors: Dict[str, List[str]] = entry["colors"]
        self.name = entry["name"]
        self.set_size(size)

    def set_size(self, size: int) -> "ColorBrewerSlice":
        self.size = int(size)
        self.items = self.colors[str(self.size)]
        return self

    @property
    def letters(self) -> str:
        return ascii_lowercase[: self.size]

    def _indices_for(self, name: str) -> List[int]:
        return [self.letters.index(ch) for ch in name]

    def _tone_index(self, tone: str) -> int:
        off = self._TONE_OFFSETS[tone]
        idx = off if off >= 0 else self.size + off
        # clamp to [0, size-1] so small palettes still work
        if idx < 0:
            idx = 0
        if idx > self.size - 1:
            idx = self.size - 1
        return idx

    # --- LSP-visible properties (word-based accessors) ---
    @property
    def lightest(self) -> str:
        "Lightest tone (leftmost)."
        return self.items[self._tone_index("lightest")]

    @property
    def lighter(self) -> str:
        "Second-lightest tone (one step in from the light end)."
        return self.items[self._tone_index("lighter")]

    @property
    def normal(self) -> str:
        "Third-lightest tone."
        return self.items[self._tone_index("normal")]
    @property
    def light(self) -> str:
        "Third-lightest tone."
        return self.items[self._tone_index("light")]

    @property
    def dark(self) -> str:
        "Third-darkest tone (three steps in from the dark end)."
        return self.items[self._tone_index("dark")]

    @property
    def darker(self) -> str:
        "Second-darkest tone."
        return self.items[self._tone_index("darker")]

    @property
    def darkest(self) -> str:
        "Darkest tone (rightmost)."
        return self.items[self._tone_index("darkest")]

    # --- dynamic letter/word combos still work ---
    @overload
    def __getattr__(self, name: Literal["lightest","lighter","light","dark","darker","darkest"]) -> str: ...
    @overload
    def __getattr__(self, name: str) -> Union[str, List[str]]: ...
    def __getattr__(self, name: str) -> Union[str, List[str]]:
        if name and all(ch in self.letters for ch in name):
            idxs = self._indices_for(name)
            return self.items[idxs[0]] if len(name) == 1 else [self.items[i] for i in idxs]
        raise AttributeError(
            f"{name!r} is not a valid accessor for size {self.size}. "
            f"Use any of: {self.letters} or one of {', '.join(self.TONE_NAMES)}"
        )

    def __dir__(self):
        # Helps interactive completion in REPLs
        base = set(super().__dir__())
        base.update(self.TONE_NAMES)
        base.update(list(self.letters))
        return sorted(base)

    def __repr__(self) -> str:
        kwargs = dict(name=self.name, size=self.size, available=self.letters)
        return pythonfmt.call("ColorBrewerSlice", [], kwargs, condensed=True)

    def to_dict(self) -> Dict[str, str]:
        # Only the word-based tones, as requested.
        return {tone: getattr(self, tone) for tone in self.TONE_NAMES}

# ~/projects/yoya/typst/components/reader/chinese-display.typ
# file = "~/data/colorbrewer.json"
alias_map = {
    "blues": "blue",
    "bugn": "blue-green",
    "bupu": "blue-purple",
    "gnbu": "green-blue",
    "greens": "green",
    "greys": "grey",
    "orrd": "orange-red",
    "oranges": "orange",
    "pubu": "purple-blue",
    "pubugn": "purple-blue-green",
    "purd": "purple-red",
    "purples": "purple",
    "rdpu": "red-purple",
    "reds": "red",
    "ylgn": "yellow-green",
    "ylgnbu": "yellow-green-blue",
    "ylorbr": "yellow-orange-brown",
    "ylorrd": "yellow-orange-red",
}
evocative_alias_map = {
    "blues": "deep-ocean",
    "bugn": "seafoam",
    "bupu": "twilight",
    "gnbu": "glacier",
    "greens": "forest",
    "greys": "fog",
    "orrd": "ember",
    "oranges": "citrus",
    "pubu": "dusk-bay",
    "pubugn": "aurora",
    "purd": "orchid",
    "purples": "amethyst",
    "rdpu": "rose-dusk",
    "reds": "crimson",
    "ylgn": "spring-meadow",
    "ylgnbu": "shoreline",
    "ylorbr": "desert-canyon",
    "ylorrd": "sunset",
}





def main():
    def callback(x):
        a = x["theme"].lower()
        key = alias_map[a]
        name = evocative_alias_map[a]
        return dict(key=key, name=name, colors=x["colors"])
    kx.writefile(
        "~/data/sequential-colorbrewer.json",
        kx.map(
            kx.filtered(
                kx.readfile(file), lambda x: x["category"] == "sequential"
            ),
            callback,
        ),
    )
    kx.cpfile(
        file,
        "/home/kdog3682/projects/hammymathclass/typst/data/colorbrewer.json",
    )


cb = ColorBrewer()
deep_ocean = cb.get("deep-ocean")
seafoam = cb.get("seafoam")
twilight = cb.get("twilight")
glacier = cb.get("glacier")
forest = cb.get("forest")
fog = cb.get("fog")
ember = cb.get("ember")
citrus = cb.get("citrus")
dusk_bay = cb.get("dusk-bay")
aurora = cb.get("aurora")
orchid = cb.get("orchid")
amethyst = cb.get("amethyst")
rose_dusk = cb.get("rose-dusk")
crimson = cb.get("crimson")
spring_meadow = cb.get("spring-meadow")
shoreline = cb.get("shoreline")
desert_canyon = cb.get("desert-canyon")
sunset = cb.get("sunset")

color_brewer = cb
# print(sunset.to_dict())
# print(cb.get(("blue", "green")))
# print(cb.get('seafoam'))




class ColorBrewerThemeV1:
    def __init__(self, key: PaletteValue):

        def create(key):
            return color_brewer.get(key).to_dict()

        primary = key
        secondary = PALLETE_MAP.get(key).get('complement')
        self.data = {
            'primary': create(primary),
            'secondary': create(secondary),
        }
    
    def get(self, key):
        return kx.dict_getter(self.data, key)







import kevinlulee as kx

def example():
    INPUT = "~/data/sequential-colorbrewer.json"
    OUTPUT = "~/data/sequential-colorbrewer.tailwind.json"
    
    TARGET_STEPS = [50,100,200,300,400,500,600,700,800,900]
    
    def best_array(colors_dict):
        for n in ("9","8","7","6","5","4","3"):
            if n in colors_dict:
                return colors_dict[n]
        return []
    
    def to_tailwind_scale(colors_dict):
        arr = best_array(colors_dict)
        scale = {}
    
        # map available colors to 100.. up to what we have
        for i, hex_color in enumerate(arr):
            step = (i + 1) * 100
            if step > 900:
                break
            scale[str(step)] = hex_color
    
        # 50 should be the same as 100
        scale["50"] = scale["100"]
    
        # fill any missing steps by carrying forward the last seen value
        last = scale["50"]
        for step in TARGET_STEPS:
            key = str(step)
            if key in scale:
                last = scale[key]
            else:
                scale[key] = last
    
        # if we didn't have a 900, ensure it's equal to 800
        scale["900"] = scale["800"]
    
        # keep keys in standard order when serialized
        ordered = {str(s): scale[str(s)] for s in TARGET_STEPS}
        return ordered
    
    def build_tailwind_palettes(data):
        out = []
        for entry in data:
            out.append({
                "key": entry["key"],
                "name": entry.get("name", ""),
                "scale": to_tailwind_scale(entry["colors"])
            })
        return out
    
    data = kx.readfile(INPUT)
    result = build_tailwind_palettes(data)
    kx.writefile(OUTPUT, result)
    print(f"Wrote {OUTPUT}")


def create_brewer_tailwind(file):
    data = kx.readfile(file)
    return {
        el['name']: el['scale'] for el in data
    }

COLOR_BREWER_TAILWIND = create_brewer_tailwind("~/data/sequential-colorbrewer.tailwind.json")
# COLOR_BREWER_JSON = create_brewer_tailwind("~/data/sequential-colorbrewer.json")

class ColorBrewerTheme:
    def __init__(self, key: PaletteValue):

        def create(key):
            return COLOR_BREWER_TAILWIND.get(key) # scales ...

        primary = key
        secondary = PALLETE_MAP.get(key).get('complement')
        self.data = {
            'primary': create(primary),
            'secondary': create(secondary),
        }
    
    def get(self, key):
        return kx.dict_getter(self.data, key)


# a = ColorBrewerTheme('deep-ocean')
# print(a.get('primary.200'))
