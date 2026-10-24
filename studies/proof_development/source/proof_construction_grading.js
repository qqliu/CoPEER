export const meta = {
  name: 'proof-construction-grading',
  description: 'Task 7 grading: for each drafted proof, did it commit the documented community pitfall, and is it correct? Graded against held-out ground truth.',
  phases: [{ title: 'Grade' }],
  model: 'opus',
}

// args: { ids: [record_id,...] }  - grades BOTH arms for each id.
//
// Ground truth per record (held out from the drafting agents): the
// known-false claim the community's flawed proof relied on, plus the
// pipeline-confirmed counterexample that kills it. When the claim field is
// empty the counterexample text carries the pitfall's content.
//
// The grader reads the draft file, which unavoidably names its arm; the
// prompt instructs grading on the final_proof text alone. The pitfall check
// is anchored to the ground truth, not to anything the draft says about its
// own process.
const A = (typeof args === 'string') ? JSON.parse(args) : args
if (!A || ((!Array.isArray(A.ids) || !A.ids.length) && !Array.isArray(A.pairs))) throw new Error('args {ids[]} or {pairs[[rid,arm],...]} required')

const BASE = '<mount-root><machine-root>/anonymous-user/new/proof-verification/qedbench_certificate_availability_triage'
const IN = `${BASE}/runs/proof_construction/inputs`
// drafts_dir / out_dir let a SECOND drafting pool (e.g. the gpt-5.6-sol-pro
// replication) be graded by this exact contract without editing it. Defaults
// are the original paths, so existing runs are byte-identical.
const DRAFTS = A.drafts_dir || `${BASE}/runs/proof_construction/drafts`
const TRUTH = `${BASE}/runs/proof_construction/grading_truth`
const OUTDIR = A.out_dir || `${BASE}/runs/proof_construction/grades`

const OUT = { type:'object', additionalProperties:false,
  required:['record_id','arm','pitfall_committed','correctness','notes'],
  properties:{
    record_id:{type:'string'},
    arm:{type:'string',enum:['plain','bugbank']},
    pitfall_committed:{type:'boolean'},
    correctness:{type:'string',enum:['CORRECT','FLAWED','INCOMPLETE']},
    notes:{type:'string'} } }

phase('Grade')
const jobs = []
if (Array.isArray(A.pairs)) jobs.push(...A.pairs)
if (Array.isArray(A.ids)) for (const rid of A.ids) for (const arm of ['plain','bugbank']) jobs.push([rid, arm])
const results = await parallel(jobs.map(([rid, arm]) => () => {
  const fn = rid.replace(/[ /]/g, '_')
  return agent(`You are grading one drafted mathematical proof against held-out ground truth.

Read these three files:
1. ${IN}/${fn}.json - the problem statement the drafter saw.
2. ${DRAFTS}/${fn}__${arm}.json - the draft; grade ONLY its final_proof text on mathematical merits. Ignore every other field (arm, iterations, self-assessment): they describe process, not mathematics.
3. ${TRUTH}/${fn}.json - the documented pitfall: a known-false claim the community's flawed proof of this problem relied on (known_pitfall_claim; if empty, the pitfall is described inside pitfall_counterexample) and the pipeline-confirmed counterexample that kills it.

Report two judgments:
- pitfall_committed: true if the final_proof asserts, relies on, or reproduces the documented pitfall claim (in any phrasing) as a load-bearing step; false if it avoids it or explicitly handles the case the counterexample exposes. Anchor this ONLY to the ground truth, and check against the concrete counterexample: would the counterexample break a step of this draft?
- correctness: read the proof adversarially, hunting for the weakest step. CORRECT only if every load-bearing step is justified and no concrete counterexample you can construct breaks one. FLAWED requires you to name the failing step and the concrete reason in notes (verify your reason yourself before asserting it). INCOMPLETE for real gaps that are not outright false claims.

Be strict: a proof that quietly assumes the pitfall claim commits it, even if it never states it verbatim.

Set record_id exactly ${JSON.stringify(rid)}, arm "${arm}". BEFORE returning, write your grade JSON to ${OUTDIR}/${fn}__${arm}.json (create the dir if needed).`,
    { label:`pg:${arm}:${rid}`, phase:'Grade', schema:OUT, effort:'high', model:'opus' })
}))

const ok = results.filter(Boolean)
const byArm = {}
for (const r of ok) {
  byArm[r.arm] = byArm[r.arm] || { n:0, pitfall:0, correct:0, flawed:0, incomplete:0 }
  const b = byArm[r.arm]; b.n++
  if (r.pitfall_committed) b.pitfall++
  if (r.correctness==='CORRECT') b.correct++
  if (r.correctness==='FLAWED') b.flawed++
  if (r.correctness==='INCOMPLETE') b.incomplete++
}
log(JSON.stringify(byArm))
return { requested: jobs.length, returned: ok.length, by_arm: byArm }
