# text_similarity_module.py
# Unified, importable module with auto-metric selection by LINE COUNT
# - No CLI / env usage
# - Provides a single public entrypoint: get_text_similarity_score
# - Uses only the metrics auto-determined from single-line vs multi-line
# - Includes exactly ONE minimal example call at bottom

from collections import Counter
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
import math
import re

# ------------------------- #
# -------- Utilities ------ #
# ------------------------- #

def _normalize(s: str) -> str:
    """Lowercase, collapse whitespace, strip edges."""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def _tokenize_words(s: str) -> List[str]:
    """Simple alnum word tokenizer (keeps digits)."""
    return [t for t in re.split(r"[^0-9a-zA-Z]+", s) if t]

def _char_ngrams(s: str, n: int = 3) -> List[str]:
    """Character n-grams with soft boundaries."""
    s = f" {s} "
    return [s[i : i + n] for i in range(max(0, len(s) - n + 1))] or [s]

def _cosine(v1: Counter, v2: Counter) -> float:
    """Cosine similarity over bag-of-words counters."""
    both = set(v1) | set(v2)
    dot = sum(v1[t] * v2[t] for t in both)
    n1 = math.sqrt(sum(v1[t] ** 2 for t in both))
    n2 = math.sqrt(sum(v2[t] ** 2 for t in both))
    return 0.0 if n1 == 0.0 or n2 == 0.0 else dot / (n1 * n2)

def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity over sets."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if (a or b) else 0.0

def _overlap(a: set, b: set) -> float:
    """Overlap coefficient over sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))

def _levenshtein_distance(a: str, b: str) -> int:
    """Classic O(len(a)*len(b)) Levenshtein distance."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(
                prev[j] + 1,      # deletion
                cur[j-1] + 1,     # insertion
                prev[j-1] + cost  # substitution
            ))
        prev = cur
    return prev[-1]

# -------------------------------------- #
# ---- Metric computation (on demand) ---#
# -------------------------------------- #

def _compute_artifacts(a: str, b: str, *, use_normalize: bool, char_ngram_n: int):
    """Precompute shared artifacts for efficiency."""
    if use_normalize:
        a = _normalize(a)
        b = _normalize(b)

    words_a = set(_tokenize_words(a))
    words_b = set(_tokenize_words(b))
    bow_a = Counter(_tokenize_words(a))
    bow_b = Counter(_tokenize_words(b))
    chargrams_a = set(_char_ngrams(a, n=char_ngram_n))
    chargrams_b = set(_char_ngrams(b, n=char_ngram_n))

    return {
        "a": a,
        "b": b,
        "words_a": words_a,
        "words_b": words_b,
        "bow_a": bow_a,
        "bow_b": bow_b,
        "chargrams_a": chargrams_a,
        "chargrams_b": chargrams_b,
    }

def _metric_scores_subset(art: Dict, metrics: List[str]) -> Dict[str, float]:
    """Compute only requested metrics."""
    a = art["a"]; b = art["b"]
    words_a = art["words_a"]; words_b = art["words_b"]
    bow_a = art["bow_a"]; bow_b = art["bow_b"]
    cga = art["chargrams_a"]; cgb = art["chargrams_b"]

    out: Dict[str, float] = {}

    if "sequence_ratio" in metrics:
        out["sequence_ratio"] = SequenceMatcher(None, a, b).ratio()

    if "levenshtein_similarity" in metrics:
        max_len = max(len(a), len(b)) or 1
        out["levenshtein_similarity"] = 1.0 - (_levenshtein_distance(a, b) / max_len)

    if "jaccard_char_ngram" in metrics:
        out["jaccard_char_ngram"] = _jaccard(cga, cgb)

    if "token_sort_ratio" in metrics:
        out["token_sort_ratio"] = SequenceMatcher(
            None, " ".join(sorted(words_a)), " ".join(sorted(words_b))
        ).ratio()

    if "cosine_bow" in metrics:
        out["cosine_bow"] = _cosine(bow_a, bow_b)

    if "jaccard_word" in metrics:
        out["jaccard_word"] = _jaccard(words_a, words_b)

    if "overlap_coefficient" in metrics:
        out["overlap_coefficient"] = _overlap(words_a, words_b)

    # round all
    return {k: round(v, 4) for k, v in out.items()}

# ------------------------------------------------ #
# ---- Auto-selection: single-line vs multi-line ---#
# ------------------------------------------------ #

_SINGLE_LINE_METRICS: Tuple[str, ...] = (
    "levenshtein_similarity",
    "sequence_ratio",
    "jaccard_char_ngram",
)  # optimized for short, single-line strings

