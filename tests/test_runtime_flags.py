"""Run-time flags: env_flag, is_editable, is_exportable (#93)."""

import pytest

from streamtex.runtime_flags import env_flag, is_editable, is_exportable

pytestmark = pytest.mark.usefixtures("reset_watch")


def test_runtime_flags(tmp_path, monkeypatch):
    for k in ("STX_EDITABLE", "IS_EDITABLE", "STX_EXPORTABLE", "IS_EXPORTABLE"):
        monkeypatch.delenv(k, raising=False)
    assert is_editable() is False and is_exportable() is False
    env = tmp_path / ".env"
    env.write_text("# deploy\nIS_EXPORTABLE='true'\nexport STX_EDITABLE=0\n")
    assert is_exportable(env) is True and is_editable(env) is False
    monkeypatch.setenv("STX_EDITABLE", "yes")
    assert is_editable(env) is True                                        # environment first
    monkeypatch.setenv("STX_EDITABLE", "maybe")
    with pytest.raises(ValueError):
        env_flag("STX_EDITABLE")
