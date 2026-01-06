from __future__ import annotations
import kevinlulee as kx

import time
import secrets

def generate_uid() -> str:
    """
    Generate a UUIDv7-style identifier (time-ordered, collision-safe).
    """
    # Timestamp in milliseconds (48 bits)
    ts_ms = int(time.time() * 1000)
    ts_bytes = ts_ms.to_bytes(6, byteorder="big")

    # Random bytes
    rand = bytearray(secrets.token_bytes(10))

    # Set version to 7 (0111)
    rand[0] = (rand[0] & 0x0F) | 0x70

    # Set variant to RFC 4122 (10xx)
    rand[2] = (rand[2] & 0x3F) | 0x80

    b = ts_bytes + rand

    return (
        f"{b[0:4].hex()}-"
        f"{b[4:6].hex()}-"
        f"{b[6:8].hex()}-"
        f"{b[8:10].hex()}-"
        f"{b[10:16].hex()}"
    )


