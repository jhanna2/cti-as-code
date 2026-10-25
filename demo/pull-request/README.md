# A pull request, and the gates that read it

The repository's argument is that an agent can propose changes to the
intelligence program the way it proposes changes to code, and that CI says when
a change is wrong before a person spends time on it. This is that, end to end.

Every output below was captured from a run of `ctiac` against a copy of
`example/`. Nothing here is hand-written.

## 1. An agent proposes a requirement

[`proposed-PIR-09.yml`](proposed-PIR-09.yml) is a new requirement drafted from a
vendor report. It reads well. It has a title, a decision, a consumer and a
question. It also cites an actor class that does not exist and a collection
source that does not exist.

## 2. CI refuses it

```
$ ctiac validate example/
FAIL [requirements] PIR-09: threat_profile_ref 'ACTOR-09' resolves to no CJ or ACTOR
FAIL [requirements] PIR-09: EEI EEI-09-1 has neither a resolvable source nor a named gap

2 violation(s)
```

The exit code is 1, so the pull request cannot merge. Neither failure needed a
person or a model to find. The program's claims about each other are checked
the same way a type checker checks a call.

## 3. The fix names what is true

[`fixed-PIR-09.yml`](fixed-PIR-09.yml) points the actor reference at a class that
exists (`ACTOR-04`), cites the ticket source that holds part of the answer
(`SRC-06`), and names what is still missing instead of pointing at a source
that does not exist.

```
$ ctiac validate example/
ok: 35 records across 8 trees, 0 violations
```

## 4. The program gets more honest, not less

The new requirement adds a named gap, and `gaps` lists it with the rest:

```
$ ctiac gaps example/ | tail -4
PIR-09  EEI-09-1  [PARTIAL]  Which payout-account changes in the last 90 days were requested by a caller who failed ve…
    Partial. SRC-06 records the verification method on each ticket, but the payout system's own change log is not a collected source, so changes made outside the support desk are invisible.

8 named gap(s)
```

## What this does not show

The agent that drafted the proposal is not part of this repository. The gates
are built and tested. The extraction agent and the pull-request workflow around
it are designed and not built (see the built-and-designed table in the main
README).
