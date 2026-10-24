# Experiment B: verify the actual evidence in saved critic outputs (frozen protocol v1)

Written 2026-09-25T18:34:49Z, before the sample was drawn and before any saved response was read for this purpose.

**Question.** How often does reference localization (a first-choice hit on the designated reference line) correspond to a genuinely supported
objection in the critic's own saved response, and how often does a miss carry a supported objection of its own?

**Population and configurations.** The 191 primary records of the accepted localization evaluation (report 93d31135, roles
evaluation_primary). Two configurations pre-selected by the already public primary Hit@1 table, never by item: the best native
view EXP4__gemini-3.1-pro (137/191) and the best local open-weight view EXP2__local_nemotron3_super_120b_a12b_fp8 (95/191). This is a
descriptive audit of two selected strong configurations, not a ranking of model families or a causal native-versus-local comparison.

**Sample.** 24 records drawn uniformly without replacement from the sorted 191 primary ids; seed = first 16 hex digits of
sha256("copeer-B-saved-evidence-v1|report:<sha>|reference:<sha>|ledger:<sha>|research_origin_main:<commit>") with the exact hashes in
B_COMMITMENT.json; python random.Random(int(seed,16)).sample(sorted_ids, 24). Review order = draw order. The first 6 records (12 saved
responses) are the feasibility pilot and are retained in the final analysis unchanged if rubric and budget stay unchanged. No expansion
24→48 on the basis of results; continuation is decided only on checker feasibility and time before any grade is read. Records are benchmark
records, not independent source units: cluster ids (reference items) are retained for paired grouping.

**Frozen objects per (record, configuration).** The chosen saved attempt (record.json path and sha256), the saved answer bytes (path and
sha256), the frozen parser's first-choice label (candidate_parse.slot_audit rank 1, normalized), attempt class, completeness flag. Absent or
technical outputs stay in the sample as MISSING_TECHNICAL. Nothing is re-generated, replaced or repaired.

**Blinding.** Verifiers receive opaque packets P01–P48 in a seeded random order: the source text with its line labels exactly as the critic saw
it, the critic's saved response verbatim, and the parsed first-choice label. Hidden: configuration identity, the reference (gold) labels, the
recorded hit/miss, any earlier grade or diagnostic rationale, and sibling packets (no verifier sees both configurations' responses for the same
record). The private key mapping packets to records and configurations is written to private/ and joined only after every assessment is
locked (file written and hashed).

**Assessment (four separate judgments, each with a short justification).**
- J1 line_asserts_challenged_proposition: does the first-choice source line assert the proposition the response challenges, under the source's
  active assumptions? YES / NO / UNCLEAR.
- J2 evidence_specified: does the response supply a sufficiently specified witness or a complete refuting argument? SPECIFIED /
  INSUFFICIENTLY_SPECIFIED / NONE.
- J3 evidence_check (only what the critic supplied; the verifier must not replace the witness, search for a better one or repair the
  mathematics): VERIFIED_VALID_KERNEL (a Lean check of exactly the supplied evidence compiled) / VERIFIED_VALID_EXACT (independent exact
  computation, script kept) / ANALYTIC_VALID (complete inspectable argument, model-assisted judgment) / INVALID (the supplied evidence fails
  an assumption or does not refute the conclusion, demonstrated) / UNRESOLVED (budget, tooling or genuine uncertainty; a timeout is not a
  proof of error) / NOT_APPLICABLE (J2 = NONE).
- J4 consequence_overreach: does the response's stated consequence overreach (e.g. declares the final theorem false from a broken intermediate
  step)? YES / NO / UNCLEAR / NOT_STATED.
Two independent readers per packet (different agents; each agent sees a record at most once). Disagreements are preserved; adjudication is a
separate later step, reported beside the two original readings. Budget per packet per reader: at most 20 minutes and at most two Lean compile
attempts in the existing project (compiles may be impossible in this session's memory cgroup; that is recorded as UNRESOLVED_TOOLING under J3
= UNRESOLVED, never as INVALID). Exact arithmetic checks are done with short Python scripts kept in the packet's output folder.

**Analysis (pre-specified).** After locking, join the private key and the frozen outcome rule (runtime resolve_and_score_corrected.py, hit1 of
the chosen record against the reference gold). Primary table per configuration: first-choice hit (yes/no) × evidence class {valid
(kernel/exact/analytic, reported separately), invalid, insufficient or unresolved, missing/technical}, using the FIRST reader's locked judgment
as the primary reading and the second reader for agreement; all 48 cells and all disagreements reported. Secondary: J1, J2, J4 distributions;
valid objections among misses ("valid alternative objections") reported in this analysis only, never folded into the headline localization
accuracy; gold scores unchanged. Uncertainty: counts with exact finite-population statements avoided (24 of 191 is descriptive); paired
comparison of the two configurations only descriptively at the record level. Costs: verifier agent time, Lean attempts and scripts are new
costs and are logged; the saved solver usage is historical and kept separate.

**Provenance labels.** Kernel checks, exact computations, and model-assisted analytic judgments are reported as three distinct categories;
"model-assisted" is stated wherever an agent judgment is the evidence. This is a prospectively specified follow-up motivated by the existing
miss diagnostic (which exposed gold and made supplied-counterexample soundness optional), not a retroactive pre-registration.

**Domain restriction.** None imposed at sampling; checker availability is recorded per packet (Lean/Mathlib for formalizable claims, exact
arithmetic for numeric claims, analytic reading otherwise) and reported as part of the evidence class.
