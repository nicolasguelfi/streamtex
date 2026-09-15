"""The HTML export must reach the same list rendering as the live page (0.7.34).

The exported document is real ``<ul>``/``<li>`` markup, so the browser applies
``list-style-position`` itself — but no selector can match on an INHERITED
``text-align``, which is why the document resolves it with a few lines of
script, the same rule the live marker observer applies.  Until 0.7.33 the
document also carried ``ol, ul { text-align: left; }``, the export twin of the
inline floor the live list root used to force: it blocked the inheritance
altogether, so the export contradicted the live page.

Lives in its own module because Playwright's sync API cannot be entered twice,
and ``test_list_alignment.py`` holds a session open for the whole module.

Run:
    uv run pytest -m e2e tests/e2e/test_list_export_alignment.py -v
"""
from __future__ import annotations

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from ._nav_harness import launch_browser  # noqa: E402

pytestmark = pytest.mark.e2e

VIEWPORT = {"width": 1920, "height": 1080}

EXPORT_MEASURE_JS = r"""() => {
  const out = [];
  document.querySelectorAll('ul').forEach(ul => {
    const li = ul.querySelector('li');
    const liBox = li.getBoundingClientRect();
    const range = document.createRange();
    range.selectNodeContents(li);
    const rects = [...range.getClientRects()].filter(r => r.width > 0);
    out.push({
      id: ul.id,
      text_align: getComputedStyle(ul).textAlign,
      position: getComputedStyle(ul).listStylePosition,
      li_left: liBox.left, li_width: liBox.width,
      first_line_left: rects.length ? rects[0].left - liBox.left : null,
    });
  });
  return out;
}"""


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    """Render a document produced by the real export buffer."""
    from playwright.sync_api import sync_playwright

    from streamtex.export import ExportConfig, HtmlExportBuffer

    buf = HtmlExportBuffer(ExportConfig(enabled=True))
    items = "".join(f"<li>{t}</li>" for t in ("alpha", "beta gamma", "delta"))
    buf.append(f'<div style="text-align:center"><ul id="inherited">{items}</ul></div>')
    buf.append(f'<div><ul id="plain">{items}</ul></div>')
    buf.append(
        '<div><ul id="declared" style="text-align: center; '
        f'list-style-position: inside;">{items}</ul></div>'
    )
    path = tmp_path_factory.mktemp("export") / "book.html"
    path.write_text(buf.generate_full_html(), encoding="utf-8")

    with sync_playwright() as p:
        browser = launch_browser(p)
        page = browser.new_context(viewport=VIEWPORT).new_page()
        page.goto(path.as_uri())
        page.wait_for_load_state("load")
        page.wait_for_timeout(300)
        rows = {r["id"]: r for r in page.evaluate(EXPORT_MEASURE_JS)}
        browser.close()
    for key, row in rows.items():
        print(f"\nexport/{key}: text_align={row['text_align']} "
              f"position={row['position']} first_line_left={row['first_line_left']}")
    yield rows


def test_export_lists_inherit_text_align(exported) -> None:
    assert exported["inherited"]["text_align"] == "center", (
        "the exported document still blocks text-align inheritance into lists "
        "(`ol, ul { text-align: left; }`)"
    )
    assert exported["plain"]["text_align"] in ("start", "left")


def test_export_moves_the_marker_inside_on_inherited_centring(exported) -> None:
    assert exported["inherited"]["position"] == "inside", \
        "an exported list that inherits a centring keeps its marker outside"
    assert exported["plain"]["position"] == "outside", \
        "an unaligned exported list must keep the standard outside marker"
    assert exported["declared"]["position"] == "inside"


def test_export_inherited_and_declared_agree(exported) -> None:
    inherited, declared = exported["inherited"], exported["declared"]
    assert abs(inherited["first_line_left"] - declared["first_line_left"]) < 2, (
        "an inherited centring and a declared one no longer produce the same "
        "first line"
    )
