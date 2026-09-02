from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

VALID_TYPES = frozenset({"crackme", "keygenme", "patchme", "unpackme"})
VALID_LANGS = frozenset({"c", "cpp", "asm", "rust", "go", "python"})
VALID_ARCH = frozenset(
    {
        "linux-x86_64",
        "linux-x86",
        "windows-x86_64",  # PE32+
        "windows-x86",  # PE32
    }
)


def os_from_arch(arch: str) -> str:
    if arch.startswith("windows"):
        return "windows"
    if arch.startswith("linux"):
        return "linux"
    return "unknown"


def bits_from_arch(arch: str) -> int:
    if arch.endswith("x86_64") or arch.endswith("amd64"):
        return 64
    if arch.endswith("x86"):
        return 32
    return 0


def pe_format_from_arch(arch: str) -> str | None:
    """Return PE32 / PE32+ for Windows targets, else None."""
    if not arch.startswith("windows"):
        return None
    return "PE32+" if bits_from_arch(arch) == 64 else "PE32"


@dataclass
class Challenge:
    id: str
    name: str
    type: str
    language: str
    arch: str
    difficulty: int
    summary: str
    public: dict[str, Any]
    private: dict[str, Any]
    params: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def binary_name(self) -> str:
        name = str(self.public.get("binary_name") or self.name)
        if self.os == "windows" and not name.lower().endswith(".exe"):
            return f"{name}.exe"
        return name

    @property
    def os(self) -> str:
        return os_from_arch(self.arch)

    @property
    def bits(self) -> int:
        return bits_from_arch(self.arch)

    @property
    def pe_format(self) -> str | None:
        return pe_format_from_arch(self.arch)

    @property
    def pack_name(self) -> str:
        return f"{self.name}-{self.arch}.zip"

    def validate(self) -> None:
        if self.type not in VALID_TYPES:
            raise ValueError(f"invalid type: {self.type}")
        if self.language not in VALID_LANGS:
            raise ValueError(f"invalid language: {self.language}")
        if self.arch not in VALID_ARCH:
            raise ValueError(f"invalid arch: {self.arch}")
        if not (1 <= self.difficulty <= 5):
            raise ValueError("difficulty must be 1..5")
        if not self.id or not self.name:
            raise ValueError("id and name are required")


def load_challenge(path: Path) -> Challenge:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid challenge.yml: {path}")
    ch = Challenge(
        id=str(data["id"]),
        name=str(data["name"]),
        type=str(data["type"]),
        language=str(data["language"]),
        arch=str(data.get("arch", "linux-x86_64")),
        difficulty=int(data.get("difficulty", 1)),
        summary=str(data.get("summary", "")),
        public=dict(data.get("public") or {}),
        private=dict(data.get("private") or {}),
        params=dict(data.get("params") or {}),
        tags=list(data.get("tags") or []),
        created=data.get("created"),
        raw=data,
    )
    ch.validate()
    return ch


def dump_challenge(ch: Challenge, path: Path) -> None:
    data = {
        "id": ch.id,
        "name": ch.name,
        "type": ch.type,
        "language": ch.language,
        "arch": ch.arch,
        "difficulty": ch.difficulty,
        "summary": ch.summary,
        "tags": ch.tags,
        "created": ch.created,
        "public": ch.public,
        "private": ch.private,
        "params": ch.params,
    }
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
