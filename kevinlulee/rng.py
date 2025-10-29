import random
import copy
from kevinlulee import kx

def mutate_value(value, k_factor = 0.3):
        """Mutate a numeric value based on k factor"""
        if not isinstance(value, (int, float)):
            return value

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

def generate_mutated_variations(data, targets=None, n=5, k=0.1, num_range = None):
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
    
    
    num_range = num_range or (1, 1000)

    # Determine which keys to mutate
    if targets is None:
        # Find all keys with numeric values
        targets = [key for key, value in data.items() if kx.is_number(value)]
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
                ref = mutated_dict[key]
                while True:
                    value = mutate_value(ref, k)
                    if num_range[0] <= value <= num_range[1]:
                        mutated_dict[key] = value
                        break
                    else:
                        attempts += 1
                        assert attempts < max_attempts, "max attempts exceeded"

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

    
import random
from typing import TypeVar, List, Sequence, Optional

T = TypeVar('T')


def set_seed(seed: int):
    """Set the random seed for reproducibility."""
    random.seed(seed)


def coinflip() -> bool:
    """Flip a coin, returns True for heads, False for tails."""
    return random.random() < 0.5


def choose(*items: Sequence[T]) -> T:
    """Choose a random item from a sequence."""
    return random.choice(_flat(items))


def select(items: Sequence[T], k: int = 1, weights: Optional[Sequence[float]] = None, with_replacement: bool = False) -> List[T]:
    """
    Select k random items from a sequence.
    
    Args:
        items: Sequence to select from
        k: Number of items to select
        weights: Optional weights for weighted selection
        with_replacement: If True, sample with replacement
    """
    if weights is not None:
        return random.choices(items, weights=weights, k=k)
    if with_replacement:
        return random.choices(items, k=k)
    else:
        return random.sample(items, k=k)


def _flat(items):
    r = list(items[0] if len(items) == 1 and isinstance(items[0], (list, tuple)) else items)
    return r

def shuffle(*items: List[T]) -> List[T]:
    """
    Shuffle a list and return it (mutative).
    """
    r = _flat(items)
    random.shuffle(r)
    return r



def randint(a, b: Optional[int] = None) -> int:
    """
    Random integer in range [a, b] inclusive.
    If a is a sequence, returns random index from that sequence.
    If b is None, returns integer in [0, a] inclusive.
    """
    if isinstance(a, (list, tuple, Sequence)) and not isinstance(a, str):
        return random.randint(0, len(a) - 1)
    if b is None:
        return random.randint(0, a)
    return random.randint(a, b)


def randfloat(a: float = 0.0, b: float = 1.0) -> float:
    """Random float in range [a, b)."""
    return a + random.random() * (b - a)


def uniform(a, b):
    return random.uniform(a, b)

# Example usage
if __name__ == "__main__":
    # Set seed for reproducibility
    
    print("Coin flip:", coinflip())
    print("Choose from list:", choose([1, 2, 3, 4, 5]))
    print("Select 3 items:", select([1, 2, 3, 4, 5], k=3))
    print("Select with replacement:", select([1, 2, 3], k=5, with_replacement=True))
    print("Select weighted:", select(['a', 'b', 'c'], k=3, weights=[0.5, 0.3, 0.2], with_replacement=True))
    print("Shuffled:", shuffle([1, 2, 3, 4, 5]))
    print("Random int [0, 10]:", randint(10))
    print("Random int [5, 15]:", randint(5, 15))
    print("Random idx from array:", randint([10, 20, 30, 40, 50]))
    print("Random float [0, 1):", randfloat())
    print("Random float [10, 20):", randfloat(10, 20))
    
    print("\n--- Running again with same seed ---")
    print("Coin flip:", coinflip())
    print("Choose from list:", choose([1, 2, 3, 4, 5]))

# if __name__ == '__main__':
#     mod.commander_run(generate_mutated_variations, rect_state, k = 0.8)
set_seed(42)
