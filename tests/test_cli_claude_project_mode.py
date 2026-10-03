"""Claude profiles — project mode and the 0.7.35 safety rules (#65-#74).

- child profiles install their parent then their overlay (#66)
- a user-authored CLAUDE.md is never overwritten (#67)
- settings.json is merged (#68), stx never commits (#69, see test_cli_claude)
- install --dry-run / conflict stop (#70)
- [claude] declaration + stx claude sync + .claude/stx.lock (#71)
- global commands: optional copy (#72), duplicates report (#73), global status/remove (#74)
"""

import json
import os
import subprocess
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from rich.console import Console

from streamtex.cli import claude_global
from streamtex.cli._claude_files import (
    global_commands_enabled,
    merge_settings,
    root_claude_md_is_owned,
    settings_cover,
)
from streamtex.cli.claude_cmd import (
    collect_source_files,
    compare_profile,
    find_profile_targets,
    install_profile,
    plan_install,
)
from streamtex.cli.claude_project import (
    LOCK_FORMAT,
    LOCK_PATH,
    ClaudeDecl,
    desired_files,
    read_declaration,
    read_lock,
    sync_project,
    validate_declaration,
)
from streamtex.cli.commands import cli

QUIET = Console(quiet=True)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    """No real dev config, no real ~/.claude, no real machine config."""
    from streamtex.cli.dev_config import GlobalDevConfig, ProjectDevConfig

    monkeypatch.setattr("streamtex.cli.dev_config.GlobalDevConfig.load",
                        staticmethod(lambda: GlobalDevConfig()))
    monkeypatch.setattr("streamtex.cli.dev_config.ProjectDevConfig.load",
                        staticmethod(lambda _p: ProjectDevConfig()))
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.delenv("STX_GLOBAL_COMMANDS", raising=False)
    return home


def _claude_repo(root: Path) -> Path:
    """A small streamtex-claude: project, presentation (extends project), shared."""
    repo = root / "streamtex-claude"
    project = repo / "profiles" / "project"
    (project / "commands" / "stx-block").mkdir(parents=True)
    (project / "manifest.toml").write_text('[profile]\nname = "project"\n')
    (project / "commands" / "stx-block" / "new.md").write_text("new block\n")
    (project / "ce" / "agents").mkdir(parents=True)
    (project / "ce" / "agents" / "scanner.md").write_text("scanner\n")
    (project / "CLAUDE.md.j2").write_text("# {{ project_name }} rules v1\nprofile={{ profile }}\n")
    (project / "settings.json").write_text(json.dumps(
        {"permissions": {"allow": ["Bash(uv run *)", "Bash(git status*)"]}}, indent=2) + "\n")

    pres = repo / "profiles" / "presentation"
    (pres / "overlay" / "commands" / "stx-presentation").mkdir(parents=True)
    (pres / "manifest.toml").write_text('[profile]\nname = "presentation"\nextends = "project"\n')
    (pres / "overlay" / "commands" / "stx-presentation" / "audit.md").write_text("audit\n")
    (pres / "overlay" / "CLAUDE.md.j2").write_text("# {{ project_name }} presentation rules\n")

    (repo / "shared" / "references").mkdir(parents=True)
    (repo / "shared" / "references" / "coding_standards.md").write_text("standards\n")
    (repo / "shared" / "commands" / "stx-ds").mkdir(parents=True)
    (repo / "shared" / "commands" / "stx-ds" / "run.md").write_text("ds\n")
    (repo / "shared" / "commands" / "stx-guide.md").write_text("guide\n")
    (repo / "install.py").write_text("")
    return repo


def _project(root: Path, name="proj", decl: str | None = None) -> Path:
    p = root / name
    p.mkdir()
    toml = '[project]\nname = "x"\n'
    if decl:
        toml += decl
    (p / "stx.toml").write_text(toml)
    return p


# ---------------------------------------------------------------------------
# #66 extends
# ---------------------------------------------------------------------------

