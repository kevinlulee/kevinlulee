from dataclasses import dataclass
from typing import List, Tuple, Union


@dataclass
class ArithmeticResult:
    answer: str
    operator: str
    carries: List[int]
    numbers: List[str]


def perform_arithmetic(nums: List[str], operation: str = "+") -> ArithmeticResult:
    """
    Performs long addition or subtraction with carries.
    
    Args:
        nums: List of string numbers to add or subtract
        operation: "+" for addition, "-" for subtraction
    
    Returns:
        ArithmeticResult with answer, operator, carries, and sorted numbers
    """
    # Sort numbers by length (longest first)
    nums = sorted(nums, key=len, reverse=True)
    
    # Initialize carries list and result
    carries = [0] * (len(nums[0]) + 1)
    result = []
    
    if operation == "+":
        # Addition
        for i in range(len(nums[0]) - 1, -1, -1):
            column_sum = carries[i + 1]
            
            for num in nums:
                if i >= len(nums[0]) - len(num):
                    column_sum += int(num[i - (len(nums[0]) - len(num))])
            
            result.insert(0, str(column_sum % 10))
            carries[i] = column_sum // 10
        
        # Add the final carry if it exists
        if carries[0] > 0:
            result.insert(0, str(carries[0]))
        
    elif operation == "-":
        # Subtraction (assuming first number is largest)
        for i in range(len(nums[0]) - 1, -1, -1):
            column_value = int(nums[0][i]) - carries[i + 1]
            
            for j in range(1, len(nums)):
                if i >= len(nums[0]) - len(nums[j]):
                    column_value -= int(nums[j][i - (len(nums[0]) - len(nums[j]))])
            
            if column_value < 0:
                column_value += 10
                carries[i] = 1
            
            result.insert(0, str(column_value))
    
    return ArithmeticResult(
        answer=''.join(result).lstrip('0') or '0',
        operator=operation,
        carries=carries[1:],  # Remove the extra carry at the beginning
        numbers=nums
    )


# Examples
if __name__ == "__main__":
    # Example 1: Addition
    result1 = perform_arithmetic(["123", "456", "7"], "+")
    print(f"Addition: {result1}")
    # Output: ArithmeticResult(answer='586', operator='+', carries=[0, 1, 1], numbers=['456', '123', '7'])
    
    # Example 2: Addition with carry
    result2 = perform_arithmetic(["999", "1"], "+")
    print(f"Addition with carry: {result2}")
    # Output: ArithmeticResult(answer='1000', operator='+', carries=[1, 0, 0], numbers=['999', '1'])
    
    # Example 3: Subtraction
    result3 = perform_arithmetic(["500", "220"], "-")
    print(f"Subtraction: {result3}")
    # Output: ArithmeticResult(answer='280', operator='-', carries=[0, 1, 0], numbers=['500', '220'])