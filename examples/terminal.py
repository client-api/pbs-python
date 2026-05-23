"""Example: open a terminal session against a QEMU VM.

Run with:
    PBS_HOST=https://pbs.example.com:8007 \\
    PBS_TOKEN='PBSAPIToken=root@pam!auto=...' \\
    PBS_NODE=orca PBS_VMID=100 \\
    python examples/terminal.py

Requires: pip install websocket-client
"""

from __future__ import annotations

import os
import sys
import time

from clientapi_pbs.configuration import Configuration
from clientapi_pbs.pbs import Pbs
from clientapi_pbs.websocket import QemuTarget


def main() -> None:
    config = Configuration(host=f"{os.environ.get('PBS_HOST', 'https://localhost:8007')}/api2/json")
    # `PBSApiToken` is the OpenAPI auth-scheme name the REST client keys
    # by; the *header* it lands on is `Authorization`. Put the full
    # `PBSAPIToken=…` string in here (no `api_key_prefix`).
    config.api_key["PBSApiToken"] = os.environ.get("PBS_TOKEN", "")

    pbs = Pbs(config)
    target = QemuTarget(
        node=os.environ.get("PBS_NODE", "pbs1"),
        vmid=int(os.environ.get("PBS_VMID", "100")),
    )

    print(f"Opening terminal on {target.node}:qemu/{target.vmid}...")
    session = pbs.connect_terminal(
        target,
        on_message=lambda text: sys.stdout.write(text),
        on_close=lambda code, reason: print(f"\n[closed: {code} {reason}]"),
        on_error=lambda exc: print(f"\n[error: {exc}]"),
    )

    session.resize(120, 32)
    session.send("uname -a\n")

    time.sleep(5)
    session.close()


if __name__ == "__main__":
    main()
