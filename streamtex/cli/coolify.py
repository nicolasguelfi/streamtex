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
    updated_at: str = ""


# ── Constants (single source of truth) ─────────────────────────────────

DEFAULT_SSH_KEY_PATH = "~/.ssh/hetzner_streamtex"
"""Default SSH key path for Hetzner server access."""

DEFAULT_SSH_KEY_NAME = "streamtex-deploy"
"""Name of the SSH key registered in Hetzner."""

DEFAULT_SSH_USER = "deploy"
"""Non-root user created during server hardening."""

DEFAULT_SERVER_TYPE = "cax21"
"""Default Hetzner server type (ARM, 4 vCPU, 8 GB RAM)."""

DEFAULT_SERVER_LOCATION = "fsn1"
"""Default Hetzner datacenter (Falkenstein, Germany)."""

DEFAULT_SERVER_IMAGE = "ubuntu-24.04"
"""Default OS image for Hetzner servers."""

DEFAULT_SERVER_NAME = "streamtex-prod"
"""Default server name in Hetzner."""

DEFAULT_DEPLOY_TIMEOUT = 300
"""Default timeout in seconds for waiting on deployments."""

STREAMLIT_PORT = 8501
"""Streamlit default port inside the Docker container."""

COOLIFY_DASHBOARD_PORT = 8000
"""Coolify dashboard port before domain configuration."""


# ── Deploy state schema ───────────────────────────────────────────────

@dataclass
class ServerInfo:
    """Hetzner server information."""
    name: str = ""
    id: int = 0
    type: str = DEFAULT_SERVER_TYPE
    location: str = DEFAULT_SERVER_LOCATION
    image: str = DEFAULT_SERVER_IMAGE
    ipv4: str = ""
    ssh_key_path: str = DEFAULT_SSH_KEY_PATH
    ssh_key_name: str = DEFAULT_SSH_KEY_NAME
    ssh_key_id: int = 0


@dataclass
class DomainInfo:
    """Domain configuration."""
    base: str = ""
    registrar: str = ""
    wildcard_dns: str = ""


@dataclass
class CoolifyInfo:
    """Coolify installation details."""
    url: str = ""
    server_uuid: str = ""
    project_uuid: str = ""
    environment: str = "production"
    environment_uuid: str = ""


@dataclass
class AppEntry:
    """A deployed application in the state file."""
    name: str = ""
    uuid: str = ""
    subdomain: str = ""
    url: str = ""
    folder: str = ""
    github_repo: str = ""
    branch: str = "main"
    deployed_at: str = ""
    replicas: int = 1
    replica_uuids: list[str] | None = None

    @property
    def all_uuids(self) -> list[str]:
        """Return primary UUID + all replica UUIDs."""
        uuids = [self.uuid] if self.uuid else []
        if self.replica_uuids:
            uuids.extend(self.replica_uuids)
        return uuids


