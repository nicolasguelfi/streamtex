"""Themable collection cards, next_project / st_next_deck (#92)."""

from unittest.mock import patch

import pytest

from streamtex.collection import CollectionConfig, ProjectMeta, next_project, st_next_deck

pytestmark = pytest.mark.usefixtures("reset_watch")


def _collection():
    c = CollectionConfig(title="T")
    c.projects = {"a": ProjectMeta("A", project_url="http://h:1"), "b": ProjectMeta("B", project_url="http://h:2")}
    return c


def test_next_project_and_wrap():
    c = _collection()
    assert next_project(c, "a")[0] == "b"
    assert next_project(c, "b") is None
    assert next_project(c, "b", wrap=True)[0] == "a"
    with pytest.raises(KeyError):
        next_project(c, "zz")


def test_st_next_deck_carries_the_language():
    out = []
    with patch("streamtex.collection._render", side_effect=lambda h, **k: out.append(h)):
        st_next_deck(_collection(), "a", lang="fr")
        st_next_deck(_collection(), "b")                                   # last: nothing
    assert len(out) == 1 and 'href="http://h:2?lang=fr"' in out[0] and "B" in out[0]


def test_collection_card_colours_are_themable(tmp_path):
    (tmp_path / "collection.toml").write_text(
        '[collection]\ntitle = "C"\ncard_border = "1px solid rgba(255,255,255,0.2)"\n'
        'card_text_color = "#ccc"\n[projects.a]\ntitle = "A"\n')
    c = CollectionConfig.from_toml(str(tmp_path / "collection.toml"))
    assert (c.card_border, c.card_text_color) == ("1px solid rgba(255,255,255,0.2)", "#ccc")
    assert CollectionConfig().card_border == "1px solid #ddd"             # 0.7.x default kept
