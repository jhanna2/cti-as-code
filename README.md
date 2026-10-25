# CTI as code

**The threat intelligence program itself, held as version-controlled records whose
claims about each other are enforced in CI.**

Detection engineering moved its rules into git years ago. Threat intelligence
never moved its program. Requirements live in a slide deck, the collection plan in
a spreadsheet, campaigns in a wiki, and none of them can fail. They go stale
silently, and the program finds out when an incident asks one of them a question.

This repository moves them. A priority intelligence requirement is a YAML record
that names the decision it serves and who makes it. Each question under it
resolves to a collection source or names a gap, and CI fails when it does
neither. Decoys, detection candidates and campaigns each point back up to a
requirement. Agents declare a contract before they may run, and an agent that
reads adversary-written text may not run unattended. One command walks the whole
chain.

The motivation is automating CTI responsibly. Collection and processing were
automated long ago, and analysis partly. Program management (the requirements,
the collection plan, the gaps, what automation may do) is the heart of the
function, where most of the time goes, and it has stayed in prose. A model can
read prose; it cannot safely change it. Nothing reviews the edit, nothing says
when it broke a requirement, and nothing records why. What keeps CTI from being
truly agentic is those foundations, not the models.

Agentic software engineering works because code has a repository an agent can
read, CI that says when a change is wrong, and pull requests a person approves.
This gives the intelligence program the same environment: models do the
processing and analysis they are good at, propose changes to the program as pull
requests, and the gates hold the decisions that must stay human.

Read [docs/CONCEPT.md](docs/CONCEPT.md) for the argument.

## Try it

```bash
pip install -e ".[test]"
ctiac validate example/     # every gate, against every record
ctiac trace example/        # requirement -> collection -> candidate -> campaign
ctiac gaps example/         # everything the program says it cannot see
ctiac report example/       # coverage summary
pytest -q                   # the gates, each watched failing
```

No install needed for a quick look: `PYTHONPATH=src python -m ctiac.cli trace example/`.
Python 3.10+ and PyYAML.

## What it looks like

Output from a run against the example program, captured and not edited.

```
$ ctiac validate example/
ok: 34 records across 8 trees, 0 violations

$ ctiac trace example/
PIR coverage (requirement -> collection):
  PIR-03  EEI-03-1  <- SRC-04
  PIR-03  EEI-03-2  <- SRC-01  PARTIAL: Partial only. SRC-01 sees actors that get written up publicly, which lags and omits the o…
  PIR-05  EEI-05-1  <- SRC-02  PARTIAL: Partial. SRC-02 answers this with near-perfect precision for the decoy estate, where no l…
  PIR-05  EEI-05-2  <- SRC-01, SRC-06
  PIR-05  EEI-05-3  <- SRC-01  PARTIAL: Open reporting sees recruitment that gets written up, which lags. Closing it properly mea…
  PIR-06  EEI-06-1  <- GAP: No source. This inventory usually lives in contracts and integration tickets rather than …
  PIR-06  EEI-06-2  <- GAP: No source. The highest-value finding available in this area and the one least likely to b…
  PIR-06  EEI-06-3  <- SRC-05
  PIR-06  EEI-06-4  <- SRC-01, SRC-05  PARTIAL: Partial. Public disclosure catches the large cases and misses small vendors entirely, and…
  PIR-08  EEI-08-1  <- SRC-04
  PIR-08  EEI-08-2  <- SRC-03, SRC-01  PARTIAL: Registration and passive-DNS history is bought, not built. SRC-03 covers the pivot; what …

Detection candidates (candidate -> requirement):
  DC-07  -> PIR-03 [active]  origin=deception
  DC-08  -> PIR-08 [active]  origin=hunt
  DC-09  -> PIR-08 [active]  origin=deception

Campaigns (cross-tier corroboration):
  CAMP-01  CAMPAIGN-001  spans 3 tier(s): external-open, external-shared, internal-deception
  CAMP-02  CAMPAIGN-002  spans 1 tier(s): internal-telemetry  <- single-tier, weakly corroborated

$ ctiac gaps example/
PIR-03  EEI-03-2  [PARTIAL]  Which actors have demonstrated intent against freight and payment platforms?
    Partial only. SRC-01 sees actors that get written up publicly, which lags and omits the ones nobody has reported yet. Closing it needs paid actor reporting, which is a purchase decision rather than a…
PIR-05  EEI-05-1  [PARTIAL]  Has any principal without an enumerated business reason read, copied or enumerated a ledg…
    Partial. SRC-02 answers this with near-perfect precision for the decoy estate, where no legitimate reader exists. The equivalent check on real stores is blocked until the legitimate-exception list is…
...
7 named gap(s)

$ ctiac report example/
PIRs: 4 (4 active)
  with every EEI sourced or gap-named: 4/4
  EEIs sourced but still carrying a named gap: 5
Detection candidates: 3  by origin: {'deception': 2, 'hunt': 1}
Decoys: 2   Campaigns: 2   Adjudicated cases: 2
```

