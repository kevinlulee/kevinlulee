from difflib import SequenceMatcher
from typing import Tuple


def compare_text_singleline(str1: str, str2: str) -> float:
    """
    Compare similarity between two single-line strings.
    Returns a similarity ratio between 0.0 and 1.0.
    
    Uses SequenceMatcher for character-level comparison.
    Best for short strings without newlines.
    
    Args:
        str1: First string to compare
        str2: Second string to compare
    
    Returns:
        Similarity ratio (0.0 = completely different, 1.0 = identical)
    """
    return SequenceMatcher(None, str1, str2).ratio()


def compare_text_multiline(str1: str, str2: str) -> Tuple[float, dict]:
    """
    Compare similarity between two multiline strings.
    Returns both overall similarity and line-by-line analysis.
    
    Uses line-based comparison for better multiline text handling.
    
    Args:
        str1: First string to compare
        str2: Second string to compare
    
    Returns:
        Tuple of (overall_similarity, details_dict) where:
        - overall_similarity: float between 0.0 and 1.0
        - details_dict: Contains line_similarity, added_lines, removed_lines, common_lines
    """
    lines1 = str1.splitlines()
    lines2 = str2.splitlines()
    
    # Get sequence matcher for lines
    matcher = SequenceMatcher(None, lines1, lines2)
    
    # Calculate overall similarity
    overall_similarity = matcher.ratio()
    
    # Get detailed diff information
    opcodes = matcher.get_opcodes()
    
    added_lines = []
    removed_lines = []
    common_lines = []
    
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            common_lines.extend(lines1[i1:i2])
        elif tag == 'delete':
            removed_lines.extend(lines1[i1:i2])
        elif tag == 'insert':
            added_lines.extend(lines2[j1:j2])
        elif tag == 'replace':
            removed_lines.extend(lines1[i1:i2])
            added_lines.extend(lines2[j1:j2])
    
    details = {
        'overall_similarity': overall_similarity,
        'added_lines': added_lines,
        'removed_lines': removed_lines,
        'common_lines': common_lines,
        'total_lines_str1': len(lines1),
        'total_lines_str2': len(lines2),
    }
    
    return overall_similarity, details


def compare_text(str1: str, str2: str):
    """
    Automatically choose the appropriate comparison method based on input.
    Uses multiline comparison if either string contains newlines.
    
    Args:
        str1: First string to compare
        str2: Second string to compare
    
    Returns:
        For single-line: float similarity ratio
        For multiline: tuple of (similarity, details_dict)
    """
    if '\n' in str1 or '\n' in str2:
        return compare_text_multiline(str1, str2)
    else:
        return compare_text_singleline(str1, str2)


# Example usage
if __name__ == "__main__":
    # Single-line comparison
    text1 = "The quick brown fox"
    text2 = "The quick brown dog"
    similarity = compare_text_singleline(text1, text2)
    print(f"Single-line similarity: {similarity:.2%}")
    
    # Multiline comparison
    text3 = """Line 1
Line 2
Line 3
Line 4"""
    
    text4 = """Line 1
Line 2 modified
Line 3
Line 5"""
    
    similarity, details = compare_text_multiline(text3, text4)
    print(f"\nMultiline similarity: {similarity:.2%}")
    print(f"Added lines: {details['added_lines']}")
    print(f"Removed lines: {details['removed_lines']}")
    print(f"Common lines: {len(details['common_lines'])}")
    
    # Auto-detect version
    print("\n--- Auto-detect ---")
    result1 = compare_text("hello world", "hello word")
    print(f"Auto single-line: {result1}")
    
    result2 = compare_text("hello\nworld", "hello\nword")
    print(f"Auto multiline: {result2}")