def test_child_profile_installs_parent_then_overlay(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path)
    installed = install_profile(str(repo), "presentation", str(target))
    assert not (target / ".claude" / "overlay").exists()
    assert (target / ".claude" / "commands" / "stx-block" / "new.md").is_file()          # parent
    assert (target / ".claude" / "commands" / "stx-presentation" / "audit.md").is_file()  # overlay
    assert (target / ".claude" / ".stx-profile").read_text().strip() == "presentation"
    # the overlay template wins and is rendered
    assert "presentation rules" in (target / "CLAUDE.md").read_text()
    # installed set == the set update/check compare against
    expected = set(collect_source_files(str(repo), "presentation"))
    assert expected <= set(installed) | {"CLAUDE.md"}


def test_install_keeps_0734_read_only_protection(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path)
    install_profile(str(repo), "project", str(target))
    for rel in (".claude/commands/stx-block/new.md", ".claude/commands/stx-ds/run.md",
                ".claude/references/coding_standards.md"):
        assert os.stat(target / rel).st_mode & 0o777 == 0o444, rel
    assert compare_profile(str(repo), "project", str(target))
    assert all(d.status == "identical" for d in compare_profile(str(repo), "project", str(target)))


# ---------------------------------------------------------------------------
# #67 CLAUDE.md ownership
# ---------------------------------------------------------------------------

def test_install_never_overwrites_user_claude_md(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path)
    (target / "CLAUDE.md").write_text("# My own rules\n")
    installed = install_profile(str(repo), "project", str(target))
    assert (target / "CLAUDE.md").read_text() == "# My own rules\n"
    assert "rules v1" in (target / ".claude" / "CLAUDE.md").read_text()
    assert ".claude/CLAUDE.md" in installed


def test_update_rerenders_owned_root_but_not_user_root(tmp_path, monkeypatch):
    repo = _claude_repo(tmp_path)
    owned, mine = _project(tmp_path, "owned"), _project(tmp_path, "mine")
    install_profile(str(repo), "project", str(owned))
    install_profile(str(repo), "project", str(mine))
    (mine / "CLAUDE.md").write_text("# mine\n")  # the user takes over the root file
    (repo / "profiles" / "project" / "CLAUDE.md.j2").write_text("# {{ project_name }} rules v2\n")

    ws = tmp_path
    (ws / "stx.toml").write_text(
        '[repos.streamtex-claude]\npath = "streamtex-claude"\ntype = "claude"\n')
    monkeypatch.chdir(ws)
    # owned: --force updates the template; the stx-owned root follows, no backup
    r = CliRunner().invoke(cli, ["claude", "update", str(owned), "--force", "--yes"])
    assert r.exit_code == 0, r.output
    assert "rules v2" in (owned / "CLAUDE.md").read_text()
    assert not (owned / ".claude" / ".backup").exists() or not list(
        (owned / ".claude" / ".backup").rglob("CLAUDE.md"))
    # mine: a plain update never touches the user's root file
    r = CliRunner().invoke(cli, ["claude", "update", str(mine), "--yes"])
    assert r.exit_code == 0, r.output
    assert (mine / "CLAUDE.md").read_text() == "# mine\n"
    assert "rules v1" in (mine / ".claude" / "CLAUDE.md").read_text()
    # the generated .claude/CLAUDE.md is never pruned as an orphan
    r = CliRunner().invoke(cli, ["claude", "update", str(mine), "--yes"])
    assert (mine / ".claude" / "CLAUDE.md").is_file()

    # --force takes the root file back explicitly: backup, render at the root,
    # no duplicate left in .claude/
    r = CliRunner().invoke(cli, ["claude", "update", str(mine), "--force", "--yes"])
    assert r.exit_code == 0, r.output
    assert "rules v2" in (mine / "CLAUDE.md").read_text()
    assert not (mine / ".claude" / "CLAUDE.md").exists()
    backups = list((mine / ".claude" / ".backup").rglob("CLAUDE.md"))
    assert backups and backups[0].read_text() == "# mine\n"


def test_root_claude_md_ownership_rule(tmp_path):
    t = tmp_path
    assert root_claude_md_is_owned(str(t))                       # absent
    (t / "CLAUDE.md").write_text("render")
    assert root_claude_md_is_owned(str(t), candidates=("render",))
    assert not root_claude_md_is_owned(str(t), candidates=("other",))
    import hashlib

    assert root_claude_md_is_owned(str(t), locked_sha=hashlib.sha256(b"render").hexdigest())


