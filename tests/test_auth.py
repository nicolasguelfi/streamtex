"""Tests for streamtex.auth — visual grid password gate."""

import os
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

# Alphabet + digits — the 36 chars used in the grid
_ALL_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_gate():
    """Import _password_gate (avoids module-level caching issues)."""
    from streamtex.auth import _password_gate
    return _password_gate


def _fresh_session(**overrides):
    """Return a session dict with all gate keys initialised."""
    session = {
        "_stx_grid": _ALL_CHARS[:],
        "_stx_match": 0,
        "_stx_circles": [None] * 6,
        "_stx_next": 0,
        "_stx_total": 0,
    }
    session.update(overrides)
    return session


@contextmanager
def _patch_gate(session=None, clicked_char=None):
    """Patch all auth.py dependencies and yield the mock ``st`` object.

    *session*: dict used as ``st.session_state``.
    *clicked_char*: the character whose ``st.button`` returns True
    (simulates a click or keystroke).  None means no interaction.
    """
    mock_st = MagicMock()
    mock_st.session_state = session if session is not None else {}

    # st.columns → context-manager mocks (adapts to arg: 3 or 6 cols)
    def _make_col():
        c = MagicMock()
        c.__enter__ = MagicMock(return_value=c)
        c.__exit__ = MagicMock(return_value=False)
        return c

    def _columns_side_effect(spec, **kw):
        n = len(spec) if isinstance(spec, list) else spec
        return [_make_col() for _ in range(n)]

    mock_st.columns.side_effect = _columns_side_effect

    # st.button → True only for *clicked_char*
    mock_st.button.side_effect = lambda label, **kw: label == clicked_char

    # st_block → context-manager mock
    block = MagicMock()
    block.__enter__ = MagicMock(return_value=block)
    block.__exit__ = MagicMock(return_value=False)

    with (
        patch("streamtex.auth.st", mock_st),
        patch("streamtex.auth.st_space"),
        patch("streamtex.auth.st_write"),
        patch("streamtex.auth.st_block", return_value=block),
        patch("streamtex.auth.components"),
        patch("streamtex.auth._render_circles"),
    ):
        yield mock_st


# ---------------------------------------------------------------------------
# Tests — gate activation (env-var logic)
# ---------------------------------------------------------------------------

