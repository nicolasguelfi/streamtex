"""Browser tests: each module starts without the decks of the previous ones."""
import sys

import pytest


def _forget_blocks():
    for name in [n for n in sys.modules if n == "blocks" or n.startswith("blocks.")]:
        del sys.modules[name]


@pytest.fixture(scope="module", autouse=True)
def _own_blocks_package():
    """Every fixture deck names its package ``blocks``; an in-process export
    (``stx export html`` through CliRunner) imports it into this process. A
    later deck would get the earlier one's blocks — the export then holds the
    wrong slides."""
    _forget_blocks()
    yield
    _forget_blocks()
