from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (parent of the generator package)."""
    return Path(__file__).resolve().parent.parent


def templates_dir() -> Path:
    return repo_root() / "templates"


def challenges_dir() -> Path:
    return repo_root() / "challenges"


def catalog_dir() -> Path:
    return repo_root() / "catalog"


def site_dir() -> Path:
    return repo_root() / "site"
