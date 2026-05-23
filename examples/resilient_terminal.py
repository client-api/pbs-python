"""Example: resilient terminal session that auto-reconnects on glitch.

Run with:
    PBS_HOST=https://pbs.example.com:8007 \\
    PBS_TOKEN='PBSAPIToken=root@pam!auto=...' \\
    PBS_NODE=orca PBS_VMID=100 \\
    python examples/resilient_terminal.py
"""

from __future__ import annotations

import os
import sys
import time

from clientapi_pbs.configuration import Configuration
from clientapi_pbs.websocket import QemuTarget
from clientapi_pbs.websocket_resilient import RetryOptions, connect_terminal_resilient


def main() -> None:
    config = Configuration(host=f"{os.environ.get('PBS_HOST', 'https://localhost:8007')}/api2/json")
    # OpenAPI auth-scheme name (NOT the `Authorization` header name).
    # The full `PBSAPIToken=…` string goes in here; no api_key_prefix.
    config.api_key["PBSApiToken"] = os.environ.get("PBS_TOKEN", "")

    target = QemuTarget(
        node=os.environ.get("PBS_NODE", "pbs1"),
        vmid=int(os.environ.get("PBS_VMID", "100")),
    )

    session = connect_terminal_resilient(
        config, target,
        on_message=lambda text: sys.stdout.write(text),
        on_close=lambda code, reason: print(f"\n[final close: {code}]"),
        on_reconnect=lambda attempt: print(f"\n[reconnected after {attempt} attempts]"),
        on_give_up=lambda err: print(f"\n[retries exhausted: {err}]"),
        retry=RetryOptions(max_retries=20, initial_delay_s=0.25),
    )

    # Long-running session: send a command every 30 s for 5 minutes.
    session.send("date\n")
    deadline = time.monotonic() + 5 * 60
    while time.monotonic() < deadline:
        time.sleep(30)
        session.send("date\n")
    session.close()


if __name__ == "__main__":
    main()
