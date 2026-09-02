from __future__ import annotations

import random
import string


def make_rng(seed: int) -> random.Random:
    return random.Random(seed & 0xFFFFFFFF)


def gen_password(rng: random.Random, length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(rng.choice(alphabet) for _ in range(length))


def xor_key_from_seed(seed: int) -> int:
    return (seed ^ 0xA5A5A5A5) & 0xFF


def encode_xor_bytes(password: str, key: int) -> list[int]:
    return [(ord(c) ^ key) & 0xFF for c in password]


def keygenme_serial(username: str, seed: int) -> str:
    """Deterministic serial used by the easy C keygenme template.

    Mixes username bytes with a seed-derived state, then emits 4 hex groups.
    """
    state = (seed ^ 0x9E3779B9) & 0xFFFFFFFF
    for ch in username.encode():
        state = (state * 1664525 + ch + 1013904223) & 0xFFFFFFFF
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= (state >> 17) & 0xFFFFFFFF
        state ^= (state << 5) & 0xFFFFFFFF
    # Derive 8 bytes of material
    parts: list[str] = []
    s = state
    for _ in range(4):
        s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
        parts.append(f"{s & 0xFFFF:04X}")
    return "-".join(parts)


def sample_usernames() -> list[str]:
    return ["alice", "bob", "petik", "root", "guest"]
