# Golden set: ttp-extractor

The evaluation set the `ttp-extractor` agent contract points at. Every agent
declares one, and CI fails when the path does not resolve, because an agent whose
evaluation set is a path nobody created is an agent nobody is measuring.

**What belongs here.** One file per case: an input document as it would arrive
after sanitisation, and the expected structured return. Cases are chosen for the
failures that matter rather than for coverage: reporting that maps cleanly,
reporting whose technique is implied rather than named, a document with two
actors in it, and at least one item from the blind spots the contract declares.

**Status: not populated.** The extraction agent is designed rather than built
(see the built-and-designed split in the README), and a golden set assembled
before the agent exists would encode guesses about its output shape rather than
measure it. The directory and the gate exist now so that the first thing the
agent needs is already required of it, rather than added after it is running and
already trusted.
