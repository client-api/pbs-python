"""Shared pytest fixtures for the PBS E2E suite."""
from __future__ import annotations

from typing import Iterator

import pytest

from clientapi_pbs import Pbs
from e2e.helpers.clients import token_client
from e2e.helpers.credentials import Credentials, MissingCredentialError
from e2e.helpers.fixtures import cleanup_e2e, first_node


@pytest.fixture(scope="session")
def creds() -> Credentials:
    try:
        return Credentials.from_env()
    except MissingCredentialError as exc:
        pytest.skip(str(exc))


@pytest.fixture(scope="session")
def pbs(creds: Credentials) -> Pbs:
    return token_client(creds)


@pytest.fixture(scope="session")
def node(pbs: Pbs) -> str:
    return first_node(pbs)


@pytest.fixture(scope="session", autouse=True)
def _session_cleanup(creds: Credentials, pbs: Pbs) -> Iterator[None]:
    cleanup_e2e(pbs)
    yield
    cleanup_e2e(pbs)
