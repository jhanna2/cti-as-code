"""The decoy-object canary: the cheapest, highest-signal detection in the program.

A decoy export has no legitimate reader, so there is no benign population to
separate a malicious read from. Occurrence is the signal. The detection needs no
baseline, no threshold, and no model, and it does not decay as the fleet grows.
This module is the argument for deception as a collection source, made runnable.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field

# Operations that count as touching a decoy. A read, a copy, or a prefix list that
# would return the decoy are all incidents; nothing legitimate does any of them.
FIRING_OPS = {"GetObject", "CopyObject", "ListObjectsV2"}


@dataclass(frozen=True)
class Decoy:
    """A decoy object plausible enough to be indistinguishable from a real export."""

    key: str
    token: str
    size: int
    sha256: str


@dataclass
class DecoyRegistry:
    """The set of decoy keys the detection fires on. No allowlist, no threshold."""

    keys: set[str] = field(default_factory=set)

    def add(self, decoy: Decoy) -> None:
        self.keys.add(decoy.key)

    def fires_on(self, key: str) -> bool:
        return key in self.keys


def mint_decoy(key: str, size: int = 268_435_456) -> Decoy:
    """Mint a decoy object with an embedded canary token.

    Named and sized like a real settlement export so it is indistinguishable until
    the moment it fires. The token is what would surface if the object were exfiltrated
    and later validated; the sha is stable for the record in deception/.
    """
    token = "ctiac-canary-" + secrets.token_hex(16)
    sha = hashlib.sha256(f"{key}:{token}".encode()).hexdigest()
    return Decoy(key=key, token=token, size=size, sha256=sha)


def detects(event: dict, registry: DecoyRegistry) -> bool:
    """Return True if an access event touches a decoy. Any such event is an incident.

    This is the Tier-1 shape: a predicate, not a model. The false-positive rate is a
    property of how well the decoy set is enumerated, not of how the environment drifts.
    """
    if event.get("op") not in FIRING_OPS:
        return False
    return registry.fires_on(event.get("key", ""))