_MULTI_LINE_METRICS: Tuple[str, ...] = (
    "cosine_bow",
    "jaccard_word",
    "overlap_coefficient",
)  # optimized for multi-line / longer text & inclusion

def _is_multiline(s: str) -> bool:
    """Return True if text spans multiple lines."""
    # More robust than counting '\n' only—treat any newline as multiline.
    return ("\n" in s)

def _select_metrics_by_line_count(s1: str, s2: str) -> List[str]:
    """
    If either string is multi-line (contains a newline), use MULTI-LINE metrics.
    Otherwise, use SINGLE-LINE metrics.
    """
    return list(_MULTI_LINE_METRICS if (_is_multiline(s1) or _is_multiline(s2)) else _SINGLE_LINE_METRICS)

# ------------------------------------------- #
# ---- Preset weights (filtered by subset) ---#
# ------------------------------------------- #

def _base_preset_weights() -> Dict[str, float]:
    """
    Base weight suggestions across all metrics.
    These will be filtered down to the active subset (single- or multi-line).
    """
    return {
        "sequence_ratio": 0.15,
        "levenshtein_similarity": 0.15,
        "token_sort_ratio": 0.15,
        "cosine_bow": 0.20,
        "jaccard_word": 0.10,
        "jaccard_char_ngram": 0.15,
        "overlap_coefficient": 0.10,
    }

def _preset_weights_for_subset(preset: str, subset_metrics: List[str]) -> Dict[str, float]:
    """
    Choose preset weights, then filter and renormalize to the selected subset.
    Supported presets: 'balanced', 'substring', 'paraphrase'
    """
    p = (preset or "balanced").lower()
    if p == "balanced":
        w = {
            "sequence_ratio": 0.15,
            "levenshtein_similarity": 0.15,
            "token_sort_ratio": 0.15,
            "cosine_bow": 0.20,
            "jaccard_word": 0.10,
            "jaccard_char_ngram": 0.15,
            "overlap_coefficient": 0.10,
        }
    elif p == "substring":
        w = {
            "sequence_ratio": 0.10,
            "levenshtein_similarity": 0.10,
            "token_sort_ratio": 0.10,
            "cosine_bow": 0.15,
            "jaccard_word": 0.10,
            "jaccard_char_ngram": 0.25,
            "overlap_coefficient": 0.20,
        }
    elif p == "paraphrase":
        w = {
            "sequence_ratio": 0.10,
            "levenshtein_similarity": 0.10,
            "token_sort_ratio": 0.20,
            "cosine_bow": 0.25,
            "jaccard_word": 0.20,
            "jaccard_char_ngram": 0.10,
            "overlap_coefficient": 0.05,
        }
    else:
        raise ValueError("Unknown preset. Use 'balanced', 'substring', or 'paraphrase'.")

    # Filter to subset and renormalize
    w_subset = {k: v for k, v in w.items() if k in subset_metrics}
    if not w_subset:
        # As a fallback (shouldn't happen), assign uniform weights
        w_subset = {k: 1.0 for k in subset_metrics}
    total = sum(w_subset.values())
    if total <= 0:
        w_subset = {k: 1.0 for k in subset_metrics}
        total = sum(w_subset.values())
    return {k: v / total for k, v in w_subset.items()}

# ------------------------------------------------ #
# --------------- Public Entrypoint ---------------#
# ------------------------------------------------ #

def get_text_similarity_score(
    s1: str,
    s2: str,
    *,
    preset: str = "balanced",
    weights: Optional[Dict[str, float]] = None,
    use_normalize: bool = True,
    char_ngram_n: int = 3
) -> float:
    """
    Args:
        s1, s2: Strings to compare.
    Returns:
        float: Weighted similarity between 0.0 (very different) and 1.0 (identical)
    """
    metrics = _select_metrics_by_line_count(s1, s2)
    art = _compute_artifacts(s1, s2, use_normalize=use_normalize, char_ngram_n=char_ngram_n)
    scores = _metric_scores_subset(art, metrics)
    norm_weights = _preset_weights_for_subset(preset, metrics)

    if weights:
        mix = dict(norm_weights)
        for k, v in weights.items():
            if k in mix:
                mix[k] = float(v)
        total = sum(mix.values())
        if total <= 0:
            mix = {k: 1.0 for k in metrics}
            total = sum(mix.values())
        norm_weights = {k: v / total for k, v in mix.items()}

    composite = sum(scores[k] * norm_weights[k] for k in norm_weights)
    return round(composite, 4)

# ------------------------------------------- #
# -------------- ONE EXAMPLE CALL ------------#
# ------------------------------------------- #

if __name__ == "__main__":
    # Minimal, single example call (required):
    demo = get_text_similarity_score("Hello world", "Hello, world!")
    # The following print is part of the self-demo, not required by importers.
    print(demo)
