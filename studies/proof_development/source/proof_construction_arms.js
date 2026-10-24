export const meta = {
  name: 'proof-construction-arms',
  description: 'Task 7: BugBank-guided iterative proof drafting vs plain self-critique drafting on 50 problems with documented community pitfalls',
  phases: [{ title: 'Draft' }],
  model: 'fable',
}

// args: { ids: [record_id,...], arms?: ['plain','bugbank'] }
//
// Claim under test: iterating toward a CORRECT proof of a new problem is
// cheaper (tokens to an accepted proof) when each draft's claims are checked
// against BugBank's known-false claims and the hits are fed back, than when
// the model revises by self-critique alone.
//
// Both arms get ONLY the problem statement (never any community proof), the
// same iteration budget (draft + up to 2 revisions), the same model/effort.
// The ONLY difference is the feedback source between iterations:
//   plain    self-critique: re-read your draft, find weaknesses, revise
//   bugbank  mechanical retrieval: extract the draft's claims, query
//            BugBank's refutes field (zero tokens), revise against any
//            matching known-false patterns
// Each problem's documented pitfall (the claim the community's flawed proof
// relied on, confirmed false by our pipeline) is held out for grading: a
// draft that asserts it is mechanically gradable as flawed.
const A = (typeof args === 'string') ? JSON.parse(args) : args
if (!A || ((!Array.isArray(A.ids) || !A.ids.length) && !Array.isArray(A.pairs)))
  throw new Error('args {ids[]} or {pairs[[rid,arm],...]} required')
const ARMS = A.arms || ['plain', 'bugbank']

const BASE = '<mount-root><machine-root>/anonymous-user/new/proof-verification/qedbench_certificate_availability_triage'
const IN = `${BASE}/runs/proof_construction/inputs`
const OUTDIR = `${BASE}/runs/proof_construction/drafts`

const OUT = { type:'object', additionalProperties:false,
  required:['record_id','arm','final_proof','iterations_used','bugbank_hits_acted_on','self_assessment'],
  properties:{
    record_id:{type:'string'},
    arm:{type:'string',enum:['plain','bugbank']},
    final_proof:{type:'string'},
    iterations_used:{type:'integer',minimum:1,maximum:3},
    bugbank_hits_acted_on:{type:'array',items:{type:'string'}},
    self_assessment:{type:'string',enum:['CONFIDENT','UNSURE']} } }

const FEEDBACK = {
  plain: `REVISION PROTOCOL (self-critique): after each draft, re-read it adversarially - hunt for the weakest step, an unjustified claim, a case you skipped - and revise. Up to 2 revisions; stop early only if your adversarial pass finds nothing to attack. Set bugbank_hits_acted_on to [].`,
  bugbank: `REVISION PROTOCOL (BugBank-checked): after each draft:
1. List the draft's load-bearing claims (at most 6 one-sentence statements) into /tmp/claude-24032/pc_claims_RECORDID.json as a JSON list of strings.
2. Run via Bash: python3 ${BASE}/scripts/bugbank_retrieve.py --claims-json /tmp/claude-24032/pc_claims_RECORDID.json -k 3 --out /tmp/claude-24032/pc_hits_RECORDID.json   (a zero-token mechanical lookup of known-false claims) and read the output.
3. If a retrieved known-false pattern matches a claim your draft relies on, your draft is at risk: revise to avoid or properly justify that step, and record the entry_id in bugbank_hits_acted_on.
4. Up to 2 revisions; stop early only if retrieval returns nothing that matches your draft.`,
}

phase('Draft')
// pairs: exact-gap relaunch after a quota kill - draft ONLY the listed
// (record, arm) cells; durable drafts on disk are never re-run.
const jobs = []
if (Array.isArray(A.pairs) && A.pairs.length) jobs.push(...A.pairs)
else for (const rid of A.ids) for (const arm of ARMS) jobs.push([rid, arm])
log(`proof construction: ${jobs.length} (problem, arm) drafts`)
const results = await parallel(jobs.map(([rid, arm]) => () => {
  const fn = rid.replace(/[ /]/g, '_')
  return agent(`You are writing a rigorous, complete mathematical proof. Read ${IN}/${fn}.json - it contains only a problem statement. No web access; do not read any other file in runs/proof_construction/.

Write a full proof of the problem's claim (or, if the claim as stated is false, say so and prove the correction - but do not assume it is false).

${FEEDBACK[arm].replace(/RECORDID/g, fn)}

Your final_proof must be the complete, self-contained final version. Set record_id to exactly ${JSON.stringify(rid)} and arm to "${arm}"; report iterations_used honestly.

BEFORE returning, write your structured answer as JSON to ${OUTDIR}/${fn}__${arm}.json (create the directory if needed).`,
    { label:`${arm}:${rid}`, phase:'Draft', schema:OUT, effort:'high', model:'fable' })
}))

const ok = results.filter(Boolean)
const byArm = {}
for (const r of ok) {
  byArm[r.arm] = byArm[r.arm] || { n:0, acted:0, confident:0 }
  byArm[r.arm].n++
  if ((r.bugbank_hits_acted_on||[]).length) byArm[r.arm].acted++
  if (r.self_assessment==='CONFIDENT') byArm[r.arm].confident++
}
log(`returned ${ok.length}/${jobs.length}: ${JSON.stringify(byArm)}`)
return { requested: jobs.length, returned: ok.length, by_arm: byArm }
