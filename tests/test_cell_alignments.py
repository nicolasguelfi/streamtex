"""CellAlignments: content alignment presets for st_grid cells (#22)."""

import pytest

from streamtex.styles import CellAlignments, Container, StxStyles

H = {"left": ("flex-start", None), "center": ("center", "center"), "right": ("flex-end", "right")}
V = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}


@pytest.mark.parametrize("h", H)
@pytest.mark.parametrize("v", V)
def test_preset(h, v):
    style = getattr(CellAlignments, f"{h}_{v}")
    css = str(style)
    assert css.startswith("display:flex;flex-direction:column;")
    assert f"justify-content:{V[v]};" in css
    assert f"align-items:{H[h][0]};" in css
    text_align = H[h][1]
    assert (f"text-align:{text_align};" in css) if text_align else ("text-align" not in css)
    assert style.style_id == f"cell_{h}_{v}"


def test_aliases_and_facade():
    assert CellAlignments.center is CellAlignments.center_middle
    assert Container.cells is CellAlignments
    assert StxStyles.cell_center is CellAlignments.center_middle


def test_composable():
    combined = Container.cells.center + Container.paddings.medium_padding
    assert "justify-content:center;" in str(combined) and "padding" in str(combined)
