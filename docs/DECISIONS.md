# Decision record

The decisions behind CTI as code, and behind the program in `example/` that
demonstrates it. Each entry records what was decided, why, and what would reverse
it. The principles in [CONCEPT.md](CONCEPT.md) are the short form; this is where
each one is argued.

This is a working artefact rather than a summary. Its value is the reversal
condition: a decision recorded without one is a preference, and a program that
cannot say what would change its mind cannot tell the difference between a
position it has tested and a habit it has kept. Entries are added at the bottom
and superseded explicitly. History is not rewritten.

The reasoning here is deliberately about the function rather than any one
environment. Where a decision assumes something about the environment, which in
the example is a fictional freight-booking platform that trusts vendor connectors, the
assumption is named as one. Record IDs such as `PIR-06` or `CJ-03` refer to the
example trees.

---

## Scope and charter

### D-01: The function does not own incident response or detection engineering

**Decided.** Intelligence pitches to detection and hands off to response. It
does not run either. The handoff artefact for detection is a **detection
candidate** record, which carries its own blind spots; the handoff to response is
a structured finding, not a message.

**Reasoning.** A first-hire intelligence function that claims response ends up
doing response, because response is always more urgent than analysis. Naming the
boundary early is what keeps the function doing the work only it can do. The
boundary is also what makes the interfaces worth defining: with no shared queue
and no shared owner, an ambiguous handoff has nowhere to land.

**Reverses if** the function is chartered to own detection content or incident
command, which is a different job and should be staffed as one.

---

### D-02: Adversary emulation is a consumer, not a boundary dispute

**Decided.** Red teaming and emulation stay out of scope, and the emulation
function is named as an intelligence consumer with a defined product: TTP shifts,
and a running adversarial heat map of which techniques against which crown jewels
are live now.

**Reasoning.** Declining to own something is a statement about work, not about
people. Emulation is one of the few consumers that can act on a TTP shift within
the week, and the campaign and clustering work produces most of what it needs
anyway. It also returns a signal that is otherwise hard to get: an exercise run
against a technique this function warned about answers whether the warning was
worth acting on.

**Reverses if** emulation is folded into the same team, at which point the
interface becomes an internal one and the separate product is overhead.

---

## Direction

### D-03: Requirements are machine-readable records under CI

**Decided.** Every PIR is a versioned record naming its consumer, the decision it
serves, its EEIs, the sources behind each EEI, and a review cadence. CI fails
when an EEI has neither a resolvable source nor a named gap, and when an active
requirement names no consumer or no decision.

**Reasoning.** A collection plan on a wiki page cannot fail. That is its defining
weakness: it goes stale silently, and nobody learns until an incident asks it a
question. Under CI, a requirement that stops being answerable breaks the build.
This is also what makes coverage a query rather than a quarterly exercise.

**Reverses if** the records start being maintained to satisfy the gates rather
than to reflect collection, which would show up as gaps named vaguely enough to
pass. The remedy then is fewer gates, not more.

---

### D-04: Threat ranking scores capability and intent separately

**Decided.** An actor's threat is not one number. Capability and intent toward us
are scored independently, and the ranking takes the worse of the two rather than
an average.

**Reasoning.** The two move independently and averaging hides both failure modes.
A highly capable actor with no interest in us and a motivated actor with no
capability average to the same middling score, and they need completely different
responses. Taking the worse also keeps the drive-by victim case visible, where
capability is high and intent is indiscriminate rather than absent.

**Reverses if** the scoring is used for anything that requires a single ordering
of actors, in which case the compression has to be made explicit rather than
buried in the metric.

---

## Collection

### D-05: Deception is a collection discipline, not a detection technique

**Decided.** The deception estate is built, funded and measured as a collection
source. It sits in the collection plan, its output is an observation record, and
it answers PIRs.

**Reasoning.** Framed as detection, honeypots compete with real detections for
attention and lose. Framed as collection, deception is the highest-fidelity
internal source available and the only one that generates original intelligence
rather than recording our own operations. The framing decides what gets built:
a detection-framed estate optimises for alerting, a collection-framed one
optimises for what the adversary reveals.

**Reverses if** the estate stops producing anything an analyst uses, at which
point it is a detection control and should be justified as one.

---

### D-06: Deception is the substitute for closed-source access

**Decided.** No dark web personas, no paid access to closed forums, in the first
year. The requirement they would serve is answered by making the adversary come
to us instead.

**Reasoning.** The reason to want closed-source access is to observe the
adversary in their own space. For an organisation holding other people's payment
and commercial data, entering that space carries legal exposure, an operational persona
commitment, and a reputational tail that would damage the sector body this
program is trying to found. Deception answers the same requirement by a route the
organisation can actually take, and it produces material that is ours to share.

