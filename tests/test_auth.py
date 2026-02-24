"""Tests for streamtex.auth — password gate."""

import os
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_gate():
    """Import _password_gate fresh (avoids module-level caching issues)."""
    from streamtex.auth import _password_gate
    return _password_gate


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPasswordGate:
    """Unit tests for _password_gate()."""

    def test_no_env_var_no_gate(self):
        """When STX_PASSWORD is absent, the gate does nothing."""
        gate = _import_gate()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STX_PASSWORD", None)
            # Should return without calling st.stop()
            with patch("streamtex.auth.st") as mock_st:
                mock_st.session_state = {}
                gate()
                mock_st.stop.assert_not_called()

    def test_empty_env_var_no_gate(self):
        """When STX_PASSWORD is empty string, the gate does nothing."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": ""}, clear=False):
            with patch("streamtex.auth.st") as mock_st:
                mock_st.session_state = {}
                gate()
                mock_st.stop.assert_not_called()

    def test_whitespace_env_var_no_gate(self):
        """When STX_PASSWORD is only whitespace, the gate does nothing."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "   "}, clear=False):
            with patch("streamtex.auth.st") as mock_st:
                mock_st.session_state = {}
                gate()
                mock_st.stop.assert_not_called()

    def test_authenticated_session_passes_through(self):
        """When session is already authenticated, the gate returns immediately."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "secret"}, clear=False):
            with patch("streamtex.auth.st") as mock_st:
                mock_st.session_state = {"_stx_authenticated": True}
                gate()
                mock_st.stop.assert_not_called()

    def test_unauthenticated_session_blocks(self):
        """When password is set but session not authenticated, st.stop() is called."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "secret"}, clear=False):
            with patch("streamtex.auth.st") as mock_st:
                mock_st.session_state = {}
                mock_st.text_input.return_value = ""
                mock_st.button.return_value = False
                gate()
                mock_st.stop.assert_called_once()

    def test_wrong_password_shows_error(self):
        """When wrong password is submitted, st.error() is called."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "secret"}, clear=False):
            with patch("streamtex.auth.st") as mock_st:
                mock_st.session_state = {}
                mock_st.text_input.return_value = "wrong"
                mock_st.button.return_value = True
                gate()
                mock_st.error.assert_called_once_with("Wrong password.")
                mock_st.stop.assert_called_once()

    def test_correct_password_authenticates(self):
        """When correct password is submitted, session state is set and rerun called."""
        gate = _import_gate()
        with patch.dict(os.environ, {"STX_PASSWORD": "secret"}, clear=False):
            with patch("streamtex.auth.st") as mock_st:
                session = {}
                mock_st.session_state = session
                mock_st.text_input.return_value = "secret"
                mock_st.button.return_value = True
                gate()
                assert session["_stx_authenticated"] is True
                mock_st.rerun.assert_called_once()
