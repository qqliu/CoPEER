export const meta = {
  name: 'cost-experiment-grading',
  description: 'Grade the cost-experiment assessments against held-out ground truth: did each arm actually catch the confirmed flaw?',
  phases: [{ title: 'Grade' }],
  model: 'fable',
}

// args: { ids: [record_id,...], arms?: [...] }
//
// The cost claim is only meaningful jointly with accuracy: a cheap arm that
// misses flaws proves nothing. Every sampled proof is confirmed-flawed (that
// is the population), so ground truth exists for all of them. The grader sees
// the assessment AND the held-out truth; grading cost is metadata, never part
// of either arm's measured cost.
//
// Grades (per assessment):
//   CAUGHT_MATCHING   found the confirmed flaw (same claim, or same defect
//                     under trivial rephrasing); counterexample (if any) valid
//   CAUGHT_DIFFERENT  reported INVALID with a DIFFERENT genuine flaw + valid
//                     support - counts as a catch; flags possible multi-flaw
//   MISSED            reported VALID or CANNOT_DECIDE on a flawed proof
//   FALSE_CATCH       reported INVALID but the stated flaw/counterexample does
//                     not hold up
const A = (typeof args === 'string') ? JSON.parse(args) : args
if (!A || (!Array.isArray(A.ids) && !Array.isArray(A.pairs)))
  throw new Error('args {ids[]} or {pairs[[rid,arm],...]} required')
const ARMS = A.arms || ['refute', 'verify_full', 'verify_earlystop']

const BASE = '<mount-root><machine-root>/anonymous-user/new/proof-verification/qedbench_certificate_availability_triage'
// assess_dir / out_dir: grade a DIFFERENT assessment pool (e.g. a local
// model's) under this exact contract; defaults are the original Task-1 paths.
const ASSESS = A.assess_dir || `${BASE}/runs/cost_experiment/assessments`
const TRUTH = `${BASE}/runs/cost_experiment/grading_truth`
const OUTDIR = A.out_dir || `${BASE}/runs/cost_experiment/grades`

const OUT = { type:'object', additionalProperties:false,
  required:['record_id','arm','grade','justification'],
  properties:{
    record_id:{type:'string'},
    arm:{type:'string'},
    grade:{type:'string',enum:['CAUGHT_MATCHING','CAUGHT_DIFFERENT','MISSED','FALSE_CATCH']},
    justification:{type:'string'} } }

phase('Grade')
// pairs: exact-gap relaunch after a quota kill - grade ONLY the listed
// (record, arm) cells; durable grades on disk are never re-run.
const jobs = []
if (Array.isArray(A.pairs)) jobs.push(...A.pairs)
if (Array.isArray(A.ids)) for (const rid of A.ids) for (const arm of ARMS) jobs.push([rid, arm])
const results = await parallel(jobs.map(([rid, arm]) => () => {
  const fn = rid.replace(/[ /]/g, '_')
  return agent(`You are grading one proof assessment against held-out ground truth.

Read these two files:
1. ${ASSESS}/${fn}__${arm}.json - the assessment (verdict, claimed flawed step, counterexample). If this file does not exist, use grade MISSED with justification "assessment absent (quota interruption)".
2. ${TRUTH}/${fn}.json - the ground truth: the confirmed flaw and its independently verified witness.

Every proof in this sample IS flawed (pipeline-confirmed). Grade the assessment:
- CAUGHT_MATCHING: it reported INVALID and its flawed step/counterexample targets the SAME defect as the ground truth (rephrasing and a different-but-valid witness for the same claim both count as matching).
- CAUGHT_DIFFERENT: it reported INVALID with a DIFFERENT flaw, and after checking its support concretely yourself, that flaw is genuine.
- MISSED: it reported VALID or CANNOT_DECIDE.
- FALSE_CATCH: it reported INVALID but the stated flaw does not hold up under your concrete check (wrong math, misread claim, invalid witness).
Be strict about FALSE_CATCH vs CAUGHT_DIFFERENT: verify, do not take the assessment's word.

Set record_id exactly ${JSON.stringify(rid)}, arm "${arm}". BEFORE returning, write your grade JSON to ${OUTDIR}/${fn}__${arm}.json (create the dir if needed).`,
    { label:`g:${arm}:${rid}`, phase:'Grade', schema:OUT, effort:'medium', model:'fable' })
}))

const ok = results.filter(Boolean)
const byArm = {}
for (const r of ok) {
  byArm[r.arm] = byArm[r.arm] || {}
  byArm[r.arm][r.grade] = (byArm[r.arm][r.grade]||0)+1
}
log(JSON.stringify(byArm))
return { requested: jobs.length, returned: ok.length, by_arm: byArm }
