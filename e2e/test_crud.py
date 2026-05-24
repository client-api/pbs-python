"""SC-30 / SC-31 — user CRUD round-trips."""
from __future__ import annotations

from clientapi_pbs import Pbs
from clientapi_pbs.models.access_users_create_users_request import (
    AccessUsersCreateUsersRequest,
)


def test_users_list_contains_root(pbs: Pbs) -> None:
    """SC-30 — root@pam is always present."""
    users = pbs.accessUsers.get_users().data or []
    ids = {getattr(u, "userid", None) for u in users}
    assert "root@pam" in ids, ids


def test_user_crud_roundtrip(pbs: Pbs) -> None:
    """SC-31 — create → list → delete cycle for a transient e2e user."""
    user_id = "e2e-user-01@pbs"
    pbs.accessUsers.create_users(
        AccessUsersCreateUsersRequest(
            userid=user_id,
            password="long-enough-password-1234",
            comment="SC-31 transient",
        )
    )
    try:
        users = pbs.accessUsers.get_users().data or []
        assert any(getattr(u, "userid", None) == user_id for u in users)
    finally:
        pbs.accessUsers.delete_users(userid=user_id)

    users_after = pbs.accessUsers.get_users().data or []
    assert all(getattr(u, "userid", None) != user_id for u in users_after)
