# CURRICULUM: turn the vault into a learning system

This module is one of the skill's two headline differentiators, and the loop it runs is
closed: the vault's gap analysis designs a curriculum, each topic is packaged into a
single self-contained tutor pack, a deliberately vault-blind tutor teaches from it, the
tutor's graded synthesis returns through the normal INGEST gate, and the next gap
analysis starts from what the grade revealed. Nothing enters the vault on the tutor's
word alone, and nothing gets studied that the vault cannot trace to a gap.

Optional module. Use it only when the owner wants to *learn* the subject rather than
store it. Skip it otherwise; it adds real maintenance cost.

## The model

The vault knows the whole knowledge graph and the owner's gaps, so it makes a better
curriculum designer than the owner does. The roles are:

- **You** are the curriculum designer. You decide what gets studied, in what order, and
  you build the pack for each topic.
- **A separate tutoring session** (a voice chat, or any conversational session that does
  not have vault access) is the tutor.
- **The owner** is the student.

This split matters, and the isolation is the point. The tutor works from one curated,
self-contained file and has no vault access, which is why it cannot leak answers:
everything it knows is material the owner is meant to learn, so it cannot short-circuit
a judgment question by quoting vault content the pack withheld. The same isolation keeps
it from wandering into unrelated material, and it lets the owner study hands-free, for
instance while walking. If the runtime has no speech, the tutor runs in text; the
isolation rule is unchanged. You own `ops/curriculum/`. Packs are generated artifacts,
not knowledge pages, so they live under ops/ and are not linted as wiki content.

## Files

```
ops/curriculum/
  curriculum.md              # the syllabus and status board
  tutor-pack-<topic>-v<N>.md # one self-contained pack per topic version: the tutor's
                             # instructions AND the teaching text in a single file
  runbook.md                 # owner-facing: how to run a session end to end
```

The pack template and the runbook are in `references/vault-templates.md`; use those
filenames exactly. The runbook belongs to the owner: if they hand you a revised version,
replace yours verbatim rather than merging.

**One file is the whole handoff.** The owner gives the pack to any conversational AI
with a file upload or a paste box (a voice product, a chat product, anything) and the
session runs. No custom instructions to install, no project to configure, no second
file for the tutor to lose track of. Everything the tutor needs to know, including how
to teach, who the student is, and what to teach, travels together.

## Maintaining curriculum.md

Every study topic gets: a two-line description, prerequisite ordering, a status, the
wiki pages that feed it, and, once graded, its next revisit date.

Status is one of `not-started`, `in-progress`, `needs-revisit`, `done`.

A topic is `done` only when a session synthesis shows the owner answered the
judgment-level questions well. A session happening is not the same as a topic being
learned, and recording it that way makes the whole board meaningless.

Treat the curriculum as cheap to revise. After each synthesis, adjust the ordering, split
or merge topics, and log why in `wiki/log.md`. When the owner asks for the next pack,
check revisit dates first: a `done` topic past its date moves to `needs-revisit` and
takes priority over new material.

## Generating a tutor pack

Triggered by the owner asking for a topic, by you advancing them to the next one, or
by a revisit: a repeat grade and a due revisit date both call for a new version.
A pack has five parts, in this order, and the template in
`references/vault-templates.md` is the contract for each.

**Part 1: tutor instructions.** How to run the session: the readiness check, voice
rules, the teaching method, and the synthesis format. Copied from the template with the
subject filled in.

**Part 2: the student.** Built fresh for each pack from the owner section of the
vault's `AGENTS.md` plus what earlier syntheses revealed: what they know well, what
they keep getting wrong, and the traps specific to them. The most valuable trap to name
is the one where general theory gets confused with facts specific to the owner's actual
situation.

**Part 3: curriculum position.** Where this topic sits in the syllabus, which topics
are already done, and two or three recall questions from that older material, each
with its expected answer, so the tutor can grade a cold response without access to
anything beyond the pack. These are the only questions the tutor may open with,
because they cover material the owner has already worked.

**Part 4: the teaching text.** Build it by walking the knowledge graph: start from the
topic's pages and follow wikilinks outward. Grabbing pages whose titles match the topic
misses exactly the connective material that makes a topic click.

Write it for listening, since it will be spoken or read aloud:

1. Plain-language overview first.
2. Key points.
3. Tensions and disagreements between sources. This is where understanding forms, so
   do not smooth it over.
4. Open questions.

Conventions: inline prose citations ("per the 2025 annual report"), no frontmatter
machinery, no wikilinks, roughly 3,000 to 5,000 words.

**Part 5: discussion questions.** Ten, ordered from recall to judgment. The tutor works
through these after teaching, never before.

Save the assembled pack as `ops/curriculum/tutor-pack-<topic>-v<N>.md`. Every
regeneration bumps `<N>`, never overwrites: a deepened teaching text, a revisit, and
a refreshed student profile are all new versions, so the pack a synthesis refers to
stays on disk.

If a synthesis shows a pack's teaching text was too thin, produce v2 addressing the gap
rather than pointing the owner at raw sources. The point of the system is that they
should not have to.

## Teach first, then retrieve

The single most important rule in the pack, learned the hard way: **the student has not
read the sources, and usually has not read the wiki either. The pack is their first
exposure.** A tutor that opens by quizzing the student on material they have never seen
is testing reading they never did, and the session dies in the first two minutes.

So the pack instructs the tutor to run two different modes:

- **New material (this topic): teach first.** Present each concept in plain speech,
  then have the student play it back, then grade the playback and correct it. Retrieval
  still does the work of learning; it comes after exposure, not instead of it. A
  revisited topic runs the same way, and Part 3 tells the tutor why it is back: a
  grade that said repeat, or a scheduled return come due.
- **Prior material (topics the curriculum marks `done`): retrieval first.** Open the session with the
  recall questions from Part 3, cold. That material has been taught and graded already,
  so testing it cold is exactly right, and it doubles as spaced review.

## Ingesting a session synthesis

The owner drops the tutor's synthesis into `raw/inbox/` named
`voice-synthesis-<topic>-<YYYY-MM-DD>.md` with `type: voice-synthesis` in the
frontmatter. It
is a source like any other and goes through the normal INGEST gate: built into the vault
by one pass, independently validated by a pass that did not build it, looped to a clean
round. When it arrives:

1. Read it. Mark every claim the owner made `hypothesis` until verified against the
   wiki. It is a record of what the owner said, not of what is true.
2. Correct anything they got wrong. If the wiki itself cannot settle it, log it to
   `wiki/open-loops.md` and consider whether ACQUIRE should propose a source. The same
   applies to questions raised in session that the tutor could not answer: the tutor is
   deliberately vault-blind, so its unanswerables are the vault's follow-up list, and
   the synthesis must carry them back.
3. Update the topic's status in `curriculum.md`: `done` on an advance
   recommendation, `needs-revisit` on repeat or deepen.
4. Decide: advance to the next topic, repeat this one, or deepen the pack's teaching
   text.
5. Schedule the revisit. No fixed interval: set the date from how the session actually
   went. A topic the owner handled at judgment level comes back later than one they
   recited. Record the date in `curriculum.md` when you grade.
6. Never modify `raw/inbox/`; the owner's originals are read-only.
7. Log the action in `wiki/log.md`.

## Grade honestly

No flattery. An inflated assessment corrupts the whole system, because every scheduling
decision downstream trusts it. If the syntheses show the owner is skimming rather than
learning, say so plainly. This is the same principle as the validator refusing to sign
off on thin coverage: the system is only useful if its verdicts mean something.
