"""Client factories for the two auth modes PBS supports."""
from __future__ import annotations

from typing import TYPE_CHECKING

from clientapi_pbs import Configuration, Pbs

if TYPE_CHECKING:
    from e2e.helpers.credentials import Credentials


def token_client(creds: "Credentials") -> Pbs:
    cfg = Configuration(host=f"{creds.url}/api2/json")
    cfg.verify_ssl = not creds.insecure
    cfg.api_key["PBSApiToken"] = creds.token_header_value
    return Pbs(cfg)


def ticket_client(
    creds: "Credentials",
    *,
    ticket: str,
    csrf: str | None = None,
) -> Pbs:
    cfg = Configuration(host=f"{creds.url}/api2/json")
    cfg.verify_ssl = not creds.insecure
    cfg.api_key["PBSAuthCookie"] = ticket
    if csrf is not None:
        cfg.api_key["CSRFPreventionToken"] = csrf
    return Pbs(cfg)


def issue_ticket(creds: "Credentials", *, password: str | None = None) -> Pbs:
    from clientapi_pbs.models.access_ticket_create_ticket_request import (
        AccessTicketCreateTicketRequest,
    )

    anon = Configuration(host=f"{creds.url}/api2/json")
    anon.verify_ssl = not creds.insecure
    bootstrap = Pbs(anon)

    response = bootstrap.accessTicket.create_ticket(
        AccessTicketCreateTicketRequest(
            username=creds.user,
            password=password if password is not None else creds.password,
        )
    )
    data = response.data
    if data is None or not data.ticket:
        raise RuntimeError(f"ticket login returned no ticket: {response!r}")
    return ticket_client(
        creds,
        ticket=data.ticket,
        csrf=data.csrf_prevention_token,
    )
