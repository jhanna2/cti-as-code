# Example program

A complete, worked threat intelligence program for a **fictional** freight-booking
platform: a marketplace where shippers book loads with carriers, with a payment
ledger, a dispatch engine, and a set of vendor connectors for carrier telematics
and warehouse systems. It does not describe any real company, and every asset
name, bucket, account, vendor and URL in it is invented.

It is deliberately small, a few records of each kind, and deliberately honest:
several requirements are only partially sourced and one leads with two gaps that
have no source at all. That is the shape a real program has in its first months,
and the records are built to show it rather than hide it.

| Tree | Records | What to look at |
|---|---|---|
| `threat-profile/` | 6 crown jewels, 7 actor classes | `ACTOR-06`: zero intent toward the platform, still a threat |
| `requirements/` | 4 PIRs | `PIR-06`: leads with two named gaps |
| `collection/` | 6 sources | `SRC-02` (deception, silent by design) and `SRC-06` (support tickets, attacker-authored) |
| `deception/` | 2 decoys | `DEC-02` (an object) and `DEC-03` (a canary credential), and the fixtures they justify |
| `detection-candidates/` | 3 candidates | `DC-07` and `DC-09` came from deception, `DC-08` from a hunt; each publishes its `not_covered` list |
| `campaigns/` | 2 campaigns | `CAMP-01`: three tiers, and a public name kept at arm's length. `CAMP-02`: retired by merge |
| `cases/` | 2 adjudicated cases | `CASE-0001`: where the human disagreed with the model, and why. `CASE-0002`: where they agreed |
| `agents/` | 2 agent contracts | `ttp-extractor` reads untrusted text, so it needs review. `gaps-digest` reads only reviewed records, so it may run unattended |
| `evals/`, `fixtures/` | Supporting files the gates check exist | |

Run `ctiac trace example/` and `ctiac gaps example/` from the repository root.
The pull request walkthrough in `demo/pull-request/` shows the gates catching an
agent's proposed change.
