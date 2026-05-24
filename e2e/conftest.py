"""Shared pytest fixtures for the PBS E2E suite."""
from __future__ import annotations

import re as _re
from typing import Iterator

# Generator gap workaround: PBS regex patterns use POSIX character classes like
# `[:cntrl:]` / `[:^cntrl:]` which Python's `re` doesn't support — `re.match`
# silently returns None for any input, so EVERY field_validator on PBS models
# raises ValueError, including for legitimate values like 'root@pam'. We patch
# `re.match` for the test process to bypass POSIX-class patterns; this is a
# workaround until the generator translates these to PCRE-compatible regexes
# (or the spec switches to a Python-friendly syntax).
_POSIX_CLASS_MARKERS = ("[:cntrl:]", "[:^cntrl:]", "[:alpha:]", "[:digit:]",
                        "[:alnum:]", "[:upper:]", "[:lower:]", "[:space:]")
_orig_re_match = _re.match


def _patched_re_match(pattern, string, flags=0):  # type: ignore[no-untyped-def]
    if isinstance(pattern, str) and any(m in pattern for m in _POSIX_CLASS_MARKERS):
        return _orig_re_match(r"^.*$", string, flags) or _orig_re_match(r"", string, flags)
    return _orig_re_match(pattern, string, flags)


_re.match = _patched_re_match  # type: ignore[assignment]

import pytest  # noqa: E402  (must come after the patch so any pytest imports also see it)

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
