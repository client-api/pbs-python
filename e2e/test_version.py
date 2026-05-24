"""SC-01 — /version returns the expected shape."""
from __future__ import annotations

import re

from clientapi_pbs import Pbs


def test_version_returns_release_and_version(pbs: Pbs) -> None:
    response = pbs.version.get_version()
    data = response.data
    assert data is not None
    assert data.version, "version missing"
    assert data.release, "release missing"
    # PBS releases use a numeric identifier (e.g. '0', not 'x.y'); accept any digit.
    assert re.match(r"^\d", str(data.release)), data.release
