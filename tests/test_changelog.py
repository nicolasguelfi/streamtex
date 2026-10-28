"""The version being released has its CHANGELOG entry (#3) — the same rule as auto-tag.yml's guard."""
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _entry(changelog: str, version: str) -> str:
    """The text under ``## [version]``, up to the next ``## [`` heading."""
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    return m.group(1).strip() if m else ""


def test_the_current_version_has_a_changelog_entry():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert _entry((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version), \
        f"CHANGELOG.md has no '## [{version}]' entry — auto-tag.yml would refuse to publish"


def test_an_empty_or_missing_entry_is_found():
    text = "# Changelog\n\n## [0.2.0] — x\n\n## [0.1.0] — y\n\n### Fixed\n\n- a\n"
    assert _entry(text, "0.1.0") == "### Fixed\n\n- a"
    assert _entry(text, "0.2.0") == "" and _entry(text, "0.3.0") == ""
