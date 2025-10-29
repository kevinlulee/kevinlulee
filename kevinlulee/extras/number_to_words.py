from __future__ import annotations
import kevinlulee as kx

def number_to_words(n):
    """
    Convert a number to its word representation.
    Examples: 2000 -> "2 thousand", 1500000 -> "1.5 million"
    """
    if n == 0:
        return "zero"
    
    # Handle negative numbers
    if n < 0:
        return "negative " + number_to_words(-n)
    
    # Define units
    units = [
        (1_000_000_000_000, "trillion"),
        (1_000_000_000, "billion"),
        (1_000_000, "million"),
        (1_000, "thousand"),
    ]
    
    # Find the appropriate unit
    for value, name in units:
        if n >= value:
            quotient = n / value
            # Format the quotient nicely
            if quotient == int(quotient):
                return f"{int(quotient)} {name}"
            else:
                # Round to 1 decimal place for cleaner output
                return f"{quotient:.1f} {name}"
    
    # For numbers less than 1000
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", 
             "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
    if n < 10:
        return ones[n]
    elif n < 20:
        return teens[n - 10]
    elif n < 100:
        return tens[n // 10] + ("" if n % 10 == 0 else " " + ones[n % 10])
    else:  # n < 1000
        result = ones[n // 100] + " hundred"
        if n % 100 != 0:
            result += " " + number_to_words(n % 100)
        return result


if __name__ == "__main__":
    # Test examples
    test_cases = [0, 5, 42, 100, 999, 2000, 1500, 1500000, 3200000, 1000000000]
    for num in test_cases:
        print(f"{num:,} -> {number_to_words(num)}")
