"""Capability gates exposed by client-api/proxmox-docker-action."""
from __future__ import annotations

import os


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").lower() in ("1", "true", "yes")


def kvm_available() -> bool:
    return _truthy("PROXMOX_KVM_AVAILABLE")


def cgroupv2_available() -> bool:
    return _truthy("PROXMOX_CGROUPV2_AVAILABLE")


def network_available() -> bool:
    return os.environ.get("PROXMOX_NO_NETWORK", "") != "1"
