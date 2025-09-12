import kevinlulee as kx
import re
from typing import Optional, List, Tuple




def colon_dict(
    text: str,
    *,
    strict: bool = False,
    skip_empty_strings: bool = True,
    allow_repeated_keys: bool = False,
    transformers: Optional[dict] = None,
) -> dict:
    """
    Parse a headered block format.

    Each header is of the form "key:" or "key: inline value".
    Subsequent non-header lines belong to the current key until the next header.

    - Returns: dict; if allow_repeated_keys=False the last value wins,
      else values are returned under a pluralized key as a list.
    - strict=True: if a key has an inline value (e.g., "a: v") and any
      subsequent non-empty content line appears before the next header,
      raise ValueError.
    - If `transformers` is provided, only keys in transformers are treated
      as headers; other "X:" lines are treated as plain content.
    """
    allowed_keys = set(transformers) if transformers else None

    items: List[Tuple[str, str]] = []
    current_key: Optional[str] = None
    buf: List[str] = []
    had_inline = False  # whether the *current* key had an inline value
    with_braces = text.strip().startswith('[')
    HEADER_RE = re.compile(r"^\[(?P<key>@?[\w-]+)\](?:\s*(?P<val>.*\S))?\s*$") if with_braces else re.compile(r"^(?P<key>@?[\w-]+):(?:\s*(?P<val>.*\S))?\s*$")

    def flush_block() -> None:
        nonlocal current_key, buf, had_inline
        if current_key is not None:
            value = "\n".join(buf).strip()
            if not (skip_empty_strings and value == ""):
                items.append((current_key, value))
        current_key = None
        buf = []
        had_inline = False

    for raw in text.splitlines():
        m = HEADER_RE.match(raw)

        # Valid header only if either no allowlist, or key is allowlisted
        if m and (allowed_keys is None or m.group("key") in allowed_keys):
            flush_block()
            current_key = m.group("key")
            inline = m.group("val")
            had_inline = inline is not None
            if inline is not None:
                buf.append(inline)
            continue  # move to next line after opening a new block

        # Not a recognized header → treat as content (if we have a current block)
        if current_key is None:
            # No active block: ignore leading/preamble content or disallowed headers.
            # (Matches original behavior which doesn't emit items without a key.)
            continue

        # Enforce strict inline rule: any non-empty content after an inline value
        if strict and had_inline and raw.strip() != "":
            raise ValueError(
                f"Inline value given for '{current_key}', but additional content found on a following line."
            )

        # if not (skip_empty_strings and raw == ""):
        buf.append(raw)

    # Flush the final block
    flush_block()

    # Transform values and collapse/group
    def transform_value(k: str, v: str):
        base = kx.coerce_argument(v)
        return (
            transformers[k](base)
            if transformers and k in transformers
            else base
        )

    transformed = [(k, transform_value(k, v)) for (k, v) in items]
    grouped = kx.group(transformed)  # {key: [values...]}

    store: dict = {}
    for k, vals in grouped.items():
        if allow_repeated_keys:
            store[kx.pluralize(k)] = vals
        else:
            store[k] = vals[-1]
    return store



