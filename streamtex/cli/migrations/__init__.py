"""StreamTeX project migration system.

Provides versioned migrations and compatibility checking for upgrading
existing projects to newer versions of the streamtex library.
"""

from .base import Migration, MigrationResult
from .compat import CompatIssue, check_compatibility
from .registry import detect_project_version, get_pending_migrations

# Import migration modules to trigger @register decorators
from . import v0_4_0  # noqa: F401
from . import v0_4_6  # noqa: F401

__all__ = [
    "Migration",
    "MigrationResult",
    "CompatIssue",
    "check_compatibility",
    "detect_project_version",
    "get_pending_migrations",
]
