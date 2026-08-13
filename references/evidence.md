# The evidence base

This skill's design claims, stated at the strength the literature supports. Each section
gives the mechanism the claim motivates, the citation-safe form of the claim, the
strongest supporting evidence, and the evidence against or limiting it. Where the
evidence is thin, this file says so. A methodology that hides its weak spots teaches its
users to overclaim, which is the failure mode this whole skill exists to prevent.

Compiled August 2026. Numbers below come from the cited papers, not from this project.

## 1. Single-pass generation omits source content

**Motivates:** the coverage bar, and validating coverage separately from accuracy.

**Citation-safe claim:** single-pass long-document generation frequently omits salient
source information; omission can substantially exceed factual-error rates, and coverage
depends on source position and context organisation.

**Evidence for.** [Elaraby & Litman, EACL 2026 (ARC)](https://aclanthology.org/2026.eacl-long.167/):
across eight LLMs summarising long legal and scientific documents, missing salient facts
dominated errors. Legal-domain omission ran 27.8% to 56.3% of salient atomic facts
against factual-error rates of 2.0% to 5.5%. Omission is measured directly (each atomic
fact labelled covered, missing, or non-factual), not inferred from a quality score.
[Liu et al., TACL 2024 (Lost in the Middle)](https://aclanthology.org/2024.tacl-1.9/):
moving the answer-bearing document to the middle of a long context cost over 20
percentage points on controlled QA, a mechanism for position-dependent omission.

**Evidence against and limits.** The effect is a population tendency, not an
inevitability: in the same Liu et al. study, one model was near-perfect across positions
on synthetic retrieval, and query-aware context organisation eliminated the deficit in
one condition. ARC's generators are small open-weight models, not 2026 frontier systems.
Say "frequently omits", never "always omits".

## 2. Self-review is not independent

**Motivates:** the separate validator that never sees the digest's reasoning or
self-map.

**Citation-safe claim:** self-evaluation is not independent. LLM judges exhibit
measurable self-preference, and intrinsic self-correction can preserve or introduce
errors. Accurate external or source-grounded feedback is a stronger basis for validation
than self-critique alone.

**Evidence for.** [Xu et al., ACL 2024 (Pride and Prejudice)](https://aclanthology.org/2024.acl-long.826/):
self-bias found in all six model families examined; repeated self-refinement amplified
it, while accurate external feedback reduced it.
[Chen et al., EMNLP 2025](https://arxiv.org/abs/2506.02592): residual self-preference
survives even after controlling for genuine quality differences; restyling outputs cut
one model's self-preference score from 18.7% to 7.2%, showing style recognition, not
quality, was driving judgment.
[Huang et al., ICLR 2024](https://arxiv.org/abs/2310.01798): intrinsic self-correction
without new evidence reduced accuracy in several settings.

**Evidence against and limits.** [Self-Refine (Madaan et al., NeurIPS 2023)](https://arxiv.org/abs/2303.17651)
shows same-model critique-and-revise averaging roughly 20 points of improvement across
seven tasks, so "models cannot self-audit" is false as an absolute. The defensible
position, and this skill's position, is that self-review is useful but biased, so
sign-off requires an independent pass. No published experiment tests a cold independent
validator on an agent-maintained vault specifically; that design is an engineering
extrapolation from the bias literature plus this project's field defects, and this file
says so plainly.

## 3. Correction passes can create defects

**Motivates:** the loop terminating on a clean validation round, never on a round of
fixes.

**Citation-safe claim:** revision is non-monotonic. A correction pass can fix one defect
while turning previously correct content wrong, so a clean validation round must follow
the final revision.

**Evidence for.** [Stav et al., 2026](https://arxiv.org/abs/2606.23196) measures
correct-to-wrong transitions directly: at or below 2.1% on readily verifiable tasks,
reaching 13.25% on hard benchmarks. [Yang et al., ACL 2025](https://aclanthology.org/2025.acl-long.203/)
decomposes the trade-off: increasing a model's willingness to critique wrong answers can
lower its tendency to preserve correct ones.

**Evidence against and limits.** Revision is often net-positive (Self-Refine, above).
The rule this supports is "validate after every modification", not "avoid revision".

## 4. Coverage and citation accuracy are different measurements

**Motivates:** the coverage instrument running both directions: source-derived recall
testing (the exam) and grounding checks (the counters).

**Citation-safe claim:** citation accuracy and coverage are orthogonal. A note can cite
every statement correctly while omitting important source content, so coverage is tested
separately, with source-derived questions whose answers must be recoverable from the
vault alone.

**Evidence for.** ARC (above) validates source-derived atomic-fact testing against human
coverage judgments (Pearson correlations up to 0.638).
[Moreira & Sweet, 2026 (Beyond Memory)](https://arxiv.org/abs/2607.24759): two
experiments recorded as 20/20 coverage fell to 14/20 and 12/20 under an evidence-only
re-audit, and rose to 18/20 after the pipeline was fixed. Note precisely: that result is
a grounding audit catching inflated coverage claims, not a closed-book exam
demonstration. [GaRAGe (Sorodoc et al., ACL Findings 2025)](https://aclanthology.org/2025.findings-acl.875/)
treats answerability and grounding as distinct axes by design.

**Evidence against and limits.** This is the thinnest claim in the set and the one this
skill words most carefully. No controlled study shows exam-style testing is *better*
than citation verification; the literature supports running both because they catch
different failures. That is what the coverage instrument does: the closed-book exam (in
RAG terms, source-derived answerability testing of the vault) tests recall, the five
zero-tolerance counters test grounding, and neither substitutes for the other.

## 5. Retrieval practice beats rereading for durable learning

**Motivates:** the vault-blind tutor: recall is tested without the material, and
corrective evidence comes after the attempt.

**Citation-safe claim:** for durable retention, effortful retrieval without the source
in front of the learner generally outperforms additional rereading, particularly on
delayed tests.

**Evidence for.** [Roediger & Karpicke, 2006](https://doi.org/10.1111/j.1467-9280.2006.01693.x):
after one week, repeated retrieval retained about 61% against about 40% for repeated
study. The immediate test ran the other way (83% for rereading against 71%), which is
the trap: rereading *feels* better precisely when it durably is not.
[Agarwal, Nunes & Blunt, 2021](https://doi.org/10.1007/s10648-021-09595-9): systematic
review of 50 classroom experiments (n = 5,374); 57% of effects medium or large.
[Karpicke & Blunt, Science 2011](https://doi.org/10.1126/science.1198785): on science
texts at a one-week delay, retrieval practice reached roughly 67% against 49% for
repeated study and 45% for concept mapping, with 84% of students better off under
retrieval practice.
[Ye, Su & Cao, KDD 2022](https://doi.org/10.1145/3534678.3539081): personalised spaced
scheduling optimised over roughly 220 million memory logs beat the prior state of the
art by a reported 12.6%.

**Evidence against and limits.** The literature does not establish that closed-book
beats open-book in every form, and no strong independent head-to-head validates one
spaced-repetition scheduler over another. Separately,
[Sapkota & Murshed, 2026](https://arxiv.org/abs/2607.01247) found the best LLM exam
grader reached only 0.58 correlation with human total scores. Design consequence in
this skill: tutor grades are stored as noisy evidence with review status, marked at
medium confidence until corroborated, never treated as ground truth. The grade steers
the next curriculum; it does not become a settled fact about the owner.

## 6. Fluency is not evidence

**Motivates:** honest grading, the over-firming checks, and the whole stance that a
convincing answer is not a validated answer.

**Citation-safe claim:** fluency is not evidence of correctness, and raw verbal
confidence is often miscalibrated. Reliability is established by source-grounded checks,
not by how convincing the answer sounds. Calibrated uncertainty can still carry real
information about error risk.

**Evidence for.** [Xiong et al., ICLR 2024](https://arxiv.org/abs/2306.13063): asking
models to state confidence yields systematic overconfidence across scales and settings.
[TruthfulQA (Lin, Hilton & Evans, ACL 2022)](https://aclanthology.org/2022.acl-long.229/):
the best model answered truthfully on about 58% of adversarial questions against roughly
94% for humans, in fully fluent prose throughout.

**Evidence against and limits.** [Kadavath et al., 2022](https://arxiv.org/abs/2207.05221):
deliberately elicited self-evaluation probabilities do predict correctness increasingly
well with scale. So "confidence carries no signal" is false; the skill's claim is the
narrower one, that surface confidence is an unreliable proxy, which survives that
result.

## 7. The retention question: why the bar is what it is

**Motivates:** the 95% coverage bar, the separate qualifier-coverage dimension, and the
refusal to sell either as a human-memory comparison.

**Citation-safe claim:** there is no defensible "humans retain X% of a book" number.
Human reading durably preserves gist and integrated structure while rapidly losing
exact propositions, qualifiers, and peripheral detail. The coverage bar is therefore an
archival completeness standard, stricter than unaided human recall, not a simulation of
it.

**Evidence.** [Radvansky et al., 2024](https://doi.org/10.3758/s13423-024-02514-3):
a survey of 916 datasets from 256 papers found no universal forgetting curve;
logarithmic, exponential-power, and linear functions all occur. Popular figures like
"70% forgotten in 24 hours" have no standing, and this project never uses them.
[Fisher & Radvansky, 2018](https://doi.org/10.1016/j.jml.2018.05.008): memory for prose
splits into three representations with different lifetimes. Surface wording is near
chance within about an hour; proposition-level memory stays above chance through about
a week but not at four; the integrated situation model stays robust through twelve
weeks. [Sacripante et al., 2023](https://doi.org/10.3758/s13421-022-01310-5): gist
outlives detail in free recall, with peripheral-detail recall reaching 13.7% at one
month in one experiment, and delayed false memories were overwhelmingly gist-consistent
(25 of 26 in one experiment). That last result is the retention literature's argument
for this skill's provenance gates: reconstruction around gist is where plausible false
specifics come from, in humans and in generative models alike.
[Reder & Anderson, 1980](https://doi.org/10.1016/S0022-5371\(80\)90122-X): carefully
built summaries of textbook chapters matched or beat full-text reading on later
main-point tests, including when full-text readers got three times the study time, with
scores converging by six to twelve months. Within its limits (chapter scale, main-point
recognition), this is direct evidence for the "read the wiki instead of the book" use,
for deliberately preserved content.

**Evidence against and limits.** [Marcelo et al., 2013](https://doi.org/10.1136/eb-2012-100537):
77 residents randomised to abstracts versus full text showed no overall decision
difference, but a significant specialty interaction: surgery improved 26 points with
full text against 14 with abstracts, while other specialties did not differ. So coverage does not establish judgment equivalence, which is why the
judgment/transfer benchmark is recorded as a deferred check rather than claimed. The
professional-reading gap is real: no study follows professionals reading ordinary
business books with proposition-level retention at fixed lags, so this file makes no
claim about what executives retain. The qualifier-coverage dimension exists because the
same literature shows qualifications and boundary conditions are the first casualties
of gist compression and the most decision-relevant content to lose.

## What we looked for and did not find

Recorded because absence shapes how strongly the claims above may be stated.

1. No controlled comparison showing exam-style coverage testing beats citation
   verification for knowledge-base auditing. They measure different failures; this skill
   runs both.
2. No published experiment on an agent-maintained vault testing a cold independent
   validator against same-context self-review. The two-validator design is motivated by
   the self-preference literature and by defects independent validators caught in this
   skill's own hardening campaign, and it awaits direct study.
3. No strong independent trial establishing one spaced-repetition scheduler over
   another. The curriculum module adapts intervals on demonstrated mastery and does not
   claim algorithmic superiority.
4. No basis for treating AI tutor grades as human-equivalent. Grades are noisy
   measurements and the vault stores them that way.
5. No defensible "humans retain X% of a book" figure at any delay, and no universal
   forgetting curve to borrow one from. The coverage bar is stated as an archival
   standard for exactly this reason.
6. No clean experiment showing full-text reading beats a high-quality distillation for
   judgment under genuinely equal recall. The closest trial (abstracts versus full
   text) is suggestive for one specialty and is cited as the honest caveat, not
   buried.
