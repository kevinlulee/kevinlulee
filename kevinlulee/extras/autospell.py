import re

QUESTION_STARTERS = {
    "who","what","when","where","why","how","which","whom","whose",
    "do","does","did","is","are","am","can","could","would","should",
    "will","have","has","had","may","might","must","shall","was","were"
}

def autospell(line: str) -> str:
    s = re.sub(r'\s+', ' ', line.strip())

    # Split into sentence-like chunks, respecting decimals like 3.14
    parts, start, i = [], 0, 0
    while i < len(s):
        ch = s[i]
        if ch in '.!?':
            is_decimal_dot = ch == '.' and i > 0 and i+1 < len(s) and s[i-1].isdigit() and s[i+1].isdigit()
            if not is_decimal_dot:
                parts.append(s[start:i+1].strip())
                i += 1
                while i < len(s) and s[i].isspace():
                    i += 1
                start = i
                continue
        i += 1
    if start < len(s):
        parts.append(s[start:].strip())

    out = []
    for chunk in parts:
        m = re.match(r'^(.*?)([.!?]+)?$', chunk)
        base = (m.group(1) or "").strip().lower()
        punct = (m.group(2) or "")

        if not base:
            continue

        # Collapse repeated punctuation to one mark
        if punct:
            punct = '!' if '!' in punct else ('?' if '?' in punct else '.')

        # Fix pronoun "I"
        base = re.sub(r"\bi\b", "I", base, flags=re.I)

        # Capitalize a name after common introductions
        def cap_name(match):
            return match.group(1) + ' ' + match.group(2).title()
        base = re.sub(r'\b(my name is)\s+([a-z]+)\b',
                      lambda m: m.group(1).capitalize() + ' ' + m.group(2).title(),
                      base, flags=re.I)
        base = re.sub(r"\b(i am|i'm)\s+([a-z]+)\b", cap_name, base, flags=re.I)

        # Sentence-case
        base = base[0].upper() + base[1:] if len(base) > 1 else base.upper()

        # Decide on punctuation when missing or obviously wrong
        starter = base.split()[0].lower()
        should_question = starter in QUESTION_STARTERS
        if not punct:
            punct = '?' if should_question else '.'
        elif punct == '.' and should_question:
            punct = '?'

        out.append(base + punct)

    return ' '.join(out)

# print(autospell('do u liek cake'))
