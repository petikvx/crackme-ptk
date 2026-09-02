from __future__ import annotations

import random
import re
import secrets
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from generator.paths import challenges_dir, templates_dir
from generator.schema import Challenge, dump_challenge, os_from_arch
from generator.secrets import (
    encode_xor_bytes,
    gen_password,
    keygenme_serial,
    make_rng,
    sample_usernames,
    xor_key_from_seed,
)

# Default mix for generated challenges when --arch is omitted
WINDOWS_ARCH_RATIO = 0.88
DEFAULT_WINDOWS_ARCH = "windows-x86_64"
DEFAULT_LINUX_ARCH = "linux-x86_64"

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = _SLUG_RE.sub("-", s).strip("-")
    return s or "challenge"


_DIFF_LABEL = {1: "easy", 2: "medium", 3: "hard", 4: "expert", 5: "insane"}

_ALGO_NAME = {
    "xor_bytes": "xor-bytes",
    "seeded_mix_serial": "serial-mix",
}


def pick_arch(explicit: str | None = None) -> str:
    """Choose target arch; ~88% Windows when not specified."""
    if explicit:
        return explicit
    if random.random() < WINDOWS_ARCH_RATIO:
        return DEFAULT_WINDOWS_ARCH
    return DEFAULT_LINUX_ARCH


def suggest_name(
    *,
    type_: str,
    language: str,
    difficulty: int,
    algo: str | None = None,
    arch: str = DEFAULT_LINUX_ARCH,
) -> str:
    """Pick a descriptive slug from type / algo / difficulty / OS."""
    diff = _DIFF_LABEL.get(difficulty, f"d{difficulty}")
    if algo and algo in _ALGO_NAME:
        base = _ALGO_NAME[algo]
    elif type_ == "crackme":
        base = "xor-bytes"
    elif type_ == "keygenme":
        base = "serial-mix"
    else:
        base = type_
    # OS is tracked in challenge.yml / catalog — keep the slug focused on mechanic.
    parts = [base, diff]
    if language != "c":
        parts.append(language)
    return slugify("-".join(parts))


def unique_name(base: str, challenges: Path) -> str:
    """Ensure name is unique among existing challenges."""
    taken: set[str] = set()
    if challenges.exists():
        for yml in challenges.glob("*/challenge.yml"):
            try:
                data = yml.read_text(encoding="utf-8")
            except OSError:
                continue
            for line in data.splitlines():
                if line.startswith("name:"):
                    taken.add(line.split(":", 1)[1].strip().strip("'\""))
                    break
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def next_id(challenges: Path) -> str:
    existing: set[str] = set()
    if challenges.exists():
        for p in challenges.iterdir():
            if p.is_dir() and p.name.startswith("cm-"):
                existing.add(p.name)
    year = date.today().year
    n = 1
    while True:
        cid = f"cm-{year}-{n:03d}"
        if cid not in existing:
            return cid
        n += 1


def template_path(type_: str, language: str, difficulty: int) -> Path:
    """Resolve best matching template directory."""
    base = templates_dir() / language / type_
    candidates = [
        base / f"difficulty-{difficulty}",
        base / "difficulty-1",
        base,
    ]
    for c in candidates:
        if c.is_dir() and any(c.iterdir()):
            return c
    raise FileNotFoundError(
        f"no template for language={language} type={type_} difficulty={difficulty}"
    )


def _jinja_env(template_root: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_root)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )


def render_dir(template_root: Path, relative: str, dest: Path, ctx: dict) -> None:
    """Render files under template_root/relative into dest.

    Files ending with `.j2` are Jinja-rendered (suffix stripped).
    Other files are copied as-is.
    """
    src = template_root / relative
    if not src.exists():
        return
    env = _jinja_env(template_root)
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "template.meta.yml":
            continue
        rel = path.relative_to(src)
        if path.name.endswith(".j2"):
            out_rel = Path(str(rel)[:-3])
            rel_env = path.relative_to(template_root)
            text = env.get_template(str(rel_env).replace("\\", "/")).render(**ctx)
            out = dest / out_rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        else:
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(path.read_bytes())


def build_context(
    *,
    type_: str,
    language: str,
    difficulty: int,
    name: str,
    seed: int | None,
) -> dict:
    seed_i = seed if seed is not None else secrets.randbits(32)
    rng = make_rng(seed_i)
    password = gen_password(rng, 12)
    xor_key = xor_key_from_seed(seed_i)
    encoded = encode_xor_bytes(password, xor_key)
    users = sample_usernames()
    serials = {u: keygenme_serial(u, seed_i) for u in users}
    return {
        "name": name,
        "type": type_,
        "language": language,
        "difficulty": difficulty,
        "seed": seed_i,
        "password": password,
        "xor_key": xor_key,
        "encoded_password": encoded,
        "encoded_password_c": ", ".join(f"0x{b:02x}" for b in encoded),
        "sample_usernames": users,
        "sample_serials": serials,
        "example_user": users[0],
        "example_serial": serials[users[0]],
    }


