"""Load the contract trees into memory and resolve cross-references.

The trees are files first, because files are diffable, versioned, and readable with
no running service. This loader is the thin layer that turns them into records keyed
by id so the validator and the trace command can walk the references between them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Repo:
    """Every contract tree, loaded and keyed by id (agents by name)."""

    root: Path
    crown_jewels: dict = field(default_factory=dict)
    actors: dict = field(default_factory=dict)
    pirs: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)
    decoys: dict = field(default_factory=dict)
    candidates: dict = field(default_factory=dict)
    campaigns: dict = field(default_factory=dict)
    cases: dict = field(default_factory=dict)
    agents: dict = field(default_factory=dict)

    def profile_ids(self) -> set[str]:
        return set(self.crown_jewels) | set(self.actors)


def _load_one_per_file(directory: Path, key: str = "id") -> dict:
    """A tree where each *.yml file holds a single record with an id field."""
    records: dict = {}
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("*.yml")):
        doc = yaml.safe_load(path.read_text()) or {}
        ident = doc.get(key)
        if ident is None:
            raise ValueError(f"{path}: record has no '{key}'")
        if ident in records:
            raise ValueError(f"{path}: duplicate {key} '{ident}'")
        doc["_path"] = str(path.relative_to(directory.parent))
        records[ident] = doc
    return records


def _load_list_file(path: Path, list_key: str) -> dict:
    """A file holding a list of records under one top-level key (the threat profile)."""
    if not path.is_file():
        return {}
    doc = yaml.safe_load(path.read_text()) or {}
    out: dict = {}
    for rec in doc.get(list_key, []):
        out[rec["id"]] = rec
    return out


def load_repo(root: str | Path) -> Repo:
    root = Path(root)
    return Repo(
        root=root,
        crown_jewels=_load_list_file(root / "threat-profile" / "crown-jewels.yml", "crown_jewels"),
        actors=_load_list_file(root / "threat-profile" / "actors.yml", "actors"),
        pirs=_load_one_per_file(root / "requirements"),
        sources=_load_one_per_file(root / "collection"),
        decoys=_load_one_per_file(root / "deception"),
        candidates=_load_one_per_file(root / "detection-candidates"),
        campaigns=_load_one_per_file(root / "campaigns"),
        cases=_load_one_per_file(root / "cases"),
        agents=_load_one_per_file(root / "agents", key="name"),
    )