# ---------------------------------------------------------------------------
# #68 settings.json
# ---------------------------------------------------------------------------

def test_settings_merge_keeps_user_entries(tmp_path):
    src, dst = tmp_path / "src.json", tmp_path / "dst.json"
    src.write_text(json.dumps({"permissions": {"allow": ["A", "B"]}, "x": 1}))
    dst.write_text(json.dumps({"permissions": {"allow": ["B", "MINE"], "deny": ["D"]}, "x": 2}))
    assert merge_settings(str(src), str(dst))
    merged = json.loads(dst.read_text())
    assert merged["permissions"]["allow"] == ["B", "MINE", "A"]
    assert merged["permissions"]["deny"] == ["D"]
    assert merged["x"] == 2                           # the user's scalar wins
    assert settings_cover(str(dst), str(src))
    assert not merge_settings(str(src), str(dst))     # idempotent


def test_install_merges_existing_settings_and_check_is_clean(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path)
    (target / ".claude").mkdir()
    (target / ".claude" / "settings.json").write_text(json.dumps(
        {"permissions": {"allow": ["Bash(my-tool *)"]}}))
    install_profile(str(repo), "project", str(target))
    allow = json.loads((target / ".claude" / "settings.json").read_text())["permissions"]["allow"]
    assert "Bash(my-tool *)" in allow and "Bash(uv run *)" in allow
    statuses = {d.path: d.status for d in compare_profile(str(repo), "project", str(target))}
    assert statuses[".claude/settings.json"] == "identical"


# ---------------------------------------------------------------------------
# #70 dry run / conflicts
# ---------------------------------------------------------------------------

def test_plan_install_and_dry_run_write_nothing(tmp_path, monkeypatch):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path)
    (target / "CLAUDE.md").write_text("# mine\n")
    (target / ".claude" / "commands" / "stx-block").mkdir(parents=True)
    (target / ".claude" / "commands" / "stx-block" / "new.md").write_text("my own version\n")
    actions, conflicts = plan_install(str(repo), "project", str(target))
    assert conflicts == [".claude/commands/stx-block/new.md"]
    assert (".claude/CLAUDE.md", "create (rendered from CLAUDE.md.j2)") in actions

    (tmp_path / "stx.toml").write_text(
        '[repos.streamtex-claude]\npath = "streamtex-claude"\ntype = "claude"\n')
    monkeypatch.chdir(tmp_path)
    before = sorted(str(p) for p in target.rglob("*"))
    r = CliRunner().invoke(cli, ["claude", "install", "project", str(target), "--dry-run"])
    assert r.exit_code == 0, r.output
    assert sorted(str(p) for p in target.rglob("*")) == before

    r = CliRunner().invoke(cli, ["claude", "install", "project", str(target)])
    assert r.exit_code != 0 and "--yes" in r.output
    assert (target / ".claude" / "commands" / "stx-block" / "new.md").read_text() == "my own version\n"

    r = CliRunner().invoke(cli, ["claude", "install", "project", str(target), "--yes"])
    assert r.exit_code == 0, r.output
    assert (target / "CLAUDE.md").read_text() == "# mine\n"


def test_reinstall_over_stx_install_is_not_a_conflict(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path)
    install_profile(str(repo), "project", str(target))
    (repo / "profiles" / "project" / "commands" / "stx-block" / "new.md").write_text("v2\n")
    _actions, conflicts = plan_install(str(repo), "project", str(target))
    assert conflicts == []


# ---------------------------------------------------------------------------
# #71 project mode
# ---------------------------------------------------------------------------

DECL = '\n[claude]\nmode = "project"\nprofile = "presentation"\n'


def _git(p: Path, *args):
    return subprocess.run(["git", *args], cwd=p, capture_output=True, text=True, timeout=30)


def test_read_declaration(tmp_path):
    assert read_declaration(str(_project(tmp_path, "a"))) is None
    d = read_declaration(str(_project(tmp_path, "b", DECL + 'exclude = ["stx-ce"]\n')))
    assert d == ClaudeDecl("presentation", [], ["stx-ce"])
    legacy = _project(tmp_path, "c", '\n[claude]\nsource = "streamtex-claude"\n')
    assert read_declaration(str(legacy)) is None          # workspace [claude] stays classic


