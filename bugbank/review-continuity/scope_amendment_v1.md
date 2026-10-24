# Scope amendment for historical phrase continuity

This amendment corrects the interpretation of the saved phrase comparison. It does not rerun the analysis, change historical answers, update benchmark labels, or establish approval of current artifacts. The original reports remain preserved.

The underlying v4 JSON is `HISTORICAL_REVIEW_PHRASE_CONTINUITY_v4.json`, SHA256 `ae67c287a2cbf78aa8e6b6529f359484cc36a8ce9938ca1fe2ec807f9d9f2618`. Its archived-packet and current-field comparisons were checked in `ASTRA_V4_PHRASE_CONTINUITY_AUDIT.md` and the separate [coordination reference removed] read-only review. The following interpretation supersedes the v4/v5 wording about material the reviewers actually saw.

## Compared material and supported results

The historical inputs are archived assigned-packet passages associated with historical answers by record identifier. Their stored hashes identify the archived packets; they do not attest which revision each reviewer received. The comparison uses whitespace-normalized equality or containment, not semantic equivalence.

| Archived passage | Current material compared | Recurrence | Associated historical YES |
|---|---|---:|---:|
| Challenged claim | `current_fields.claim_quote` | 62/64: 61 equal, 1 contained | 55 |
| Proposed counterexample | `current_fields.witness` or `current_fields.explanation` | 40/64: 36 equal, 4 contained | 38 |
| Explanation | `current_fields.explanation` or `current_fields.witness` | 5/64: 3 equal, 2 contained | Not a separate review endpoint |
| Selected theorem-header excerpt in the archived packet | Text occurring anywhere in the current Lean file | 4/64 | 4 associated historical Q3 YES answers; no approval transfer |

The historical YES intersections do not change any NO or CANNOT_DETERMINE answer. They describe an association between retained archived text and historical judgments, not fresh judgments on current files. Matching excerpts need not have unchanged surrounding assumptions, definitions, arguments, or consequences. In particular, an archived witness description may occur in a current explanation; that occurrence alone does not establish that the current dossier endorses the old witness in the same role.

The four Lean occurrences do not establish four unchanged currently selected certificates. Some archived headers survive as other declarations. Conversely, ordinary namespace qualification must not be mistaken for a different declaration: `refutation` inside `namespace SE_cs_97637_a97647` is the selected `SE_cs_97637_a97647.refutation`, and the analogous qualification applies to `SE_math_4537650_q.SE_math_4537650__q_refuted`. No conclusion about equivalence of full declaration contexts or compiled proof artifacts follows from this text test.

## Withdrawal of the additional v5 subdivision

The v5 JSON, SHA256 `aebadc763a1ac2cad3e25ef8fdafb85daf4ee61ab7b772dfcaa1ed915ea82c6d`, introduced a subdivision reporting zero identical currently selected statements and four headers present elsewhere only. Its handling of namespace-qualified names misclassifies the two examples above. That subdivision, its `counts_v5_q3` and per-record selected-statement classifications, and its use in `CANDIDATE_v2_NOTE.json` are withdrawn as evidence. They are not replaced here with another selected-statement or semantic-equivalence count. The checked file-occurrence count of four remains the supported result.

The v5 top-level `method` and `scope` strings also retain the earlier overstatement that the historical judgment concerned the same words now present. Read those historical strings subject to this amendment, not as an alternative live interpretation. References to a single September 10 non-author cohort are not established by this comparison: the joined answer dates span September 6–12, and this analysis does not establish reviewer role or affiliation. The approved manuscript accordingly refers to retained dossiers with historical reviews.

## Consequence for the release and manuscript

This comparison adds evidence about which parts of archived dossiers persist after revision. It does not establish human approval of the current release, source applicability, witness admissibility, or formalization fidelity. The existing approval-policy fields, current kernel receipts, corpus counts and localization scores remain unchanged. The approved manuscript wording is [coordination reference removed]'s [coordination reference removed] paragraph, accepted by [coordination reference removed] in [coordination reference removed] and [coordination reference removed] in [coordination reference removed]. It reports text recurrence with the reviewed-revision limitation, not the withdrawn v5 subdivision.
