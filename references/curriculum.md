# CURRICULUM: turn the vault into a learning system

This module is one of the skill's two headline differentiators, and the loop it runs is
closed: the vault's gap analysis designs a curriculum, the curriculum produces
self-contained study documents, a deliberately vault-blind tutor teaches from them, the
tutor's graded synthesis returns through the normal INGEST gate, and the next gap
analysis starts from what the grade revealed. Nothing enters the vault on the tutor's
word alone, and nothing gets studied that the vault cannot trace to a gap.

Optional module. Use it only when the owner wants to *learn* the subject rather than
just store it. Skip it otherwise; it adds real maintenance cost.

## The model

The vault knows the whole knowledge graph and the owner's gaps, so it makes a better
curriculum designer than the owner does. The roles are:

- **You** are the curriculum designer. You decide what gets studied and in what order.
- **A separate tutoring session** (a voice chat, or any conversational session that does
  not have vault access) is the tutor.
- **The owner** is the student.

This split matters, and the isolation is the point. The tutor works from a curated,
self-contained study document and has no vault access, which is why it cannot leak
answers: everything it knows is material the owner is meant to learn, so it cannot
short-circuit a judgment question by quoting vault content the study document withheld.
The same isolation keeps it from wandering into unrelated material, and it lets the owner
study hands-free, for instance while walking. If the runtime has no speech, the tutor
runs in text; the isolation rule is unchanged. You own `ops/curriculum/`. Study documents are generated artifacts, not knowledge pages, so they live under ops/ and are not linted as wiki content.

## Files

```
ops/curriculum/
  curriculum.md              # the syllabus and status board
  kb-<topic>-v<N>.md         # self-contained study documents (mini-KBs), one per topic version
  voice-tutor-prompt.md      # the tutor's whole instruction set, installed as the
                             # tutoring product's custom instructions
  runbook.md                 # owner-facing: how to run a session end to end
```

`voice-tutor-prompt.md` and `runbook.md` are templated in
`references/vault-templates.md`; use those filenames exactly. Both belong to the owner.
If they hand you a revised version, replace yours verbatim rather than merging.

## Maintaining curriculum.md

Every study topic gets: a two-line description, prerequisite ordering, a status, the
wiki pages that feed it, and, once graded, its next revisit date.

Status is one of `not-started`, `in-progress`, `needs-revisit`, `done`.

A topic is `done` only when a session synthesis shows the owner answered the
judgment-level questions well. A session happening is not the same as a topic being
learned, and recording it that way makes the whole board meaningless.

Treat the curriculum as cheap to revise. After each synthesis, adjust the ordering, split
or merge topics, and log why in `wiki/log.md`.

## Generating a study document (mini-KB)

Triggered by the owner asking for a topic, or by you advancing them to the next one.

**Build it by walking the knowledge graph.** Start from the topic's pages and follow
wikilinks outward. Grabbing pages whose titles match the topic misses exactly the
connective material that makes a topic click.

**Write it for listening**, since it will be spoken or read aloud:

1. Plain-language overview first.
2. Key points.
3. Tensions and disagreements between sources. This is where understanding actually
   forms, so do not smooth it over.
4. Open questions.

Conventions: inline prose citations ("per the 2025 annual report"), no frontmatter
machinery, no wikilinks, roughly 3,000 to 5,000 words. Save as
`ops/curriculum/kb-<topic>-v<N>.md`.

End with two sections the tutor uses:

- **Discussion questions.** Ten, ordered from recall to judgment.
- **Tutor notes.** What the owner already knows well, what they keep getting wrong, and
  topic-specific traps. The most valuable trap to name is the one where general theory
  gets confused with facts specific to the owner's actual situation.

If a synthesis shows a study document was too thin, produce v2 addressing the gap rather
than pointing the owner at raw sources. The point of the system is that they should not
have to.

## Ingesting a session synthesis

The owner drops the tutor's synthesis into `raw/inbox/` named
`voice-synthesis-<topic>-<date>.md` with `type: voice-synthesis` in the frontmatter. It
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
3. Update the topic's status in `curriculum.md`.
4. Decide: advance to the next topic, repeat this one, or deepen the study document.
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
