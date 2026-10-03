"""ProjectBlockRegistry(shared_dirs=): shared block directories (#90, #19)."""

import pytest

pytestmark = pytest.mark.usefixtures("reset_watch")


def test_registry_falls_back_on_shared_dirs_and_keeps_its_own_iteration(tmp_path):
    from streamtex.blocks import BlockNotFoundError, ProjectBlockRegistry

    local = tmp_path / "m1" / "blocks"
    shared = tmp_path / "shared-blocks" / "blocks"
    (shared / "trainers").mkdir(parents=True)
    local.mkdir(parents=True)
    (local / "bck_intro.py").write_text("WHO = 'local intro'\ndef build(**_): pass\n")
    (local / "bck_glossary.py").write_text("WHO = 'local glossary'\ndef build(**_): pass\n")
    (shared / "bck_glossary.py").write_text("WHO = 'shared glossary'\ndef build(**_): pass\n")
    (shared / "trainers" / "bck_trainer.py").write_text("WHO = 'shared trainer'\ndef build(**_): pass\n")

    reg = ProjectBlockRegistry(local, shared_dirs=[shared])
    assert reg.bck_intro.WHO == "local intro"
    assert reg.bck_glossary.WHO == "local glossary"           # local wins
    assert reg.bck_trainer.WHO == "shared trainer"            # recursive fallback
    assert [m.WHO for m in reg] == ["local glossary", "local intro"]  # iteration: own blocks only
    assert len(reg) == 2 and reg.list_shared_blocks() == ["bck_trainer"]
    with pytest.raises(BlockNotFoundError, match="Shared: bck_trainer"):
        reg.get("bck_nope")
    assert ProjectBlockRegistry(local).list_shared_blocks() == []   # no shared_dirs: as before
