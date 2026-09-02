from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from generator.schema import Challenge, load_challenge


class BuildError(RuntimeError):
    pass


def challenge_dir_from_arg(path: Path) -> Path:
    path = path.resolve()
    if path.is_file() and path.name == "challenge.yml":
        return path.parent
    if (path / "challenge.yml").is_file():
        return path
    raise FileNotFoundError(f"challenge.yml not found under {path}")


def load_from_arg(path: Path) -> tuple[Path, Challenge]:
    cdir = challenge_dir_from_arg(path)
    return cdir, load_challenge(cdir / "challenge.yml")


def build_challenge(path: Path) -> Path:
    cdir, ch = load_from_arg(path)
    build_dir = cdir / "build"
    dist_dir = cdir / "dist"
    build_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    if ch.language == "c":
        binary = _build_c(cdir, ch, build_dir, dist_dir)
    else:
        raise BuildError(f"build not implemented for language={ch.language}")

    return binary


def _build_c(cdir: Path, ch: Challenge, build_dir: Path, dist_dir: Path) -> Path:
    src_dir = cdir / ch.private.get("source_dir", "private/src")
    sources = sorted(src_dir.glob("*.c"))
    if not sources:
        raise BuildError(f"no .c sources in {src_dir}")

    binary_name = ch.binary_name
    out = dist_dir / binary_name
    cmd = [
        "gcc",
        "-O1",
        "-fno-inline",
        "-Wall",
        "-Wextra",
        "-o",
        str(out),
        *[str(s) for s in sources],
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise BuildError(
            f"gcc failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
        )

    # Strip symbols for the player-facing binary
    if shutil.which("strip"):
        subprocess.run(["strip", "-s", str(out)], check=False)

    # Keep unstripped copy for author debugging
    debug_copy = build_dir / f"{binary_name}.debug"
    # Rebuild without strip into build/ — simplest: copy before strip already done.
    # Recompile to build/ without strip.
    debug_out = build_dir / binary_name
    cmd_dbg = [
        "gcc",
        "-O0",
        "-g",
        "-Wall",
        "-o",
        str(debug_out),
        *[str(s) for s in sources],
    ]
    subprocess.run(cmd_dbg, check=False, capture_output=True, text=True)
    if debug_out.exists() and not debug_copy.exists():
        shutil.copy2(debug_out, debug_copy)

    return out
