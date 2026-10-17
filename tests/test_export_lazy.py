"""lazy_load_images: an HTML export whose images load as the reader nears them (#115)."""
from __future__ import annotations

from streamtex.export import lazy_load_images


def _marker(i: int) -> str:
    return f'<div id="m{i}" class="streamtex-marker" data-marker-index="{i}" style=""></div>'


def _lazy(html: str) -> list[bool]:
    import re
    return ['loading="lazy"' in t for t in re.findall(r"<img\b[^>]*>", html)]


DECK = (f'<body>{_marker(0)}<img src="a"><img src="b">{_marker(1)}<img src="c">'
        f'{_marker(2)}<img src="d"></body>')


def test_images_of_the_first_slide_load_at_once():
    assert _lazy(lazy_load_images(DECK)) == [False, False, True, True]


def test_lazy_images_decode_async():
    assert '<img loading="lazy" decoding="async" src="c">' in lazy_load_images(DECK)


def test_a_marker_that_is_not_a_stop_does_not_end_the_first_slide():
    markers = [{"index": 0}, {"index": 1, "stop": False}, {"index": 2}]
    assert _lazy(lazy_load_images(DECK, markers)) == [False, False, False, True]


def test_a_single_slide_keeps_all_its_images():
    html = f'{_marker(0)}<img src="a"><img src="b">'
    assert lazy_load_images(html) == html


def test_without_markers_only_the_first_image_loads_at_once():
    assert _lazy(lazy_load_images('<img src="a"><p>x</p><img src="b"><IMG src="c">')) == [False, True, True]


def test_an_explicit_loading_attribute_is_kept():
    html = DECK.replace('<img src="d">', '<img loading="eager" src="d">')
    out = lazy_load_images(html)
    assert '<img loading="eager" src="d">' in out and out.count("loading=") == 2


def test_no_image_no_change():
    assert lazy_load_images(f"{_marker(0)}<p>x</p>{_marker(1)}") == f"{_marker(0)}<p>x</p>{_marker(1)}"
