"""ctiac CLI: validate, trace, gaps, report.

`trace` is the central demonstration: one command prints whether every requirement
has collection behind it and every candidate has a requirement above it, which is
the claim the whole set of trees exists to support. `gaps` prints the other half:
everything the program has declared it cannot yet see.
"""
from __future__ import annotations

import sys
from pathlib import Path

from .loader import load_repo
from .schema import validate


def _root(argv: list[str]) -> Path:
    return Path(argv[0]) if argv else Path.cwd()


def record_count(repo) -> int:
    return (
        len(repo.crown_jewels) + len(repo.actors) + len(repo.pirs) + len(repo.sources)
        + len(repo.decoys) + len(repo.candidates) + len(repo.campaigns)
        + len(repo.cases) + len(repo.agents)
    )


def _refuse_empty(repo) -> int:
    """An empty tree is an invocation error, never a pass.

    The trees load relative to the working directory unless a root is given, so
    running from the wrong place finds nothing. Reporting that as "0 violations"
    would be a green result that read no records, which is precisely the failure
    this repository argues against everywhere else.
    """
    if record_count(repo):
        return 0
    print(
        f"no records found under {repo.root}\n"
        "Pass the repository root explicitly, e.g. "
        "`ctiac validate example/`.",
        file=sys.stderr,
    )
    return 2


def cmd_validate(argv: list[str]) -> int:
    repo = load_repo(_root(argv))
    if empty := _refuse_empty(repo):
        return empty
    violations = validate(repo)
    if not violations:
        print(f"ok: {record_count(repo)} records across 8 trees, 0 violations")
        return 0
    for v in violations:
        print(f"FAIL {v}")
    print(f"\n{len(violations)} violation(s)")
    return 1


def _one_line(text: str, width: int = 90) -> str:
    flat = " ".join((text or "").split())
    return flat if len(flat) <= width else flat[: width - 1] + "\u2026"


def cmd_trace(argv: list[str]) -> int:
    repo = load_repo(_root(argv))
    if empty := _refuse_empty(repo):
        return empty
    print("PIR coverage (requirement -> collection):")
    for pid, pir in sorted(repo.pirs.items()):
        if pir.get("status") != "active":
            print(f"  {pid}  [retired]")
            continue
        for eei in pir.get("eei", []) or []:
            srcs = [s for s in (eei.get("sources") or []) if s in repo.sources]
            gap = (eei.get("gap") or "").strip()
            if srcs and gap:
                # Sourced and still incomplete. Printing this as covered is how a
                # partial answer quietly becomes a confident one.
                print(f"  {pid}  {eei['id']}  <- {', '.join(srcs)}  PARTIAL: {_one_line(gap)}")
            elif srcs:
                print(f"  {pid}  {eei['id']}  <- {', '.join(srcs)}")
            else:
                print(f"  {pid}  {eei['id']}  <- GAP: {_one_line(gap) or '(unnamed)'}")
    print("\nDetection candidates (candidate -> requirement):")
    for cid, cand in sorted(repo.candidates.items()):
        pir = repo.pirs.get(cand.get("pir"))
        status = "active" if pir and pir.get("status") == "active" else "UNRESOLVED"
        print(f"  {cid}  -> {cand.get('pir')} [{status}]  origin={cand.get('origin')}")
    print("\nCampaigns (cross-tier corroboration):")
    for cid, camp in sorted(repo.campaigns.items()):
        tiers = sorted({o.get("source_tier") for o in camp.get("observations", []) or []})
        mark = "" if len(tiers) >= 2 else "  <- single-tier, weakly corroborated"
        print(f"  {cid}  {camp.get('name')}  spans {len(tiers)} tier(s): {', '.join(tiers)}{mark}")
    return 0


def cmd_gaps(argv: list[str]) -> int:
    """Every named gap, in one place.

    A named gap is the program saying what it cannot see. Collected together they
    are the collection plan's honest half, and the input to any argument for a new
    source. An unnamed gap is indistinguishable from coverage, which is why the
    requirements gate refuses one.
    """
    repo = load_repo(_root(argv))
    if empty := _refuse_empty(repo):
        return empty
    count = 0
    for pid, pir in sorted(repo.pirs.items()):
        if pir.get("status") != "active":
            continue
        for eei in pir.get("eei", []) or []:
            gap = (eei.get("gap") or "").strip()
            if not gap:
                continue
            count += 1
            srcs = [s for s in (eei.get("sources") or []) if s in repo.sources]
            kind = "PARTIAL" if srcs else "OPEN"
            print(f"{pid}  {eei['id']}  [{kind}]  {_one_line(eei.get('question', ''))}")
            print(f"    {_one_line(gap, 200)}")
    print(f"\n{count} named gap(s)")
    return 0


def cmd_report(argv: list[str]) -> int:
    repo = load_repo(_root(argv))
    if empty := _refuse_empty(repo):
        return empty
    active = [p for p in repo.pirs.values() if p.get("status") == "active"]
    covered = 0
    for pir in active:
        eeis = pir.get("eei", []) or []
        if eeis and all(
            any(s in repo.sources for s in (e.get("sources") or [])) or e.get("gap")
            for e in eeis
        ):
            covered += 1
    partial = sum(
        1
        for pir in active
        for e in (pir.get("eei") or [])
        if (e.get("gap") or "").strip()
        and any(s in repo.sources for s in (e.get("sources") or []))
    )
    print(f"PIRs: {len(repo.pirs)} ({len(active)} active)")
    print(f"  with every EEI sourced or gap-named: {covered}/{len(active)}")
    print(f"  EEIs sourced but still carrying a named gap: {partial}")
    by_origin: dict = {}
    for c in repo.candidates.values():
        by_origin[c.get("origin", "?")] = by_origin.get(c.get("origin", "?"), 0) + 1
    print(f"Detection candidates: {len(repo.candidates)}  by origin: {by_origin}")
    print(f"Decoys: {len(repo.decoys)}   Campaigns: {len(repo.campaigns)}   Adjudicated cases: {len(repo.cases)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: ctiac <validate|trace|gaps|report> [root]", file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    table = {"validate": cmd_validate, "trace": cmd_trace, "gaps": cmd_gaps, "report": cmd_report}
    fn = table.get(cmd)
    if fn is None:
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    return fn(rest)


if __name__ == "__main__":
    raise SystemExit(main())
