import math
from decimal import Decimal, ROUND_HALF_UP


def smart_round(x):
    """
    Heuristically round a number to its 'intended' decimal precision.
    Detects long runs of 0s/9s in the fractional part (common float noise)
    and rounds at the boundary. Falls back to ~12 significant digits.
    """

    # Work from a fixed-point view of the float
    s = format(x, ".17f")  # 17 decimal places of the binary float
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    if "." not in s:
        return -float(s) if neg else float(s)

    intp, frac = s.split(".")

    # Find earliest run (≥3) of '0' or '9' in the fractional part
    def first_run(fr, digit):
        i, n = 0, len(fr)
        while i < n:
            if fr[i] == digit:
                j = i
                while j < n and fr[j] == digit:
                    j += 1
                if j - i >= 3:
                    return i  # start index of the run
                i = j
            else:
                i += 1
        return None

    for d in ("0", "9"):
        pos = first_run(frac, d)
        if pos is not None:  # round at the boundary before the run
            q = Decimal("1e-" + str(pos))
            dnum = Decimal(format(x, ".17g"))
            out = float(dnum.quantize(q, rounding=ROUND_HALF_UP))
            return -out if neg and out > 0 else out

    # Fallback: trim to ~5 significant digits (safe, no extra params)
    return float(format(x, ".5g"))


def get_angles(
    step_deg: float | None = None,
    num_slices: int | None = None,
    index: int | None = None,
    offset_deg: float = 0.0,
    position: str = "center",  # ["start","center","end"]
) -> list[float] | float:
    """
    Equally partition a circle and return angles in degrees.

    - Provide exactly one of:
        step_deg: angular spacing between slices (degrees)
        num_slices: how many equal slices to make
    - If index is None: returns all angles for the requested 'position'.
      Otherwise: returns the single angle for that slice index (wrapped).
    - offset_deg rotates the whole set.

    Returns: list[float] (all angles) or float (single angle).
    """
    # exactly one of step_deg or num_slices must be set
    assert (step_deg is None) ^ (num_slices is None)

    if num_slices is not None:
        assert num_slices >= 1
        n = num_slices
    else:
        assert step_deg > 0.0
        n_float = 360.0 / step_deg
        n = int(round(n_float))
        # require clean tiling of the circle when step is given
        assert isclose(
            n_float, n, abs_tol=1e-9
        ), "360 must be divisible by step_deg"

    step = 360.0 / n
    assert position in {"start", "center", "end"}

    def start_at(i: int) -> float:
        return (offset_deg + i * step) % 360.0

    if index is None:
        if position == "start":
            return [start_at(i) for i in range(n)]
        if position == "end":
            return [(start_at(i) + step) % 360.0 for i in range(n)]
        return [(start_at(i) + step / 2.0) % 360.0 for i in range(n)]
    else:
        i = index % n
        s = start_at(i)
        if position == "start":
            return s
        if position == "end":
            return (s + step) % 360.0
        return (s + step / 2.0) % 360.0


def get_mantissa_and_exponent(number):
    """
    Convert a number to mantissa and exponent form.
    Returns (mantissa, exponent) where number = mantissa × 10^exponent
    and mantissa is in the range [1, 10) or 0 if number is 0.

    Examples:
        50000 -> (5.0, 4)  because 50000 = 5 × 10^4
        12345 -> (1.2345, 4)  because 12345 = 1.2345 × 10^4
        0.00123 -> (1.23, -3)  because 0.00123 = 1.23 × 10^-3
    """
    if number == 0:
        return 0, 0

    exponent = math.floor(math.log10(abs(number)))
    mantissa = number / (10**exponent)

    return mantissa, exponent


def get_decimal_string(value):
    s = str(value)

    negative = value < 0
    if negative:
        s = s[1:]

    if "." in s:
        integer_part, decimal_part = s.split(".")
    else:
        integer_part = s
        decimal_part = None

    if len(integer_part) > 3:
        reversed_int = integer_part[::-1]
        chunks = [
            reversed_int[i : i + 3] for i in range(0, len(reversed_int), 3)
        ]
        integer_part = ",".join(chunks)[::-1]

    result = integer_part
    if decimal_part is not None:
        result += "." + decimal_part
    if negative:
        result = "-" + result

    return result