def test_sync_installs_locks_and_is_idempotent(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path, decl=DECL)
    _git(target, "init")
    (target / "CLAUDE.md").write_text("# mine\n")
    plan = sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)
    assert plan.install and not plan.keep_modified
    lock = read_lock(str(target))
    assert lock.profile == "presentation"
    assert ".claude/commands/stx-presentation/audit.md" in lock.files
    assert lock.claude_md == ".claude/CLAUDE.md"
    assert (target / "CLAUDE.md").read_text() == "# mine\n"
    gi = (target / ".gitignore").read_text()
    assert ".claude/*" in gi and "!.claude/stx.lock" in gi
    assert _git(target, "log").returncode != 0            # still no commit at all
    again = sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)
    assert not (again.install or again.update or again.prune or again.merge)


def test_sync_three_way_upstream_change_local_edit_and_prune(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path, decl=DECL)
    sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)

    # upstream change on an untouched file -> updated
    (repo / "profiles" / "project" / "ce" / "agents" / "scanner.md").write_text("scanner v2\n")
    # local edit -> kept
    edited = target / ".claude" / "commands" / "stx-block" / "new.md"
    os.chmod(edited, 0o644)
    edited.write_text("my edit\n")
    (repo / "profiles" / "project" / "commands" / "stx-block" / "new.md").write_text("new v2\n")
    # a file of mine in .claude -> never touched
    (target / ".claude" / "mine.md").write_text("mine\n")

    plan = sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)
    assert ".claude/ce/agents/scanner.md" in plan.update
    assert ".claude/commands/stx-block/new.md" in plan.keep_modified
    assert (target / ".claude" / "ce" / "agents" / "scanner.md").read_text() == "scanner v2\n"
    assert edited.read_text() == "my edit\n"
    assert (target / ".claude" / "mine.md").is_file()

    # exclude a group -> its unchanged files are pruned
    (target / "stx.toml").write_text('[project]\nname = "x"\n' + DECL + 'exclude = ["ce"]\n')
    plan = sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)
    assert ".claude/ce/agents/scanner.md" in plan.prune
    assert not (target / ".claude" / "ce").exists()

    # --force replaces the local edit, with a backup
    plan = sync_project(str(target), str(repo), read_declaration(str(target)), force=True,
                        console=QUIET)
    assert edited.read_text() == "new v2\n"
    assert any((target / ".claude" / ".backup").rglob("new.md"))


def test_sync_remove_is_symmetric(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path, decl=DECL)
    sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)
    (target / ".claude" / "custom" / "notes.md").write_text("keep me\n")
    sync_project(str(target), str(repo), None, remove=True, console=QUIET)
    left = sorted(str(p.relative_to(target)) for p in (target / ".claude").rglob("*") if p.is_file())
    assert left == [".claude/custom/README.md", ".claude/custom/notes.md"]
    assert not (target / "CLAUDE.md").exists()   # stx wrote it (absent before): removed with the lock


def test_sync_dry_run_writes_nothing(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path, decl=DECL)
    plan = sync_project(str(target), str(repo), read_declaration(str(target)), dry_run=True,
                        console=QUIET)
    assert plan.install
    assert not (target / ".claude").exists()


def test_exclude_filters_desired_files_and_validation(tmp_path):
    repo = _claude_repo(tmp_path)
    files = desired_files(str(repo), ClaudeDecl("presentation", exclude=["stx-presentation"]))
    assert not any("stx-presentation" in f for f in files)
    target = _project(tmp_path, decl=DECL + 'exclude = ["nothing-like-this"]\n')
    assert validate_declaration(str(target), str(repo)) == [
        "[claude] exclude 'nothing-like-this' matches nothing in the profile"]
    target2 = _project(tmp_path, "p2", '\n[claude]\nmode = "project"\nprofile = "nope"\n')
    assert "does not exist" in validate_declaration(str(target2), str(repo))[0]