**Reverses if** a specific, named requirement cannot be answered any other way
and the legal position is cleared in advance. Not on general appetite for
coverage.

---

### D-07: Collection class and handling class are separate taxonomies

**Decided.** Where a source sits (internal, open, member, closed) and how its
content must be handled are recorded as two independent properties. The sanitiser
refuses to process a document whose source declares no handling class.

**Reasoning.** Conflating them produces both errors. Internal telemetry is
high-value and low-risk to process; an open forum scrape is low-value and the
highest-risk text in the pipeline. A single ranking cannot express that, and the
version that gets built ends up treating trusted-and-useful as the same axis.
The highest-value tier and the highest-risk tier barely overlap, which is exactly
why one axis will not do.

**Reverses if** a third property starts hiding inside one of these two, which
would show up as handling exceptions that do not follow from the class.

---

### D-08: The deception estate is declared as code, with separated duties

**Decided.** Decoys are declared as records and the placement is derived from the
declaration. Where plausibility is generated by reading the real estate, the work
is split across three roles that no single process holds together: a scanner that
reads the real estate and emits shape only, a planner that turns shape into
proposed declarations, and a builder that synthesises artefacts from approved
declarations. Gates sit between each.

**Reasoning.** Plausibility is defined against a moving target, so a hand-refreshed
estate rots at fleet scale. Deriving it from the real estate is the tractable
version and also the most dangerous automation in the program: the failure mode
is a real artefact reaching the decoy estate, placed by a process whose purpose is
to make things look real, into an environment built to be reachable. The
separation makes the no-real-artefact property checkable rather than promised,
because the only process with access to real content cannot place anything and
the only process that places has no source of real content.

**Reverses if** the estate is small enough to maintain by hand, in which case the
automation is unjustified risk.

---

### D-09: Source records carry physical provenance and licensing

**Decided.** Every source record names where the data actually is: asset and
location for internal sources, dataset and table, the fields that matter, the
access method. External sources name transport and endpoint with auth by secret
reference. Paid sources declare redistribution terms. All of it is gated.

**Reasoning.** Two questions decide whether a registry is real. When a scoping
answer depends on a source, can somebody else verify what it does and does not
cover? When the source dies, does the record say enough to replace it? Both need
the physical detail that usually stays in one person's head. Licensing is
separate and worse: redistribution terms surface in an audit rather than in a
build, and the failure is a restricted indicator reaching a partner.

**Reverses if** the fields go stale faster than they are useful, which would mean
they belong in the systems that own them and the record should reference rather
than copy.

---

## Analysis

### D-10: Campaigns are first-class machine-readable objects

**Decided.** A campaign is a record clustering observations across collection
tiers, citing the requirements it answers. CI fails on an observation with no
source tier, and reports how many tiers each campaign spans.

**Reasoning.** No single observation is a campaign. A vendor report is somebody
else's finding, a decoy hit is one alert, a peer sighting is a rumour. Clustered,
they are an actor that can be tracked, warned on, and shared. Making the tier
count visible is what keeps a single-source campaign from being presented with
the confidence of a corroborated one.

**Reverses if** clusters start being created to make coverage look better, which
is visible as campaigns that never gain a second tier.

---

### D-11: Internal cluster identity is the priority; external naming is a lookup

**Decided.** Internal cluster names are flat designators asserting only that
observations belong together. Correspondence with publicly named clusters is
recorded in a separate block that nothing else resolves through, and every entry
must state what knowing it would change.

**Reasoning.** Two different things travel under the word attribution. External
naming is worth what it changes, which is usually nothing, and it pays in exactly
two cases: completing the picture for containment, and forecasting what an actor
does next. Internal cluster identity pays continuously, because a cluster is the
unit that makes a detection generalise and the unit response acts on, arriving
with prior scoping and adjudication attached. An evocative internal name blurs
the two, gets repeated outside the context that qualified it, and is expensive to
withdraw.

**Reverses if** the organisation's obligations require alignment to public actor
names, in which case the mapping stops being advisory and needs its own
maintenance.

---

### D-12: Actor prioritisation uses classical machine learning, not a model call

**Decided.** Clustering and ranking over the observation set run as deterministic
classical algorithms. No frontier model in that path.

**Reasoning.** A clustering decision has to be reproducible, explainable after
the fact, and cheap across the whole observation set. Those are three properties
a model call does not have and classical methods do. This is the clearest
instance of the general rule: the question is which tool the step earns, and
sometimes the answer is neither judgement nor prose.

