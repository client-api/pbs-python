"""Test fixture conventions and cleanup primitives.

All entities created by E2E tests are named with the `e2e-` prefix. Cleanup is
best-effort and idempotent.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clientapi_pbs import Pbs

log = logging.getLogger(__name__)

E2E_PREFIX = "e2e-"


def first_node(pbs: "Pbs") -> str:
    """Return the first node name reported by /nodes."""
    response = pbs.nodes.get_nodes()
    nodes = getattr(response, "data", None) or []
    if not nodes:
        raise RuntimeError("no PBS nodes found — is the server running?")
    name = getattr(nodes[0], "node", None)
    if not name:
        raise RuntimeError(f"first node has no .node attribute: {nodes[0]!r}")
    return name


def cleanup_e2e(pbs: "Pbs") -> None:
    """Best-effort cleanup of every e2e-* user. Safe to call multiple times."""
    _cleanup_users(pbs)


def _cleanup_users(pbs: "Pbs") -> None:
    try:
        response = pbs.accessUsers.get_users()
    except Exception as exc:
        log.debug("user list failed during cleanup: %r", exc)
        return
    for user in getattr(response, "data", None) or []:
        userid = getattr(user, "userid", "") or ""
        if userid.startswith(E2E_PREFIX):
            try:
                pbs.accessUsers.delete_users(userid=userid)
            except Exception as exc:
                log.debug("delete_users(%s) failed: %r", userid, exc)
