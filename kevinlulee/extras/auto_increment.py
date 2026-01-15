from __future__ import annotations
import kevinlulee as kx

"""
AutoIncrement callable for generating sequential strings from a template
containing exactly one placeholder:

    {n}  numeric
    {a}  lowercase alphabetic
    {A}  uppercase alphabetic
    {i}  lowercase Roman numeral
    {I}  uppercase Roman numeral

Example:
    inc = AutoIncrement("section-{I}")
    inc()  -> "section-I"
    inc()  -> "section-II"
"""

__all__ = [
    "AutoIncrement",
]

import re


def to_alpha(n, upper=False):
    if n < 1:
        raise ValueError("Alphabetic index must be >= 1")
    chars = []
    while n:
        n -= 1
        n, r = divmod(n, 26)
        base = ord("A" if upper else "a")
        chars.append(chr(base + r))
    return "".join(reversed(chars))


def to_roman(n, upper=True):
    if not (0 < n < 4000):
        raise ValueError("Roman numerals must be 1..3999")

    numerals = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    out = []
    for v, s in numerals:
        while n >= v:
            out.append(s)
            n -= v

    result = "".join(out)
    return result if upper else result.lower()


ENCODERS = {
    "n": lambda n: n,
    "a": lambda n: to_alpha(n, upper=False),
    "A": lambda n: to_alpha(n, upper=True),
    "i": lambda n: to_roman(n, upper=False),
    "I": lambda n: to_roman(n, upper=True),
}


class AutoIncrement:
    def __init__(self, template, start=1, step=1):
        self.template = template
        self.step = step
        self.pos = start

        m = re.findall(r"\{([nAiI])\}", template)
        if len(m) != 1:
            raise ValueError("Template must contain exactly one of {n,a,A,i,I}")

        self._key = m[0]
        self._encode = ENCODERS[self._key]

    def __call__(self):
        value = self.pos
        self.pos += self.step
        return self.template.format(**{self._key: self._encode(value)})

    def get(self):
        return self.pos

    def set(self, n):
        self.pos = n

    def reset(self, n=1):
        self.pos = n