**Reverses if** the featurisation, rather than the clustering, becomes the
bottleneck. That is a language problem and a reasonable place for a model, with
the clustering still deterministic underneath.

---

## Dissemination

### D-13: Contribute closely; do not publish openly

**Decided.** The default is closed. Intelligence goes to named members under TLP
rather than to a public audience. Open publication stays available as a
deliberate exception: an already-burned indicator, a warning that has to reach
parties outside any sharing relationship, or a sector interest that plainly
outweighs the collection loss.

**Reasoning.** Publishing burns collection, invites retaliation against an
organisation holding assets these actors want, and carries a review path through
legal and customer notification. The argument for publishing anyway is that
contribution earns standing, but contribution and publication are different acts.
Delivered closely, the same intelligence is worth more to the recipient: it is
exclusive while still actionable and has not told the adversary which indicator
to rotate. The closure is then the offer rather than the limitation.

**Reverses if** the sector body needs public credibility that closed contribution
cannot build, which would be visible as members joining and not submitting.

---

### D-14: Sharing fills an unconvened layer and interoperates with the rest

**Decided.** Where a program starts or joins a sharing body, it covers the layer
nobody else is convening and interoperates with the bodies that already exist
rather than competing with them. In the example that is the compute and
infrastructure layer, beside existing model-layer and cross-sector efforts.

**Reasoning.** A threat conversation that is already convened does not need a
second host. A layer that is not convened is where a new node adds something,
and an organisation that sits between parties who compete with each other and
will not share directly holds the trust that makes the node possible.
Affiliating under an existing body dilutes exactly that asset.

**Reverses if** an existing body extends to the layer with credible governance,
in which case joining is cheaper and faster than founding.

---

## Engineering the function

### D-15: Agent-legible by default, through an API rather than MCP

**Decided.** Every foundation is a machine-readable record reachable through a
documented, authenticated, read-only, least-privilege HTTP API. Writes are signed
pull requests. The access surface is deliberately not an MCP server.

**Reasoning.** Agent-legibility cannot be retrofitted onto foundations built for
human eyes, so it is a constraint on the foundations. The API choice is narrower:
a broad tool-invocation surface reachable from agents that read hostile input
runs against the trust posture the rest of the program takes. This also becomes a
purchasing criterion, since a tool that traps its data in a console is a dead end
for an agentic program.

**Reverses if** the MCP security model matures to the point where the exposure is
comparable to an ordinary scoped API. This is a timing judgement, not a
principle.

---

### D-16: Automation is a ladder with gates and a short fixed boundary

**Decided.** Autonomy is earned one rung at a time. Each rung has an entry gate
that is evidence from the rung below, a documented rollback, and a defined
degraded mode. A short list of decisions does not climb: attribution claims,
anything leaving the organisation, retiring a requirement or a source,
insider-threat calls, and narrowing a collection filter.

**Reasoning.** The gates are what make speed compound. A rung entered on measured
evidence stays entered; a rung entered on optimism gets rolled back and takes the
credibility of the rungs beneath it, which is how a program ends up doing less
automation at two years than at six months. The boundary is short deliberately.
Each item is either irreversible or a business judgement, and neither property is
fixed by a better model. Everything absent from it is automatable and mostly
should be.

**Reverses if** a boundary item turns out to be reversible in practice, which
would be a reason to move that item rather than to abandon the boundary.

---

### D-17: Deterministic checks may block; probabilistic ones may only raise

**Decided.** Authority follows determinism. A reproducible, auditable check can
sit in the path and refuse. A model's judgement raises for review. Layering both
over the same content is normal, and placement follows the latency and cost
budget: cheap structural checks inline, model evaluation out of band.

**Reasoning.** A model has a failure distribution rather than a specification, so
it belongs where a wrong answer costs a false alarm instead of a silently dropped
item. That asymmetry is what makes it safe to run a model across content the hard
rules already cleared: it widens what gets noticed without widening what can be
lost. The inverse fails quietly, because a model with blocking authority is a
filter whose criteria nobody can state.

**Reverses if** a model check reaches a measured error rate that makes blocking
cheaper than the misses it prevents, which is an evidence question and should be
answered with evidence rather than confidence.

---

### D-18: Sanitisation is deterministic and sits before every model call

**Decided.** There is no path from a collector to a model that does not pass
through a static sanitisation stage. It strips, flags and stamps. It never
decides content is irrelevant and drops it.

**Reasoning.** This stage decides what a downstream model is allowed to see, over
content an adversary wrote for that purpose, so a model cannot hold the decision:
that moves the injection one step earlier onto a more privileged victim. The
constraint is on authority, not presence, and a model reading the same document
out of band and raising what the static rules found unremarkable is a good use of
one. Refusing to suppress on relevance is separate and equally load-bearing: a
suppression decision here would be an unreviewable filter.

