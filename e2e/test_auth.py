"""SC-10 … SC-14 — authentication paths."""
from __future__ import annotations

import pytest

from clientapi_pbs import Configuration, Pbs
from clientapi_pbs.exceptions import ApiException
from clientapi_pbs.models.access_ticket_create_ticket_request import (
    AccessTicketCreateTicketRequest,
)
from e2e.helpers.clients import issue_ticket, ticket_client, token_client
from e2e.helpers.credentials import Credentials


def test_ticket_login_returns_ticket_and_csrf(creds: Credentials) -> None:
    """SC-10 — POST /access/ticket yields ticket + CSRFPreventionToken."""
    anon = Configuration(host=f"{creds.url}/api2/json")
    anon.verify_ssl = not creds.insecure
    pbs = Pbs(anon)

    response = pbs.accessTicket.create_ticket(
        AccessTicketCreateTicketRequest(username=creds.user, password=creds.password)
    )
    data = response.data
    assert data is not None
    assert data.ticket, "ticket missing"
    assert data.csrf_prevention_token, "CSRFPreventionToken missing"


def test_invalid_password_raises_401(creds: Credentials) -> None:
    """SC-11 — wrong password ⇒ 401."""
    with pytest.raises(ApiException) as excinfo:
        issue_ticket(creds, password="definitely-not-the-password")
    assert excinfo.value.status == 401, excinfo.value


def test_token_auth_lists_users(creds: Credentials) -> None:
    """SC-12 — API-token auth roundtrips against a GET that requires permissions.

    PBS doesn't grant `/nodes` read perms to the default test token; `/access/users`
    is reachable by any authenticated principal.
    """
    pbs = token_client(creds)
    response = pbs.accessUsers.get_users()
    assert getattr(response, "data", None) is not None


def test_malformed_token_raises_401(creds: Credentials) -> None:
    """SC-13 — bogus token UUID ⇒ 401."""
    cfg = Configuration(host=f"{creds.url}/api2/json")
    cfg.verify_ssl = not creds.insecure
    cfg.api_key["PBSApiToken"] = "PBSAPIToken=root@pam!test:00000000-0000-0000-0000-000000000000"
    pbs = Pbs(cfg)
    with pytest.raises(ApiException) as excinfo:
        pbs.accessUsers.get_users()
    assert excinfo.value.status == 401, excinfo.value


def test_ticket_write_without_csrf_is_rejected(creds: Credentials) -> None:
    """SC-14 — ticket auth writes require CSRFPreventionToken header."""
    anon = Configuration(host=f"{creds.url}/api2/json")
    anon.verify_ssl = not creds.insecure
    bootstrap = Pbs(anon)
    ticket_response = bootstrap.accessTicket.create_ticket(
        AccessTicketCreateTicketRequest(username=creds.user, password=creds.password)
    )
    ticket = ticket_response.data.ticket
    assert ticket

    no_csrf = ticket_client(creds, ticket=ticket, csrf=None)

    # GETs work without CSRF (use /access/users since /nodes is restricted in PBS).
    response = no_csrf.accessUsers.get_users()
    assert getattr(response, "data", None) is not None

    from clientapi_pbs.models.access_users_create_users_request import (
        AccessUsersCreateUsersRequest,
    )

    with pytest.raises(ApiException) as excinfo:
        no_csrf.accessUsers.create_users(
            AccessUsersCreateUsersRequest(
                userid="e2e-csrf-probe@pbs",
                password="not-a-real-secret-1234",
                comment="should fail without CSRF",
            )
        )
    assert excinfo.value.status == 401, excinfo.value
