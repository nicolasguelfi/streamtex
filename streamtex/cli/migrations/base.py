"""Base classes for the migration system."""

from dataclasses import dataclass, field


@dataclass
class MigrationResult:
    """Result of applying a single migration."""

    version: str
    description: str
    applied: bool
    changes: list[str] = field(default_factory=list)
    skipped_reason: str = ""


class Migration:
    """Base class for versioned migrations.

    Subclasses must set ``version`` and ``description`` class attributes,
    and implement :meth:`check` and :meth:`apply`.
    """

    version: str = ""
    description: str = ""

    def check(self, project_path: str) -> bool:
        """Return True if this migration needs to be applied."""
        raise NotImplementedError

    def apply(self, project_path: str, *, dry_run: bool = False) -> MigrationResult:
        """Apply the migration. Return a result describing what changed."""
        raise NotImplementedError
