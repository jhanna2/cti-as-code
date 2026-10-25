"""Contract validation: the CI gates from docs/CONTRACTS.md, enforced.

A gate is a rule the trees must satisfy. Each returns Violations; the CLI exits
nonzero if any survive. A gate without a negative test in tests/ is a comment, so
every rule here is paired with a constructed-failure test.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .loader import Repo


@dataclass(frozen=True)
class Violation:
    tree: str
    ident: str
    message: str

    def __str__(self) -> str:
        return f"[{self.tree}] {self.ident}: {self.message}"


def _resolvable_source(repo: Repo, sid: str) -> bool:
    return sid in repo.sources


def check_requirements(repo: Repo) -> list[Violation]:
    v: list[Violation] = []
    for pid, pir in repo.pirs.items():
        status = pir.get("status")
        if status == "retired" and not pir.get("retired_reason"):
            v.append(Violation("requirements", pid, "retired PIR has no retired_reason"))
        if status == "active":
            if not pir.get("consumer"):
                v.append(Violation("requirements", pid, "active PIR has no consumer"))
            if not pir.get("decision"):
                v.append(Violation("requirements", pid, "active PIR has no decision"))
        for ref in pir.get("threat_profile_refs", []) or []:
            if ref not in repo.profile_ids():
                v.append(Violation("requirements", pid, f"threat_profile_ref '{ref}' resolves to no CJ or ACTOR"))
        for eei in pir.get("eei", []) or []:
            eid = eei.get("id", "?")
            sources = eei.get("sources") or []
            resolvable = any(_resolvable_source(repo, s) for s in sources)
            if not resolvable and not eei.get("gap"):
                v.append(Violation("requirements", pid, f"EEI {eid} has neither a resolvable source nor a named gap"))
    return v


def check_candidates(repo: Repo) -> list[Violation]:
    v: list[Violation] = []
    for cid, cand in repo.candidates.items():
        pir_id = cand.get("pir")
        pir = repo.pirs.get(pir_id)
        if pir is None:
            v.append(Violation("detection-candidates", cid, f"cites PIR '{pir_id}' which does not resolve"))
        elif pir.get("status") != "active":
            v.append(Violation("detection-candidates", cid, f"cites PIR '{pir_id}' which is not active"))
        if not cand.get("not_covered"):
            v.append(Violation("detection-candidates", cid, "not_covered is empty (a candidate must publish its blind spot)"))
        if cand.get("origin") == "hunt" and not cand.get("hunt_ref"):
            v.append(Violation("detection-candidates", cid, "origin is hunt but hunt_ref is missing"))
        fixtures = cand.get("fixtures") or {}
        for kind in ("true_positive", "false_positive"):
            rel = fixtures.get(kind)
            if not rel:
                v.append(Violation("detection-candidates", cid, f"missing {kind} fixture"))
            elif not (repo.root / rel).is_file():
                v.append(Violation("detection-candidates", cid, f"{kind} fixture not found: {rel}"))
    return v


def check_decoys(repo: Repo) -> list[Violation]:
    v: list[Violation] = []
    for did, dec in repo.decoys.items():
        if not dec.get("plausibility"):
            v.append(Violation("deception", did, "no plausibility (an obvious decoy catches nobody)"))
        maint = dec.get("maintenance") or {}
        if not maint.get("refresh_days"):
            v.append(Violation("deception", did, "no maintenance.refresh_days (an unrefreshed decoy becomes noise)"))
        if dec.get("pir") and dec["pir"] not in repo.pirs:
            v.append(Violation("deception", did, f"cites PIR '{dec['pir']}' which does not resolve"))
    return v


_HANDLING_CLASSES = {"open", "open-hostile", "member", "closed"}


def check_sources(repo: Repo) -> list[Violation]:
    """A source you cannot locate is a source you cannot audit or replace.

    The registry's value is the joins, but a join to a record that does not say
    where the data physically is leaves every scoping answer unverifiable. These
    gates ask for the minimum that makes a record actionable by someone who did
    not write it.
    """
    v: list[Violation] = []
    for sid, src in repo.sources.items():
        cls = src.get("class")
        if not cls:
            # The sanitiser refuses to process a document whose source declares
            # no class, so an unclassed source is a stalled pipeline.
            v.append(Violation("collection", sid, "declares no class"))
        prov = src.get("provenance") or {}
        if not prov:
            v.append(Violation("collection", sid, "has no provenance block; where the data comes from is not recorded"))
            continue
        if cls == "internal":
            # A source may sit on one asset or span many. A deception estate is
            # the second kind, so the emitters carry the placement instead.
            emitters = prov.get("emitters") or []
            if emitters:
                for em in emitters:
                    missing = [f for f in ("asset", "location") if not em.get(f)]
                    if missing:
                        ref = em.get("decoy_ref") or em.get("kind") or "(unnamed)"
                        v.append(Violation("collection", sid, f"emitter '{ref}' names no {' or '.join(missing)}"))
            else:
                for field in ("asset", "location"):
                    if not prov.get(field):
                        v.append(Violation("collection", sid, f"internal source names no {field}"))
            store = prov.get("store") or {}
            if not (store.get("dataset") and store.get("table")):
                v.append(Violation("collection", sid, "internal source does not say which dataset and table hold it"))
        else:
            origin = prov.get("origin") or {}
            if not (origin.get("transport") or prov.get("vendor")):
                v.append(Violation("collection", sid, "external source names neither a transport nor a vendor"))
        if cls in _HANDLING_CLASSES and not (prov.get("handling") or {}).get("sanitisation"):
            v.append(Violation("collection", sid, f"class '{cls}' is outside the trust boundary and declares no sanitisation handling"))
        if prov.get("vendor") and not prov.get("licensing"):
            # Redistribution terms surface in an audit, not in a build.
            v.append(Violation("collection", sid, "paid source declares no licensing terms"))
    return v


def check_campaigns(repo: Repo) -> list[Violation]:
    v: list[Violation] = []
    for cid, camp in repo.campaigns.items():
        if camp.get("status") == "merged" and not camp.get("merged_into"):
            v.append(Violation("campaigns", cid, "merged campaign has no merged_into"))
        for pir_id in camp.get("pirs", []) or []:
            pir = repo.pirs.get(pir_id)
            if pir is None or pir.get("status") != "active":
                v.append(Violation("campaigns", cid, f"answers PIR '{pir_id}' which does not resolve to an active PIR"))
        for obs in camp.get("observations", []) or []:
            if not obs.get("source_tier"):
                v.append(Violation("campaigns", cid, f"observation {obs.get('id','?')} has no source_tier"))
        v += _check_public_overlap(cid, camp)
    return v


def _check_public_overlap(cid: str, camp: dict) -> list[Violation]:
    """An external name is worth what it changes. See D-11.

    Every suspected correspondence with a publicly named cluster has to carry a
    confidence and say what knowing it would change. An entry that cannot answer
    the second is not evidence, it is a name someone liked, and the whole point
    of keeping the block non-resolvable is that nothing downstream can start
    depending on one.
    """
    v: list[Violation] = []
    for entry in camp.get("public_overlap", []) or []:
        name = entry.get("name") or "(unnamed)"
        for field in ("name", "confidence", "would_change"):
            if not entry.get(field):
                v.append(Violation("campaigns", cid, f"public_overlap '{name}' has no {field}"))
        if entry.get("name") and entry["name"] == camp.get("name"):
            v.append(Violation("campaigns", cid, f"public_overlap '{name}' is the campaign's own name; an external label is not cluster identity"))
    return v


def check_agents(repo: Repo) -> list[Violation]:
    v: list[Violation] = []
    for name, agent in repo.agents.items():
        # The load-bearing gate: an agent exposed to attacker-controlled text may
        # not run autonomously. A merged suppression would be a persistence mechanism.
        if agent.get("untrusted_inputs") and agent.get("approval") == "autonomous":
            v.append(Violation("agents", name, "untrusted_inputs and approval:autonomous; an adversary could argue into the automation"))
        eval_set = agent.get("evaluation_set")
        if not eval_set:
            v.append(Violation("agents", name, "no evaluation_set"))
        elif not (repo.root / eval_set).exists():
            # A declared path nobody created is an agent nobody is measuring.
            v.append(Violation("agents", name, f"evaluation_set '{eval_set}' does not resolve"))
        if not agent.get("blind_spots"):
            v.append(Violation("agents", name, "no declared blind_spots"))
    return v


def check_cases(repo: Repo) -> list[Violation]:
    v: list[Violation] = []
    for cid, case in repo.cases.items():
        # Human-only writes: the moment an agent writes its own precedent, the
        # learning loop becomes a feedback loop that amplifies its own errors.
        if not case.get("reviewer"):
            v.append(Violation("cases", cid, "no reviewer (cases are human-adjudicated only)"))
    return v


def validate(repo: Repo) -> list[Violation]:
    return (
        check_requirements(repo)
        + check_candidates(repo)
        + check_decoys(repo)
        + check_sources(repo)
        + check_campaigns(repo)
        + check_agents(repo)
        + check_cases(repo)
    )
