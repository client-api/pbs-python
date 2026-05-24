"""Example: list cluster nodes.

Run with:
    PBS_HOST=https://pbs.example.com:8007 \\
    PBS_TOKEN='PBSAPIToken=root@pam!auto:...' \\
    python examples/list_nodes.py
"""

from __future__ import annotations

import os

from clientapi_pbs.configuration import Configuration
from clientapi_pbs.pbs import Pbs


def main() -> None:
    config = Configuration(host=f"{os.environ.get('PBS_HOST', 'https://localhost:8007')}/api2/json")
    # OpenAPI auth-scheme name (NOT the `Authorization` header name).
    # The full `PBSAPIToken=…` string goes in here; no api_key_prefix.
    config.api_key["PBSApiToken"] = os.environ.get("PBS_TOKEN", "")

    pbs = Pbs(config)
    response = pbs.nodes.get_nodes()
    nodes = getattr(response, "data", None) or []
    print(f"Found {len(nodes)} node(s):")
    for node in nodes:
        print(
            f"  - {getattr(node, 'node', None)} "
            f"(status={getattr(node, 'status', None)}, "
            f"cpu={getattr(node, 'cpu', None)}, "
            f"mem={getattr(node, 'mem', None)}/{getattr(node, 'maxmem', None)})",
        )


if __name__ == "__main__":
    main()
