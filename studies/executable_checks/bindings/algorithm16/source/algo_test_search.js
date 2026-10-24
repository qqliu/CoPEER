export const meta = {
  name: 'algo-test-search',
  description: 'Part-B task 8, stage 2: blind test-search over Fable-gated algorithm solutions - implement faithfully, build an oracle, find a concrete failing input or a measured bound violation; then independent verification',
  phases: [{ title: 'TestSearch' }, { title: 'Verify' }],
  model: 'opus',
}

// args: { ids: [record_id,...] }  (Fable strong-both selection)
//
// The analogy to the proof pipeline, stage for stage:
//   claim          -> the solution's stated spec / complexity bound
//   counterexample -> a concrete input where the FAITHFUL implementation is
//                     wrong vs a brute-force oracle, or an instrumented
//                     operation-count curve exceeding the claimed bound
//   Lean kernel    -> a deterministic, runnable Python test with exact
//                     arithmetic, committed with its reproduction command
//   independent verification -> a second agent re-implements the ORACLE from
//                     scratch and reruns the test; it may read the claim and
//                     the failing input but must not copy the searcher's code
const A = (typeof args === 'string') ? JSON.parse(args) : args
if (!A || !Array.isArray(A.ids) || !A.ids.length) throw new Error('args {ids[]} required')

const BASE = '<workspace>/qedbench_certificate_availability_triage'
const RECORDS = `${BASE}/data/records_alg_graph.jsonl`
const FABLE_VERDICTS = `${BASE}/outputs_algo_tests/triage_verdicts_fable`
const OUT = `${BASE}/outputs_algo_tests`
const TESTS = '<workspace>/partB_feasibility/algorithm_tests'

const SEARCH = { type:'object', additionalProperties:false,
  required:['record_id','outcome','claim_kind','target_claim','test_path','failing_input','observed_vs_claimed','faithfulness_notes'],
  properties:{ record_id:{type:'string'},
    outcome:{type:'string',enum:['BUG_FOUND','BOUND_VIOLATION_FOUND','NO_BUG_FOUND','NOT_FAITHFULLY_IMPLEMENTABLE']},
    claim_kind:{type:'string',enum:['CORRECTNESS','PERFORMANCE']},
    target_claim:{type:'string'}, test_path:{type:'string'},
    failing_input:{type:'string'}, observed_vs_claimed:{type:'string'},
    faithfulness_notes:{type:'string'} } }

const VERIFY = { type:'object', additionalProperties:false,
  required:['record_id','verdict','notes'],
  properties:{ record_id:{type:'string'},
    verdict:{type:'string',enum:['CONFIRMED','REFUTED_TEST_INVALID','CANNOT_REPRODUCE']},
    notes:{type:'string'} } }

log(`algo test-search: ${A.ids.length} Fable-gated records`)

const results = await pipeline(A.ids,
  rid => agent(`You are the blind TEST-SEARCH stage for one algorithm solution. Read ${RECORDS} and find the JSON line whose record_id is exactly ${JSON.stringify(rid)} (problem_text + solution_text_line_numbered). Also read ${FABLE_VERDICTS}/${rid.replace(/[ /]/g,'_')}__p0.json and __p1.json for the triage's quoted target claim and test sketch. No web.

1. IMPLEMENT THE SOLUTION'S ALGORITHM FAITHFULLY in plain Python 3 stdlib - exactly what the solution describes, including its bugs. If a load-bearing step is genuinely unimplementable as written, report NOT_FAITHFULLY_IMPLEMENTABLE with the exact gap in faithfulness_notes; never invent the missing step.
2. Build a BRUTE-FORCE ORACLE for the problem (exhaustive/reference computation, exact arithmetic only - int/Fraction, floats never decide anything).
3. CORRECTNESS claims: search inputs of size <= 12 (exhaustive over a bounded family, plus adversarial constructions from the triage sketch) for an input where the implementation's output differs from the oracle. PERFORMANCE claims: instrument OPERATION COUNTS (explicit counters at the dominant operations - comparisons, edge relaxations, recursive calls; never wall clock) and measure across at least 4 sizes; a violation means the measured growth provably exceeds the claimed bound with the constants visible in your output.
4. Write ONE self-contained runnable file ${TESTS}/${rid.replace(/[ /]/g,'_')}/test.py (create dirs) containing: the faithful implementation, the oracle, the search/measurement, and a __main__ that PRINTS the verdict deterministically (fixed seeds if sampling). Run it; report what it printed.

Set record_id exactly ${JSON.stringify(rid)}. BEFORE returning, write your result JSON to ${OUT}/test_search/${rid.replace(/[ /]/g,'_')}.json (create dirs).`,
    { label:`ts:${rid}`, phase:'TestSearch', schema:SEARCH, effort:'high', model:'opus' }),
  (search, rid) => {
    if (!search || (search.outcome !== 'BUG_FOUND' && search.outcome !== 'BOUND_VIOLATION_FOUND')) return search
    return agent(`You are the INDEPENDENT VERIFIER for an algorithm bug report. Default to skepticism.

Read ${OUT}/test_search/${rid.replace(/[ /]/g,'_')}.json (the report) and ${RECORDS} for record ${JSON.stringify(rid)} (the original solution text). Read their ${TESTS}/${rid.replace(/[ /]/g,'_')}/test.py ONLY to hunt for flaws: an UNFAITHFUL implementation (their bug, not the solution's), a wrong oracle, floats deciding, a bound misread from the claim.

Write your OWN oracle FROM SCRATCH at ${TESTS}/${rid.replace(/[ /]/g,'_')}/verify_oracle.py - no imports from or copying of their code - and recheck their failing input (or re-measure their operation counts with your own counters). Run it.

CONFIRMED only if your independent check shows the solution's algorithm genuinely fails its stated claim on that input / genuinely exceeds the stated bound. Note whether the refuted claim is the solution's substantive claim or a typo it plainly did not mean.

Set record_id exactly ${JSON.stringify(rid)}. BEFORE returning, write your verdict JSON to ${OUT}/test_verify/${rid.replace(/[ /]/g,'_')}.json (create dirs).`,
      { label:`tv:${rid}`, phase:'Verify', schema:VERIFY, effort:'high', model:'opus' })
      .then(v => ({ ...search, verification: v }))
  })

const done = results.filter(Boolean)
const byOutcome = {}
let confirmed = 0
for (const r of done) {
  byOutcome[r.outcome] = (byOutcome[r.outcome]||0)+1
  if (r.verification?.verdict === 'CONFIRMED') confirmed++
}
log(`${JSON.stringify(byOutcome)} | verified CONFIRMED: ${confirmed}`)
return { requested: A.ids.length, returned: done.length, outcomes: byOutcome, confirmed }