class TestGateActivation:
    """Env-var driven on/off behaviour."""

    def test_no_env_var_no_gate(self):
        gate = _import_gate()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STX_PASSWORD", None)
            os.environ.pop("STX_GATE", None)
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_empty_env_var_no_gate(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": ""}):
            os.environ.pop("STX_GATE", None)
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_whitespace_env_var_no_gate(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "   "}):
            os.environ.pop("STX_GATE", None)
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_authenticated_session_passes_through(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            with _patch_gate(session={"_stx_authenticated": True}) as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_stx_gate_enables_gate_locally(self):
        """STX_GATE=1 activates the gate even without STX_PASSWORD."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_GATE": "1"}):
            os.environ.pop("STX_PASSWORD", None)
            with _patch_gate(session=_fresh_session()) as mock_st:
                gate()
                mock_st.stop.assert_called_once()

    def test_stx_gate_zero_does_not_enable(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_GATE": "0"}):
            os.environ.pop("STX_PASSWORD", None)
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — grid rendering
# ---------------------------------------------------------------------------

class TestGrid:
    """Grid generation and rendering."""

    def test_grid_initialized_with_ordered_chars(self):
        """First visit creates an ordered A-Z 0-9 grid in session state."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {}
            with _patch_gate(session=session):
                gate()
                assert session["_stx_grid"] == _ALL_CHARS

    def test_grid_renders_36_buttons(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            with _patch_gate(session=_fresh_session()) as mock_st:
                gate()
                assert mock_st.button.call_count == 36

    def test_unauthenticated_stops(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            with _patch_gate(session=_fresh_session()) as mock_st:
                gate()
                mock_st.stop.assert_called_once()
                mock_st.rerun.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — circle display (infinite loop of 6)
# ---------------------------------------------------------------------------

class TestCircles:
    """Activity circles fill left-to-right and wrap after 6."""

    def test_first_click_fills_circle_0(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session()
            with _patch_gate(session=session, clicked_char="A"):
                gate()
                assert session["_stx_circles"][0] is not None
                assert session["_stx_next"] == 1
                assert session["_stx_total"] == 1

    def test_six_clicks_fill_all_circles(self):
        """After 6 clicks all 6 circles are filled."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session(_stx_next=5, _stx_total=5,
                                     _stx_circles=["#c"] * 5 + [None])
            with _patch_gate(session=session, clicked_char="F"):
                gate()
                assert all(c is not None for c in session["_stx_circles"])
                assert session["_stx_next"] == 0  # wrapped

    def test_seventh_click_resets_and_fills_circle_0(self):
        """7th click clears previous cycle and fills circle 0."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session(_stx_next=0, _stx_total=6,
                                     _stx_circles=["#c"] * 6)
            with _patch_gate(session=session, clicked_char="G"):
                gate()
                # Circle 0 re-filled, circles 1-5 cleared
                assert session["_stx_circles"][0] is not None
                assert session["_stx_circles"][1] is None
                assert session["_stx_next"] == 1
                assert session["_stx_total"] == 7


# ---------------------------------------------------------------------------
# Tests — S-T-X embedded sequence detection
# ---------------------------------------------------------------------------

class TestSequence:
    """S→T→X can appear anywhere in the stream of clicks."""

    def test_direct_stx_authenticates(self):
        """S then T then X in 3 consecutive clicks → authenticated."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            # Simulate click 3 (X) after S→T already matched
            session = _fresh_session(_stx_match=2)
            with _patch_gate(session=session, clicked_char="X"):
                gate()
                assert session["_stx_authenticated"] is True
                assert session["_stx_match"] == 3

    def test_stx_after_noise_authenticates(self):
        """Random clicks then S→T→X still authenticates."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            # User typed A, B then S, T — now match=2, clicking X
            session = _fresh_session(_stx_match=2, _stx_total=4)
            with _patch_gate(session=session, clicked_char="X"):
                gate()
                assert session["_stx_authenticated"] is True

    def test_s_starts_matching(self):
        """Clicking S starts the match counter at 1."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session()
            with _patch_gate(session=session, clicked_char="S"):
                gate()
                assert session["_stx_match"] == 1

    def test_wrong_char_resets_match(self):
        """A non-matching char resets match to 0."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session(_stx_match=1)  # S matched
            with _patch_gate(session=session, clicked_char="A"):
                gate()
                assert session["_stx_match"] == 0

    def test_s_restarts_match_mid_sequence(self):
        """Clicking S when match>0 restarts match to 1 (not 0)."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session(_stx_match=2)  # S→T matched
            with _patch_gate(session=session, clicked_char="S"):
                gate()
                assert session["_stx_match"] == 1  # restarted from S

    def test_t_without_s_does_not_advance(self):
        """Clicking T when match=0 does not advance (T is not S)."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session()
            with _patch_gate(session=session, clicked_char="T"):
                gate()
                assert session["_stx_match"] == 0

    def test_no_auth_without_full_sequence(self):
        """Partial S→T does not authenticate."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = _fresh_session(_stx_match=1)
            with _patch_gate(session=session, clicked_char="T"):
                gate()
                assert session["_stx_match"] == 2
                assert "_stx_authenticated" not in session


# ---------------------------------------------------------------------------
# Tests — configurable password (_get_target & custom sequences)
# ---------------------------------------------------------------------------

def _import_get_target():
    """Import _get_target helper."""
    from streamtex.auth import _get_target
    return _get_target


class TestConfigurablePassword:
    """STX_PASSWORD value defines the target sequence."""

    def test_single_char_password(self):
        """STX_PASSWORD=a → click A → authenticated."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "a"}):
            session = _fresh_session()
            with _patch_gate(session=session, clicked_char="A"):
                gate()
                assert session["_stx_authenticated"] is True
                assert session["_stx_match"] == 1

    def test_custom_sequence(self):
        """STX_PASSWORD=abc → A→B→C → authenticated on C."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "abc"}):
            # Simulate A→B already matched, now clicking C
            session = _fresh_session(_stx_match=2)
            with _patch_gate(session=session, clicked_char="C"):
                gate()
                assert session["_stx_authenticated"] is True
                assert session["_stx_match"] == 3

    def test_password_case_insensitive(self):
        """STX_PASSWORD=Abc and STX_PASSWORD=ABC produce the same target."""
        get_target = _import_get_target()
        with patch.dict(os.environ, {"STX_PASSWORD": "Abc"}):
            t1 = get_target()
        with patch.dict(os.environ, {"STX_PASSWORD": "ABC"}):
            t2 = get_target()
        assert t1 == t2 == ("A", "B", "C")

    def test_invalid_chars_filtered(self):
        """STX_PASSWORD=a!b@c → sequence ("A", "B", "C"), symbols ignored."""
        get_target = _import_get_target()
        with patch.dict(os.environ, {"STX_PASSWORD": "a!b@c"}):
            assert get_target() == ("A", "B", "C")

    def test_all_invalid_chars_uses_default(self):
        """STX_PASSWORD=!@# → empty after filtering → falls back to default."""
        get_target = _import_get_target()
        with patch.dict(os.environ, {"STX_PASSWORD": "!@#"}):
            assert get_target() == ("S", "T", "X")

    def test_stx_gate_uses_default_target(self):
        """STX_GATE=1 without STX_PASSWORD → default S-T-X sequence."""
        get_target = _import_get_target()
        with patch.dict(os.environ, {"STX_GATE": "1"}):
            os.environ.pop("STX_PASSWORD", None)
            assert get_target() == ("S", "T", "X")

    def test_get_target_with_digits(self):
        """STX_PASSWORD=abc123 → sequence includes digits."""
        get_target = _import_get_target()
        with patch.dict(os.environ, {"STX_PASSWORD": "abc123"}):
            assert get_target() == ("A", "B", "C", "1", "2", "3")
