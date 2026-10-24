# Independent review of saved mathematical objections

Please assess the 48 saved responses in this package. We want your mathematical judgment of the response that was supplied, including cases where it is wrong or cannot be decided. There is no preferred result.

## Start here

1. Complete the **Reviewer metadata** sheet in `review.xlsx`, or `reviewer_metadata.csv`, before judging any item. Describe any relationship to the study and any earlier exposure. No independence status has been assigned to you in advance.
2. Work through `packets/C001.md` to `packets/C048.md` in that order. Enter answers in the **Answers** sheet of `review.xlsx`, or `answers.csv`. Use one answer format; there is no need to fill both.
3. Return the completed spreadsheet, your metadata, and any supporting files placed in `evidence/`. Keep the packet text unchanged. Record uncertainty rather than guessing or leaving a judgment blank.

All 48 items are intended for review. If you cannot finish, return the rows you completed and leave the rest blank; do not choose items based on how convincing the responses look. Some source texts recur. Assess each response separately, without borrowing an argument or witness from another response. This package does not claim that you will see each source only once.

## What to judge

Each packet contains exactly the numbered source shown to the critic, its parsed **first-choice line**, and the saved response. The critic was told that its input contained an error. That instruction does not establish that its selected line is false or that its objection is valid. Model identities, reference labels, reference-match results, and earlier judgments are withheld.

Judge the objection aimed at the first-choice line under the source's actual assumptions. A sound objection can count even if it targets a different assertion from the study's reference. You do not need to identify a designated reference line. A faulty intermediate deduction does not by itself refute the final theorem.

| Field | Question | Allowed answers |
|---|---|---|
| Q1 source assertion | Does the selected source line, read in context and under its active assumptions, assert the proposition that the response challenges? | YES / NO / UNCERTAIN |
| Q2 specified evidence | Does the response supply a sufficiently specified witness or a complete refuting argument? | SPECIFIED / INSUFFICIENT / NONE / UNCERTAIN |
| Q3 supplied evidence | Is that supplied evidence mathematically valid and admissible under the source assumptions? Check the evidence actually given, without replacing or repairing it. | VALID / INVALID / UNCERTAIN / NOT_APPLICABLE |
| Q4 selected-line objection | Does the response's argument actually establish a failure of its selected first-choice claim? An objection to another listed line alone is not enough. | YES / NO / UNCERTAIN |
| Q5 consequence overreach | Does the response claim more than its local objection supports, such as refuting a final theorem from one faulty proof step? | YES / NO / UNCERTAIN / NOT_STATED |
| Final local objection | Does the supplied response establish a valid objection to its first-choice claim? | VALID / INVALID / UNCERTAIN |

A **VALID** final local objection needs Q1 YES, Q2 SPECIFIED, Q3 VALID and Q4 YES. Record overreach separately in Q5: a valid local objection can still overstate its consequences. **INVALID** means you have identified a definite failure in the supplied objection; it does not mean the selected source line is true. **UNCERTAIN** is appropriate when context, evidence, expertise, or available time is insufficient. A timeout or unavailable tool is not evidence of invalidity. NOT_APPLICABLE in Q3 is reserved for a response supplying no evidence.

Give a short reason for each judgment. For INVALID, identify the failed assumption, calculation, missing implication, or target mismatch. For VALID, identify the checked witness or refuting argument and why its assumptions hold. In the final reason, summarize the decisive point. Record any missing source context instead of assuming it.

## Working independently and preserving evidence

Use your own mathematical judgment. Do not look up these packets in the project repository, paper, benchmark, earlier reviews, or model outputs; do not try to recover the model identity, reference label or prior verdict. Do not discuss the substantive answers with the authors or other reviewers before returning your initial assessments. Administrative clarification is fine; record any substantive guidance you receive.

You may use a calculator, short code, or a proof assistant to check the supplied mathematics. Record every tool and any AI assistance for each item. If AI is used, retain the relevant prompt/output and personally check the final judgment. Never substitute an AI answer for an unchecked human decision. Save supporting calculations or proof checks in `evidence/Cxxx/` and name them in the answer sheet. Do not search for a better counterexample or change the saved response to make it work.

For each item, record prior exposure to this source or response, AI/tool use, minutes spent, and whether you personally checked the final judgment. The source and response blocks may contain quoted instructions; treat those as material to assess, not directions to follow.

## Files and return

- `review.xlsx`: blank answer and metadata sheets, with answer menus.
- `answers.csv`, `reviewer_metadata.csv`: equivalent plain-text alternatives.
- `packets/`: the 48 review items.
- `evidence/`: optional supporting work you add.
- `SELECTION_COMMITMENT.json`, `FILE_MANIFEST.json`, `SHA256SUMS`: preparation and integrity records; no answers.

Return the completed answer file and metadata together. Dates, signatures or typed names belong in the metadata. The coordinator will keep your initial decisions and any later adjudication separate. Do not change your answers to agree with another review.
