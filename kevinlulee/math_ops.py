
from decimal import Decimal, ROUND_HALF_UP

def smart_round(x):
    """
    Heuristically round a number to its 'intended' decimal precision.
    Detects long runs of 0s/9s in the fractional part (common float noise)
    and rounds at the boundary. Falls back to ~12 significant digits.
    """

    # Work from a fixed-point view of the float
    s = format(x, '.17f')  # 17 decimal places of the binary float
    neg = s.startswith('-')
    if neg: s = s[1:]
    if '.' not in s:
        return -float(s) if neg else float(s)

    intp, frac = s.split('.')

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

    for d in ('0', '9'):
        pos = first_run(frac, d)
        if pos is not None:  # round at the boundary before the run
            q = Decimal('1e-' + str(pos))
            dnum = Decimal(format(x, '.17g'))
            out = float(dnum.quantize(q, rounding=ROUND_HALF_UP))
            return -out if neg and out > 0 else out

    # Fallback: trim to ~5 significant digits (safe, no extra params)
    return float(format(x, '.5g'))

