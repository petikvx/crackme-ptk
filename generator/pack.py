from __future__ import annotations

import re
import zipfile
from pathlib import Path

from generator.build import load_from_arg
from generator.schema import Challenge

LEAK_PATTERNS = [
    re.compile(r"private/", re.I),
    re.compile(r"SOLUTION", re.I),
    re.compile(r"challenge\.yml", re.I),
]


class PackError(RuntimeError):
    pass


class LeakError(RuntimeError):
    pass


def pack_challenge(path: Path, *, output: Path | None = None) -> Path:
    cdir, ch = load_from_arg(path)
    binary = cdir / "dist" / ch.binary_name
    if not binary.is_file():
        raise PackError(f"missing binary: {binary} (run ptk build first)")

    readme = cdir / ch.public.get("readme", "public/README.md")
    if not readme.is_file():
        raise PackError(f"missing public readme: {readme}")

    out = output or (cdir / "dist" / f"{ch.name}-linux-x86_64.zip")
    out.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(binary, arcname=ch.binary_name)
        zf.write(readme, arcname="README.md")
        # Optional public extras (hints), never private/
        public_dir = cdir / "public"
        for extra in public_dir.rglob("*"):
            if not extra.is_file():
                continue
            if extra.resolve() == readme.resolve():
                continue
            arc = Path("public") / extra.relative_to(public_dir)
            zf.write(extra, arcname=str(arc))

    _leak_check(out, ch)
    return out


def _leak_check(zip_path: Path, ch: Challenge) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        for name in names:
            for pat in LEAK_PATTERNS:
                if pat.search(name):
                    raise LeakError(f"possible leak in archive path: {name}")
            if name.startswith("private/") or "/private/" in name:
                raise LeakError(f"private path in archive: {name}")

        # Flag/password must not appear as plaintext in packaged files (text)
        secrets_to_hide: list[str] = []
        if ch.type == "crackme" and ch.private.get("password"):
            secrets_to_hide.append(str(ch.private["password"]))
        if ch.private.get("example_serial"):
            secrets_to_hide.append(str(ch.private["example_serial"]))

        for info in zf.infolist():
            if info.is_dir():
                continue
            # Skip binary for plaintext password scan (strings may still contain it
            # for easy crackmes — that's expected for difficulty 1).
            if info.filename == ch.binary_name:
                continue
            data = zf.read(info.filename)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for secret in secrets_to_hide:
                if secret and secret in text:
                    raise LeakError(
                        f"secret leaked in {info.filename} inside public pack"
                    )