**Reverses if** nothing. A change here is a change to the trust boundary and
needs its own decision rather than an amendment to this one.

---

### D-19: Assume a hosted frontier model and no custom security models

**Decided.** The program is designed against a hosted frontier model with no
fine-tuned models of its own. Structured outputs and strict tool use constrain
the response, and every return is validated deterministically before anything
downstream trusts it.

**Reasoning.** This is the conservative assumption: a function with its own
trained models has strictly more options than the discipline requires. What is
actually given up is narrow. There is no cheap high-volume classifier, which is
another reason the high-volume work is deterministic; no offline inference; and
behaviour is not owned across provider updates, which argues for pinned versions
and a held evaluation set. Standardising on one model family also narrows the
surface the security function has to characterise, which matters more at one
person than any marginal capability from a second provider.

**Reverses if** the volume of a specific classification step makes a small
fine-tuned model cheaper than the deterministic path it replaces.

---

### D-20: Judgement is retrieved rather than trained

**Decided.** Human-adjudicated triage decisions are stored as case records, and
the model's triage steps retrieve the nearest past decisions as precedent. Cases
are human-written only. A drift monitor baselines agent triage against the
human-reviewed record.

**Reasoning.** Without fine-tuning, judgement cannot be trained into weights, and
retrieval is the better substitute rather than a consolation. It grounds the
model in the organisation's own decisions instead of generic priors, and unlike a
weight it is auditable, because a disposition can name the cases that drove it.
Cases stay human-written because the moment an agent writes its own precedent the
learning loop amplifies its own errors.

**Reverses if** the case corpus grows large enough that retrieval quality becomes
the limiting factor, which is a retrieval engineering problem before it is an
argument for training.

---

## Measurement

### D-21: Measure decisions changed, not volume produced

**Decided.** The program reports which decisions changed because the function
exists. Throughput counts are diagnostic, not performance measures.

**Reasoning.** There is one way automation fails that looks like success:
volume rises without precision. More collected, more enriched, more reviewed, and
none of it more intelligence. Throughput is exactly the number that goes up when
a program automates the wrong thing, so the headline measure has to be per
finding rather than aggregate, and it has to name a decision on the other end.

**Reverses if** decision attribution becomes so contested that it costs more to
argue than to measure, in which case a proxy is needed, chosen openly.

---

## The artefact itself

### D-22: The records are a baseline to be diffed, not a plan to be re-typed

**Decided.** The program's design is carried as records with named gaps and
labelled assumptions rather than as prose. Contact with the real environment
resolves fields: a gap gets a source, a source's health changes, an assumption is
confirmed or replaced, a requirement retires. It does not restart the design.

**Reasoning.** Any program designed before its environment is seen is partly
wrong, and the useful question is not how to avoid that but how to make being
wrong cheap. Prose makes it expensive, because a wrong assumption is a paragraph
somebody has to find and rewrite, and the ones nobody finds quietly stay. Records
make it cheap and visible: every environment claim is a field, every unanswered
question is a named gap rather than a silence, and the delta between the design
and reality is a diff rather than a rereading.

That is also what makes the design usable by an agent rather than only by its
author. The trees are the input a planning agent needs on day one: what the
function is for, what it collects, which requirements have coverage and which do
not. The work that follows, sequenced into tracks and phases, is generated
against that baseline and re-generated as situational awareness lands, which is the same
argument the rest of the program makes about machine-readable foundations turned
on the program itself.

Two properties this imposes and the trees already carry. Every environment claim
is labelled as inference where it is inference, so a reader can tell what was
assumed from what was established. And every gap is named rather than left
absent, because an unnamed gap is indistinguishable from coverage and will not
appear in any diff.

**Reverses if** resolving a gap turns out to require restructuring the records
rather than filling a field. That would mean the schema encoded an assumption it
should have held as data, and the schema is what needs to change.

---

### D-23: The vendor connector estate is in scope, bounded to the threat model and the warning

**Decided.** The example organisation trusts a set of vendor connectors, for
carrier telematics and warehouse systems, so the connector layer is inside the
security perimeter rather than the vendors' problem. It enters the program as
records: CJ-06 for the connectors, ACTOR-07 for the vendor and supply-chain
access class, and PIR-06 for the requirement. The scope this function claims is
the threat model, the requirements, the external collection, the boundary
between vendor-held trust and the dispatch system jointly with detection, and
the warning. It does not claim integration engineering, vendor management, or an
availability outcome.

