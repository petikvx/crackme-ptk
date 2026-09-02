from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from generator.paths import repo_root
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
        return _build_c(cdir, ch, build_dir, dist_dir)
    if ch.language == "asm":
        return _build_asm(cdir, ch, dist_dir)
    raise BuildError(f"build not implemented for language={ch.language}")


def _c_compiler(ch: Challenge) -> tuple[str, str | None]:
    """Return (compiler, strip_tool)."""
    if ch.os == "windows":
        if ch.bits == 32:
            cc = shutil.which("i686-w64-mingw32-gcc")
            strip = shutil.which("i686-w64-mingw32-strip") or shutil.which("strip")
            if not cc:
                raise BuildError(
                    "PE32 C build requires mingw-w64 32-bit "
                    "(i686-w64-mingw32-gcc)"
                )
            return cc, strip
        cc = shutil.which("x86_64-w64-mingw32-gcc")
        if not cc:
            raise BuildError(
                "PE32+ C build requires mingw-w64 "
                "(x86_64-w64-mingw32-gcc)"
            )
        strip = shutil.which("x86_64-w64-mingw32-strip") or shutil.which("strip")
        return cc, strip

    if ch.bits == 32:
        cc = shutil.which("gcc")
        if not cc:
            raise BuildError("gcc not found")
        return cc, shutil.which("strip")

    cc = shutil.which("gcc")
    if not cc:
        raise BuildError("gcc not found")
    return cc, shutil.which("strip")


def _build_c(cdir: Path, ch: Challenge, build_dir: Path, dist_dir: Path) -> Path:
    src_dir = cdir / ch.private.get("source_dir", "private/src")
    sources = sorted(src_dir.glob("*.c"))
    if not sources:
        raise BuildError(f"no .c sources in {src_dir}")

    cc, strip_tool = _c_compiler(ch)
    binary_name = ch.binary_name
    out = dist_dir / binary_name
    cmd = [
        cc,
        "-O1",
        "-fno-inline",
        "-Wall",
        "-Wextra",
        "-o",
        str(out),
        *[str(s) for s in sources],
    ]
    if ch.os == "linux" and ch.bits == 32:
        cmd[1:1] = ["-m32"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise BuildError(
            f"{cc} failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
        )

    if strip_tool:
        subprocess.run([strip_tool, "-s", str(out)], check=False)

    debug_out = build_dir / binary_name
    cmd_dbg = [cc, "-O0", "-g", "-Wall", "-o", str(debug_out), *[str(s) for s in sources]]
    if ch.os == "linux" and ch.bits == 32:
        cmd_dbg[1:1] = ["-m32"]
    subprocess.run(cmd_dbg, check=False, capture_output=True, text=True)

    return out


def find_fasm() -> str:
    """Locate fasm binary: PATH, then third_party/fasm/fasm.x64|fasm."""
    for name in ("fasm.x64", "fasm"):
        found = shutil.which(name)
        if found:
            return found
    root = repo_root() / "third_party" / "fasm"
    for name in ("fasm.x64", "fasm"):
        candidate = root / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise BuildError(
        "fasm not found. Install Flat Assembler and put it in PATH, e.g.:\n"
        "  # Debian/Ubuntu\n"
        "  sudo apt install fasm\n"
        "  # or download from https://flatassembler.net/download.php\n"
        "  # Linux package → extract → export PATH=\"$PWD/fasm:$PATH\"\n"
        "  # Windows INCLUDE (optional for our templates): fasmw*.zip INCLUDE/"
    )


def _build_asm(cdir: Path, ch: Challenge, dist_dir: Path) -> Path:
    if ch.os != "windows":
        raise BuildError("asm templates currently target Windows PE via FASM only")

    src_dir = cdir / ch.private.get("source_dir", "private/src")
    sources = sorted(src_dir.glob("*.asm"))
    if not sources:
        raise BuildError(f"no .asm sources in {src_dir}")
    if len(sources) != 1:
        raise BuildError("asm build expects exactly one .asm file")

    fasm = find_fasm()
    out = dist_dir / ch.binary_name
    # Assemble in src dir so relative includes work if present
    cmd = [fasm, str(sources[0]), str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(src_dir))
    if proc.returncode != 0:
        raise BuildError(
            f"fasm failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
        )
    if not out.is_file():
        # Some fasm versions write next to source
        alt = sources[0].with_suffix(".exe")
        if alt.is_file():
            alt.rename(out)
        else:
            raise BuildError(f"fasm produced no output at {out}")
    return out
