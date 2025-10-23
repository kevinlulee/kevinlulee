import re
from typing import List, Optional

# Prefer hashes appearing after common context words like "commit", "revert", etc.
_CONTEXT_SHA = re.compile(
    r"""(?xi)
    (?:\bcommit\b
      | \bcherry[-\s]?picked\s+from\s+commit\b
      | \breverts?\b
      | \breverted\b
      | \bfixup!?\b
      | \bbackport(?:ed)?\s+of\b
      | \bsha(?:-?1|256)?\b
      | \bhash\b
      | \bid\b
      | \bref(?:s)?\b)
    [^\da-f]{0,5}
    (?P<sha>[0-9a-f]{7,64})
    """,
)

# Fallback: any standalone 7–64 hex run (not part of a longer hex word)
_GENERIC_SHA = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{7,64}(?![0-9a-f])")


def extract_git_commit_id(
    message: str, *, return_all: bool = False
) -> Optional[str | List[str]]:
    """
    Extract a Git commit hash from a commit message string.

    - Prefers hashes found after context words like 'commit', 'revert', etc.
    - Supports SHA-1 (40 chars), SHA-256 (64 chars), and abbreviated >=7 chars.
    - Returns the 'best' match (prefers 64, then 40, then longest abbrev), or
      returns a list of all matches if return_all=True.
    - Returns None / [] if nothing looks like a hash.

    Examples:
        extract_commit_id("cherry picked from commit a1b2c3d4e5f6") -> "a1b2c3d4e5f6"
        extract_commit_id("Reverts 3f4e2c1 (bad commit)") -> "3f4e2c1"
        extract_commit_id("Fix: refs #abc1234 and 0123abcd") -> "0123abcd"
    """
    if not message:
        return [] if return_all else None

    # 1) Context-aware candidates
    cands = [m.group("sha").lower() for m in _CONTEXT_SHA.finditer(message)]
    # 2) Fallback to generic if none found
    if not cands:
        cands = [m.group(0).lower() for m in _GENERIC_SHA.finditer(message)]

    # Deduplicate while preserving order
    seen = set()
    cands = [h for h in cands if not (h in seen or seen.add(h))]

    if not cands:
        return [] if return_all else None

    if return_all:
        # Sort for convenience: longer (64/40) first, then by appearance order
        return sorted(cands, key=lambda s: (-(len(s) in (64, 40)), -len(s)))

    # Pick the "best" single candidate: prefer 64, then 40, then longest abbrev
    def score(s: str) -> tuple[int, int]:
        if len(s) == 64:
            return (3, 64)
        if len(s) == 40:
            return (2, 40)
        return (1, len(s))

    return max(cands, key=score)
