"""Tests for streamtex.auth — visual S-T-X grid password gate."""

import os
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

# Alphabet + digits — the 36 chars used in the grid
_ALL_CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_gate():
    """Import _password_gate (avoids module-level caching issues)."""
    from streamtex.auth import _password_gate
    return _password_gate


@contextmanager
def _patch_gate(session=None, clicked_char=None):
    """Patch all auth.py dependencies and yield the mock ``st`` object.

    *session*: dict used as ``st.session_state``.
    *clicked_char*: the character whose ``st.button`` returns True
    (simulates a click or keystroke).  None means no interaction.
    """
    mock_st = MagicMock()
    mock_st.session_state = session if session is not None else {}

    # st.columns → list of context-manager mocks
    col = MagicMock()
    col.__enter__ = MagicMock(return_value=col)
    col.__exit__ = MagicMock(return_value=False)
    mock_st.columns.return_value = [col] * 6

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
        patch("streamtex.auth._render_progress"),
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
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_empty_env_var_no_gate(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": ""}):
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_whitespace_env_var_no_gate(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "   "}):
            with _patch_gate() as mock_st:
                gate()
                mock_st.stop.assert_not_called()

    def test_authenticated_session_passes_through(self):
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            with _patch_gate(session={"_stx_authenticated": True}) as mock_st:
                gate()
                mock_st.stop.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — grid rendering
# ---------------------------------------------------------------------------

class TestGrid:
    """Grid generation and rendering."""

    def test_grid_initialized_with_36_chars(self):
        """First visit creates a shuffled 36-char grid in session state."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {}
            with _patch_gate(session=session):
                gate()
                assert "_stx_grid" in session
                assert len(session["_stx_grid"]) == 36
                assert set(session["_stx_grid"]) == set(_ALL_CHARS)

    def test_grid_renders_36_buttons(self):
        """All 36 cells are rendered as buttons."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": []}
            with _patch_gate(session=session) as mock_st:
                gate()
                assert mock_st.button.call_count == 36

    def test_unauthenticated_stops(self):
        """When no click/keystroke happens, st.stop() is called."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": []}
            with _patch_gate(session=session) as mock_st:
                gate()
                mock_st.stop.assert_called_once()
                mock_st.rerun.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — S-T-X sequence logic (click or keystroke)
# ---------------------------------------------------------------------------

class TestSequence:
    """Click / keystroke sequence tracking and authentication."""

    def test_first_correct_click_advances(self):
        """Clicking/typing S as first step adds it to the sequence."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": []}
            with _patch_gate(session=session, clicked_char="S") as mock_st:
                gate()
                assert session["_stx_seq"] == ["S"]
                mock_st.rerun.assert_called_once()

    def test_second_correct_click_advances(self):
        """Clicking/typing T after S advances the sequence."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": ["S"]}
            with _patch_gate(session=session, clicked_char="T") as mock_st:
                gate()
                assert session["_stx_seq"] == ["S", "T"]
                mock_st.rerun.assert_called_once()

    def test_complete_sequence_authenticates(self):
        """Clicking/typing X after S-T authenticates the session."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": ["S", "T"]}
            with _patch_gate(session=session, clicked_char="X") as mock_st:
                gate()
                assert session["_stx_authenticated"] is True
                mock_st.rerun.assert_called_once()

    def test_wrong_click_resets_sequence(self):
        """A wrong click/keystroke silently resets the sequence."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": ["S"]}
            with _patch_gate(session=session, clicked_char="A") as mock_st:
                gate()
                assert session["_stx_seq"] == []
                mock_st.rerun.assert_called_once()

    def test_wrong_first_click_resets(self):
        """A wrong first click resets (sequence stays empty)."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "stx"}):
            session = {"_stx_grid": _ALL_CHARS[:], "_stx_seq": []}
            with _patch_gate(session=session, clicked_char="Z") as mock_st:
                gate()
                assert session["_stx_seq"] == []
                mock_st.rerun.assert_called_once()
