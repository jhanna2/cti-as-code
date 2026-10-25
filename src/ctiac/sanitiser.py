"""The sanitisation stage: the deterministic scrub before every model call.

There is no path from a scraper to a model that does not pass through here, and the
governing rule is that the sanitiser is deterministic. This stage decides what a
downstream model is allowed to see, over content an adversary wrote for that purpose,
so a model cannot hold the decision: it moves the injection one step earlier onto a
more privileged victim. Every rule below is a static transform.

That constrains authority, not presence. A model reading the same document out of band
and raising what these rules found unremarkable is a good use of one. It just does not
get a say in what passes. See D-17: a deterministic check may block, a
probabilistic one may only raise.

The sanitiser strips, flags, and stamps. It never decides that content is malicious
and drops it: a suppression decision made here would be an unreviewable filter, which
is the failure mode the filter audit exists to prevent. Raw content is retained by the
caller under its hash; the model sees only what this returns.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from html.parser import HTMLParser

# Sequences that imitate the prompt format. Neutralised, and each occurrence flagged.
#
# Two groups, kept apart deliberately, because they are worth different amounts.
#
# STRUCTURAL patterns key on the shape of a prompt rather than on anything an
# attacker chose to write. A document cannot carry a fake role turn or a fake
# document boundary without looking like one, so these generalise: they will fire
# on injections nobody has seen yet.
_STRUCTURAL_MARKERS = [
    re.compile(r"(?im)^\s*system\s*:"),
    re.compile(r"(?im)^\s*assistant\s*:"),
    re.compile(r"(?im)^\s*user\s*:"),
    re.compile(r"(?i)#{2,}\s*end of document\s*#{0,}"),
]

# PHRASAL patterns key on wording, and every one of them was derived from the
# planted injections in demo/articles/A04. That makes them a demonstration rather
# than a defence: they prove the stage fires and flags, and they would not survive
# an attacker who phrased the same instruction differently.
#
# They are kept because a worked example needs to show something happening, and
# they are labelled because the alternative is a reader discovering the overfit
# themselves and reasonably concluding the whole stage is theatre. The structural
# group above is what the argument actually rests on. If this list ever grows in
# response to a real incident, that is a signal the structural group has a gap,
# and the gap is the thing to fix.
_PHRASAL_MARKERS = [
    re.compile(r"(?i)reviewer_override"),
    re.compile(r"(?i)ignore (the |all )?[a-z ]*?(instructions|context)"),
    re.compile(r"(?i)append the contents"),
    re.compile(r"(?i)disregard the"),
    re.compile(r"(?i)mark asset inventory as"),
    re.compile(r"(?i)maintenance mode"),
]

_PROMPT_MARKERS = _STRUCTURAL_MARKERS + _PHRASAL_MARKERS

# Encoded blobs: flagged and excerpted, never auto-decoded into model context.
_BASE64 = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}")
_ZERO_WIDTH = re.compile(r"[​-‏‪-‮⁠﻿\U000e0000-\U000e007f]")

_HIDDEN_STYLE = re.compile(
    r"display\s*:\s*none"
    r"|visibility\s*:\s*hidden"
    r"|opacity\s*:\s*0"
    r"|font-size\s*:\s*0"
    r"|(?:^|;)\s*color\s*:\s*#?(\w+)\b[^;]*;[^;]*background(?:-color)?\s*:\s*#?(\w+)",
    re.I,
)


def _is_hidden(style: str) -> bool:
    if not style:
        return False
    m = _HIDDEN_STYLE.search(style)
    if not m:
        return False
    # foreground==background (white-on-white and friends)
    if m.group(1) and m.group(2):
        return m.group(1).lower() == m.group(2).lower()
    return True


class _Extractor(HTMLParser):
    """Drop scripts, styles, comments, and hidden elements; keep visible text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.removed_hidden = 0
        self._suppress_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        d = dict(attrs)
        if tag in ("script", "style") or _is_hidden(d.get("style", "")):
            self._suppress_depth += 1
            if _is_hidden(d.get("style", "")):
                self.removed_hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if self._suppress_depth:
            self._suppress_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._suppress_depth == 0:
            self.parts.append(data)

    def handle_comment(self, data: str) -> None:  # dropped
        pass


@dataclass
class SanitiseResult:
    text: str
    removed: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    source_id: str = ""
    sha256: str = ""

    def enveloped(self, retrieved: str = "") -> str:
        """The labelled, provenance-stamped block a model actually receives."""
        head = f"<<<DOCUMENT source_id={self.source_id} sha256={self.sha256[:8]} retrieved={retrieved}>>>"
        notes = "\n".join(f"[SANITISER: {f}]" for f in self.flags)
        body = self.text if not notes else f"{self.text}\n\n{notes}"
        return f"{head}\n{body}\n<<<END DOCUMENT>>>"


def sanitise(raw: str, source_id: str = "unknown", cap_bytes: int = 32_000) -> SanitiseResult:
    sha = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()
    res = SanitiseResult(text="", source_id=source_id, sha256=sha)

    # 1. Extract visible text; drop scripts, styles, comments, hidden elements.
    ex = _Extractor()
    ex.feed(raw)
    text = "".join(ex.parts)
    if ex.removed_hidden:
        res.removed.append(f"{ex.removed_hidden} hidden element(s)")
        res.flags.append(f"{ex.removed_hidden} hidden element(s) removed")

    # 2. Normalise unicode; strip zero-width and bidi controls.
    text = unicodedata.normalize("NFKC", text)
    if _ZERO_WIDTH.search(text):
        res.flags.append("zero-width or bidi control characters stripped")
        text = _ZERO_WIDTH.sub("", text)

    # 3. Detect encoded blobs. Flag and excerpt; never auto-decode.
    b64 = _BASE64.findall(text)
    for blob in b64:
        res.flags.append(f"base64 blob detected, NOT decoded ({len(blob)} chars, excerpt {blob[:12]}...)")
        text = text.replace(blob, "[base64 blob removed, retained in raw for review]")

    # 4. Drop lines that masquerade as prompt structure. A line carrying a fake
    #    role turn or a document-boundary marker is dropped wholesale, not just at
    #    the marker: the whole injected instruction goes, flagged, with the raw
    #    retained for review. This neutralises an attack signature; it is not the
    #    semantic suppression D-18 forbids, which is a judgement about
    #    relevance rather than a structural transform.
    dropped = 0
    kept_lines: list[str] = []
    for line in text.splitlines():
        if any(pat.search(line) for pat in _PROMPT_MARKERS):
            dropped += 1
            continue
        kept_lines.append(line)
    text = "\n".join(kept_lines)
    if dropped:
        res.flags.append(f"{dropped} prompt-structure line(s) dropped")

    # 5. Cap length. Oversized documents push instructions past a reviewer.
    encoded = text.encode("utf-8")
    if len(encoded) > cap_bytes:
        text = encoded[:cap_bytes].decode("utf-8", "ignore")
        res.flags.append(f"truncated to {cap_bytes} bytes")

    # Collapse the whitespace the extraction leaves behind.
    res.text = re.sub(r"\n{3,}", "\n\n", "\n".join(l.strip() for l in text.splitlines())).strip()
    return res
