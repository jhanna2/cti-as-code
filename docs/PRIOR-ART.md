# Prior art, and where it stops

CTI as code borrows from several existing practices. This page credits them and
says where each one stops, so the new part is stated precisely rather than
claimed broadly.

Surveyed in September 2026. If you know of work that does what this repository
does, open an issue. I would rather cite it than be wrong about it.

## What exists

| Practice | What it versions | Where it stops |
|---|---|---|
| **Threat intelligence platforms** (commercial and open source) | Collection, processing and increasingly analysis: ingestion, parsing, enrichment, model-assisted extraction, at scale | The data and the analysis. Program management (requirements, coverage, gaps, what automation may do) stays outside them, in prose and spreadsheets |
| **Detection as code** (in use from about 2019; Sigma, vendor pipelines) | The detection rule, with tests and CI | The rule. Nothing says which intelligence requirement it serves or what it misses. Here detection is a consumer, and a candidate must name both |
| **Threat modeling as code** ([OWASP pytm](https://github.com/OWASP/pytm), Threagile) | A model of a system: assets, boundaries, data flows | The system under analysis. The threat profile here plays that role and is only the first of eight trees |
| **Infrastructure-as-code deception** ([Tracebit](https://ai.tracebit.com/how-do-i-deploy-deception-technology-canaries-and-honeytokens-across-my-aws-environment) and others) | Decoy resources, deployed with Terraform alongside real ones | Deployment. A decoy here is a collection source with a requirement above it, a plausibility claim and a refresh cadence the build checks |
| **STIX / TAXII, MISP, OpenCTI** | Threat objects: indicators, actors, relationships, sightings | The threat. None describes why the program collects, for whom, or where it is blind. These records can cite STIX objects; they do not replace them |
| **PIR methodology** ([Red Hat's PIR guide](https://github.com/redhat-infosec/priority-intelligence-requirements-dev), vendor guidance, the intelligence-cycle literature) | A process for writing good requirements, in prose and spreadsheets | Nothing can fail. A requirement that loses its source or its consumer goes stale silently |
| **PIR tracking inside a platform** ([MISP feature request #8658](https://github.com/MISP/MISP/issues/8658), 2022, open) | Proposes scoring ingested events against defined PIRs | Inside one tool's UI rather than as versioned records, and without gates on the requirements themselves |

## What is new here

As far as I have found, nobody has treated the **intelligence program itself** as
version-controlled records with CI gates. Specifically:

1. **Requirements as records that can fail.** A PIR names its decision and
   consumer, each essential element resolves to a source or names a gap, and the
   build breaks when either is missing.
2. **Named gaps as a first-class, gated output.** An empty source list fails; a
   named gap passes. The collection plan's blind spots are a query
   (`ctiac gaps`), not an omission.
3. **One traceable chain across the program.** Decision to requirement to
   source; decoy, detection candidate and campaign each back up to a
   requirement; all of it walked by one command.
4. **Mandatory self-declared blind spots** on detection candidates, agents and
   external-name correspondences, enforced rather than encouraged.
5. **Campaign corroboration made visible.** Observations carry their collection
   tier, and single-tier campaigns are flagged as weakly corroborated.
6. **Agents as gated records in an intelligence program**, with the rule that
   anything reading adversary-authored text cannot run autonomously enforced as
   a CI check.
7. **Human-only adjudication records** as the precedent store for retrieval and
   the baseline for drift, with the human-only rule enforced.

None of these components is exotic on its own. The contribution is the object
being versioned, and the gates that make the program's honesty about itself
checkable by someone who was not there.
