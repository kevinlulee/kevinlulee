"""
Convert numbers to natural language representations.
"""


def number_to_words(n):
    """Convert a number to its word representation."""
    words = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
        "seventeen", "eighteen", "nineteen"
    ]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
    if n < 20:
        return words[n]
    elif n < 100:
        if n % 10 == 0:
            return tens[n // 10]
        return f"{tens[n // 10]}-{words[n % 10]}"
    else:
        return str(n)


def number_of_times(n):
    """Convert a number to 'once', 'twice', or 'N times' format."""
    if n == 1:
        return "once"
    elif n == 2:
        return "twice"
    else:
        return f"{number_to_words(n)} times"


def ordinal(n):
    """Convert a number to its ordinal form (1st, 2nd, 3rd, etc.)."""
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def ordinal_word(n):
    """Convert a number to its ordinal word (first, second, third, etc.)."""
    ordinals = [
        "zeroth", "first", "second", "third", "fourth", "fifth", 
        "sixth", "seventh", "eighth", "ninth", "tenth",
        "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
        "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth"
    ]
    if n < len(ordinals):
        return ordinals[n]
    return ordinal(n)
