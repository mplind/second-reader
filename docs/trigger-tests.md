# Description trigger tests

Evaluation prompts for the SKILL.md `description` field. Run these against your harness
when the description changes: the skill should activate on every SHOULD, stay silent on
every SHOULD NOT. The near-misses are the cases that matter; a description that
over-triggers on them costs users context on unrelated work.

## Should trigger

1. "Set up a knowledge vault about corporate governance."
2. "Ingest this PDF into my vault."
3. "I have 40 podcast transcripts. Turn them into a knowledge base I can query."
4. "What does my vault say about switching costs? Cite sources."
5. "Audit my knowledge base. What is thin or unsourced?"
6. "Which gaps should I fill next in my research vault?"
7. "Build me a study curriculum from my vault."
8. "Quiz me on what I have ingested so far."
9. "Tutor me on chapter 6, closed book."
10. "File this answer back into the vault."
11. "Resume where we left off in the vault."
12. "Drop everything in raw/inbox into the wiki."
13. "I want a second brain for my reading." (category term still routes here)
14. "Run the vault gate before I use this for the client briefing."

## Should not trigger

15. "Summarize this PDF." (one-off summarization, no vault)
16. "Fix the formatting in this Markdown file." (generic editing)
17. "Rename these notes to kebab-case." (vault mechanics, no knowledge operation)
18. "Take a quick note: dentist Tuesday 3pm." (casual capture, wrong cost profile)
19. "What does this article say?" (single-document QA, no persistence asked)
20. "Organize my Obsidian tags." (housekeeping, not ingestion or query)
21. "Write a blog post from my notes." (authoring, not vault maintenance)
22. "Translate this EPUB to English." (document processing, no vault)

## Near-miss rationale

Items 15, 18, and 19 are the expensive false positives: they look like ingestion but the
user wants a cheap one-shot. The description's closing line ("Not for one-off
summarization, ordinary Markdown editing, generic note formatting, or casual capture")
exists for these three. Item 13 goes the other way: users arrive with the category
vocabulary they know, and the description names the category term directly.