def test_workspace_root_in_project_mode_is_a_target(tmp_path):
    root = _project(tmp_path, "root", DECL)
    assert find_profile_targets(str(root)) == [(str(root), "presentation")]
    classic = _project(tmp_path, "classic")
    (classic / ".claude").mkdir()
    (classic / ".claude" / ".stx-profile").write_text("project\n")
    assert find_profile_targets(str(classic)) == []        # 0.7.34: the root is not scanned


def test_sync_command_cli(tmp_path, monkeypatch):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path, decl=DECL)
    monkeypatch.setattr("streamtex.cli.claude_cmd.find_claude_repo", lambda *_a: str(repo))
    r = CliRunner().invoke(cli, ["claude", "sync", str(target)])
    assert r.exit_code == 0, r.output
    assert (target / LOCK_PATH).is_file()
    r = CliRunner().invoke(cli, ["claude", "sync", str(_project(tmp_path, "nodecl"))])
    assert r.exit_code != 0 and 'mode = "project"' in r.output


# ---------------------------------------------------------------------------
# #72 / #73 / #74 global commands
# ---------------------------------------------------------------------------

def test_global_commands_setting_and_flag(_isolate, monkeypatch):
    home = _isolate
    assert global_commands_enabled() is True
    cfg = home / ".config" / "streamtex"
    cfg.mkdir(parents=True)
    (cfg / "config.toml").write_text("[claude]\nglobal_commands = false\n")
    assert global_commands_enabled() is False
    monkeypatch.setenv("STX_GLOBAL_COMMANDS", "1")
    assert global_commands_enabled() is True
    assert global_commands_enabled(False) is False


def test_install_global_commands_respects_setting_and_records(_isolate, tmp_path, monkeypatch):
    from streamtex.cli.workspace_cmd import _install_global_commands

    home = _isolate
    repo = _claude_repo(tmp_path)
    monkeypatch.setattr("streamtex.cli.claude_cmd.find_claude_repo", lambda *_a: str(repo))
    monkeypatch.setenv("STX_GLOBAL_COMMANDS", "0")
    _install_global_commands(str(tmp_path), {}, QUIET)
    assert not (home / ".claude").exists()
    monkeypatch.setenv("STX_GLOBAL_COMMANDS", "1")
    _install_global_commands(str(tmp_path), {}, QUIET)
    assert (home / ".claude" / "commands" / "stx-ds" / "run.md").is_file()
    record = json.loads((home / ".config" / "streamtex" / "global-commands.json").read_text())
    assert set(record["files"]) == {"stx-ds/run.md", "stx-guide.md"}


def test_global_classify_and_remove(_isolate, tmp_path, monkeypatch):
    home = _isolate
    repo = _claude_repo(tmp_path)
    g = home / ".claude" / "commands"
    (g / "stx-ds").mkdir(parents=True)
    (g / "stx-ds" / "run.md").write_text("ds\n")                 # current
    (g / "stx-pattern").mkdir()
    (g / "stx-pattern" / "list.md").write_text("old\n")          # obsolete (read-only)
    (g / "stx-guide.md").write_text("guide edited by me\n")      # modified (writable)
    (g / "my-own.md").write_text("not stx\n")                    # not stx: ignored
    for p in (g / "stx-ds" / "run.md", g / "stx-pattern" / "list.md"):
        os.chmod(p, 0o444)
    states = {e.name: e.state for e in claude_global.classify(str(repo / "shared" / "commands"))}
    assert states == {"stx-ds": "current", "stx-pattern": "obsolete", "stx-guide.md": "modified"}

    monkeypatch.setattr(claude_global, "_shared_commands_dir", lambda: str(repo / "shared" / "commands"))
    r = CliRunner().invoke(cli, ["claude", "global", "remove"])
    assert r.exit_code == 0 and (g / "stx-ds").exists()          # dry run
    r = CliRunner().invoke(cli, ["claude", "global", "remove", "--yes"])
    assert r.exit_code == 0, r.output
    assert sorted(p.name for p in g.iterdir()) == ["my-own.md", "stx-guide.md"]


