from generator.secrets import keygenme_serial


def test_serial_stable():
    assert keygenme_serial("alice", 0x12345678) == "FB94-B1E3-6DE6-2C0D"
    assert keygenme_serial("bob", 0x12345678) == "144A-7721-260C-A9FB"


def test_serial_changes_with_seed():
    assert keygenme_serial("alice", 1) != keygenme_serial("alice", 2)
