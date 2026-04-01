"""Tests for the replica scaling feature in coolify.py."""

import json
from unittest.mock import patch

import pytest

from streamtex.cli.coolify import (
    AppEntry,
    CoolifyClient,
    CoolifyError,
    DeployState,
)

# ── AppEntry ──────────────────────────────────────────────────────────


class TestAppEntry:
    def test_defaults(self):
        app = AppEntry(name="test", uuid="abc")
        assert app.replicas == 1
        assert app.replica_uuids is None

    def test_all_uuids_no_replicas(self):
        app = AppEntry(uuid="primary")
        assert app.all_uuids == ["primary"]

    def test_all_uuids_with_replicas(self):
        app = AppEntry(uuid="primary", replica_uuids=["r2", "r3"])
        assert app.all_uuids == ["primary", "r2", "r3"]

    def test_all_uuids_empty_uuid(self):
        app = AppEntry()
        assert app.all_uuids == []


# ── DeployState serialization ─────────────────────────────────────────


class TestDeployStateSerialization:
    def test_round_trip_no_replicas(self):
        state = DeployState(
            applications=[AppEntry(name="svc", uuid="u1", folder="f")]
        )
        d = state.to_dict()
        loaded = DeployState.from_dict(d)
        assert loaded.applications[0].replicas == 1
        assert loaded.applications[0].replica_uuids is None

    def test_round_trip_with_replicas(self):
        state = DeployState(
            applications=[
                AppEntry(
                    name="svc", uuid="u1", folder="f",
                    replicas=3, replica_uuids=["r2", "r3"],
                )
            ]
        )
        d = state.to_dict()
        # replicas=3 should be in the dict
        app_d = d["applications"][0]
        assert app_d["replicas"] == 3
        assert app_d["replica_uuids"] == ["r2", "r3"]

        loaded = DeployState.from_dict(d)
        assert loaded.applications[0].replicas == 3
        assert loaded.applications[0].replica_uuids == ["r2", "r3"]

    def test_replicas_default_omitted_from_dict(self):
        """replicas=1 (default) should not appear in serialized dict."""
        state = DeployState(
            applications=[AppEntry(name="svc", uuid="u1")]
        )
        d = state.to_dict()
        app_d = d["applications"][0]
        assert "replicas" not in app_d

    def test_json_round_trip(self):
        state = DeployState(
            applications=[
                AppEntry(
                    name="svc", uuid="u1",
                    replicas=2, replica_uuids=["r2"],
                )
            ]
        )
        j = json.dumps(state.to_dict())
        loaded = DeployState.from_dict(json.loads(j))
        assert loaded.applications[0].replicas == 2
        assert loaded.applications[0].replica_uuids == ["r2"]


# ── CoolifyClient.scale_app ──────────────────────────────────────────


class TestScaleApp:
    def _make_client(self):
        return CoolifyClient("https://coolify.test", "fake-token")

    def test_scale_same_count_noop(self):
        client = self._make_client()
        app = AppEntry(name="svc", uuid="u1", replicas=2, replica_uuids=["r2"])
        result = client.scale_app(app, 2, "proj", "srv")
        assert result.replicas == 2
        assert result.replica_uuids == ["r2"]

    def test_scale_below_one_raises(self):
        client = self._make_client()
        app = AppEntry(name="svc", uuid="u1")
        with pytest.raises(CoolifyError, match="replicas must be >= 1"):
            client.scale_app(app, 0, "proj", "srv")

    @patch.object(CoolifyClient, "_get")
    @patch.object(CoolifyClient, "_post")
    @patch.object(CoolifyClient, "_patch")
    def test_scale_up(self, mock_patch, mock_post, mock_get):
        client = self._make_client()
        app = AppEntry(name="svc", uuid="u1")

        # Mock _get for primary app info and env vars
        mock_get.side_effect = [
            # get_app (primary config)
            {"fqdn": "https://svc.test", "git_repository": "owner/repo",
             "git_branch": "main", "dockerfile_location": "/Dockerfile",
             "health_check_path": "/_stcore/health"},
            # get_env_vars
            [{"key": "FOLDER", "value": "modules/svc", "is_preview": False}],
        ]

        # Mock _post for create_public_app, set_env_var, rebuild
        mock_post.side_effect = [
            {"uuid": "r2"},           # create replica 1
            {"uuid": "env1"},         # set_env_var FOLDER
            {"deployment_uuid": "d1", "message": "queued"},  # rebuild replica 1
            {"uuid": "r3"},           # create replica 2
            {"uuid": "env2"},         # set_env_var FOLDER
            {"deployment_uuid": "d2", "message": "queued"},  # rebuild replica 2
        ]

        # Mock _patch for update_app (set domains)
        mock_patch.return_value = {"uuid": "ok"}

        result = client.scale_app(app, 3, "proj", "srv")
        assert result.replicas == 3
        assert result.replica_uuids == ["r2", "r3"]

    @patch.object(CoolifyClient, "_post")
    @patch.object(CoolifyClient, "_delete")
    def test_scale_down(self, mock_delete, mock_post):
        client = self._make_client()
        app = AppEntry(
            name="svc", uuid="u1",
            replicas=3, replica_uuids=["r2", "r3"],
        )

        # Mock stop + delete
        mock_post.return_value = {"message": "stopped"}
        mock_delete.return_value = {}

        result = client.scale_app(app, 1, "proj", "srv")
        assert result.replicas == 1
        assert result.replica_uuids is None

    @patch.object(CoolifyClient, "_post")
    @patch.object(CoolifyClient, "_delete")
    def test_scale_down_partial(self, mock_delete, mock_post):
        client = self._make_client()
        app = AppEntry(
            name="svc", uuid="u1",
            replicas=3, replica_uuids=["r2", "r3"],
        )

        mock_post.return_value = {"message": "stopped"}
        mock_delete.return_value = {}

        result = client.scale_app(app, 2, "proj", "srv")
        assert result.replicas == 2
        assert result.replica_uuids == ["r2"]


# ── rebuild/restart all replicas ──────────────────────────────────────


class TestRebuildAllReplicas:
    @patch.object(CoolifyClient, "_post")
    def test_rebuild_all(self, mock_post):
        client = CoolifyClient("https://coolify.test", "fake-token")
        app = AppEntry(uuid="u1", replica_uuids=["r2", "r3"])

        mock_post.return_value = {"deployment_uuid": "d", "message": "ok"}
        results = client.rebuild_all_replicas(app)
        assert len(results) == 3
        assert all(r.success for r in results)

    @patch.object(CoolifyClient, "_post")
    def test_restart_all(self, mock_post):
        client = CoolifyClient("https://coolify.test", "fake-token")
        app = AppEntry(uuid="u1", replica_uuids=["r2"])

        mock_post.return_value = {"deployment_uuid": "d", "message": "ok"}
        results = client.restart_all_replicas(app)
        assert len(results) == 2
