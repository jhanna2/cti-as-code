# CTI as code

Detection engineering moved its rules into version control years ago. A detection
is a file, it is reviewed as a pull request, it carries test cases, and CI refuses
one that does not parse or does not fire on its own true positive. Nobody argues
about this any more.

Threat intelligence has not made the same move with its own program. The
requirements live in a slide deck. The collection plan is a spreadsheet. The
campaign is a wiki page, the source list is in one analyst's head, and the
decision about which agent may act unattended is a conversation somebody had in
a meeting. None of these can fail. They go stale silently, and the program
learns they were wrong when an incident asks one of them a question.

**CTI as code is the claim that the intelligence program itself should be
version-controlled records whose claims about each other are enforced in CI.**
Not the indicators, and not the detections. The program: what it is for, who it
serves, what it collects, what it cannot see, what it has concluded, and what its
automation is allowed to do.

## Where the work actually is

This started as a narrower question: how do you automate threat intelligence
responsibly?

Most of the intelligence cycle has been automated for years. Collection and
processing are what threat intelligence platforms sell: feeds pulled, indicators
parsed, deduplicated and enriched. Analysis has been partly automated, and models
are genuinely good at it: turning prose into structured techniques, extracting
indicators, clustering reporting, drafting an assessment. Ensemble extraction is
not new, and large platforms run it at a scale a single team should not try to
match.

Program management is the part nobody has automated, and it is the heart of the
function. Setting and maintaining the requirements. Knowing which sources answer
which of them, and which answer nothing. Noticing when a requirement has lost its
consumer. Tracking what the program cannot see. Deciding what the automation may
do unattended. That work takes most of an intelligence lead's time and energy,
and it has the largest effect on whether the function changes anything in the
security program around it. It is also held almost entirely in prose,
spreadsheets and people's heads.

Models read prose well, so reading is not the obstacle. Writing is. An agent can
summarise a collection plan in a spreadsheet; it cannot safely change one,
because nothing reviews the edit, nothing fails when the edit leaves a
requirement unanswered, and nothing records who changed what and why. The
documents other teams keep (crown jewels in a wiki, asset owners in a CMDB) can
stay where they are as sources an agent reads. The program's own state needs a
form that can be diffed, reviewed and checked.

What keeps threat intelligence from being truly agentic is not the models. It is
the program foundations, which are hard and messy and live where an agent cannot
safely change them.

Agentic software engineering shows the way out. Coding agents became useful not
because models learned to write perfect code, but because software already had
the environment an agent needs: a repository it can read, tests and CI that say
whether a change is correct, and pull requests through which a person approves
what lands. The agent proposes, the build checks, a human signs. Threat
intelligence has no equivalent. Nothing can tell an agent that its change to the
collection plan left a requirement unanswered, because the collection plan is a
spreadsheet.

CTI as code builds that environment: the program as a repository, its standards
as CI, and changes to it as pull requests an agent can open and a person
approves. Put the program into records a machine can
read, and models can do what they are good at, processing and analysis, against
a ground truth they can query: the requirements, the sources, the gaps. Put the
program's standards into gates, and the decisions that must not be automated
(attribution, anything leaving the organisation, retiring a requirement,
narrowing collection) are held in place mechanically rather than by policy. The
records are what make automating CTI responsible rather than merely fast.

## What is different about this

Several "as code" practices already exist, and this borrows from all of them. See
[PRIOR-ART.md](PRIOR-ART.md) for the lineage and where each stops.

- **Detection as code** versions the rule. Here detection is a *consumer*: the
  intelligence function pitches a detection candidate to it, and the candidate
  must say which requirement it serves and what it will not catch.
- **Threat modeling as code** versions the model of a system. Here the threat
  profile is only the first tree, the set of IDs everything else cites.
- **STIX** describes the threat: the indicator, the actor, the relationship. It
  says nothing about why the program collects, for whom, or where it is blind.
  These records describe the program, and they can point at STIX objects.
- **Deception via infrastructure as code** deploys decoys from templates. Here a
  decoy is a collection source with a requirement above it, a plausibility claim,
  and a refresh cadence the build checks.

The new part is the object being versioned. An intelligence requirement, an
essential element of information, a collection gap, a campaign's cross-source
corroboration, and an agent's approval level all become records with resolvable
references, and the program's standards become gates that fail the build.

## The principles

