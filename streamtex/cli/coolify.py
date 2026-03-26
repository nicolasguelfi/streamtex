"""Coolify API client — shared module for CLI commands and Claude agents.

Provides a Python wrapper around the Coolify v4 REST API for managing
applications deployed on Hetzner servers.

Usage::

    from streamtex.cli.coolify import CoolifyClient

    client = CoolifyClient.from_env()  # reads .stx-deploy.env
    apps = client.list_apps()
    client.rebuild("app-uuid-here")
    client.wait_healthy("app-uuid-here", timeout=300)
"""

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DeployResult:
    """Result of a deploy/restart operation."""

    uuid: str
    """Application UUID."""

    deployment_uuid: str = ""
    """Deployment UUID returned by Coolify."""

    success: bool = True
    """Whether the API call succeeded."""

    message: str = ""
    """Status message or error."""

    healthy: bool = False
    """Whether the service reached healthy state (after wait)."""


@dataclass
class AppInfo:
    """Summary of a Coolify application."""

    uuid: str
    name: str
    status: str
    fqdn: str
    repository: str = ""
    branch: str = ""
    description: str = ""


class CoolifyError(Exception):
    """Raised when a Coolify API call fails."""


class CoolifyClient:
    """Client for the Coolify v4 REST API.

    Parameters
    ----------
    url : str
        Base URL of the Coolify instance (e.g. ``https://coolify.example.org``).
    token : str
        Bearer token for API authentication.
    """

    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.token = token

    # ── Factory ────────────────────────────────────────────────────────

    @classmethod
    def from_env(cls, env_path: str | Path | None = None) -> "CoolifyClient":
        """Create a client from ``.stx-deploy.env`` or environment variables.

        Search order:
        1. Explicit *env_path*
        2. ``.stx-deploy.env`` in current directory
        3. ``.stx-deploy.env`` in workspace root (parent of current dir)
        4. ``COOLIFY_URL`` and ``COOLIFY_API_TOKEN`` environment variables
        5. Read from ``.stx-deploy.json`` infrastructure section

        Raises :class:`CoolifyError` if credentials cannot be found.
        """
        coolify_url = None
        coolify_token = None

        # Try .stx-deploy.env files
        candidates = []
        if env_path:
            candidates.append(Path(env_path))
        candidates.extend([
            Path.cwd() / ".stx-deploy.env",
            Path.cwd().parent / ".stx-deploy.env",
        ])

        for p in candidates:
            if p.is_file():
                env_vars = _parse_env_file(p)
                coolify_url = coolify_url or env_vars.get("COOLIFY_URL")
                coolify_token = coolify_token or env_vars.get("COOLIFY_API_TOKEN")
                if coolify_url and coolify_token:
                    break

        # Fallback to environment variables
        coolify_url = coolify_url or os.environ.get("COOLIFY_URL")
        coolify_token = coolify_token or os.environ.get("COOLIFY_API_TOKEN")

        # Fallback to .stx-deploy.json
        if not coolify_url or not coolify_token:
            for json_path in [
                Path.cwd() / ".stx-deploy.json",
                Path.cwd().parent / ".stx-deploy.json",
            ]:
                if json_path.is_file():
                    data = json.loads(json_path.read_text(encoding="utf-8"))
                    infra = data.get("infrastructure", {})
                    coolify = infra.get("coolify", {})
                    if not coolify_url:
                        coolify_url = coolify.get("url")
                    break

        # Fallback token from .env in streamtex repo
        if not coolify_token:
            for dotenv_path in [
                Path.cwd() / ".env",
                Path.cwd().parent / "streamtex" / ".env",
            ]:
                if dotenv_path.is_file():
                    env_vars = _parse_env_file(dotenv_path)
                    coolify_token = coolify_token or env_vars.get("COOLIFY_API_TOKEN")
                    if coolify_token:
                        break

        if not coolify_url:
            raise CoolifyError(
                "Coolify URL not found. Set COOLIFY_URL in .stx-deploy.env "
                "or run: stx deploy setup"
            )
        if not coolify_token:
            raise CoolifyError(
                "Coolify API token not found. Set COOLIFY_API_TOKEN in .stx-deploy.env "
                "or run: stx deploy setup"
            )

        return cls(coolify_url, coolify_token)

    # ── Applications ───────────────────────────────────────────────────

    def list_apps(self) -> list[AppInfo]:
        """List all applications in Coolify."""
        data = self._get("/api/v1/applications")
        return [
            AppInfo(
                uuid=app.get("uuid", ""),
                name=app.get("name", ""),
                status=app.get("status", "unknown"),
                fqdn=app.get("fqdn", ""),
                repository=app.get("git_repository", ""),
                branch=app.get("git_branch", ""),
                description=app.get("description", ""),
            )
            for app in data
        ]

    def get_app(self, uuid: str) -> AppInfo:
        """Get details of a specific application."""
        app = self._get(f"/api/v1/applications/{uuid}")
        return AppInfo(
            uuid=app.get("uuid", ""),
            name=app.get("name", ""),
            status=app.get("status", "unknown"),
            fqdn=app.get("fqdn", ""),
            repository=app.get("git_repository", ""),
            branch=app.get("git_branch", ""),
            description=app.get("description", ""),
        )

    # ── Deployments ────────────────────────────────────────────────────

    def rebuild(self, uuid: str) -> DeployResult:
        """Trigger a full rebuild (pull git, rebuild Docker image, install PyPI).

        Uses ``POST /applications/{uuid}/start`` which triggers a complete
        build pipeline — NOT ``/restart`` which only restarts the existing
        container.
        """
        try:
            data = self._post(f"/api/v1/applications/{uuid}/start")
            return DeployResult(
                uuid=uuid,
                deployment_uuid=data.get("deployment_uuid", ""),
                success=True,
                message=data.get("message", "Deployment queued"),
            )
        except CoolifyError as e:
            return DeployResult(uuid=uuid, success=False, message=str(e))

    def restart(self, uuid: str) -> DeployResult:
        """Quick restart (reuse existing Docker image, no rebuild).

        Only use for env var or config changes that don't require a new image.
        """
        try:
            data = self._post(f"/api/v1/applications/{uuid}/restart")
            return DeployResult(
                uuid=uuid,
                deployment_uuid=data.get("deployment_uuid", ""),
                success=True,
                message=data.get("message", "Restart queued"),
            )
        except CoolifyError as e:
            return DeployResult(uuid=uuid, success=False, message=str(e))

    def stop(self, uuid: str) -> DeployResult:
        """Stop an application."""
        try:
            data = self._post(f"/api/v1/applications/{uuid}/stop")
            return DeployResult(
                uuid=uuid, success=True,
                message=data.get("message", "Stop queued"),
            )
        except CoolifyError as e:
            return DeployResult(uuid=uuid, success=False, message=str(e))

    def wait_healthy(
        self, uuid: str, timeout: int = 300, poll_interval: int = 10,
    ) -> bool:
        """Poll until the application reaches ``running:healthy`` state.

        Returns ``True`` if healthy within *timeout* seconds, ``False`` otherwise.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                app = self.get_app(uuid)
                if "healthy" in app.status:
                    return True
                if "error" in app.status or "exited" in app.status:
                    return False
            except CoolifyError:
                pass
            time.sleep(poll_interval)
        return False

    # ── Environment Variables ──────────────────────────────────────────

    def get_env_vars(self, uuid: str) -> list[dict]:
        """Get environment variables for an application."""
        return self._get(f"/api/v1/applications/{uuid}/envs")

    def set_env_var(self, uuid: str, key: str, value: str, is_build: bool = False) -> dict:
        """Set an environment variable on an application."""
        return self._post(
            f"/api/v1/applications/{uuid}/envs",
            body={"key": key, "value": value, "is_build_time": is_build},
        )

    # ── Domain ─────────────────────────────────────────────────────────

    def set_fqdn(self, uuid: str, fqdn: str) -> dict:
        """Set the FQDN (domain) for an application."""
        return self._patch(
            f"/api/v1/applications/{uuid}",
            body={"fqdn": fqdn},
        )

    # ── HTTP helpers ───────────────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, path: str) -> dict | list:
        url = f"{self.url}{path}"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        return self._do_request(req)

    def _post(self, path: str, body: dict | None = None) -> dict:
        url = f"{self.url}{path}"
        data = json.dumps(body or {}).encode() if body else b"{}"
        req = urllib.request.Request(url, data=data, headers=self._headers(), method="POST")
        return self._do_request(req)

    def _patch(self, path: str, body: dict | None = None) -> dict:
        url = f"{self.url}{path}"
        data = json.dumps(body or {}).encode() if body else b"{}"
        req = urllib.request.Request(url, data=data, headers=self._headers(), method="PATCH")
        return self._do_request(req)

    def _do_request(self, req: urllib.request.Request) -> dict | list:
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode()
                if not body:
                    return {}
                return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise CoolifyError(
                f"HTTP {e.code} on {req.get_method()} {req.full_url}: {body}"
            ) from e
        except urllib.error.URLError as e:
            raise CoolifyError(f"Connection error: {e.reason}") from e


# ── Utility ────────────────────────────────────────────────────────────


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE env file (no shell expansion)."""
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def load_deploy_state(path: str | Path | None = None) -> dict:
    """Load ``.stx-deploy.json`` from the workspace.

    Searches current dir, then parent dir.
    Returns empty dict if not found.
    """
    candidates = []
    if path:
        candidates.append(Path(path))
    candidates.extend([
        Path.cwd() / ".stx-deploy.json",
        Path.cwd().parent / ".stx-deploy.json",
    ])
    for p in candidates:
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_deploy_state(state: dict, path: str | Path | None = None) -> Path:
    """Save ``.stx-deploy.json`` to the workspace.

    If *path* is None, writes to the first existing location or cwd.
    """
    if path:
        out = Path(path)
    else:
        for p in [Path.cwd() / ".stx-deploy.json", Path.cwd().parent / ".stx-deploy.json"]:
            if p.is_file():
                out = p
                break
        else:
            out = Path.cwd() / ".stx-deploy.json"

    out.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
