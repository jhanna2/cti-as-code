"""The decoy canary fires on any read of a decoy and stays silent on real neighbours.

No baseline, no threshold. The false-positive guard is a read of a real export in the
same prefix as the decoy: a correct detection keys on the decoy object, not the prefix.
"""
import json
from pathlib import Path

from ctiac.canary import DecoyRegistry, mint_decoy, detects

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "example"
DECOY_KEY = "s3://ledger-exports-prod/settlements/2026-q3/decoy-export-00007.csv.gz"


def _event(name):
    return json.loads((EXAMPLE / f"fixtures/deception/{name}").read_text())["event"]


def _registry():
    reg = DecoyRegistry()
    d = mint_decoy(DECOY_KEY)
    reg.add(d)
    return reg


def test_decoy_read_fires():
    assert detects(_event("decoy_read.json"), _registry()) is True


def test_adjacent_real_read_is_silent():
    assert detects(_event("adjacent_prefix_read.json"), _registry()) is False


def test_minted_token_is_unique_and_embedded():
    a = mint_decoy(DECOY_KEY)
    b = mint_decoy(DECOY_KEY)
    assert a.token != b.token
    assert a.token.startswith("ctiac-canary-")
    assert len(a.sha256) == 64


def test_non_read_ops_do_not_fire():
    assert detects({"op": "HeadBucket", "key": DECOY_KEY}, _registry()) is False
