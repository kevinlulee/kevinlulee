import random
import copy
from kevinlulee import kx

def mutate_value(value, k_factor = 0.3):
        """Mutate a numeric value based on k factor"""
        if not isinstance(value, (int, float)):
            return value

        # Calculate mutation range
        if value == 0:
            # Special case for zero - use small absolute range
            mutation_range = k_factor
        else:
            mutation_range = abs(value) * k_factor

        # Generate random mutation
        mutation = random.uniform(-mutation_range, mutation_range)
        mutated = value + mutation

        # Preserve type (int vs float)
        if isinstance(value, int):
            return int(round(mutated))
        else:
            return mutated

def generate_mutated_variations(data, targets=None, n=5, k=0.1):
    """
    Mutates numeric values in a dictionary and returns a list of mutated copies.
    
    Args:
        data (dict): The input dictionary to mutate
        targets (list): List of keys to mutate. If None, mutates all numeric values
        n (int): Number of dictionaries to return (including original)
        k (float): Mutation factor (0-1), determines how far to mutate around original value
    
    Returns:
        list: List of n dictionaries, first one is the original
    """
    
    
    # Determine which keys to mutate
    if targets is None:
        # Find all keys with numeric values
        targets = [key for key, value in data.items() if isinstance(value, (int, float))]
    else:
        targets = kx.to_array(targets)
    # Create list of dictionaries
    result = []
    seen_dicts = set()
    
    # First dictionary is the original
    original_copy = copy.deepcopy(data)
    result.append(original_copy)
    seen_dicts.add(frozenset(original_copy.items()))
    
    # Generate n-1 mutated copies, ensuring no duplicates
    max_attempts = n * 100  # Prevent infinite loops
    attempts = 0
    
    while len(result) < n and attempts < max_attempts:
        mutated_dict = copy.deepcopy(data)
        
        # Mutate targeted keys
        # raise Exception(targets, mutated_dict)
        for key in targets:
            if key in mutated_dict:
                mutated_dict[key] = mutate_value(mutated_dict[key], k)
        
        # Check if this dictionary is unique
        dict_signature = frozenset(mutated_dict.items())
        if dict_signature not in seen_dicts:
            result.append(mutated_dict)
            seen_dicts.add(dict_signature)
        
        attempts += 1
    
    return result

def cluster_rng(a, b, k=None, mode=float):
    """
    Generate a random number between a and b with optional clustering.
    
    Args:
        a: Lower bound (inclusive)
        b: Upper bound (inclusive for int, exclusive for float)
        k: Clustering factor (0-1). If None, uniform distribution.
           0 = cluster towards a, 1 = cluster towards b, 0.5 = center
        mode: 'int' or 'float' to specify return type
    
    Returns:
        Random number of specified type
    """
    if mode == int:
        if k is None:
            return random.randint(a, b)
        else:
            # Use beta distribution for clustering
            # Transform k to beta parameters for desired clustering
            if k == 0.5:
                alpha = beta = 1  # Uniform
            elif k < 0.5:
                alpha = 1
                beta = 1 + (0.5 - k) * 10  # Cluster towards a
            else:
                alpha = 1 + (k - 0.5) * 10  # Cluster towards b
                beta = 1
            
            # Generate beta random variable and scale to range
            beta_val = random.betavariate(alpha, beta)
            return int(a + beta_val * (b - a + 1))
    
    elif mode == float:
        if k is None:
            return random.uniform(a, b)
        else:
            # Use beta distribution for clustering
            if k == 0.5:
                alpha = beta = 1  # Uniform
            elif k < 0.5:
                alpha = 1
                beta = 1 + (0.5 - k) * 10  # Cluster towards a
            else:
                alpha = 1 + (k - 0.5) * 10  # Cluster towards b
                beta = 1
            
            # Generate beta random variable and scale to range
            beta_val = random.betavariate(alpha, beta)
            return float(a + beta_val * (b - a))
    
    else:
        raise ValueError("mode must be 'int' or 'float'")

import random

import random

import random

def generate_centered_sequence(center_val, center_index=2, length=5, k=0.5, positive_only=True):
    """
    Generate a sorted sequence of numbers with center_val at center_index.

    Args:
        center_val (int): The central value to place at center_index.
        center_index (int): The index at which center_val should appear.
        length (int): Total number of elements in the sequence.
        k (float): Range factor controlling spread from center_val.
        positive_only (bool): If True, ensures all numbers are > 0.
    """
    nums_before = center_index
    nums_after = length - center_index - 1
    total_needed = nums_before + nums_after

    sequence = [None] * length
    sequence[center_index] = center_val
    used = {center_val}

    def generate_unique_numbers(count, direction):
        numbers = []
        range_multiplier = 1
        attempts = 0
        max_attempts = 300

        while len(numbers) < count and attempts < max_attempts:
            base_range = max(abs(center_val) * k * range_multiplier, 1)
            offset = random.uniform(1, base_range)
            candidate = int(center_val + offset) if direction == 'up' else int(center_val - offset)

            if positive_only and candidate <= 0:
                attempts += 1
                continue

            if candidate not in used:
                numbers.append(candidate)
                used.add(candidate)

            attempts += 1
            if attempts % 50 == 0:
                range_multiplier *= 1.5  # Expand range if stuck

        return numbers

    lower = generate_unique_numbers(nums_before, 'down')
    higher = generate_unique_numbers(nums_after, 'up')

    if len(lower) < nums_before or len(higher) < nums_after:
        raise ValueError("Unable to generate enough unique values. Try increasing 'k' or 'length'.")

    return sorted(lower) + [center_val] + sorted(higher)

# Example usage
if __name__ == "__main__":
    
    sequence2 = generate_centered_sequence(2, 2, 4, 0.8)
    print(f"\nCustom parameters: {sequence2}")
    
# if __name__ == '__main__':
#     rect_state = {'width': 5, 'height': 3}
#     rows = generate_mutated_variations(rect_state, k = 0.8, targets = ('width'))
#     print(rows)