Each is enforced somewhere in this repository, and each links to the decision that
argues it.

### 1. The program is records, not prose

Every requirement, source, decoy, detection candidate, campaign, adjudicated case
and agent is a structured, addressable record in a tree. The prose explains the
records; it is not where the program lives.

A collection plan on a wiki page cannot fail. That is its defining weakness. A
requirement held as a record can, and once it can, coverage is a query rather than
a quarterly exercise. ([D-03](DECISIONS.md#d-03-requirements-are-machine-readable-records-under-ci))

### 2. Every reference resolves, and the chain runs both ways

A requirement names the decision it serves and the person who makes it. Its
essential elements name the sources that answer them. A source names the
requirements it serves. A detection candidate, a decoy and a campaign each name
the requirement above them. CI fails on a reference that resolves to nothing.

The chain is the audit. A source that traces to no requirement is noise, and a
requirement that traces to no decision serves no one. `ctiac trace` prints the
whole chain in one command, which is the program's central claim made checkable
by someone who was not present for the work.

### 3. A gap is named, or the build fails

An essential element with no source and no named gap fails CI. An essential
element with no source and a *named* gap passes, and so does a sourced one that
admits it is partial.

This is the gate that matters most, because the failure it prevents is the most
common one in the field: an unnamed gap is indistinguishable from coverage. The
tempting alternative is to point a requirement at whichever source happens to
exist and report it covered. Named gaps are also the most useful output the
program has. `ctiac gaps` prints them together, and that list is the case for every
new source, purchase or hire.

### 4. Every record publishes its own blind spot

A detection candidate carries a non-empty `not_covered`. An agent carries
`blind_spots`. A correspondence between an internal cluster and a publicly named
actor carries `would_change`: what knowing it would change, and "nothing" is an
acceptable answer that must be written down. A partially sourced requirement says
what the source misses.

Pitching a detection without stating what it misses is how coverage numbers start
lying. Requiring the field turns an omission into a failed build.

### 5. A gate without a negative test is a comment

Every gate in `src/ctiac/schema.py` has a test that constructs the forbidden shape
and asserts rejection. A rule nobody has watched fail is a rule nobody knows
works.

### 6. An empty result is an error, not a pass

Run against the wrong directory, the validator finds no records. Reporting that as
"0 violations" would be a green build that read nothing, so it exits with an
error. The same idea runs through the records: a deception source that is silent
because it is working looks identical to one that is silent because it is broken,
so its liveness is proven by a scheduled synthetic fire rather than by counting
events.

### 7. Authority follows determinism

A deterministic, reproducible check may sit in the path and block. A model's
judgement may only raise for review. Both can read the same content; only one may
decide what is dropped.
([D-17](DECISIONS.md#d-17-deterministic-checks-may-block-probabilistic-ones-may-only-raise))

The sharpest case is sanitisation. The stage that decides what a model is allowed
to see, over text an adversary wrote for that purpose, cannot itself be a model,
because that moves the injection one step earlier onto a more privileged victim.
The sanitiser in this repository is a static transform, and a golden test holds
its published output to the code byte for byte.
([D-18](DECISIONS.md#d-18-sanitisation-is-deterministic-and-sits-before-every-model-call))

### 8. Agents are records, and untrusted input never runs autonomously

An agent may not run until it has a contract: what triggers it, which model,
what approval level, whether it reads attacker-influenceable text, where its
evaluation set is, what it costs, and where it is known to fail. The load-bearing
gate is one line:

```python
if agent["untrusted_inputs"] and agent["approval"] == "autonomous":
    raise ContractViolation
```

Intelligence work is unusual in how much of its input is written by the
adversary: scraped reporting, forum posts, log fields a customer controls, support
tickets quoting a caller, submissions to a sharing body. An agent that reads that
text and can act without review is a channel through which the adversary can
argue directly into the automation, and a merged suppression is a persistence
mechanism.

### 9. Humans hold a short, fixed boundary, and writes are pull requests

Automation is earned one rung at a time, each rung entered on measured evidence
from the rung below
([D-16](DECISIONS.md#d-16-automation-is-a-ladder-with-gates-and-a-short-fixed-boundary)).
A short list of decisions never climbs: attribution claims, anything leaving the
organisation, retiring a requirement or a source, insider-threat calls, and
narrowing a collection filter. Each is irreversible or a business judgement, and
no better model changes either property.

Agents read the trees. They do not write them. An agent that wants to change the
program opens a pull request, validated against the same gates a human commit
is, and a person signs it. Adjudicated cases are stricter still: a case record
with no human reviewer fails, because the moment an agent writes its own precedent
a learning loop becomes one that amplifies its own errors.
([D-20](DECISIONS.md#d-20-judgement-is-retrieved-rather-than-trained))

### 10. Being wrong is cheap

Any program designed before its environment is fully known is partly wrong. Prose
makes that expensive, because a wrong assumption is a paragraph somebody has to
find, and the ones nobody finds stay. Records make it cheap: every environment
claim is a field, every unanswered question is a named gap, and the difference
between the design and reality is a diff.
([D-22](DECISIONS.md#d-22-the-records-are-a-baseline-to-be-diffed-not-a-plan-to-be-re-typed))

### 11. Agent-legible by default

If a foundation is not machine-readable and reachable by an agent, it is not
finished. The trees are how a human reviews the program and also how an agent
reads it, which is what lets an agent answer "which requirements have no
collection" without a person assembling the answer by hand. This is also a
purchasing rule: a tool that traps its data in a console is a dead end for an
agentic program, however good the console is.
([D-15](DECISIONS.md#d-15-agent-legible-by-default-through-an-api-rather-than-mcp))

## What it makes possible

The records are not the goal. They are what makes several things buildable that
cannot be built over prose. Each is designed in [SYSTEMS.md](SYSTEMS.md).

**Collection as a controlled loop.** Every collection function filters its intake,
and almost none can say afterwards what the filter got wrong. With requirements
as records, both the filtered and the unfiltered stream can be scored against
them. What passed and matched nothing is waste. What matched a requirement and was
filtered out is a miss, and a miss that persists across audits is a collection
gap discovered automatically rather than by somebody noticing. The gap register
stops being a spreadsheet and becomes an output.

**Campaigns that show their corroboration.** A campaign is a record that clusters
observations and tags each one with the tier it came from: internal telemetry,
deception, open reporting, a peer's sighting. `trace` reports how many tiers each
campaign spans, so a single-source campaign cannot be presented with the
confidence of a corroborated one.

**Cluster identity kept apart from public names.** Internal clusters get flat
designators. Suspected overlap with a vendor-named actor lives in a separate block
that nothing else resolves through, and every entry must say what knowing it
would change. An evocative external name cannot quietly become the program's own
conclusion.
([D-11](DECISIONS.md#d-11-internal-cluster-identity-is-the-priority-external-naming-is-a-lookup))

**Deception declared rather than placed.** A decoy is a collection source with a
requirement above it. Declared as a record, its placement can be derived from the
declaration and a drifted decoy becomes a failing check. Generating plausible
decoys by reading the real estate is the most dangerous automation in the
program, so it is split across a scanner, a planner and a builder that no single
process holds together.
([D-08](DECISIONS.md#d-08-the-deception-estate-is-declared-as-code-with-separated-duties))

**Judgement retrieved rather than trained.** Human-adjudicated triage decisions
are records. A model's triage step retrieves the nearest ones as precedent, and a
drift monitor baselines agent triage against them. Neither works without a case
store that only humans can write to.

## What it is not

It is not a threat intelligence platform, and it does not store indicators. It
sits beside whatever holds them and says why the program collects them.

It is not a replacement for STIX, ATT&CK or a detection-as-code pipeline. It
cites all three.

It is not a claim that the records are the intelligence. A requirement that
passes every gate can still be the wrong requirement. The gates enforce the
program's honesty about itself: that it names who it serves, what it can see and
what it cannot. They do not do the analysis.

And the gates can be gamed. If records start being written to satisfy the gates
rather than to describe the program, gaps get named vaguely enough to pass. The
remedy then is fewer gates, not more.

## Where to go next

| To see | Read |
|---|---|
| Every record type and the gate that guards it | [CONTRACTS.md](CONTRACTS.md) |
| The systems the records make buildable | [SYSTEMS.md](SYSTEMS.md) |
| Each decision argued, with what would reverse it | [DECISIONS.md](DECISIONS.md) |
| What came before, and where it stops | [PRIOR-ART.md](PRIOR-ART.md) |
| A worked program for a fictional freight-booking platform | [`example/`](../example/) |
