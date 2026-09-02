from __future__ import annotations

import sys
from pathlib import Path

import click

from generator import __version__
from generator.build import BuildError, build_challenge
from generator.catalog import build_catalog
from generator.gen import generate
from generator.pack import LeakError, PackError, pack_challenge
from generator.schema import VALID_ARCH, VALID_LANGS, VALID_TYPES
from generator.verify import VerifyError, verify_challenge


def _parse_seed(_ctx: click.Context, _param: click.Parameter, value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value, 0)
    except ValueError as e:
        raise click.BadParameter("expected int (decimal or 0xHEX)") from e


@click.group()
@click.version_option(__version__, prog_name="ptk")
def main() -> None:
    """crackme-ptk — generate, build, verify and pack crackmes (Windows/Linux)."""


@main.command("gen")
@click.option("--type", "type_", type=click.Choice(sorted(VALID_TYPES)), required=True)
@click.option("--lang", "language", type=click.Choice(sorted(VALID_LANGS)), required=True)
@click.option("--difficulty", type=click.IntRange(1, 5), default=1, show_default=True)
@click.option(
    "--name",
    default=None,
    help="Optional slug; auto-chosen from type/algo/difficulty if omitted",
)
@click.option(
    "--arch",
    type=click.Choice(sorted(VALID_ARCH)),
    default=None,
    help="Target arch (default: ~88% windows-x86_64, ~12% linux-x86_64)",
)
@click.option(
    "--seed",
    default=None,
    callback=_parse_seed,
    help="Optional deterministic seed (decimal or 0xHEX)",
)
@click.option("--id", "challenge_id", default=None, help="Optional challenge id (cm-YYYY-NNN)")
def gen_cmd(
    type_: str,
    language: str,
    difficulty: int,
    name: str | None,
    arch: str,
    seed: int | None,
    challenge_id: str | None,
) -> None:
    """Generate a new challenge from templates."""
    try:
        out = generate(
            type_=type_,
            language=language,
            difficulty=difficulty,
            name=name,
            seed=seed,
            challenge_id=challenge_id,
            arch=arch,
        )
    except FileNotFoundError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    except FileExistsError as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    click.echo(f"generated {out}")


@main.command("build")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def build_cmd(path: Path) -> None:
    """Compile a challenge to dist/ (ELF)."""
    try:
        binary = build_challenge(path)
    except (BuildError, FileNotFoundError, ValueError) as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    click.echo(f"built {binary}")


@main.command("verify")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def verify_cmd(path: Path) -> None:
    """Run author checks against the built binary."""
    try:
        verify_challenge(path)
    except VerifyError as e:
        click.echo(f"FAIL: {e}", err=True)
        sys.exit(1)
    click.echo("verify OK")


@main.command("pack")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", type=click.Path(path_type=Path), default=None)
def pack_cmd(path: Path, output: Path | None) -> None:
    """Create the public zip (binary + public README), with leak checks."""
    try:
        z = pack_challenge(path, output=output)
    except (PackError, LeakError, FileNotFoundError, ValueError) as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)
    click.echo(f"packed {z}")


@main.command("catalog")
def catalog_cmd() -> None:
    """Rebuild catalog/index.json (public metadata only)."""
    out = build_catalog()
    click.echo(f"wrote {out}")


@main.command("all")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def all_cmd(path: Path) -> None:
    """build + verify + pack for one challenge."""
    try:
        binary = build_challenge(path)
        click.echo(f"built {binary}")
        verify_challenge(path)
        click.echo("verify OK")
        z = pack_challenge(path)
        click.echo(f"packed {z}")
    except (BuildError, VerifyError, PackError, LeakError, FileNotFoundError, ValueError) as e:
        click.echo(f"error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
