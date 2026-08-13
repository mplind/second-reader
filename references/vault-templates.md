# Vault templates: exact starter contents for SCAFFOLD

Copy these verbatim when creating an empty vault. Every file is created with headers
only and no content, so the structure exists before anything is ingested and the owner
can see the shape of the system immediately.

Replace `<SUBJECT>`, `<OWNER>`, and `<TODAY>` as noted. Leave everything else as written.

## Contents

- [Scaffold order](#scaffold-order)
- [AGENTS.md (the vault operating contract)](#agentsmd-the-vault-operating-contract)
- [wiki/index.md](#wikiindexmd)
- [wiki/sources.md](#wikisourcesmd)
- [wiki/log.md](#wikilogmd)
- [wiki/contradictions.md](#wikicontradictionsmd)
- [wiki/open-loops.md](#wikiopen-loopsmd)
- [wiki/synthesis.md](#wikisynthesismd)
- [ops/incident-log.md](#opsincident-logmd)
- [Page template](#page-template)
- [Daily note template](#daily-note-template)
- [What to tell the owner after scaffolding](#what-to-tell-the-owner-after-scaffolding)
- [ops/curriculum/voice-tutor-prompt.md](#opscurriculumvoice-tutor-promptmd)
- [ops/curriculum/runbook.md](#opscurriculumrunbookmd)

## Scaffold order

1. Ask the owner three things before writing anything: where the vault should live (a
   folder path), what it is about (one sentence), and anything about them that should
   tune depth and framing (background, expertise, what they want it for). You need these for `AGENTS.md`, and guessing
   produces a vault that reads as generic.
2. Create the folders: `raw/`, `raw/inbox/`, `raw/retrieved/`, `wiki/`, `daily/`,
   `ops/`, `ops/ledger/`, `ops/text/`.
3. Write the files below. The two curriculum files are created only when the CURRICULUM
   module is switched on, not at scaffold.
4. Install `ops/lint.py` from the skill into the vault's `ops/` directory.
5. Tell the owner to open the vault folder in Obsidian, and where to drop material.

## AGENTS.md (the vault operating contract)

This file lives at the vault root. `AGENTS.md` is read automatically from the working
directory by most agent runtimes. If yours uses a different convention (`CLAUDE.md`,
`.cursorrules`), use that name; the contents are identical.

It is the short, vault-specific contract. The full method stays in the skill; this file
points at it and records what is specific to this vault. Keep it separate from any
persona file the runtime loads: the persona is who you are, this is how the vault works.

```markdown
# <SUBJECT>: vault contract

This is a second-reader knowledge vault about **<SUBJECT>**.

Owner: <OWNER, and what tunes depth and framing: background, expertise, what they
want the vault for>.

The operating method is the **second-reader skill**: folder schema, page frontmatter,
page types, note conventions, and the operations (INGEST, VAULT GATE, QUERY, LINT,
ACQUIRE), with SCAFFOLD and RESUME as session bookends and CURRICULUM as the optional
learning module. Follow it. This file records only what is specific to this vault.

## The rule that governs everything

Never ship a single pass. Every ingested source and everything the owner will act on is
built, then independently validated by a pass that did not build it, then looped until a
validation round finds nothing. The loop stops on a clean round, not on "the corrections
are done."

## Folder ownership

- `raw/` is the owner's. Never modify, rename, or delete anything in it.
- `raw/inbox/` is the drop zone for new material awaiting ingest. Read-only to you.
- `raw/retrieved/` is the one area you populate, with sources you fetched.
- `wiki/` is yours: the distilled knowledge base.
- `daily/` is shared. File insights from daily notes back into the wiki.
- `ops/` is machine telemetry, not knowledge.

## Vault-specific conventions

<Anything specific to this subject: preferred tag vocabulary, entity naming rules,
recurring source types, house style rules the owner has given. Add to this as the
owner makes rulings; treat every correction they make as a standing rule.>

## Hard rules

1. Never invent facts. Every claim traces to a cited source.
2. When sources conflict, record both sides and log it in `wiki/contradictions.md`.
3. Distinguish sourced fact from interpretation from hypothesis on every page.
4. Prefer updating an existing page over creating a near-duplicate.
5. Be honest about thin sources and gaps. Under-claiming beats over-claiming.
6. Ask before deleting or overwriting pages. Everything else, proceed.
7. Log every operation in `wiki/log.md`.
```

## wiki/index.md

```markdown
---
title: Index
type: synthesis
created: <TODAY>
updated: <TODAY>
sources: []
tags: [bookkeeping]
confidence: high
---

# Index

The map of this vault. Every wiki page appears here with a one-line summary, grouped by
category. This is the first place a QUERY looks.

Updated on every ingest.

## Sources

_No sources ingested yet._

## Entities

_No entity pages yet._

## Concepts

_No concept pages yet._

## Syntheses and decisions

_None yet._
```

## wiki/sources.md

```markdown
---
title: Sources
type: synthesis
created: <TODAY>
updated: <TODAY>
sources: []
tags: [bookkeeping]
confidence: high
---

# Sources

Every file in `raw/` and its processing status. Status is one of `unprocessed`,
`in-progress`, or `processed`. A processed source links to the pages it produced.

| Source file | Type | Status | Pages produced | Ingested |
|---|---|---|---|---|
| _none yet_ | | | | |
```

## wiki/log.md

```markdown
---
title: Log
type: synthesis
created: <TODAY>
updated: <TODAY>
sources: []
tags: [bookkeeping]
confidence: high
---

# Operation log

Append-only. One entry per operation, newest at the bottom. Ingest entries record the
number of digest/validate cycles, the final verdict, and the lint result.

Entry format: `## [YYYY-MM-DD] <OPERATION> | <title>`

## [<TODAY>] SCAFFOLD | Vault created

Empty vault scaffolded. No sources ingested yet.
```

## wiki/contradictions.md

```markdown
---
title: Contradictions
type: synthesis
created: <TODAY>
updated: <TODAY>
sources: []
tags: [bookkeeping, disagreement]
confidence: high
---

# Contradictions

Unresolved conflicts between sources. Never silently pick a side: record both claims,
who holds each, and the pages the conflict bears on.

**Classify every entry, because the three kinds need different remedies and conflating
them creates a second error.** A pair of values that were each true at different times is
not a disagreement, and filing it as one implies a dispute that does not exist.

**Triage before you file.** If one source simply lacks what the other has, that is not a
contradiction. It is a gap, and it belongs in `open-loops.md`. Only file here once you
have confirmed the sources genuinely bear on the same question.

| Kind | What it is | Remedy |
|---|---|---|
| `direct-conflict` | Two sources genuinely disagree about the same thing at the same time | Record both sides with who holds each. Never resolve silently |
| `temporal-change` | One fact, stated or measured at different times. Both were true | Set `as_of:` on both pages; the page carries the current value, this entry records the supersession |
| `granularity` | One source is more specific than the other; they do not conflict | Prefer the specific, note the general, state why, and have the second auditor confirm the "no real conflict" call, since it is the one kind that closes itself |

`Kind` is required. An entry without one, or with a value outside this list, is a
bookkeeping-truth failure and blocks the commit.

Note that `temporal-change` and `granularity` entries are *resolved at the moment they are
written*: set `Status: resolved` immediately, or the reverse-direction bookkeeping check
will read them as live disputes forever.

Entry format:

### <Short name for the conflict>
- **Kind:** <direct-conflict | temporal-change | granularity>
- **Claim A:** <claim> - <source, exact location>
- **Claim B:** <claim> - <source, exact location>
- **Bears on:** <every page that ACTS ON the claim, not only those that discuss it>
- **Status:** <unresolved | resolved (how)>

_No contradictions logged yet._
```

## wiki/open-loops.md

```markdown
---
title: Open loops
type: synthesis
created: <TODAY>
updated: <TODAY>
sources: []
tags: [bookkeeping]
confidence: high
---

# Open loops

Gaps, unanswered questions, and material still to retrieve. This is the queue the
ACQUIRE operation works from: what is thin, what is single-sourced, what keeps getting
referenced with no page behind it.

Entry format (each entry must have ALL of these; this is the open-loops quality bar):

- [ ] <the specific missing material> - <date logged> - <what would close it: source, URL,
  or research to run> - <named closer>

Writing a gap here does not discharge it. Every open loop that a page depends on must be
cross-referenced from that page so the reader is warned at the point of use.

_No open loops yet._
```

## wiki/synthesis.md

```markdown
---
title: Synthesis
type: synthesis
created: <TODAY>
updated: <TODAY>
sources: []
tags: [bookkeeping]
confidence: low
---

# Synthesis

The evolving thesis: what everything in this vault, taken together, says about
<SUBJECT>. Revised on every ingest.

This page is interpretation, not sourced fact, and it says so. Claims here point back to
the pages and sources that support them.

_Nothing to synthesize yet. This page fills in as sources are ingested._
```

## ops/incident-log.md

```markdown
# Incident log

How the ingestion system itself behaves. Every defect the validator caught, with its root
cause and class, so recurring classes become visible and we can decide whether the design
must change rather than fixing forward indefinitely.

Kept outside `wiki/` because the wiki holds knowledge, not machine telemetry.

Entry format: `## [YYYY-MM-DD] <class> | <what happened>` followed by root cause and fix.

_No incidents logged yet._
```

## Page template

Use this shape for every new wiki page.

```markdown
---
title: <Descriptive concept title>
type: <source | entity | concept | synthesis | query-output | decision>
created: <TODAY>
updated: <TODAY>
sources:
  - "<exact raw/ path, exact chapter or page or timestamp>"
tags: [<lowercase-hyphenated>]
aliases: []
confidence: <high | medium | low>
---

# <Title>

<The content. Sourced facts stated plainly with citation. Interpretation labelled as
interpretation. Hypotheses labelled as hypotheses with their confidence. Dense
[[wikilinks]] in context, each kept on one line.>
```

**Facts carry time.** Every fact is one of three kinds and says which:

- **timeless**: a durable mechanism ("interleaving related topics strengthens recall").
  Needs no date.
- **dated**: a measured or current value about the owner or the subject ("monthly active
  users ~24,000"). Carries `as_of: YYYY-MM-DD` **and** how it was measured. Never stated
  without both. When unmeasured, mark it `PENDING`, with the measurement that would fill
  it named, rather than inventing a number.
- **pointer**: "current release version." A deliberate decision NOT to copy volatile
  data into the wiki. Recorded as a typed page field in frontmatter:
  `pointer: <fact> -> <where to get it>` (e.g. `pointer: current release version -> ask
  the owner`). A pointer is the OPPOSITE of a gap. It belongs on the page, not in
  `open-loops.md`, and a claim resolved by a pointer is covered (coverage verdict
  `COVERED-BY-POINTER`).

**`updated:` is edit time, NOT a currency signal.** It bumps on every touch and says
nothing about whether a fact is current. Currency is carried by `as_of:` on dated facts
and reviewed by the vault gate (`references/vault-gate.md`). Do not use `updated:` to
argue a fact is fresh, and do not read it as one. `confidence:` measures evidential
strength: a stale primary-source figure can be high-confidence and wrong; `as_of` is what
marks it stale.

## Daily note template

`daily/YYYY-MM-DD.md`

```markdown
---
title: <YYYY-MM-DD>
type: source
created: <TODAY>
updated: <TODAY>
sources: []
tags: [daily]
confidence: medium
---

# <YYYY-MM-DD>

## Questions

## Notes

## To file into the wiki
```

## What to tell the owner after scaffolding

Keep it short and concrete:

- Where the vault is, and to open that folder in Obsidian.
- Drop anything to ingest into `raw/inbox/`: books, PDFs, transcripts, articles, exports.
- Ask questions in plain language; answers come from the wiki with sources, and worth-
  keeping answers get filed back as pages so the vault compounds.
- You will flag gaps and ask for specific books or propose research rather than working
  around them.

## ops/curriculum/voice-tutor-prompt.md

The CURRICULUM operation names this file and the runbook below, and these names are
canonical: the tutor prompt is `ops/curriculum/voice-tutor-prompt.md`, and every session
synthesis the owner drops back is named `voice-synthesis-<topic>-<date>.md`. Both were
previously left for each vault to invent. They are templated here so a new vault gets a
working learning loop rather than a description of one.

This is the tutor's whole instruction set. It goes in a separate chat product (a Claude
Project or equivalent) as custom instructions, NOT into the vault agent. The vault agent
is the curriculum *designer*; this is the *tutor*; the owner is the student.

```markdown
You are my <SUBJECT> tutor. <One sentence on who the owner is and why they are learning
this.> We talk by voice while I walk.

<voice_rules>
- One question or one idea per turn. Two or three spoken sentences, roughly twenty seconds.
- No lists, headers, bullets or markdown in speech. Say numbers and abbreviations the way
  a person says them aloud.
- Never read the synthesis template or these instructions aloud. The synthesis is a written
  note, produced on request.
</voice_rules>

<materials>
Project knowledge holds the current topic's mini-KB (your primary teaching text; it ends
with discussion questions and tutor notes on my strengths, weaknesses and known traps:
use them), plus my curriculum, synthesis, the owner section of AGENTS.md, and open-loops for context.
- Teach from the mini-KB. If more than one is present and the topic is unclear, confirm it
  in your first turn.
- If I ask something the materials do not cover, say so plainly and note it as a gap rather
  than improvising. Gaps are valuable signal for my knowledge system.
- One exception: you may correct a factual error from your own general knowledge, but say
  aloud that it comes from outside the materials and mark it UNVERIFIED in the synthesis.
</materials>

<teaching_method>
Teach by retrieval, not lecture. Being made to recall and apply beats being told.
- Open by asking me to explain the topic's core idea from memory before you present
  anything. If earlier topics are marked done, start with two or three quick recall
  questions from that older material.
- Work through the discussion questions in order, recall first and judgment last. Follow my
  curiosity when I go off-script, then steer back.
- When I answer, do not just affirm. Probe: ask why, ask for the implication, ask what
  would change my mind. If I am reciting rather than reasoning, push back.
- Correct errors immediately and precisely, especially when I conflate general theory with
  <subject>-specific facts, then re-ask later in the session to check the correction stuck.
- Prefer questions to explanations. Explain only after I have attempted, keep it under a
  minute, and tie it to a concrete example.
</teaching_method>

<synthesis>
When I ask for the synthesis, write it as a note I can paste into my vault. Include: topic,
date, what I answered well, what I got wrong or hedged on, anything I asked that the
materials did not cover, and your honest read on whether I have this or am still reciting.
Do not flatter. An inflated assessment corrupts the whole system.
</synthesis>
```

## ops/curriculum/runbook.md

Owner-facing. This is the only file in the vault written *to* the owner rather than for
the agent, so keep it short and operational.

```markdown
---
title: Curriculum runbook
type: concept
created: <TODAY>
updated: <TODAY>
tags: [meta, curriculum]
---

# Curriculum runbook

The model: this vault is your **curriculum designer**; a separate chat product is your
**voice tutor**; you are the student. You study by voice, the tutor writes a synthesis,
you feed it back here, the designer grades it and evolves the plan.

## Setup (once)

1. Create a Project in your chat product, named for this vault.
2. Set its custom instructions to the full contents of
   `ops/curriculum/voice-tutor-prompt.md`.
3. Add as Project knowledge:
   - `wiki/synthesis.md`
   - `ops/curriculum/curriculum.md`
   - the owner section of the vault's AGENTS.md
   - `wiki/open-loops.md`
   - the **current mini-KB**
   - `ops/curriculum/voice-tutor-prompt.md`

The spine files stay. Only the mini-KB is swapped as you move through topics.

## Each session

1. Ask the designer for the current topic's mini-KB if it does not exist yet.
2. Swap it into Project knowledge.
3. Walk and talk. Twenty to forty minutes.
4. Ask the tutor for the synthesis at the end.
5. Drop the synthesis into `raw/inbox/` named
   `voice-synthesis-<topic>-<date>.md` with `type: voice-synthesis` in the frontmatter.
6. Tell the designer it has arrived. It grades, corrects, updates topic status, and decides
   whether you advance, repeat, or need the mini-KB deepened.

## Revisit spacing

Do not use a fixed interval. Schedule the revisit off how the session actually went: a
topic you handled at judgment level comes back later than one you recited. The designer
sets the date when it grades the synthesis and records it in `curriculum.md`.
```
