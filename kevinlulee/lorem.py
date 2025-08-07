roygbiv = [
    "red",
    "orange",
    "purple",
    "white",
    "yellow",
    "green",
    "blue",
    "black",
    "gray",
    "teal",
    "indigo",
    "violet",
]

numbers = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
]
alphabet = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]

dct = dict(a = 1, b = 2)

def paragraph(n):
    base_text = (
        "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt "
        "ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco "
        "laboris nisi ut aliquip ex ea commodo consequat"
    )
    words = base_text.split()
    repeated_words = (words * ((n // len(words)) + 1))[:n]
    return ' '.join(repeated_words)


nested_object = {
    'a': {
        'b': 'hi',
        'c': {
            'd': 'bye',
            'a': '1'
        }
    }
}
