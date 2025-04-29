from typing import List, Union, Dict, Tuple, Any
from pprint import pprint


class ArithmeticObject:
    def __init__(self, value: str, x: int, y: int):
        self.value = value
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"ArithmeticObject(value='{self.value}', x={self.x}, y={self.y})"


def long_arithmetic(num1: Union[str, int], num2: Union[str, int], operation: str = '+') -> List[ArithmeticObject]:
    """
    Perform long addition or subtraction, returning array of objects with coordinates and values.
    
    Args:
        num1: First number
        num2: Second number
        operation: '+' for addition, '-' for subtraction
    
    Returns:
        List of ArithmeticObject representing the equation and result
    """
    # Convert inputs to strings
    num1_str = str(num1)
    num2_str = str(num2)
    
    # Ensure num1 is the longer/larger number for subtraction
    if operation == '-' and len(num2_str) > len(num1_str):
        num1_str, num2_str = num2_str, num1_str
        operation = '-'  # Keep as subtraction
    elif operation == '-' and len(num1_str) == len(num2_str) and num1_str < num2_str:
        num1_str, num2_str = num2_str, num1_str
        operation = '-'  # Keep as subtraction
    
    # Initialize result
    result_objects = []
    
    # Calculate maximum width
    max_width = max(len(num1_str), len(num2_str))
    
    # Calculate the result
    if operation == '+':
        carry = 0
        result_str = ''
        
        for i in range(1, max_width + 1):
            # Get digits from right to left
            d1 = int(num1_str[-i]) if i <= len(num1_str) else 0
            d2 = int(num2_str[-i]) if i <= len(num2_str) else 0
            
            # Calculate sum and new carry
            current_sum = d1 + d2 + carry
            digit = current_sum % 10
            carry = current_sum // 10
            
            # Build result from right to left
            result_str = str(digit) + result_str
        
        # Add final carry if exists
        if carry > 0:
            result_str = str(carry) + result_str
    else:  # Subtraction
        borrow = 0
        result_str = ''
        
        for i in range(1, max_width + 1):
            # Get digits from right to left
            d1 = int(num1_str[-i]) if i <= len(num1_str) else 0
            d2 = int(num2_str[-i]) if i <= len(num2_str) else 0
            
            # Apply borrow from previous column
            d1 = d1 - borrow
            
            # Check if we need to borrow for this column
            if d1 < d2:
                d1 += 10
                borrow = 1
            else:
                borrow = 0
                
            # Calculate difference
            digit = d1 - d2
            
            # Build result from right to left
            result_str = str(digit) + result_str
        
        # Remove leading zeros
        result_str = result_str.lstrip('0')
        if result_str == '':
            result_str = '0'
    
    # Create the output objects
    # First number
    for i, digit in enumerate(num1_str):
        result_objects.append(ArithmeticObject(digit, i, 0))
    
    # Operation symbol
    result_objects.append(ArithmeticObject(operation, len(num1_str) - max_width - 1, 1))
    
    # Second number
    for i, digit in enumerate(num2_str):
        result_objects.append(ArithmeticObject(digit, i + (len(num1_str) - len(num2_str)), 1))
    
    # Separator line
    for i in range(max(len(num1_str), len(num2_str)) + 1):
        result_objects.append(ArithmeticObject('-', i, 2))
    
    # Result
    for i, digit in enumerate(result_str):
        result_objects.append(ArithmeticObject(digit, i + (len(num1_str) - len(result_str)), 3))
    
    return result_objects


# Examples
example1 = long_arithmetic(123, 456, '+')
example2 = long_arithmetic(999, 1, '+')
example3 = long_arithmetic(1000, 999, '-')
example4 = long_arithmetic(456, 123, '-')

print("Example 1 (123 + 456):")
pprint(example1)
# print("\nExample 2 (999 + 1):")
# print(example2)
# print("\nExample 3 (1000 - 999):")
# print(example3)
# print("\nExample 4 (456 - 123):")
# print(example4)