**Reasoning.** An earlier version of this program treated vendor connectors as a
contractual risk before a technical one: the vendor's controls were the vendor's
to describe. That was wrong, and it was wrong in the direction that costs the
most, because it moved the layer with the least telemetry out of scope. Each
connector holds standing trust granted once, during onboarding, then forgotten,
and a compromise at the vendor arrives with that trust already in hand. Treating
the connectors as in scope raises two things the contractual premise had
suppressed. An attacker who steals nothing from the platform can still deliver a
strategic result by manipulating or withholding the data the connectors carry. And the
layer that reaches the dispatch system without touching a platform server is the
layer with the least security telemetry anywhere in the estate.

The bounded scope is the load-bearing half. An intelligence function that claims
integration security outright will be correctly ignored by the engineers who own
the connectors, and it cannot deliver segmentation, monitoring or an accountable
owner. What it can deliver is that the highest-consequence unexamined row in the
profile stops being unexamined, and PIR-06 is deliberately written with two
essential elements carrying no source at all, because naming the gap is the
contribution available on day one.

**Reverses if** the connectors turn out to be so narrowly scoped that no single
vendor compromise is material to bookings or settlement. That would drop CJ-06
back toward a procurement concern and make PIR-06 a lower priority than the
credential and ledger work. It is an inference from the shape of the example
and it is the first thing to check.

---

### D-24: Insider risk starts in intelligence and is handed off, not kept

**Decided.** Intelligence owns the insider threat model, the external tradecraft,
the signal definitions, deception aimed at the insider path, and the warning. It
does not own adjudication, employment consequences, standing surveillance of
individuals, or manager-requested monitoring. Work on a named person arrives
through a named legal owner or it does not arrive. The end state is an
insider-risk function with HR and legal as principals, and intelligence hands the
capability over when there is an accountable owner and an agreed adjudication
process. Behavioural and sentiment scoring of employees is declined rather than
deferred.

**Reasoning.** Two of the seven actor classes in the profile (ACTOR-03 and
ACTOR-04) act through legitimate access, and both target assets whose loss is
unrecoverable, so the risk is named and the capability did not exist anywhere in
the program. An
intelligence function is a reasonable place to start it, because most of the
first year's work is external tradecraft, signal definition and briefing, all of
which are ordinary intelligence work. It is a bad place to finish, because
adjudicating colleagues is a different job with a different evidentiary standard,
and a function that does both will be worse at each.

The sequencing follows from the constraints rather than from preference. The
fraudulent carrier is an external actor running a published tradecraft against an
onboarding process, so it can be worked immediately without agreeing how colleagues
are monitored. The malicious insider cannot. Declining behavioural scoring is the
other half: it is what most insider products sell, it needs a mature legal and HR
structure to be defensible, and in a company that prizes autonomy it
would be read as evidence the autonomy was never real, which is the same
routed-around failure the profile already warns about for approval gates.

**Reverses if** the company charters an insider-risk function with HR and legal
as principals, at which point this decision has succeeded and intelligence
becomes an input rather than the starting owner.

---

## Open, not yet decided

Recorded because a decision log that only holds settled questions is a
retrospective justification rather than a working artefact.

| Question | What it blocks | What would settle it |
|---|---|---|
| Does dissemination get a record type? | Nothing states what was sent, to whom, under what TLP, against which requirement. The precision metric has no artefact behind its denominator, and the licensing terms in D-09 claim enforcement at an export boundary that does not exist | A worked case where the absence caused a real ambiguity, or the first member complaint about what was shared |
| Is the intelligence cycle the organising spine? | Processing and exploitation has no named home, and analysis sits inside collection. If the cycle is the spine, both are gaps; if it is not, the program should say so once and stop being read against it | A decision about who the function reports to and in whose vocabulary |
| Build or buy the intel store | The function has an intent layer that nothing sells and a data layer that nothing should be rebuilt for. Which side an existing platform already covers is unknown | Finding out what is actually running, which is week-one work |
| What tunes a decoy | The feedback loop from member response back to the deception estate is drawn and not recorded. No field on a decoy says what changed it or why | The first time a member submission actually changes a placement |
| How concentrated is a single vendor connector | The weighting of CJ-03 and CJ-06, and therefore whether PIR-06 outranks the credential and ledger requirements. D-23's reversal condition turns on it | Real traffic and settlement volume per connector, which is week-one work and needs nobody's permission |
| Who owns insider risk | D-24's handoff has no recipient. Until there is one, intelligence holds a capability it has argued it should not keep permanently | A charter agreed with HR and legal, and a named accountable owner |
