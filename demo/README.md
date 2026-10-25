# Demos

Two walkthroughs of the parts of the repository that are built and tested.

## Sanitiser

Intelligence work reads text written by the adversary. This is what that looks
like, and what a model in a CTI-as-code pipeline is allowed to see of it.

| File | What it is |
|---|---|
| [`articles/A04-poisoned-forum-post.html`](articles/A04-poisoned-forum-post.html) | A scraped forum post with two real claims and five planted prompt injections: a fake system turn, a fake end-of-document marker, a hidden paragraph, white-on-white text, and a base64 payload |
| [`transcripts/A04-sanitised-model-input.txt`](transcripts/A04-sanitised-model-input.txt) | The exact output of `src/ctiac/sanitiser.py` on that post. Generated, not hand-written |
| [`articles/A01-manifestkit-advisory.html`](articles/A01-manifestkit-advisory.html) | A clean advisory, which must pass through without flags |
| [`articles/A02-slow-manifest-report.html`](articles/A02-slow-manifest-report.html) | The fictional vendor report cited by `CAMP-01` |

Five injections go in. The two real claims come out, every instruction aimed at a
model is stripped, and the item is flagged so it routes to a person rather than
to the auto-dismiss the injection asked for.

`tests/test_sanitiser.py` holds the transcript to the code byte for byte. If the
sanitiser changes, the transcript is regenerated in the same commit, so the file a
reader sees can never quietly drift from what the code does.

## Pull request

[`pull-request/`](pull-request/) shows an agent proposing a change to the program,
the gates refusing it, and the fix. Every output in it was captured from a run.
