"""Tests for StreamTeX enums."""

from streamtex.enums import Tag, Tags, ListType, ListTypes


class TestTag:
    def test_tag_repr(self):
        t = Tag("div")
        assert repr(t) == "div"

    def test_predefined_tags(self):
        assert repr(Tags.div) == "div"
        assert repr(Tags.span) == "span"
        assert repr(Tags.h1) == "h1"
        assert repr(Tags.p) == "p"


class TestListType:
    def test_list_type_repr(self):
        lt = ListType("ol")
        assert repr(lt) == "ol"

    def test_predefined_list_types(self):
        assert repr(ListTypes.ordered) == "ol"
        assert repr(ListTypes.unordered) == "ul"
