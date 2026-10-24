# Primary adjudication of the evidence census

The frozen primary annotations and the independent 24-record recoding are immutable. Agreement is always computed on those initial labels.

Every positive family, repair, named-restriction alternative, and global-minimality field receives a full-packet second reading by an assistant other than its primary coder. The final census adopts clear corrections and improved evidence spans. A positive property left uncertain by that review is excluded from the final positive count, retaining the uncertainty flag and explanation. This is a conservative documentation convention, not a verdict that the underlying property is mathematically false. Keep decisions clear the reviewed field's initial uncertainty; unrelated uncertainty is preserved.

Each reviewed field's final direct decision controls its own uncertainty status
after all field reviews have been read. Suggestions about another field cannot
reintroduce an uncertainty explicitly resolved by that field's accepted evidence.
This makes the result independent of review iteration order while preserving
uncertainty for fields without a direct resolution. In particular,
`SE_math_2803642__q` retains the repaired `n=5` claim with its explicit evidence;
the separately unresolved named-restriction property is excluded. The blind-sample
override described below is applied after these direct reviews, and the coverage
ledger records the resulting final values.

The coverage check binds 277 initial positive property assignments in 191 records to exactly one review each. The source reviews, final decisions, and field-level corrections are retained separately. `adjudicate_reviews.py` deterministically applies these decisions; it does not infer mathematical labels or modify source packets.

The primary reviewer also examined the substantive disagreements in the blind sample:

- `mse_1261062__ans1261609`: retain family=false. The packet states an infinite prime-power progression but does not supply its general modular argument. The disagreement remains in the initial agreement table and as documentation uncertainty.
- `reddit_askmath_19b1r7e`: retain repair=true. The packet explicitly invokes the nonzero cancellation condition in the integer domain and identifies the exact canceled identity; applying that stated cancellation law explains the sufficient local repair. No whole-proof repair is asserted.
- `reddit_learnmath_157rs31`: exclude the named-restriction flag conservatively. The primary witness is explicitly strictly convex, but the packet does not contrast it against a named boundary exception or give an alternative. Keep the mechanism ambiguity.
- `Algorithms_36__sol5`: exclude repair=true under the second review's uncertainty decision because its text supplies a necessary path criterion without making the sufficient repaired implication explicit.

Object, mechanism, and role disagreements are retained as evidence of classification ambiguity rather than forced into unanimous consensus. The primary indexing labels remain available, and their uncertainty and agreement limits are reported. These labels are not used as validated mathematical natural kinds or as causal outcomes.
