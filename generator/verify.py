from __future__ import annotations

import subprocess
from pathlib import Path

from generator.build import load_from_arg
from generator.secrets import keygenme_serial, sample_usernames


class VerifyError(RuntimeError):
    pass


def verify_challenge(path: Path) -> None:
    cdir, ch = load_from_arg(path)
    binary = cdir / "dist" / ch.binary_name
    if not binary.is_file():
        raise VerifyError(f"missing binary: {binary} (run ptk build first)")

    if ch.type == "crackme":
        password = ch.private.get("password")
        if not password:
            raise VerifyError("crackme missing private.password")
        _expect(binary, [password], expect_success=True)
        _expect(binary, ["wrong-password-xxx"], expect_success=False)
    elif ch.type == "keygenme":
        seed = int(ch.params["seed"])
        for user in sample_usernames()[:3]:
            serial = keygenme_serial(user, seed)
            _expect(binary, [user, serial], expect_success=True)
        _expect(binary, ["alice", "AAAA-BBBB-CCCC-DDDD"], expect_success=False)
    else:
        raise VerifyError(f"verify not implemented for type={ch.type}")


def _expect(binary: Path, args: list[str], *, expect_success: bool) -> None:
    proc = subprocess.run(
        [str(binary), *args],
        capture_output=True,
        text=True,
        timeout=10,
    )
    ok = proc.returncode == 0
    if ok != expect_success:
        raise VerifyError(
            f"unexpected result for args={args!r}: "
            f"rc={proc.returncode} success={ok} expected_success={expect_success}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
