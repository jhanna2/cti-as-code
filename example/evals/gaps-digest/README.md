# Golden set: gaps-digest

The evaluation set for the `gaps-digest` agent contract.

**What belongs here.** A frozen copy of the example trees and the digest a
person agrees is correct for it: every named gap listed once, partial gaps kept
apart from open ones, and no gap invented. The first measurement is mechanical,
because `ctiac gaps` prints the same list deterministically. The agent's digest
is checked against that list, and anything it adds or drops is a failure.

**Status: not populated.** The agent is designed rather than built, and the set
waits for it for the reason given in `evals/ttp-extractor/README.md`.