def test_duplicates_report(_isolate, tmp_path):
    home = _isolate
    (home / ".claude" / "commands" / "stx-ds").mkdir(parents=True)
    (home / ".claude" / "commands" / "stx-pattern").mkdir()
    target = _project(tmp_path)
    (target / ".claude" / "commands" / "stx-ds").mkdir(parents=True)
    assert claude_global.duplicated_groups(str(target)) == ["stx-ds"]
    console = Console(record=True, width=200)
    repo = _claude_repo(tmp_path)
    claude_global.print_commands_report(str(tmp_path), [(str(target), "project")], str(repo), console)
    out = console.export_text()
    assert "stx-ds" in out and "stx-pattern" in out
    console = Console(record=True, width=200)
    (home / ".claude" / "commands" / "stx-ds").rmdir()
    (home / ".claude" / "commands" / "stx-pattern").rmdir()
    claude_global.print_commands_report(str(tmp_path), [(str(target), "project")], str(repo), console)
    assert console.export_text() == ""


# ---------------------------------------------------------------------------
# #69 side effects measured on the maintainer's workspaces
# ---------------------------------------------------------------------------

def _git_repo_with_tracked_claude(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    _git(p, "init")
    _git(p, "config", "user.email", "t@t")
    _git(p, "config", "user.name", "t")
    (p / ".claude").mkdir()
    (p / ".claude" / ".stx-profile").write_text("project\n")
    (p / ".claude" / "old.md").write_text("old\n")
    _git(p, "add", "-A")
    _git(p, "commit", "-m", "init")


def test_managed_clone_keeps_the_migration_commit_user_project_does_not(tmp_path):
    from streamtex.cli.claude_cmd import _update_single_target

    repo = _claude_repo(tmp_path / "src")
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "stx.toml").write_text('[repos.docs]\npath = "docs"\ntype = "docs"\n')
    clone, mine = ws / "docs", ws / "projects" / "mine"
    _git_repo_with_tracked_claude(clone)
    _git_repo_with_tracked_claude(mine)
    for t in (clone, mine):
        _update_single_target(str(repo), "project", str(t), False, QUIET, yes=True)
    assert "stop tracking" in _git(clone, "log", "-1", "--format=%s").stdout   # 0.7.34 behaviour
    assert _git(mine, "log", "-1", "--format=%s").stdout.strip() == "init"      # #69: never


def test_lock_records_its_format_and_refuses_a_newer_one(tmp_path):
    repo = _claude_repo(tmp_path)
    target = _project(tmp_path, decl=DECL)
    sync_project(str(target), str(repo), read_declaration(str(target)), console=QUIET)
    lock_file = target / LOCK_PATH
    assert f"format = {LOCK_FORMAT}" in lock_file.read_text()
    # a lock written by 0.7.35-0.7.40 has no format: read as format 1
    lock_file.write_text(lock_file.read_text().replace(f"format = {LOCK_FORMAT}\n", ""))
    assert read_lock(str(target)).profile == "presentation"
    lock_file.write_text(lock_file.read_text().replace("[lock]\n", f"[lock]\nformat = {LOCK_FORMAT + 1}\n"))
    with pytest.raises(click.ClickException, match="format"):
        read_lock(str(target))


def test_hooks_step_puts_uv_lock_back_byte_for_byte(tmp_path, monkeypatch):
    from streamtex.cli import workspace_cmd

    ws = tmp_path / "ws"
    repo = ws / "docs"
    repo.mkdir(parents=True)
    (repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "d"\n[tool.uv.sources]\nstreamtex = { path = "../streamtex", editable = true }\n')
    (repo / "uv.lock").write_bytes(b"original lock\n")
    (repo / ".gitignore").write_text("dirty too\n")   # another modified file must not matter

    def fake_run(cmd, **kw):
        (repo / "uv.lock").write_bytes(b"rewritten by uv --no-sources\n")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(workspace_cmd.subprocess, "run", fake_run)
    monkeypatch.setattr(workspace_cmd, "_find_uv", lambda: "uv")
    workspace_cmd._install_precommit_hooks(str(ws), {"repos": {"docs": {"path": "docs"}}}, QUIET)
    assert (repo / "uv.lock").read_bytes() == b"original lock\n"
