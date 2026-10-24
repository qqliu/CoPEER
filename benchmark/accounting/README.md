# Token accounting

Run from the repository root with Python 3.10 or later; no extra dependencies, network access, or model calls are required:

```sh
python -B benchmark/accounting/replay.py
```

The command recomputes Table 2's recorded token column and Appendix P's campaign totals from numeric usage inputs. It checks every result against the accepted saved report and joins the usage inputs to the released `benchmark/selections.jsonl`. `saved_replay.json` records a successful run.

## Inputs and accounting rules

- `selected_records.jsonl` contains the numeric usage fields for 3,809 unique selected records. `selection_usage_join.jsonl` binds them to 3,990 selected item/view pairs. The 14 reporting views cover 13 retained physical configurations. The main table uses the EXP5 Haiku view; the EXP1 Haiku view is retained for the appendix.
- `campaign_attempts.jsonl` contains 6,982 distinct physical attempts: 5,408 from the initial campaign and 1,574 correction/recovery attempts. It includes the 18 physical configurations needed for Appendix P's cumulative accounting. Each attempt has an anonymous stable identifier, disjoint coverage identifiers, numeric usage inputs, completeness and orphan flags, and original evidence hashes. Selected attempts link to these identifiers. Shared Haiku outputs and copied receipts are charged once.
- `usage_rules.py` contains the original pure usage and aggregation functions, extracted unchanged. `replay.py` supplies portable input loading, deduplication checks, and the two campaign scopes. `expected_accounting.json` is the identity-free saved aggregate projection; `PROVENANCE.json` binds it to the accepted report and original rule sources.

Complete native usage contributes to **measured tokens**. Partial native usage contributes only its recorded amount to the **observed lower bound**. Missing telemetry stays unknown. A **conservative charge** is a token-budget accounting quantity, not a measured token count or a monetary price: each incomplete attempt receives the maximum of 40,000 tokens, its observed lower bound, and any recorded override or reservation. Provider-native input, cache, and output fields retain their original names and semantics. The native `cache_read_tokens` field is preserved without adding it again to attributable totals; `running_estimate_at_end` is a diagnostic estimate and does not replace complete native usage.

For Table 2, “recorded tokens” is the observed usage lower bound on the 191 main benchmark inputs. Selected-population costs include all attempts retained in each selected record. These are overlapping views of the campaign and are never added to its cumulative totals.

## Reproduced totals

| Cumulative scope | Measured tokens | Observed lower bound | Conservative charge | Incomplete-usage attempts |
|---|---:|---:|---:|---:|
| 13 retained configurations | 38,663,036 | 39,636,145 | 57,293,200 | 411 |
| All 18 registered configurations | 52,477,740 | 53,450,849 | 71,467,904 | 420 |

Five initial Haiku dispatches have no completed attempt receipt. Their retained reservations are 120,000 tokens each; the inputs preserve zero observed usage, one unknown attempt, and the reservation charge for each. Twenty-three selected preflight refusals record no inference and therefore no physical attempt (12 DeepSeek and 11 Kimi records). The 18-configuration scope includes costs for configurations whose corrected evaluation was incomplete; its cost total does not represent 18 completed benchmark comparisons.

The projection retains scientific model identities and numeric evidence. It omits provider-account and authentication envelopes, operational paths, process metadata, and raw session transcripts. Original evidence hashes bind provenance; the public numeric projections have their own release-manifest hashes. Native usage that was never logged cannot be reconstructed by this replay.