def generate(
    *,
    type_: str,
    language: str,
    difficulty: int = 1,
    name: str | None = None,
    seed: int | None = None,
    challenge_id: str | None = None,
    arch: str | None = None,
) -> Path:
    root = challenges_dir()
    root.mkdir(parents=True, exist_ok=True)
    arch = pick_arch(arch)
    os_name = os_from_arch(arch)
    algo = "xor_bytes" if type_ == "crackme" else "seeded_mix_serial"
    if name:
        name_slug = slugify(name)
    else:
        name_slug = unique_name(
            suggest_name(
                type_=type_,
                language=language,
                difficulty=difficulty,
                algo=algo,
                arch=arch,
            ),
            root,
        )
    cid = challenge_id or next_id(root)
    out = root / cid
    if out.exists():
        raise FileExistsError(f"challenge already exists: {out}")

    tpl = template_path(type_, language, difficulty)
    ctx = build_context(
        type_=type_,
        language=language,
        difficulty=difficulty,
        name=name_slug,
        seed=seed,
    )
    ctx["arch"] = arch
    ctx["os"] = os_name
    ctx["binary_name"] = f"{name_slug}.exe" if os_name == "windows" else name_slug

    out.mkdir(parents=True)
    render_dir(tpl, "public", out / "public", ctx)
    render_dir(tpl, "private", out / "private", ctx)

    ch = Challenge(
        id=cid,
        name=name_slug,
        type=type_,
        language=language,
        arch=arch,
        difficulty=difficulty,
        summary=_summary_for(type_, language, difficulty, algo=algo, os_name=os_name),
        tags=[type_, language, f"diff-{difficulty}", os_name, algo],
        created=date.today().isoformat(),
        public={
            "readme": "public/README.md",
            "binary_name": name_slug,
        },
        private={
            "source_dir": "private/src",
            "solution": "private/SOLUTION.md",
            "flag_or_key": (
                ctx["password"]
                if type_ == "crackme"
                else f"serial(user)=seeded-mix(seed={ctx['seed']})"
            ),
        },
        params={
            "seed": ctx["seed"],
            "algo": algo,
        },
    )
    if type_ == "crackme":
        ch.private["password"] = ctx["password"]
        ch.params["xor_key"] = ctx["xor_key"]
    else:
        ch.private["example_user"] = ctx["example_user"]
        ch.private["example_serial"] = ctx["example_serial"]

    dump_challenge(ch, out / "challenge.yml")

    sol = out / "private" / "SOLUTION.md"
    if not sol.exists():
        sol.write_text(_default_solution(type_, ctx), encoding="utf-8")

    readme = out / "public" / "README.md"
    if not readme.exists():
        readme.write_text(_default_readme(ch), encoding="utf-8")

    return out


def _summary_for(
    type_: str,
    language: str,
    difficulty: int,
    *,
    algo: str | None = None,
    os_name: str = "linux",
) -> str:
    bits = [type_, language, f"diff {difficulty}", os_name]
    if algo:
        bits.append(algo)
    return ", ".join(bits)


def _default_solution(type_: str, ctx: dict) -> str:
    if type_ == "crackme":
        return (
            "# Solution\n\n"
            f"Password: `{ctx['password']}`\n\n"
            f"Seed: `{ctx['seed']}`\n"
            f"XOR key: `0x{ctx['xor_key']:02x}`\n"
        )
    return (
        "# Solution\n\n"
        "Serial algorithm: seeded mix of username bytes → 4×16-bit hex groups.\n\n"
        f"Seed: `{ctx['seed']}`\n\n"
        f"Example: user `{ctx['example_user']}` → `{ctx['example_serial']}`\n"
    )


def _default_readme(ch: Challenge) -> str:
    goal = (
        "Find the correct password."
        if ch.type == "crackme"
        else "Write a keygen: given a username, produce a valid serial."
    )
    target = (
        "Windows x86_64 PE (.exe)"
        if ch.os == "windows"
        else "Linux x86_64 ELF"
    )
    return (
        f"# {ch.name}\n\n"
        f"**Type:** {ch.type}  \n"
        f"**Language:** {ch.language}  \n"
        f"**Difficulty:** {ch.difficulty}  \n"
        f"**OS:** {ch.os}  \n"
        f"**Arch:** {ch.arch}\n\n"
        f"{ch.summary}\n\n"
        f"## Goal\n\n{goal}\n\n"
        "## Rules\n\n"
        f"- Target: {target}\n"
        "- Author private sources and solutions are not included in this pack\n"
    )