[`demo/pull-request/`](demo/pull-request/) shows the other half: an agent proposes a requirement, CI refuses it with the exact failures, and the fix names the gap.

`GAP` is a correct output, not a failure. The failure is a requirement with no
source *and* no named gap, because an unnamed gap is indistinguishable from
coverage.

## The principles

Argued in full in [CONCEPT.md](docs/CONCEPT.md), and each enforced somewhere in
this repository.

1. The program is records, not prose.
2. Every reference resolves, and the chain runs both ways.
3. A gap is named, or the build fails.
4. Every record publishes its own blind spot.
5. A gate without a negative test is a comment.
6. An empty result is an error, not a pass.
7. Authority follows determinism: deterministic checks may block, models may only raise.
8. Agents are records, and untrusted input never runs autonomously.
9. Humans hold a short, fixed boundary, and writes are pull requests.
10. Being wrong is cheap: the records are a baseline to be diffed.
11. Agent-legible by default.

## What is here

| Path | Contents |
|---|---|
| [`docs/CONCEPT.md`](docs/CONCEPT.md) | The idea and its principles. Start here |
| [`docs/CONTRACTS.md`](docs/CONTRACTS.md) | The eight record types and every gate, enforced or designed |
| [`docs/SYSTEMS.md`](docs/SYSTEMS.md) | What the records make buildable: filter audit, actor ranking, assurance loop, deception as code, the automation ladder |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Twenty-four design decisions, each with what would reverse it |
| [`docs/PRIOR-ART.md`](docs/PRIOR-ART.md) | Detection as code, threat modeling as code, STIX, and where each stops |
| [`example/`](example/) | A complete worked program for a fictional freight-booking platform |
| [`src/ctiac/`](src/ctiac/) | Loader, validator, CLI, sanitiser, decoy canary |
| [`demo/`](demo/) | A poisoned article and exactly what a model sees after sanitisation, and a pull request the gates refuse |
| [`tests/`](tests/) | A negative test for every gate |

## Built, and designed

Kept explicit, because a design that quietly implies working software is not worth
much.

**Built and tested.** The eight record trees with a worked example. The validator
enforcing every gate marked *Enforced* in [CONTRACTS.md](docs/CONTRACTS.md), each
with a negative test. `trace`, `gaps` and `report`. The deterministic sanitiser,
which strips five planted prompt injections from a poisoned article while keeping
its real claims, with a golden test holding its published output to the code. The
decoy canary predicate. CI running all of it.

**Designed, not built.** The read API, the model-driven extraction pipeline, the
filter audit, actor clustering and ranking, the sharing pipeline, and the
retrieval and drift loop over adjudicated cases. They are specified in
[SYSTEMS.md](docs/SYSTEMS.md) with their gates. Nothing here has run against real
telemetry; every fixture is synthetic.

## Using it for your own program

Copy `example/` and replace the records. The validator takes any directory with
the same layout: `ctiac validate path/to/your-program/`. Start with the threat
profile and three requirements, name the gaps honestly, and let `ctiac gaps`
become the case for your next source.

## Author and licence

Created by Jeff Hanna. First published October 2026.

Code is licensed under [Apache 2.0](LICENSE). The documentation in `docs/` and the
example records are licensed under [CC BY 4.0](LICENSE-docs): reuse them freely,
with attribution. To cite this work, see [CITATION.cff](CITATION.cff).
