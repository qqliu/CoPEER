# Review evidence

This directory provides anonymous categorical judgments and numerical reproduction
for the review studies reported in Co-PEER. It preserves separate review rounds
and distinguishes human review with AI assistance from an LLM-only diagnostic.
It also includes 160 self-contained scientific review packets: 100 for the random
audit, 30 for the selected-artifact review, and 30 for the Sonnet diagnostic.
Each packet index binds the original reviewed bytes to the distributed projection.

Run from the repository root with Python 3 (standard library only):

```sh
python bugbank/reviews/reproduce.py --check
```

To inspect the complete numerical output:

```sh
python bugbank/reviews/reproduce.py
```

The script is portable: it finds data relative to its own location and needs no
network, model access, credentials, or private source files. It recomputes counts
from saved categorical judgments; it does not re-evaluate mathematical claims.

| Directory | Evidence | Reported result |
| --- | --- | --- |
| `original100/` | 100 returned human reviews from 110 assigned packets | 76 approved mathematics and Lean; among these, source interpretation received 61 YES, 7 NO, and 8 CANNOT_DETERMINE |
| `selected33/` | One human review of 32 mathematical artifacts and one documentary supplement | Complete three-question judgments, including one mathematics NOT_ASSESSED response |
| `scoped_supplements/` | Human review of three selected mathematical supplements | All three criteria approved in each, for their stated formal scope |
| `earlier_selected30/` | AI-assisted, human-confirmed review of 30 selected artifacts | 27 approved on all three criteria |
| `selected30/` | Separate AI-assisted, human-confirmed review of 30 selected artifacts | 29 approved on all three criteria, including all 20 main-evaluation records |
| `random100/` | AI-assisted, human-confirmed random audit of 100 of 284 dossiers | 91 joint approvals; weighted estimate 91.0%, joint 95% sampling interval 81.0%–96.5% |
| `reference_lines/` | Two human reviews of disjoint 40-text samples | 35/40 initially and 38/40 after corrections; threshold 38/40 |
| `sonnet_misses/` | LLM-only analysis of 30 of 58 readable first-choice misses | 12 alternative false assertions, 15 selected assertions judged not false, and 3 source/annotation issues; primary LLM reader approved counterexamples in 11 of the 12 alternative cases |

`cohorts.json` defines the questions and study-level review disclosures.
`expected_results.json` records the numerical output reproduced by the script.
Question Q1 concerns the source claim and its assumptions, Q2 the counterexample's
validity under those assumptions, and Q3 the Lean statement's correspondence.
Reference-line reviews instead ask whether marked lines state the claim, whether
an asserting line is missing, and whether an extra marked line is present. Their
clean answer pattern is YES/NO/NO.

## Random-audit calculation

The sample contains 67 of 191 main-evaluation dossiers and 33 of 93 other dossiers.
The two groups contain 63 and 28 all-YES reviews, respectively. The estimate is
`(191/284)*(63/67) + (93/284)*(28/33)`. For each group, the script inverts exact
hypergeometric tails at 97.5% confidence. It adds the group bounds on the number
of non-all-YES dossiers and takes complements to obtain at least 95% joint
coverage by Bonferroni. Inclusive tails and equality at the cutoff match the
analysis used for the paper. The full frame IDs and numerical seed reproduce
the sampled records in their saved order.

The sampling plan and interval method preceded the review. The analysis retains
all 100 returned judgments under a reviewer-admissibility clarification made
after receipt; the weighted point estimate was also added after receipt. The
interval describes sampling variation under this review procedure. The review
uses AI assistance and personal human checking; it is not an estimate of the
error rate of an unaided reviewer.

## Interpretation and anonymity

Human reviewers are described collectively. Reviewer names, codes, affiliations,
rosters, individual timestamps, raw spreadsheets, identifying comments, tool logs,
and private returns are omitted. Public mathematical record IDs and review-packet
IDs are retained to connect numerical judgments with the paper. Two pre-existing
comment-attribution ambiguities in the original100 cohort are explicit flags;
the script also reports the corresponding 98-row sensitivity. The original100
records did not establish exact reviewed packet revisions, so their judgments
refer to that review round.

The selected30 cohort retains the original `other94` frame label. The later
random100 audit uses the 284-dossier release and its `other93` group. These are
distinct review rounds. The selected samples supply item-level checks; the random
audit supplies the sampling-based estimate. Results are kept separate.

The Sonnet diagnostic is an LLM-only assessment. Its final assertion categories
incorporate additional LLM checks; the 11/12 soundness count uses the primary
reader's separate judgment of the generated counterexample. No human review or
new Lean certificate is asserted for that diagnostic, and it changed no benchmark
scores.

## Coverage

These exports reproduce the reported numerical summaries without private files.
The random100, selected30 and Sonnet packet projections retain the complete source,
counterexample and inline formal proof or saved critic answer. Operational links
and project identity metadata are removed; original and distributed hashes remain
separate. The mathematical corpus and benchmark provide further formal and source
evidence. The random-audit protocol consolidates the saved instructions and
amendments; its nine-flag report preserves every disagreement.

Scientific review notes are included for the selected33 and earlier selected30
rounds. The Sonnet directory preserves the saved scientific readings, categorical
votes, adjudication rationales and disagreements with generic LLM role labels.
Private human-review narratives and consent records remain outside this release.
The original100 reviewed revisions were not recorded, and its exact packets
cannot be reconstructed from its numerical rows. Line-review tables retain
record IDs, line labels and original sheet hashes; their original full review
sheets are not included here. No omitted input is required for the numerical
reproduction command above.

## Source continuity evidence

[Source continuity](source_continuity/README.md) supplies the 16 matched original
and replacement certificates discussed in Appendix D.3, together with the saved
compilation and source-interpretation evidence. It includes the sorting-condition
bridge and Gaussian equality correction, 24 saved compiler checks for 12 original
certificates, and the accompanying audit of 123 theorem and lemma declarations.
Its [manifest](source_continuity/MANIFEST.json) records original and distributed
hashes separately. These are saved artifact checks; this export performed no new
compilation or human review.

## Version resolution, feedback-derived audit guidance, and an unused reviewer template

- `version_resolution/` reconciles saved human judgments with exact artifact versions and the current
  inclusion decisions: the nine random-audit cases, the eighteen historical dispositions, the frozen
  adverse masks, and a descriptive full-mask exclusion sensitivity on the earlier evaluated collection
  (`full_mask_sensitivity.py`, replayable from the repository root; the current core has no overlap with the masks).
- `initial100/feedback_filter/` preserves the audit guidance and schema derived from the initial human
  reviews, which informed the later automated filtering pass.
- `independent_criticism_20260926/` (and its ZIP) is a blank, unreviewed reviewer template prepared for an
  additional saved-output review that was not carried out; it contains no returned judgments and no result
  in the paper depends on it.