@dataclass
class DeployState:
    """Unified state schema for .stx-deploy.json.

    Used by BOTH the Python CLI and the Claude commands.
    All fields are optional — the state is built up incrementally
    as each phase completes.
    """
    version: str = "2.0"
    server: ServerInfo | None = None
    domain: DomainInfo | None = None
    coolify: CoolifyInfo | None = None
    applications: list[AppEntry] | None = None
    phases_completed: dict[str, str] | None = None
    """Timestamps for each completed phase: provision, secure, install_coolify, configure_domain."""

    cdn: dict | None = None
    security: dict | None = None

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON storage."""
        d: dict = {"version": self.version}
        if self.server:
            d["infrastructure"] = {"server": {
                k: v for k, v in self.server.__dict__.items() if v
            }}
        if self.domain:
            d.setdefault("infrastructure", {})["domain"] = {
                k: v for k, v in self.domain.__dict__.items() if v
            }
        if self.coolify:
            d.setdefault("infrastructure", {})["coolify"] = {
                k: v for k, v in self.coolify.__dict__.items() if v
            }
        if self.cdn:
            d.setdefault("infrastructure", {})["cdn"] = self.cdn
        if self.security:
            d.setdefault("infrastructure", {})["security"] = self.security
        if self.phases_completed:
            d["phases_completed"] = self.phases_completed
        if self.applications:
            d["applications"] = [
                {k: v for k, v in app.__dict__.items()
                 if v and not (k == "replicas" and v == 1)}
                for app in self.applications
            ]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "DeployState":
        """Deserialize from a plain dict (loaded from JSON)."""
        infra = data.get("infrastructure", {})
        server_data = infra.get("server", {})
        domain_data = infra.get("domain", {})
        coolify_data = infra.get("coolify", {})

        server = ServerInfo(**{
            k: v for k, v in server_data.items()
            if k in ServerInfo.__dataclass_fields__
        }) if server_data else None

        domain = DomainInfo(**{
            k: v for k, v in domain_data.items()
            if k in DomainInfo.__dataclass_fields__
        }) if domain_data else None

        coolify = CoolifyInfo(**{
            k: v for k, v in coolify_data.items()
            if k in CoolifyInfo.__dataclass_fields__
        }) if coolify_data else None

        apps_data = data.get("applications", [])
        applications = [
            AppEntry(**{k: v for k, v in a.items() if k in AppEntry.__dataclass_fields__})
            for a in apps_data
        ] if apps_data else None

        return cls(
            version=data.get("version", "1.0"),
            server=server,
            domain=domain,
            coolify=coolify,
            applications=applications,
            phases_completed=data.get("phases_completed"),
            cdn=infra.get("cdn"),
            security=infra.get("security"),
        )


def load_typed_state(path: str | Path | None = None) -> DeployState:
    """Load ``.stx-deploy.json`` as a typed :class:`DeployState`.

    Returns a default (empty) state if the file does not exist.
    """
    raw = load_deploy_state(path)
    if not raw:
        return DeployState()
    return DeployState.from_dict(raw)


def save_typed_state(state: DeployState, path: str | Path | None = None) -> Path:
    """Save a :class:`DeployState` to ``.stx-deploy.json``."""
    return save_deploy_state(state.to_dict(), path)


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
                updated_at=app.get("updated_at", ""),
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
            updated_at=app.get("updated_at", ""),
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

    # ── Application management ────────────────────────────────────────

    def create_app(
        self,
        project_uuid: str,
        server_uuid: str,
        name: str,
        repository: str,
        branch: str = "main",
        build_pack: str = "dockerfile",
        dockerfile_location: str = "/Dockerfile",
        environment_name: str = "production",
    ) -> dict:
        """Create a new Coolify application.

        Returns the full application dict including ``uuid``.
        Note: this requires Coolify v4.0.0-beta.350+.
        """
        return self._post("/api/v1/applications", body={
            "project_uuid": project_uuid,
            "server_uuid": server_uuid,
            "environment_name": environment_name,
            "name": name,
            "git_repository": repository,
            "git_branch": branch,
            "build_pack": build_pack,
            "dockerfile_location": dockerfile_location,
        })

    def create_public_app(
        self,
        project_uuid: str,
        server_uuid: str,
        name: str,
        repository: str,
        branch: str = "main",
        build_pack: str = "dockerfile",
        dockerfile_location: str = "/Dockerfile",
        environment_name: str = "production",
        ports_exposes: str = "8501",
    ) -> dict:
        """Create a Coolify application from a public git repository.

        Uses the ``/applications/public`` endpoint which does not require
        a Coolify-managed git source.  Returns a dict with ``uuid`` and
        ``domains`` keys.
        """
        return self._post("/api/v1/applications/public", body={
            "project_uuid": project_uuid,
            "server_uuid": server_uuid,
            "environment_name": environment_name,
            "build_pack": build_pack,
            "name": name,
            "git_repository": repository,
            "git_branch": branch,
            "dockerfile_location": dockerfile_location,
            "ports_exposes": ports_exposes,
            "instant_deploy": False,
        })

    def update_app(self, uuid: str, **fields: object) -> dict:
        """Update application fields (domains, health_check_path, etc.)."""
        return self._patch(f"/api/v1/applications/{uuid}", body=fields)

    def delete_app(self, uuid: str) -> dict:
        """Delete an application."""
        return self._delete(f"/api/v1/applications/{uuid}")

    # ── Scaling (replicas) ────────────────────────────────────────────

    def scale_app(
        self,
        app: AppEntry,
        target_replicas: int,
        project_uuid: str,
        server_uuid: str,
    ) -> AppEntry:
        """Scale an application to *target_replicas* containers.

        Creates or deletes Coolify applications so that the total number
        of containers (primary + replicas) equals *target_replicas*.
        All replicas share the same FQDN so Traefik load-balances across them.

        Returns the updated :class:`AppEntry` with new replica UUIDs.
        """
        if target_replicas < 1:
            raise CoolifyError("replicas must be >= 1")

        current = 1 + len(app.replica_uuids or [])

        if target_replicas == current:
            return app

        if target_replicas > current:
            app = self._scale_up(app, current, target_replicas,
                                 project_uuid, server_uuid)
        else:
            app = self._scale_down(app, current, target_replicas)

        app.replicas = target_replicas
        return app

    def _scale_up(
        self, app: AppEntry, current: int, target: int,
        project_uuid: str, server_uuid: str,
    ) -> AppEntry:
        """Create additional replicas."""
        # Read primary config to replicate
        primary = self._get(f"/api/v1/applications/{app.uuid}")
        fqdn = primary.get("fqdn", app.url)
        repository = primary.get("git_repository", app.github_repo)
        branch = primary.get("git_branch", app.branch)
        dockerfile = primary.get("dockerfile_location", "/Dockerfile")
        health_path = primary.get("health_check_path", "/_stcore/health")

        # Read env vars from primary
        env_vars = self.get_env_vars(app.uuid)

        if app.replica_uuids is None:
            app.replica_uuids = []

        for i in range(current, target):
            replica_name = f"{app.name}-r{i + 1}"

            # Create replica app
            result = self.create_public_app(
                project_uuid=project_uuid,
                server_uuid=server_uuid,
                name=replica_name,
                repository=repository,
                branch=branch,
                dockerfile_location=dockerfile,
            )
            replica_uuid = result.get("uuid", "")
            if not replica_uuid:
                raise CoolifyError(f"Failed to create replica {replica_name}")

            # Set same FQDN (Traefik will load-balance)
            self.update_app(
                replica_uuid,
                domains=fqdn,
                health_check_path=health_path,
                health_check_enabled=True,
            )

            # Copy env vars from primary
            for ev in env_vars:
                if isinstance(ev, dict) and ev.get("key"):
                    is_preview = ev.get("is_preview", False)
                    if not is_preview:
                        self.set_env_var(
                            replica_uuid, ev["key"], ev.get("value", ""),
                        )

            # Trigger build
            self.rebuild(replica_uuid)

            app.replica_uuids.append(replica_uuid)

        return app

    def _scale_down(self, app: AppEntry, current: int, target: int) -> AppEntry:
        """Remove excess replicas (from the end)."""
        if not app.replica_uuids:
            return app

        to_remove = current - target
        removed = []
        for _ in range(to_remove):
            if not app.replica_uuids:
                break
            replica_uuid = app.replica_uuids.pop()
            try:
                self.stop(replica_uuid)
                self.delete_app(replica_uuid)
            except CoolifyError:
                pass  # best-effort cleanup
            removed.append(replica_uuid)

        if not app.replica_uuids:
            app.replica_uuids = None

        return app

    def rebuild_all_replicas(self, app: AppEntry) -> list[DeployResult]:
        """Rebuild the primary application and all its replicas."""
        results = []
        for uuid in app.all_uuids:
            results.append(self.rebuild(uuid))
        return results

    def restart_all_replicas(self, app: AppEntry) -> list[DeployResult]:
        """Restart the primary application and all its replicas."""
        results = []
        for uuid in app.all_uuids:
            results.append(self.restart(uuid))
        return results

    def verify_token(self) -> bool:
        """Verify that the API token is valid by listing apps.

        Returns True if the token is valid, False otherwise.
        """
        try:
            self._get("/api/v1/applications")
            return True
        except CoolifyError:
            return False

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

    def _delete(self, path: str) -> dict:
        url = f"{self.url}{path}"
        req = urllib.request.Request(url, headers=self._headers(), method="DELETE")
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
