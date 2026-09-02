from collections import Counter

from generator.gen import pick_arch
from generator.schema import Challenge
from generator.secrets import keygenme_serial


def test_serial_stable():
    assert keygenme_serial("alice", 0x12345678) == "FB94-B1E3-6DE6-2C0D"
    assert keygenme_serial("bob", 0x12345678) == "144A-7721-260C-A9FB"


def test_serial_changes_with_seed():
    assert keygenme_serial("alice", 1) != keygenme_serial("alice", 2)


def test_pick_arch_biased_windows():
    counts = Counter(pick_arch(None) for _ in range(1000))
    assert counts["windows-x86_64"] / 1000 > 0.8
    assert counts["linux-x86_64"] / 1000 < 0.25


def test_windows_binary_name_exe():
    ch = Challenge(
        id="x",
        name="demo",
        type="crackme",
        language="c",
        arch="windows-x86_64",
        difficulty=1,
        summary="",
        public={"binary_name": "demo"},
        private={},
    )
    assert ch.os == "windows"
    assert ch.binary_name == "demo.exe"
    assert ch.pack_name == "demo-windows-x86_64.zip"
