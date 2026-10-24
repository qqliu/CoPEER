export const meta = {
  name: 'cost-experiment-arms',
  description: 'Paired token-cost experiment: counterexample-first refutation vs whole-proof verification (complete and early-stop variants) on a fixed uniform sample of 100 confirmed-flawed proofs',
  phases: [{ title: 'Assess' }],
  model: 'opus',
}

// args: { ids: [record_id,...], arms?: ['refute','verify_full','verify_earlystop'] }
//
// DESIGN (paper experiment; do not tweak casually):
// - All arms receive IDENTICAL input: the problem statement and the numbered
//   proof, via a per-record input file that contains NOTHING else. Ground truth
//   lives in a separate grading_truth/ directory no assessment agent may read.
// - Neither arm is told the proof is flawed; both are asked to assess it. The
//   arms differ ONLY in mandated METHOD:
//     refute            hunt for one concrete counterexample; stop when found
//     verify_full       judge EVERY numbered step; complete report
//     verify_earlystop  judge steps in order; MAY stop at first definitive failure
//   verify_earlystop is the stronger baseline: if refutation is cheaper even
//   than early-stopping verification, the claim is robust.
// - Token accounting comes from the per-agent transcripts afterwards
//   (scripts/cost_experiment_telemetry.py), NOT from anything an agent reports:
//   self-reported effort is not evidence.
// - Same model and effort for every arm; one file-read tool call per agent
//   (symmetric across arms, counted identically).
const A = (typeof args === 'string') ? JSON.parse(args) : args
if (!A || !Array.isArray(A.ids) || !A.ids.length) throw new Error('args {ids[]} required')
const ARMS = A.arms || ['refute', 'verify_full', 'verify_earlystop']

const IN = '<mount-root><machine-root>/anonymous-user/new/proof-verification/qedbench_certificate_availability_triage/runs/cost_experiment/inputs'
const OUTDIR = '<mount-root><machine-root>/anonymous-user/new/proof-verification/qedbench_certificate_availability_triage/runs/cost_experiment/assessments'

const OUT = { type:'object', additionalProperties:false,
  required:['record_id','arm','verdict','flawed_step','counterexample','reasoning_summary'],
  properties:{
    record_id:{type:'string'},
    arm:{type:'string',enum:['refute','verify_full','verify_earlystop','verify_earlystop_witness']},
    verdict:{type:'string',enum:['VALID','INVALID','CANNOT_DECIDE']},
    flawed_step:{type:'string'},
    counterexample:{type:'string'},
    reasoning_summary:{type:'string'} } }

const METHOD = {
  refute: `METHOD you must follow — COUNTEREXAMPLE-FIRST: read the proof looking for its riskiest concrete claims, and try to construct ONE concrete counterexample (explicit numbers, explicit small structure, explicit trace) to some claim the proof actually relies on. The moment you have a counterexample you have checked carefully, report INVALID with that counterexample and STOP — do not audit the rest of the proof. If after honest effort you cannot refute anything and believe the proof is correct, report VALID with counterexample "".`,
  verify_full: `METHOD you must follow — COMPLETE VERIFICATION: verify the proof step by step. For EVERY numbered step, decide whether it is justified given the problem and the preceding steps, and record a one-line justification or objection per step in reasoning_summary. You must judge every step even after finding a problem. Verdict INVALID if any step fails (name the first failing step in flawed_step), VALID otherwise. counterexample may be "" — your job is verification, not witness construction.`,
  verify_earlystop_witness: `METHOD you must follow — VERIFICATION WITH EARLY STOP, WITNESS REQUIRED: verify the proof step by step in order. For each numbered step, decide whether it is justified given the problem and the preceding steps. You MAY stop at the first step you are certain fails — but a verdict of INVALID is only complete when you ALSO produce a CONCRETE counterexample (explicit numbers, explicit small structure, explicit trace) to that failing step, checked carefully, in the counterexample field. This arm exists to equalize deliverables: your INVALID must come with the same artifact a counterexample-first assessment produces. If you reach the end without a definitive failure, report VALID with counterexample "".`,
  verify_earlystop: `METHOD you must follow — VERIFICATION WITH EARLY STOP: verify the proof step by step in order. For each numbered step, decide whether it is justified given the problem and the preceding steps. You MAY stop at the first step you are certain fails; report INVALID with that step in flawed_step. If you reach the end, report VALID. counterexample may be "" — your job is verification, not witness construction.`,
}

log(`cost experiment: ${A.ids.length} records x ${ARMS.length} arms = ${A.ids.length * ARMS.length} assessments`)

phase('Assess')
const jobs = []
for (const rid of A.ids) for (const arm of ARMS) jobs.push([rid, arm])
const results = await parallel(jobs.map(([rid, arm]) => () => {
  const fn = rid.replace(/[ /]/g, '_')
  return agent(`You are assessing a mathematical proof for correctness. Read ${IN}/${fn}.json — it contains the problem statement and a line-numbered proof. Use ONLY that file: no web, no other files, no code execution.

${METHOD[arm]}

Honesty rules: do not assume the proof is flawed; many proofs are fine. Do not pad. In your structured output set record_id to exactly ${JSON.stringify(rid)} and arm to exactly "${arm}".

BEFORE returning, write your structured answer as JSON to ${OUTDIR}/${fn}__${arm}.json (create the directory if needed) so an interruption cannot destroy completed work.`,
    { label:`${arm}:${rid}`, phase:'Assess', schema:OUT, effort:'high', model:'opus' })
}))

const ok = results.filter(Boolean)
const byArm = {}
for (const r of ok) {
  byArm[r.arm] = byArm[r.arm] || { n:0, INVALID:0, VALID:0, CANNOT_DECIDE:0 }
  byArm[r.arm].n++; byArm[r.arm][r.verdict]++
}
log(`returned ${ok.length}/${jobs.length}: ${JSON.stringify(byArm)}`)
return { requested: jobs.length, returned: ok.length, by_arm: byArm }
