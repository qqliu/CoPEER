export const meta = {
  name: 'code-twin-search',
  description: 'Executable-twin program (task 8 expanded, PI directive): BLIND Fable re-derivation of a runnable Python counterexample test for every certified record and every no-faithful-Lean record, plus independent verification',
  phases: [{ title: 'Search' }, { title: 'Verify' }],
  model: 'fable',
}

// args: { ids: [record_id,...] }
//
// PI directives baked in:
// - model: FABLE for the search (and verify), pinned at agent level;
// - BLIND: the agent sees only the claim text (target_claim + source_quote)
//   from runs/code_twin/inputs/<rid>.json - never the Lean certificate, never
//   the confirmed witness, never the web. For certified records this makes
//   the runnable test an INDEPENDENT third derivation of the flaw (after the
//   original search and its verifier); for no-Lean records it tests whether
//   executable counterexamples cover the gap Lean could not.
// - Deliverable: one self-contained deterministic Python test per record,
//   archived under partB_feasibility/code_twins/<rid>/test.py, exact
//   arithmetic only, printing its verdict deterministically.
const A = (typeof args === 'string') ? JSON.parse(args) : args
if (!A || !Array.isArray(A.ids) || !A.ids.length) throw new Error('args {ids[]} required')

const BASE = '<mount-root><machine-root>/anonymous-user/new/proof-verification/qedbench_certificate_availability_triage'
const IN = `${BASE}/runs/code_twin/inputs`
const OUT = `${BASE}/runs/code_twin`
const TESTS = '<mount-root><machine-root>/anonymous-user/new/proof-verification/partB_feasibility/code_twins'

const SEARCH = { type:'object', additionalProperties:false,
  required:['record_id','outcome','test_path','witness_description','refutation_explanation','search_space'],
  properties:{ record_id:{type:'string'},
    outcome:{type:'string',enum:['WITNESS_FOUND','NO_WITNESS_EXHAUSTIVE','NO_WITNESS_INCONCLUSIVE','CLAIM_NOT_FINITELY_REFUTABLE']},
    test_path:{type:'string'}, witness_description:{type:'string'},
    refutation_explanation:{type:'string'}, search_space:{type:'string'} } }

const VERIFY = { type:'object', additionalProperties:false,
  required:['record_id','verdict','notes'],
  properties:{ record_id:{type:'string'},
    verdict:{type:'string',enum:['CONFIRMED','REFUTED_WITNESS_INVALID','CANNOT_REPRODUCE']},
    notes:{type:'string'} } }

log(`code-twin: ${A.ids.length} blind Fable searches`)

const results = await pipeline(A.ids,
  rid => {
    const fn = rid.replace(/[ /]/g, '_')
    return agent(`You are a BLIND counterexample-search agent. Read ${IN}/${fn}.json - it contains a mathematical claim quoted verbatim from a proof (target_claim, source_quote). Use ONLY that file: no web, no other records, no repository files.

Write a DETERMINISTIC, STDLIB-ONLY Python 3 program that EXHAUSTIVELY searches a bounded space for a concrete counterexample to the claim, using EXACT arithmetic only (int, fractions.Fraction, itertools - floats never decide anything). The program must be SELF-CONTAINED and REUSABLE: a reader who runs it sees the claim (docstring), the search, and a printed verdict naming the witness explicitly, deterministically (fixed iteration order, no randomness or seeded only).

Save it to ${TESTS}/${fn}/test.py (create dirs). Run it. Report:
- WITNESS_FOUND with the concrete witness and exactly why it violates the claim;
- NO_WITNESS_EXHAUSTIVE naming the exact space swept;
- NO_WITNESS_INCONCLUSIVE or CLAIM_NOT_FINITELY_REFUTABLE, honestly, when the claim text does not supply enough to decide or is not finitely checkable. Never invent data the claim does not supply.

Set record_id exactly ${JSON.stringify(rid)}. BEFORE returning, write your result JSON to ${OUT}/searches/${fn}.json (create dirs).`,
      { label:`ct:${rid}`, phase:'Search', schema:SEARCH, effort:'high', model:'fable' })
  },
  (search, rid) => {
    if (!search || search.outcome !== 'WITNESS_FOUND') return search
    const fn = rid.replace(/[ /]/g, '_')
    return agent(`You are an INDEPENDENT ADVERSARIAL VERIFIER. A blind searcher claims a runnable counterexample. Default to skepticism.

Read ${IN}/${fn}.json for THE CLAIM and ${OUT}/searches/${fn}.json for the reported witness. Read their ${TESTS}/${fn}/test.py ONLY to hunt for flaws (floats deciding, wrong bounds, a predicate that does not decide the stated claim). Write your OWN checker FROM SCRATCH at ${TESTS}/${fn}/verify.py - exact arithmetic, no copying - and recompute whether the claim genuinely fails on their witness. Run it.

CONFIRMED only on your own recomputation. Note whether the refuted statement is the substantive claim or a typo the author plainly did not mean.

Set record_id exactly ${JSON.stringify(rid)}. BEFORE returning, write your verdict JSON to ${OUT}/verifies/${fn}.json (create dirs).`,
      { label:`cv:${rid}`, phase:'Verify', schema:VERIFY, effort:'high', model:'fable' })
      .then(v => ({ ...search, verification: v }))
  })

const done = results.filter(Boolean)
const o = {}
let confirmed = 0
for (const r of done) {
  o[r.outcome] = (o[r.outcome]||0)+1
  if (r.verification?.verdict === 'CONFIRMED') confirmed++
}
log(`${JSON.stringify(o)} | verified CONFIRMED: ${confirmed}`)
return { requested: A.ids.length, returned: done.length, outcomes: o, confirmed }
