#!/usr/bin/env node

/* Resumable, fail-closed runner for the paired open-frontier experiment. */

import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  closeSync, existsSync, lstatSync, mkdirSync, openSync, readFileSync,
  readdirSync, realpathSync, renameSync, rmSync, statSync, writeFileSync,
} from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const BASE = resolve(HERE, '..');
const REPO = resolve(BASE, '..');
const INPUTS = join(BASE, 'runs', 'open_frontier_fable', 'inputs');
const RUN = join(BASE, 'runs', 'open_frontier_paired_v2_20260901');
const BASELINE_SCHEMA = join(RUN, 'schemas', 'baseline.schema.json');
const AUDIT_SCHEMA = join(RUN, 'schemas', 'audit.schema.json');
const REVISION_SCHEMA = join(RUN, 'schemas', 'revision.schema.json');
const ACTIVE_BASELINE_SCHEMA = join(RUN, 'schemas', 'baseline_whole_proof_v2.schema.json');
const ACTIVE_REVISION_SCHEMA = join(RUN, 'schemas', 'revision_whole_proof_v2.schema.json');
// Keep the legacy program byte-for-byte: all pre-cutover receipts bind its
// exact path and hash.  Only newly materialized receipts use the whole-proof
// v2 program.
const LEGACY_FEEDBACK_SCRIPT = join(HERE, 'open_frontier_paired_v2_feedback.py');
const ACTIVE_FEEDBACK_SCRIPT = join(HERE, 'open_frontier_paired_v2_feedback_whole_proof_v2.py');
const STOCK_RETRIEVER = join(HERE, 'bugbank_retrieve.py');
const BUGBANK_DB = join(REPO, 'BugBank', 'bugbank.sqlite');
const STOP_FILE = process.env.OPEN_FRONTIER_PAIRED_V2_STOP_FILE ||
  '<workspace-home>/paired_v2_ops/STOP_REQUESTED';
const stopRequested = () => !dryRun && existsSync(STOP_FILE);
const RUN_ID = 'open_frontier_paired_v2_20260901';
const LEGACY_RECEIPT_SCHEMA = 'open_frontier_paired_v2_bugbank_exposure_receipt_v1';
const ACTIVE_RECEIPT_SCHEMA = 'open_frontier_paired_v2_bugbank_exposure_receipt_v2';
const CLAIM_COVERAGE_POLICY = 'WHOLE_PROOF_UNCAPPED_V2';
const PROMPT_SCHEMA = 'open_frontier_paired_v2_prompt_exposure_v1';
const AUDIT_METADATA_SCHEMA = 'open_frontier_paired_v2_audit_metadata_v1';
const TERMINAL_SCHEMA = 'open_frontier_paired_v2_pair_terminal_v3';
const RETRIEVAL_K = 3;
// This is an operational batch ceiling, not a scientific stopping condition.
// The user-requested protocol runs to proof-state closure and token matching;
// raise this ceiling and resume if any arm ever reaches it unfinished.
const PROTOCOL_MAX_ITERATIONS = 50;
const REQUESTED_MODEL = 'gpt-5.6-sol';
const REQUESTED_REASONING_EFFORT = 'max';

function arg(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const stage = arg('stage', 'baseline');
const concurrency = Number(arg('concurrency', '6'));
const iterationArgument = arg('iteration', null);
const requestedIteration = iterationArgument === null ? null : Number(iterationArgument);
const maxIterations = Number(arg('max-iterations', String(PROTOCOL_MAX_ITERATIONS)));
const retrievalK = Number(arg('k', String(RETRIEVAL_K)));
const dryRun = process.argv.includes('--dry-run');
const only = new Set((arg('only', '') || '').split(',').filter(Boolean));
const exclude = new Set((arg('exclude', '') || '').split(',').filter(Boolean));
const selectedCells = new Set((arg('cells', '') || '').split(',').filter(Boolean));
const recoveryRunnerPids = new Set((arg('recover-runner-pids', '') || '').split(',')
  .filter(Boolean).map((value) => Number(value)));
const stages = new Set([
  'baseline', 'audit-baseline', 'receipt', 'revision', 'audit-revision',
  'terminal', 'all', 'validate', 'recover-revisions',
]);
if (!stages.has(stage)) throw new Error(`unsupported stage: ${stage}`);
if (!Number.isInteger(concurrency) || concurrency < 1) throw new Error('concurrency must be positive');
if (!Number.isInteger(maxIterations) || maxIterations < 1 || maxIterations > PROTOCOL_MAX_ITERATIONS) {
  throw new Error(`max-iterations must be in [1, ${PROTOCOL_MAX_ITERATIONS}]`);
}
if (retrievalK !== RETRIEVAL_K) throw new Error(`retrieval depth is fixed at k=${RETRIEVAL_K}`);
if (['receipt', 'revision', 'audit-revision'].includes(stage) &&
    (!Number.isInteger(requestedIteration) || requestedIteration < 1 || requestedIteration > maxIterations)) {
  throw new Error(`--iteration in [1, ${maxIterations}] is required for ${stage}`);
}
if ([...selectedCells].some((cell) => !/^[A-Za-z0-9_.-]+:(plain|bugbank)$/.test(cell))) {
  throw new Error('--cells must be a comma-separated list of record_id:plain|bugbank');
}
if (stage === 'recover-revisions' &&
    (!recoveryRunnerPids.size || [...recoveryRunnerPids].some((pid) => !Number.isInteger(pid) || pid < 1))) {
  throw new Error('--recover-runner-pids is required for recover-revisions');
}

const funIds = JSON.parse(readFileSync(join(BASE, 'runs', 'open_frontier_fable', 'problem_ids.json'), 'utf8'));
const tcsIds = JSON.parse(readFileSync(join(BASE, 'runs', 'open_frontier_fable', 'problem_ids_dagstuhl.json'), 'utf8'));
const allIds = [...funIds, ...tcsIds];
if (new Set(allIds).size !== allIds.length) throw new Error('duplicate source record IDs');
if (!allIds.every((id) => typeof id === 'string' && /^[A-Za-z0-9_.-]+$/.test(id))) {
  throw new Error('unsafe source record ID');
}
const ids = allIds.filter((id) => (only.size === 0 || only.has(id)) && !exclude.has(id));
if (!ids.length) throw new Error('no selected records');

if (!dryRun && stage !== 'validate') {
  for (const directory of [
    'baselines', 'audits/baseline', 'audits/iterations', 'audits/metadata/baseline',
    'audits/metadata/iterations', 'retrievals', 'retrievals_whole_proof_v2',
    'iterations', 'prompts', 'prompts_whole_proof_v2',
    'pair_terminals', 'logs/baseline', 'logs/audit-baseline', 'logs/receipt',
    'logs/revision', 'logs/audit-revision', 'states', 'locks', 'summaries',
  ]) mkdirSync(join(RUN, directory), { recursive: true });
}

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isNonemptyString = (value) => typeof value === 'string' && value.length > 0;
const isSha256 = (value) => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
const isWholeProofPromptMetadata = (value) =>
  isObject(value) && value.claim_coverage_policy === CLAIM_COVERAGE_POLICY;
const sha256Bytes = (value) => createHash('sha256').update(value).digest('hex');
const sha256Text = (value) => sha256Bytes(Buffer.from(value, 'utf8'));
const sha256File = (path) => sha256Bytes(readFileSync(path));
const readJSON = (path) => JSON.parse(readFileSync(path, 'utf8'));

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (isObject(value)) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]));
  }
  return value;
}

const canonicalJSON = (value) => JSON.stringify(canonicalize(value));
function addPayloadHash(value, field = 'metadata_payload_sha256') {
  const copy = structuredClone(value);
  delete copy[field];
  return { ...copy, [field]: sha256Text(canonicalJSON(copy)) };
}
const exactArray = (left, right) => Array.isArray(left) && Array.isArray(right) &&
  left.length === right.length && left.every((value, index) => value === right[index]);
const repoPath = (path) => relative(REPO, path).split(sep).join('/');

function artifact(path) {
  const bytes = readFileSync(path);
  return { path: repoPath(path), sha256: sha256Bytes(bytes), size_bytes: bytes.length };
}

function atomicWrite(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  const temporary = `${path}.tmp.${process.pid}.${Date.now()}`;
  writeFileSync(temporary, data);
  renameSync(temporary, path);
}

function writeExclusiveOrVerify(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  try {
    const descriptor = openSync(path, 'wx', 0o644);
    try { writeFileSync(descriptor, data); } finally { closeSync(descriptor); }
    return 'CREATED';
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
    if (!readFileSync(path).equals(Buffer.from(data))) {
      throw new Error(`immutable artifact conflicts with expected bytes: ${path}`);
    }
    return 'EXISTS_IDENTICAL';
  }
}

function countOccurrences(text, needle) {
  if (!needle.length) return 0;
  let count = 0;
  let offset = 0;
  while ((offset = text.indexOf(needle, offset)) !== -1) {
    count += 1;
    offset += needle.length;
  }
  return count;
}

const inputPath = (id) => join(INPUTS, `${id}.json`);
const baselinePath = (id) => join(RUN, 'baselines', `${id}.json`);
const baselineAuditPath = (id) => join(RUN, 'audits', 'baseline', `${id}.json`);
const revisionPath = (id, arm, iteration) => join(RUN, 'iterations', id, arm, `iter_${iteration}.json`);
const revisionAuditPath = (id, arm, iteration) => join(RUN, 'audits', 'iterations', id, arm, `iter_${iteration}.json`);
const legacyReceiptPath = (id, iteration) => join(RUN, 'retrievals', `${id}__iter_${iteration}.json`);
const activeReceiptPath = (id, iteration) => join(RUN, 'retrievals_whole_proof_v2', `${id}__iter_${iteration}.json`);
function receiptPath(id, iteration) {
  const active = activeReceiptPath(id, iteration);
  if (existsSync(active)) return active;
  const legacy = legacyReceiptPath(id, iteration);
  // A legacy receipt remains operative only when it already has a completed
  // child revision. Prepared-only legacy receipts are sealed but inert.
  if (existsSync(legacy) && existsSync(revisionPath(id, 'bugbank', iteration))) return legacy;
  return active;
}
const legacyPromptMetadataPath = (id, arm, iteration) => join(RUN, 'prompts', `${id}__${arm}__iter_${iteration}.json`);
const activePromptMetadataPath = (id, arm, iteration) => join(RUN, 'prompts_whole_proof_v2', `${id}__${arm}__iter_${iteration}.json`);
function promptMetadataPath(id, arm, iteration) {
  const active = activePromptMetadataPath(id, arm, iteration);
  if (existsSync(active)) return active;
  const legacy = legacyPromptMetadataPath(id, arm, iteration);
  // An old prepared prompt records an interrupted attempt; it is not reused
  // for a post-cutover model call.
  if (existsSync(legacy) && existsSync(revisionPath(id, arm, iteration))) return legacy;
  return active;
}
const auditMetadataPath = (id, arm, iteration) => arm === 'neutral'
  ? join(RUN, 'audits', 'metadata', 'baseline', `${id}.json`)
  : join(RUN, 'audits', 'metadata', 'iterations', id, arm, `iter_${iteration}.json`);

function scratchPath(id, stageName, arm = null, iteration = null) {
  const components = ['/tmp/open_frontier_paired_v2', id, stageName];
  if (arm !== null) components.push(arm);
  if (iteration !== null) components.push(`iter_${iteration}`);
  return join(...components);
}

function validResults(results) {
  // `results` is the complete ordered claim inventory, not a six-item window.
  return Array.isArray(results) && results.length >= 1 && results.every((result) =>
    isObject(result) && isNonemptyString(result.claim) && isNonemptyString(result.proof_sketch));
}

function validBaseline(path, id) {
  if (!existsSync(path)) return false;
  try {
    const value = readJSON(path);
    return value.record_id === id && value.stage === 'ARM_NEUTRAL_BASELINE' &&
      ['FULL', 'PARTIAL', 'NONE'].includes(value.claimed_resolution) && validResults(value.results) &&
      isNonemptyString(value.final_writeup) && Array.isArray(value.checks_performed) &&
      value.checks_performed.every(isNonemptyString) && ['CONFIDENT', 'UNSURE'].includes(value.self_assessment);
  } catch { return false; }
}

function expectedAuditOverall(claims) {
  if (claims.some((claim) => claim.verdict === 'REFUTED')) return 'REFUTED';
  if (claims.length && claims.every((claim) => claim.verdict === 'VERIFIED')) return 'VERIFIED';
  return 'INCONCLUSIVE';
}

function expectedClaimedResolutionVerdict(parent, targetVerdict) {
  const claimedRank = { NONE: 0, PARTIAL: 1, FULL: 2 }[parent.claimed_resolution];
  const targetRank = {
    NO_VALID_PROGRESS: 0,
    OVERCLAIMED: 0,
    VALID_PARTIAL_PROGRESS: 1,
    FULLY_RESOLVES_TARGET: 2,
  }[targetVerdict];
  if (!Number.isInteger(claimedRank) || !Number.isInteger(targetRank)) return null;
  if (claimedRank === targetRank) return 'ACCURATE';
  return claimedRank > targetRank ? 'OVERSTATED' : 'UNDERSTATED';
}

function checkerBinding(path, scratch) {
  if (path === 'none') return null;
  if (!isNonemptyString(path) || !path.startsWith('/')) throw new Error('checker_path must be absolute or none');
  if (!resolve(path).startsWith(`${resolve(scratch)}${sep}`)) throw new Error('checker escapes exact scratch directory');
  return { original_scratch_path: path };
}

function liveCheckerArtifact(path, scratch) {
  checkerBinding(path, scratch);
  const realScratch = realpathSync(scratch);
  const realChecker = realpathSync(path);
  if (!realChecker.startsWith(`${realScratch}${sep}`)) throw new Error('checker symlink escapes scratch');
  const info = lstatSync(realChecker);
  if (!info.isFile() || info.isSymbolicLink()) throw new Error('checker is not a regular file');
  return { original_scratch_path: path, sha256: sha256File(realChecker), size_bytes: info.size };
}

function validateAuditValue(value, context) {
  const { id, stageName, arm, iteration, parentHash, parent, scratch } = context;
  if (!isObject(value) || value.record_id !== id || value.stage !== stageName || value.arm !== arm ||
      value.iteration !== iteration || value.parent_sha256 !== parentHash || value.complete !== true ||
      !Array.isArray(value.claims) || value.claims.length !== parent.results.length ||
      !Array.isArray(value.confirmed_refutations) || !Array.isArray(value.checks_performed) ||
      !value.checks_performed.every(isNonemptyString) ||
      !['FULLY_RESOLVES_TARGET', 'VALID_PARTIAL_PROGRESS', 'NO_VALID_PROGRESS', 'OVERCLAIMED'].includes(value.target_verdict) ||
      !['ACCURATE', 'OVERSTATED', 'UNDERSTATED'].includes(value.claimed_resolution_verdict) ||
      !isNonemptyString(value.target_evidence) ||
      value.claimed_resolution_verdict !==
        expectedClaimedResolutionVerdict(parent, value.target_verdict)) return false;
  const checkerRecords = [];
  for (let index = 0; index < value.claims.length; index += 1) {
    const claim = value.claims[index];
    if (!isObject(claim) || claim.idx !== index || claim.claim !== parent.results[index].claim ||
        claim.claim_sha256 !== sha256Text(claim.claim) ||
        !['VERIFIED', 'REFUTED', 'UNRESOLVED'].includes(claim.verdict) ||
        !isNonemptyString(claim.evidence) || !isNonemptyString(claim.witness) ||
        !isNonemptyString(claim.search_method) || !isNonemptyString(claim.checker_path)) return false;
    try {
      const checker = checkerBinding(claim.checker_path, scratch);
      if (checker) checkerRecords.push({ idx: index, ...checker });
    } catch { return false; }
  }
  const refutations = value.claims.filter((claim) => claim.verdict === 'REFUTED').map((claim) => claim.idx);
  if (!exactArray(value.confirmed_refutations, refutations) ||
      new Set(value.confirmed_refutations).size !== value.confirmed_refutations.length ||
      value.overall !== expectedAuditOverall(value.claims)) return false;
  return { checkerRecords };
}

function validAudit(path, context) {
  if (!existsSync(path)) return false;
  try { return Boolean(validateAuditValue(readJSON(path), context)); } catch { return false; }
}

function pythonReceiptPayloadHash(raw) {
  const program = [
    'import hashlib,json,sys',
    'x=json.loads(sys.stdin.buffer.read().decode("utf-8"))',
    'x.pop("receipt_payload_sha256",None)',
    'b=json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":")).encode("utf-8")',
    'sys.stdout.write(hashlib.sha256(b).hexdigest())',
  ].join(';');
  const result = spawnSync('python3', ['-c', program], {
    input: raw, encoding: 'utf8', maxBuffer: 128 * 1024 * 1024,
  });
  if (result.status !== 0 || !isSha256(result.stdout.trim())) throw new Error('receipt hash recomputation failed');
  return result.stdout.trim();
}

const receiptValidationCache = new Map();
function receiptContract(schema) {
  if (schema === LEGACY_RECEIPT_SCHEMA) {
    return { script: LEGACY_FEEDBACK_SCRIPT, wholeProof: false };
  }
  if (schema === ACTIVE_RECEIPT_SCHEMA) {
    return { script: ACTIVE_FEEDBACK_SCRIPT, wholeProof: true };
  }
  return null;
}

function receiptValidation(path, id, iteration, parentPath, parent) {
  if (!existsSync(path)) return { valid: false, error: 'MISSING_RECEIPT' };
  const signature = [id, iteration, path, statSync(path).size, statSync(path).mtimeMs,
    parentPath, statSync(parentPath).size, statSync(parentPath).mtimeMs,
    statSync(BUGBANK_DB).size, statSync(BUGBANK_DB).mtimeMs,
    statSync(LEGACY_FEEDBACK_SCRIPT).size, statSync(LEGACY_FEEDBACK_SCRIPT).mtimeMs,
    statSync(ACTIVE_FEEDBACK_SCRIPT).size, statSync(ACTIVE_FEEDBACK_SCRIPT).mtimeMs,
    statSync(STOCK_RETRIEVER).size, statSync(STOCK_RETRIEVER).mtimeMs].join('|');
  if (receiptValidationCache.has(signature)) return receiptValidationCache.get(signature);
  const result = receiptValidationUncached(path, id, iteration, parentPath, parent);
  receiptValidationCache.set(signature, result);
  return result;
}

function receiptValidationUncached(path, id, iteration, parentPath, parent) {
  if (!existsSync(path)) return { valid: false, error: 'MISSING_RECEIPT' };
  try {
    const rawBytes = readFileSync(path);
    const raw = rawBytes.toString('utf8');
    const value = JSON.parse(raw);
    const contract = receiptContract(value.schema);
    if (!contract) return { valid: false, error: 'UNKNOWN_RECEIPT_SCHEMA' };
    const parentBytes = readFileSync(parentPath);
    const claims = parent.results.map((result, claimIndex) => {
      const claim = {
        claim_index: claimIndex, claim: result.claim, claim_sha256: sha256Text(result.claim),
      };
      if (!contract.wholeProof) return claim;
      const queryText = `${result.claim}\n\n${result.proof_sketch}`;
      return {
        ...claim,
        proof_sketch_sha256: sha256Text(result.proof_sketch),
        query_text_sha256: sha256Text(queryText),
      };
    });
    if (!isObject(value) || value.run_id !== RUN_ID ||
        value.pair_id !== id || value.record_id !== id || value.arm !== 'bugbank' ||
        value.iteration !== iteration || value.stage !== 'BUGBANK_FEEDBACK_EXPOSURE' ||
        value.status !== 'COMPLETE' || value.parent_claim_count !== claims.length ||
        !isObject(value.parent) || value.parent.sha256 !== sha256Bytes(parentBytes) ||
        value.parent.size_bytes !== parentBytes.length || value.parent.record_id !== id ||
        !Array.isArray(value.parent_claims) || value.parent_claims.length !== claims.length ||
        !Array.isArray(value.queries) || value.queries.length !== claims.length ||
        !isObject(value.parameters) || value.parameters.k_per_claim !== RETRIEVAL_K ||
        value.parameters.status_filter !== 'all' || value.parameters.exclude_self !== false ||
        (contract.wholeProof
          ? value.parameters.query_text_basis !== 'claim statement, two newlines, proof_sketch' ||
            value.parameters.salient_term_tie_break !== 'first occurrence in query text'
          : value.parameters.query_text_basis !== undefined ||
            value.parameters.salient_term_tie_break !== 'first occurrence in exact claim') ||
        !isObject(value.invocation) || value.invocation.k !== RETRIEVAL_K ||
        !isObject(value.database) || value.database.sha256 !== sha256File(BUGBANK_DB) ||
        resolve(value.database.path) !== resolve(BUGBANK_DB) ||
        !isObject(value.script) || value.script.sha256 !== sha256File(contract.script) ||
        resolve(value.script.path) !== resolve(contract.script) ||
        (contract.wholeProof && (
          !isObject(value.legacy_script) ||
          value.legacy_script.sha256 !== sha256File(LEGACY_FEEDBACK_SCRIPT) ||
          value.legacy_script.size_bytes !== statSync(LEGACY_FEEDBACK_SCRIPT).size ||
          resolve(value.legacy_script.path) !== resolve(LEGACY_FEEDBACK_SCRIPT)
        )) ||
        (!contract.wholeProof && value.legacy_script !== undefined) ||
        !isObject(value.stock_retriever) || value.stock_retriever.sha256 !== sha256File(STOCK_RETRIEVER) ||
        resolve(value.stock_retriever.path) !== resolve(STOCK_RETRIEVER) ||
        !isSha256(value.receipt_payload_sha256) || value.receipt_payload_sha256 !== pythonReceiptPayloadHash(raw)) {
      return { valid: false, error: 'RECEIPT_CONTRACT_MISMATCH' };
    }
    const retrieved = [];
    const seen = new Set();
    let hitCount = 0;
    for (let index = 0; index < claims.length; index += 1) {
      const expected = claims[index];
      const stored = value.parent_claims[index];
      const query = value.queries[index];
      if (!isObject(stored) || canonicalJSON(stored) !== canonicalJSON(expected) || !isObject(query) ||
          Object.entries(expected).some(([key, wanted]) => query[key] !== wanted) || !Array.isArray(query.hits) ||
          query.hit_count !== query.hits.length) return { valid: false, error: 'RECEIPT_CLAIM_BINDING_MISMATCH' };
      hitCount += query.hits.length;
      for (const hit of query.hits) {
        if (!isObject(hit) || !isNonemptyString(hit.entry_id) || !isSha256(hit.hit_payload_sha256) ||
            !isSha256(hit.entry_payload_sha256) || !isSha256(hit.treatment_content_sha256)) {
          return { valid: false, error: 'INVALID_RECEIPT_HIT' };
        }
        if (!seen.has(hit.entry_id)) { seen.add(hit.entry_id); retrieved.push(hit.entry_id); }
      }
    }
    if (!isObject(value.exposure_summary) || value.exposure_summary.hit_count !== hitCount) {
      return { valid: false, error: 'RECEIPT_HIT_COUNT_MISMATCH' };
    }
    return {
      valid: true, value, raw, file_sha256: sha256Bytes(rawBytes),
      size_bytes: rawBytes.length, retrieved,
    };
  } catch (error) { return { valid: false, error: String(error) }; }
}

function baselinePrompt(id) {
  const input = inputPath(id);
  const scratch = scratchPath(id, 'baseline');
  return `You are the arm-neutral baseline solver for one cell of a preregistered paired experiment.

Read ONLY ${input}. Its "target" is the exact research problem; use "source_paper_text" only for definitions and results already proved there. Do not read BugBank, any prior frontier run, any verification report, or any other solution in the repository. Do not use the web. You may create and run exact-arithmetic checks under ${scratch}, but do not modify repository files.

Produce your strongest rigorous progress from scratch. A FULL result requires a complete proof of the recorded target. Otherwise give precisely scoped partial results, reductions, bounds, special cases, or a concrete counterexample to a natural conjecture. Put every load-bearing claim in its own results item, in proof order. There is no claim-count cap; do not omit a claim merely to keep the list short. Prefer sound claims to speculative breadth. Check finite assertions whenever practical, persist reusable checker programs under the scratch directory, and describe the checks in checks_performed.

Hard limits: final_writeup under 3,000 words and each proof_sketch under 500 words. Return JSON matching the schema, with record_id exactly ${JSON.stringify(id)} and stage exactly "ARM_NEUTRAL_BASELINE". This draft is arm-neutral; do not mention or anticipate an experimental arm.`;
}

function auditPrompt({ id, arm, iteration, parent, parentPath, parentHash, stageName, scratch }) {
  const expected = parent.results.map((result, idx) => ({
    idx, claim: result.claim, claim_sha256: sha256Text(result.claim),
  }));
  const label = arm === 'neutral' ? 'arm-neutral baseline' : `${arm} revision at iteration ${iteration}`;
  return `You are the independent adversarial audit agent for the ${label}.

Read ONLY source input ${inputPath(id)} and draft ${parentPath}. Do not read any retrieval database, treatment receipt, prior frontier run, verification report, or other solution. Do not use the web. Do not trust claimed_resolution or self_assessment.

First judge target coverage independently. Read the exact target, not merely the draft's claim list. target_verdict is FULLY_RESOLVES_TARGET only if the draft proves the entire requested target at the requested strength; VALID_PARTIAL_PROGRESS for correct but incomplete progress; NO_VALID_PROGRESS if nothing material survives; and OVERCLAIMED when the headline/final writeup asserts coverage not established by the claims. Separately judge whether claimed_resolution is ACCURATE, OVERSTATED, or UNDERSTATED. Explain this in target_evidence. A technically true but vacuous, much coarser, or mismatched result does not fully resolve a requested matching/tight classification.

Then audit every listed claim from scratch. Hunt for missing cases, quantifier errors, model or statement mismatches, invalid reductions, and counterexamples. For finite or computational claims, write and run exact-arithmetic checks under ${scratch}; never use floating point for a decision. Persist each checker program under that exact directory and return its absolute path in checker_path. Use literal "none" for witness, search_method, or checker_path only when genuinely inapplicable. A finite counterexample requires a concrete witness and persisted checker. VERIFIED requires a rigorous completed proof; REFUTED requires a concrete reproducible flaw or counterexample; otherwise use UNRESOLVED.

The parent SHA-256 is ${parentHash}. Return record_id ${JSON.stringify(id)}, stage ${stageName}, arm ${arm}, iteration ${iteration}, and parent_sha256 exactly as supplied. Exact claim bindings:
${JSON.stringify(expected, null, 2)}

Preserve every idx, claim, and claim_sha256 exactly. confirmed_refutations must be exactly the increasing idx list for REFUTED claims. overall is REFUTED if any claim is refuted, VERIFIED only if the nonempty list is entirely verified, and INCONCLUSIVE otherwise. Return schema-valid JSON. Do not modify repository files.`;
}

function baseContext(id) {
  const parentPath = baselinePath(id);
  if (!validBaseline(parentPath, id)) return { ok: false, status: 'MISSING_OR_INVALID_BASELINE' };
  const parent = readJSON(parentPath);
  const parentHash = sha256File(parentPath);
  const auditPath = baselineAuditPath(id);
  const auditContext = {
    id, stageName: 'BASELINE_AUDIT', arm: 'neutral', iteration: 0,
    parentHash, parent, scratch: scratchPath(id, 'audit-baseline'),
  };
  if (!validAudit(auditPath, auditContext)) return { ok: false, status: 'MISSING_OR_INVALID_BASELINE_AUDIT' };
  const auditPromptText = auditPrompt({
    id, arm: 'neutral', iteration: 0, parent, parentPath, parentHash,
    stageName: 'BASELINE_AUDIT', scratch: auditContext.scratch,
  });
  if (!validAuditMetadata(id, 'neutral', 0, readJSON(auditPath), auditContext, auditPromptText)) {
    return { ok: false, status: 'MISSING_OR_INVALID_BASELINE_AUDIT_METADATA' };
  }
  return {
    ok: true, parentPath, parent, parentHash, auditPath,
    audit: readJSON(auditPath), auditHash: sha256File(auditPath),
  };
}

function validRevisionCore(value) {
  return isObject(value) && ['FULL', 'PARTIAL', 'NONE'].includes(value.claimed_resolution) &&
    validResults(value.results) && isNonemptyString(value.final_writeup) &&
    Array.isArray(value.audit_feedback_acted_on) && value.audit_feedback_acted_on.every(isNonemptyString) &&
    Array.isArray(value.checks_performed) && value.checks_performed.every(isNonemptyString) &&
    ['CONFIDENT', 'UNSURE'].includes(value.self_assessment) &&
    Array.isArray(value.retrieved_entry_ids) && Array.isArray(value.acted_on_entry_ids) &&
    Array.isArray(value.dismissed_hits);
}

function validateTreatmentPartition(value, retrieved) {
  if (!exactArray(value.retrieved_entry_ids, retrieved) ||
      !value.acted_on_entry_ids.every(isNonemptyString) ||
      new Set(value.acted_on_entry_ids).size !== value.acted_on_entry_ids.length) return false;
  const retrievedSet = new Set(retrieved);
  if (!value.acted_on_entry_ids.every((entryId) => retrievedSet.has(entryId))) return false;
  const actedSet = new Set(value.acted_on_entry_ids);
  if (!exactArray(value.acted_on_entry_ids, retrieved.filter((entryId) => actedSet.has(entryId)))) return false;
  if (!value.dismissed_hits.every((item) => isObject(item) && isNonemptyString(item.entry_id) &&
      isNonemptyString(item.reason))) return false;
  const dismissed = value.dismissed_hits.map((item) => item.entry_id);
  return new Set(dismissed).size === dismissed.length &&
    exactArray(dismissed, retrieved.filter((entryId) => !actedSet.has(entryId)));
}

function validateRevisionValue(value, { id, arm, iteration, context, receipt }) {
  if (!validRevisionCore(value) || value.record_id !== id || value.stage !== 'REVISION' ||
      value.arm !== arm || value.iteration !== iteration || value.parent_sha256 !== context.parentHash ||
      value.audit_sha256 !== context.auditHash) return false;
  if (arm === 'plain') {
    return value.treatment_status === 'PLAIN_SELF_CRITIQUE' && value.receipt_path === '' &&
      value.receipt_sha256 === '' && exactArray(value.retrieved_entry_ids, []) &&
      exactArray(value.acted_on_entry_ids, []) && exactArray(value.dismissed_hits, []);
  }
  return receipt?.valid && value.treatment_status === 'BUGBANK_RECEIPT_EXPOSED' &&
    value.receipt_path === repoPath(receiptPath(id, iteration)) &&
    value.receipt_sha256 === receipt.file_sha256 &&
    validateTreatmentPartition(value, receipt.retrieved);
}

function normalizeRevisionTemporary(path, { id, arm, iteration, context, receipt }) {
  const value = readJSON(path);
  if (!validRevisionCore(value)) throw new Error('revision output lacks substantive fields');
  if (arm === 'plain' && (value.acted_on_entry_ids.length || value.dismissed_hits.length)) {
    throw new Error('plain output attempted treatment bookkeeping');
  }
  const wrapper = arm === 'plain' ? {
    treatment_status: 'PLAIN_SELF_CRITIQUE', receipt_path: '', receipt_sha256: '',
    retrieved_entry_ids: [], acted_on_entry_ids: [], dismissed_hits: [],
  } : {
    treatment_status: 'BUGBANK_RECEIPT_EXPOSED',
    receipt_path: repoPath(receiptPath(id, iteration)), receipt_sha256: receipt.file_sha256,
    retrieved_entry_ids: receipt.retrieved, acted_on_entry_ids: value.acted_on_entry_ids,
    dismissed_hits: value.dismissed_hits,
  };
  const normalized = {
    ...value, record_id: id, stage: 'REVISION', arm, iteration,
    parent_sha256: context.parentHash, audit_sha256: context.auditHash, ...wrapper,
  };
  if (!validateRevisionValue(normalized, { id, arm, iteration, context, receipt })) {
    throw new Error('revision failed wrapper lineage/treatment validation');
  }
  writeFileSync(path, JSON.stringify(normalized, null, 2) + '\n');
}

function buildRevisionPromptBundle(id, arm, iteration, context, receipt = null) {
  const sourceRaw = readFileSync(inputPath(id), 'utf8');
  const parentRaw = readFileSync(context.parentPath, 'utf8');
  const auditRaw = readFileSync(context.auditPath, 'utf8');
  const scratch = scratchPath(id, 'revision', arm, iteration);
  // No iteration-3 prompt existed when the proof-state/token-matching protocol
  // was adopted.  Version the additional closure instruction at that clean
  // boundary so immutable iteration-1/2 prompt receipts remain reproducible.
  const closureInstruction = iteration >= 3 ? `
Proof-state closure is exact over claimed_resolution, every claim and proof_sketch in results, and final_writeup. If no material correction is required, copy those fields from the parent exactly; do not paraphrase or polish them. Bookkeeping fields may change independently.

` : '';
  const common = `You are revising one open-problem draft in a controlled paired experiment.

Read only source ${inputPath(id)}, exact parent ${context.parentPath}, and its independent audit ${context.auditPath}. The source defines the target. Parent SHA-256: ${context.parentHash}. Audit SHA-256: ${context.auditHash}. Do not use the web, prior frontier outputs, other solutions, or verification reports. Write exact-arithmetic checks only under ${scratch}; do not modify repository files.

Respond to every REFUTED or UNRESOLVED item and to the target-coverage and claimed-resolution judgments. Preserve correct progress; repair, narrow, replace, or remove unsupported claims. Do not call an open target solved without a complete proof at the requested strength. Keep exact claim wording when it remains correct; gratuitous rewording prevents a reproducible fixed point. Preserve every current load-bearing claim and add a separate results item for every new load-bearing claim when the proof expands. There is no claim-count cap. Keep final_writeup under 3,000 words and each proof_sketch under 500 words.

${closureInstruction}The complete independent audit follows verbatim:
--- BEGIN INDEPENDENT AUDIT ---
${auditRaw}--- END INDEPENDENT AUDIT ---

`;
  let prompt;
  let exposure;
  if (arm === 'plain') {
    const inputTokenCount = [sourceRaw, parentRaw, auditRaw].reduce(
      (sum, text) => sum + (text.match(/bugbank/gi) || []).length, 0,
    );
    prompt = `${common}Use native adversarial self-critique and the independent audit only. Do not read a retrieval database, retrieval result, treatment receipt, or external memory. Return revision-schema JSON. Use treatment_status PLAIN_SELF_CRITIQUE; empty receipt_path and receipt_sha256; and empty retrieved_entry_ids, acted_on_entry_ids, and dismissed_hits. The wrapper independently normalizes those fields.`;
    const markerCount = countOccurrences(prompt, '--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---');
    const forbiddenHashes = [sha256File(BUGBANK_DB)];
    const pairedReceiptPath = receiptPath(id, iteration);
    if (existsSync(pairedReceiptPath)) {
      forbiddenHashes.push(sha256File(pairedReceiptPath));
      try { forbiddenHashes.push(readJSON(pairedReceiptPath).receipt_payload_sha256); } catch { /* invalid receipt fails its own arm */ }
    }
    const exposedForbiddenHashes = forbiddenHashes.filter(
      (hash) => isSha256(hash) && prompt.includes(hash),
    );
    if (markerCount || exposedForbiddenHashes.length) {
      throw new Error('plain prompt contains a receipt marker or pinned treatment hash');
    }
    exposure = {
      complete_receipt_payload_embedded: false, receipt_verbatim_occurrences: 0,
      receipt_start_byte: null, receipt_end_byte: null,
      plain_input_treatment_name_token_count: inputTokenCount,
      prompt_treatment_name_token_count: (prompt.match(/bugbank/gi) || []).length,
      complete_receipt_marker_count: markerCount,
      exposed_forbidden_treatment_hashes: exposedForbiddenHashes,
      retrieved_entry_ids: [],
    };
  } else {
    if (!receipt?.valid) throw new Error('valid receipt required for treated prompt');
    const actionSemantics = iteration >= 3
      ? ' In this closure protocol, list an ID in acted_on_entry_ids only when this iteration materially changes the proof state because of that record. If the parent already addresses the risk and no new proof change is needed, put the ID in dismissed_hits and state that reason.'
      : '';
    const prefix = `${common}Use the following complete BugBank exposure receipt as diagnostic memory, not authority. Independently check every applicable counterexample and hypothesis warning. For every unique retrieved ID, either list it in acted_on_entry_ids or give a specific reason in dismissed_hits.${actionSemantics} Preserve first-retrieval order; the two lists must partition retrieved_entry_ids. The wrapper owns all lineage and exposure fields.

--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---
`;
    const suffix = `--- END COMPLETE BUGBANK EXPOSURE RECEIPT ---

Return revision-schema JSON. Use treatment_status BUGBANK_RECEIPT_EXPOSED and receipt_path ${JSON.stringify(repoPath(receiptPath(id, iteration)))}. Exact unique retrieved_entry_ids in first-retrieval order:
${JSON.stringify(receipt.retrieved, null, 2)}`;
    prompt = `${prefix}${receipt.raw}${suffix}`;
    const occurrences = countOccurrences(prompt, receipt.raw);
    if (occurrences !== 1) throw new Error(`receipt verbatim occurrence count is ${occurrences}`);
    const characterOffset = prompt.indexOf(receipt.raw);
    const startByte = Buffer.byteLength(prompt.slice(0, characterOffset), 'utf8');
    exposure = {
      complete_receipt_payload_embedded: true, receipt_verbatim_occurrences: occurrences,
      receipt_start_byte: startByte, receipt_end_byte: startByte + receipt.size_bytes,
      plain_input_treatment_name_token_count: null,
      prompt_treatment_name_token_count: (prompt.match(/bugbank/gi) || []).length,
      retrieved_entry_ids: receipt.retrieved,
    };
  }
  const promptBytes = Buffer.from(prompt, 'utf8');
  const source = artifact(inputPath(id));
  const parent = artifact(context.parentPath);
  const audit = artifact(context.auditPath);
  const receiptMetadata = arm === 'plain' ? null : {
    path: repoPath(receiptPath(id, iteration)), sha256: receipt.file_sha256,
    size_bytes: receipt.size_bytes, receipt_payload_sha256: receipt.value.receipt_payload_sha256,
  };
  const expectedMetadata = {
    schema: PROMPT_SCHEMA, run_id: RUN_ID, record_id: id, stage: 'REVISION_PROMPT', arm, iteration,
    claim_coverage_policy: CLAIM_COVERAGE_POLICY,
    treatment_status: arm === 'plain' ? 'PLAIN_SELF_CRITIQUE' : 'BUGBANK_RECEIPT_EXPOSED',
    bugbank_exposed: arm === 'bugbank', prompt_text: prompt,
    prompt_utf8_sha256: sha256Bytes(promptBytes), prompt_size_bytes: promptBytes.length,
    source, parent, audit, receipt: receiptMetadata, exposure,
    requested_execution: {
      model: REQUESTED_MODEL, reasoning_effort: REQUESTED_REASONING_EFFORT,
      sandbox: 'workspace-write', working_directory: scratch,
      repository_writes_forbidden: true,
    },
  };
  return { prompt, expectedMetadata, scratch };
}

function validatePromptMetadataValue(value, { id, arm, iteration, context, receipt }) {
  if (!isObject(value) || !isNonemptyString(value.created_at) ||
      value.schema !== PROMPT_SCHEMA || value.run_id !== RUN_ID || value.record_id !== id ||
      value.stage !== 'REVISION_PROMPT' || value.arm !== arm || value.iteration !== iteration ||
      !isNonemptyString(value.prompt_text) ||
      value.prompt_size_bytes !== Buffer.byteLength(value.prompt_text, 'utf8') ||
      value.prompt_utf8_sha256 !== sha256Text(value.prompt_text) ||
      canonicalJSON(value.source) !== canonicalJSON(artifact(inputPath(id))) ||
      canonicalJSON(value.parent) !== canonicalJSON(artifact(context.parentPath)) ||
      canonicalJSON(value.audit) !== canonicalJSON(artifact(context.auditPath)) ||
      !value.prompt_text.includes(readFileSync(context.auditPath, 'utf8')) ||
      !value.prompt_text.includes(inputPath(id)) || !value.prompt_text.includes(context.parentPath) ||
      !isObject(value.requested_execution) || value.requested_execution.model !== REQUESTED_MODEL ||
      value.requested_execution.reasoning_effort !== REQUESTED_REASONING_EFFORT ||
      value.requested_execution.sandbox !== 'workspace-write' ||
      value.requested_execution.repository_writes_forbidden !== true) return false;
  const withoutHash = structuredClone(value);
  delete withoutHash.metadata_payload_sha256;
  if (value.metadata_payload_sha256 !== sha256Text(canonicalJSON(withoutHash))) return false;
  const marker = '--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---';
  if (arm === 'plain') {
    if (!isObject(value.exposure) || value.exposure.complete_receipt_payload_embedded !== false ||
        value.exposure.receipt_verbatim_occurrences !== 0 ||
        value.exposure.receipt_start_byte !== null || value.exposure.receipt_end_byte !== null ||
        !exactArray(value.exposure.retrieved_entry_ids, []) ||
        value.exposure.prompt_treatment_name_token_count !==
          (value.prompt_text.match(/bugbank/gi) || []).length) return false;
    if (value.treatment_status !== 'PLAIN_SELF_CRITIQUE' || value.bugbank_exposed !== false ||
        value.receipt !== null || value.prompt_text.includes(marker) ||
        value.prompt_text.includes(sha256File(BUGBANK_DB))) return false;
    const pairedPath = receiptPath(id, iteration);
    if (existsSync(pairedPath)) {
      const pairedHash = sha256File(pairedPath);
      let payloadHash = null;
      try { payloadHash = readJSON(pairedPath).receipt_payload_sha256; } catch { /* other arm validates it */ }
      if (value.prompt_text.includes(pairedHash) ||
          (isSha256(payloadHash) && value.prompt_text.includes(payloadHash))) return false;
    }
    return true;
  }
  const receiptCharacterOffset = value.prompt_text.indexOf(receipt.raw);
  const receiptStartByte = receiptCharacterOffset < 0 ? -1
    : Buffer.byteLength(value.prompt_text.slice(0, receiptCharacterOffset), 'utf8');
  if (!isObject(value.exposure) || value.exposure.complete_receipt_payload_embedded !== true ||
      value.exposure.receipt_verbatim_occurrences !== 1 ||
      value.exposure.receipt_start_byte !== receiptStartByte ||
      value.exposure.receipt_end_byte !== receiptStartByte + receipt.size_bytes ||
      !exactArray(value.exposure.retrieved_entry_ids, receipt.retrieved) ||
      value.exposure.prompt_treatment_name_token_count !==
        (value.prompt_text.match(/bugbank/gi) || []).length) return false;
  if (!receipt?.valid || value.treatment_status !== 'BUGBANK_RECEIPT_EXPOSED' ||
      value.bugbank_exposed !== true || countOccurrences(value.prompt_text, receipt.raw) !== 1 ||
      canonicalJSON(value.receipt) !== canonicalJSON({
        path: repoPath(receiptPath(id, iteration)), sha256: receipt.file_sha256,
        size_bytes: receipt.size_bytes, receipt_payload_sha256: receipt.value.receipt_payload_sha256,
      })) return false;
  return true;
}

function ensurePromptMetadata(id, arm, iteration, bundle, context, receipt) {
  const path = promptMetadataPath(id, arm, iteration);
  if (existsSync(path)) {
    const value = readJSON(path);
    return artifact(path);
  }
  const value = addPayloadHash({ ...bundle.expectedMetadata, created_at: new Date().toISOString() });
  const bytes = Buffer.from(JSON.stringify(value, null, 2) + '\n');
  if (!dryRun) {
    try { writeExclusiveOrVerify(path, bytes); }
    catch (error) {
      if (!validPromptMetadata(id, arm, iteration, context, receipt)) throw error;
      return artifact(path);
    }
  }
  return { path: repoPath(path), sha256: sha256Bytes(bytes), size_bytes: bytes.length };
}

function validPromptMetadata(id, arm, iteration, context, receipt) {
  const path = promptMetadataPath(id, arm, iteration);
  if (!existsSync(path)) return false;
  try {
    const value = readJSON(path);
    if (!validatePromptMetadataValue(value, { id, arm, iteration, context, receipt })) return false;
    if (resolve(path).startsWith(`${resolve(join(RUN, 'prompts_whole_proof_v2'))}${sep}`)) {
      return value.claim_coverage_policy === CLAIM_COVERAGE_POLICY &&
        value.prompt_text.includes('There is no claim-count cap.') &&
        !value.prompt_text.includes('Use at most six claims');
    }
    return value.claim_coverage_policy === undefined;
  } catch { return false; }
}

function proofState(value) {
  return {
    claimed_resolution: value.claimed_resolution,
    results: value.results.map((result) => ({
      claim: result.claim,
      proof_sketch: result.proof_sketch,
    })),
    final_writeup: value.final_writeup,
  };
}

function proofStateSha256(value) {
  return sha256Text(canonicalJSON(proofState(value)));
}

function auditableArmCost(id, arm, throughIteration) {
  const costs = executionCosts(id, arm, throughIteration);
  const modelEntries = costs.entries.filter(
    (entry) => entry.stage === 'revision' || entry.stage === 'audit-revision',
  );
  const stateIdentityAndExecutionAreExact = (entry) => {
    if (!isNonemptyString(entry.state_path)) return false;
    try {
      const value = readJSON(resolve(REPO, entry.state_path));
      return value.record_id === id && value.arm === arm &&
        value.iteration === entry.iteration && value.stage === entry.stage &&
        value.model === REQUESTED_MODEL &&
        value.reasoning_effort === REQUESTED_REASONING_EFFORT;
    } catch { return false; }
  };
  const auditable = costs.missing_state_count === 0 && modelEntries.length === 2 * throughIteration &&
    modelEntries.every((entry) => ['COMPLETE', 'RECOVERED_COMPLETE'].includes(entry.status) &&
      Number.isInteger(entry.tokens_used) && entry.tokens_used >= 0 &&
      stateIdentityAndExecutionAreExact(entry));
  const modelTokens = modelEntries.reduce((sum, entry) => sum + entry.tokens_used, 0);
  // A partial sum must never be presented as an arm's completed-call total.
  // Receipt bookkeeping is deliberately excluded even though it is normally
  // zero: endpoint costs are revision and independent-audit model calls only.
  return { ...costs, tokens_used: auditable ? modelTokens : null, auditable };
}

function assessIteration(id, parent, revision, audit, iteration, fixedPointEligible) {
  const claimsUnchanged = exactArray(
    parent.results.map((result) => result.claim), revision.results.map((result) => result.claim),
  );
  const proofUnchanged = canonicalJSON(proofState(parent)) === canonicalJSON(proofState(revision));
  const bugbankRecheckRequired = revision.arm === 'bugbank' &&
    revision.acted_on_entry_ids.length > 0;
  const coverageSettled = audit.claimed_resolution_verdict === 'ACCURATE' &&
    audit.target_verdict !== 'OVERCLAIMED';
  const auditSettled = audit.confirmed_refutations.length === 0 && coverageSettled;
  let tokenBudgetTarget = null;
  let tokenBudgetUsed = null;
  let tokenBudgetMatched = false;
  let tokenBudgetAuditable = false;
  if (revision.arm === 'bugbank') {
    const currentCosts = auditableArmCost(id, 'bugbank', iteration);
    tokenBudgetAuditable = currentCosts.auditable;
    tokenBudgetMatched = tokenBudgetAuditable;
  } else {
    const treated = armProgress(id, 'bugbank');
    const currentCosts = auditableArmCost(id, 'plain', iteration);
    const treatedCosts = treated.terminal
      ? auditableArmCost(id, 'bugbank', treated.iteration)
      : null;
    tokenBudgetUsed = currentCosts.tokens_used;
    tokenBudgetAuditable = currentCosts.auditable && treated.terminal &&
      treatedCosts?.auditable === true;
    if (treated.terminal) tokenBudgetTarget = treatedCosts.tokens_used;
    tokenBudgetMatched = tokenBudgetAuditable && Number.isInteger(tokenBudgetTarget) &&
      tokenBudgetUsed >= tokenBudgetTarget;
  }
  const solvedByAudit = verifiedFullAudit(revision, audit);
  if (solvedByAudit) {
    // The first strict independent audit that verifies the exact target is a
    // solution endpoint for either arm. Do not spend more calls merely to
    // reach an unchanged-proof iteration or match the other arm's tokens.
    return {
      status: 'VERIFIED_FULL', terminal: true,
      terminal_reason: 'VERIFIED_FULL_INDEPENDENT_AUDIT',
      fixed_point: proofUnchanged,
      waiting_for_bugbank_budget: false,
      ordered_claim_set_unchanged: claimsUnchanged, proof_state_unchanged: proofUnchanged,
      parent_proof_state_sha256: proofStateSha256(parent),
      revision_proof_state_sha256: proofStateSha256(revision),
      bugbank_recheck_required: false, token_budget_target: tokenBudgetTarget,
      token_budget_used: tokenBudgetUsed, token_budget_matched: tokenBudgetMatched,
      token_budget_auditable: tokenBudgetAuditable, every_claim_verified: true,
      iteration_limit_reached: iteration >= maxIterations,
      reason: 'The independent audit verified every claim and the full exact target; the arm stops at this first correct solution without further refinement or token matching.',
    };
  }
  const fixed = fixedPointEligible && proofUnchanged && !bugbankRecheckRequired &&
    auditSettled && tokenBudgetMatched;
  if (fixed) {
    const everyClaimVerified = audit.claims.length > 0 && audit.claims.every((claim) => claim.verdict === 'VERIFIED');
    const verifiedFull = everyClaimVerified && revision.claimed_resolution === 'FULL' &&
      audit.target_verdict === 'FULLY_RESOLVES_TARGET' && audit.claimed_resolution_verdict === 'ACCURATE';
    return {
      status: verifiedFull ? 'VERIFIED_FULL' : 'INCONCLUSIVE_FIXED_POINT', terminal: true,
      terminal_reason: 'AUDITED_FIXED_POINT', fixed_point: true,
      waiting_for_bugbank_budget: false,
      ordered_claim_set_unchanged: claimsUnchanged, proof_state_unchanged: true,
      parent_proof_state_sha256: proofStateSha256(parent),
      revision_proof_state_sha256: proofStateSha256(revision),
      bugbank_recheck_required: false, token_budget_target: tokenBudgetTarget,
      token_budget_used: tokenBudgetUsed, token_budget_matched: tokenBudgetMatched,
      token_budget_auditable: tokenBudgetAuditable, every_claim_verified: everyClaimVerified,
      reason: verifiedFull
        ? 'Audited proof-state fixed point fully resolves the target; every claim is verified and the arm budget condition is met.'
        : 'Audited proof-state fixed point is sound against confirmed refutation and meets the arm budget condition, but does not fully resolve the target.',
    };
  }
  let reason;
  if (!proofUnchanged) {
    reason = revision.arm === 'bugbank'
      ? 'The proof state changed; the new proof requires a fresh BugBank retrieval, revision, and independent audit.'
      : 'The proof state changed; another native self-refinement and independent audit are required.';
  } else if (bugbankRecheckRequired) {
    reason = 'BugBank feedback was acted on; the revised proof requires a fresh BugBank retrieval, revision, and audit cycle.';
  } else if (!auditSettled) {
    reason = 'A refutation or target/label audit issue remains actionable.';
  } else if (revision.arm === 'bugbank' && !tokenBudgetAuditable) {
    reason = 'The BugBank completed-call token total is not fully auditable from model-call states.';
  } else if (revision.arm === 'plain' && tokenBudgetTarget === null) {
    reason = 'The plain arm is waiting for the BugBank arm to reach a terminal proof state and establish its token target.';
  } else if (revision.arm === 'plain' && !tokenBudgetAuditable) {
    reason = 'The matched-token comparison is not fully auditable from completed model-call states.';
  } else if (revision.arm === 'plain' && !tokenBudgetMatched) {
    reason = `The plain arm has used ${tokenBudgetUsed} recorded tokens, below the BugBank target ${tokenBudgetTarget}; another self-refinement cycle is required.`;
  } else {
    reason = 'The arm has not met every proof-state closure condition.';
  }
  return {
    status: 'CONTINUE', terminal: false, terminal_reason: null, fixed_point: false,
    waiting_for_bugbank_budget: fixedPointEligible && revision.arm === 'plain' && proofUnchanged &&
      !bugbankRecheckRequired && auditSettled && tokenBudgetTarget === null,
    iteration_limit_reached: iteration >= maxIterations,
    ordered_claim_set_unchanged: claimsUnchanged, proof_state_unchanged: proofUnchanged,
    parent_proof_state_sha256: proofStateSha256(parent),
    revision_proof_state_sha256: proofStateSha256(revision),
    bugbank_recheck_required: bugbankRecheckRequired,
    token_budget_target: tokenBudgetTarget, token_budget_used: tokenBudgetUsed,
    token_budget_matched: tokenBudgetMatched, token_budget_auditable: tokenBudgetAuditable,
    every_claim_verified: audit.claims.length > 0 && audit.claims.every((claim) => claim.verdict === 'VERIFIED'),
    reason,
  };
}

function auditContextForRevision(id, arm, iteration, revision) {
  const path = revisionPath(id, arm, iteration);
  return {
    id, stageName: 'REVISION_AUDIT', arm, iteration,
    parentHash: sha256File(path), parent: revision,
    scratch: scratchPath(id, 'audit-revision', arm, iteration),
  };
}

function verifiedFullAudit(revision, audit) {
  return isObject(audit) && audit.complete === true &&
    Array.isArray(revision.results) && Array.isArray(audit.claims) &&
    audit.claims.length === revision.results.length && audit.claims.length > 0 &&
    audit.claims.every((claim) => claim.verdict === 'VERIFIED') &&
    audit.overall === 'VERIFIED' &&
    Array.isArray(audit.confirmed_refutations) && audit.confirmed_refutations.length === 0 &&
    revision.claimed_resolution === 'FULL' &&
    audit.target_verdict === 'FULLY_RESOLVES_TARGET' &&
    audit.claimed_resolution_verdict === 'ACCURATE';
}

function auditMetadataBase(id, arm, iteration, audit, context, prompt) {
  const validation = validateAuditValue(audit, context);
  if (!validation) throw new Error('invalid audit cannot have metadata');
  const promptBytes = Buffer.from(prompt, 'utf8');
  const parentPath = arm === 'neutral' ? baselinePath(id) : revisionPath(id, arm, iteration);
  return {
    schema: AUDIT_METADATA_SCHEMA, run_id: RUN_ID, record_id: id,
    stage: context.stageName, arm, iteration,
    source: artifact(inputPath(id)), parent: artifact(parentPath),
    prompt_text: prompt, prompt_utf8_sha256: sha256Bytes(promptBytes),
    prompt_size_bytes: promptBytes.length,
    requested_execution: {
      model: REQUESTED_MODEL, reasoning_effort: REQUESTED_REASONING_EFFORT,
      sandbox: 'workspace-write', working_directory: context.scratch,
      repository_writes_forbidden: true,
    },
  };
}

function archiveCheckerArtifacts(id, arm, iteration, audit, context) {
  const directory = arm === 'neutral'
    ? join(RUN, 'checkers', 'audits', 'baseline', id)
    : join(RUN, 'checkers', 'audits', 'iterations', id, arm, `iter_${iteration}`);
  const records = [];
  for (let idx = 0; idx < audit.claims.length; idx += 1) {
    const checkerPath = audit.claims[idx].checker_path;
    if (checkerPath === 'none') continue;
    const live = liveCheckerArtifact(checkerPath, context.scratch);
    const destination = join(directory, `claim_${idx}__${live.sha256}.checker`);
    const bytes = readFileSync(checkerPath);
    writeExclusiveOrVerify(destination, bytes);
    records.push({
      idx, original_scratch_path: checkerPath, original_sha256: live.sha256,
      original_size_bytes: live.size_bytes, durable: artifact(destination),
    });
  }
  return records;
}

function ensureAuditMetadata(id, arm, iteration, audit, context, prompt) {
  const value = addPayloadHash({
    ...auditMetadataBase(id, arm, iteration, audit, context, prompt),
    checker_artifacts: archiveCheckerArtifacts(id, arm, iteration, audit, context),
  });
  const path = auditMetadataPath(id, arm, iteration);
  const bytes = Buffer.from(JSON.stringify(value, null, 2) + '\n');
  if (!dryRun && existsSync(path) && !readFileSync(path).equals(bytes)) {
    const legacy = `${path}.pre_durable_v1`;
    writeExclusiveOrVerify(legacy, readFileSync(path));
    atomicWrite(path, bytes);
  } else if (!dryRun) {
    writeExclusiveOrVerify(path, bytes);
  }
  return { path, value };
}

function validAuditMetadata(id, arm, iteration, audit, context, prompt) {
  const path = auditMetadataPath(id, arm, iteration);
  if (!existsSync(path)) return false;
  try {
    const value = readJSON(path);
    const withoutHash = structuredClone(value);
    delete withoutHash.metadata_payload_sha256;
    if (value.metadata_payload_sha256 !== sha256Text(canonicalJSON(withoutHash))) return false;
    const checkerRecords = withoutHash.checker_artifacts;
    delete withoutHash.checker_artifacts;
    if (canonicalJSON(withoutHash) !==
        canonicalJSON(auditMetadataBase(id, arm, iteration, audit, context, prompt))) return false;
    if (!Array.isArray(checkerRecords)) return false;
    const expectedIndices = audit.claims.map((claim, idx) => claim.checker_path === 'none' ? null : idx)
      .filter((idx) => idx !== null);
    if (!exactArray(checkerRecords.map((record) => record.idx), expectedIndices)) return false;
    for (const record of checkerRecords) {
      if (!isObject(record) || record.original_scratch_path !== audit.claims[record.idx].checker_path ||
          !isSha256(record.original_sha256) || !Number.isInteger(record.original_size_bytes) ||
          !isObject(record.durable) || !isSha256(record.durable.sha256) ||
          !Number.isInteger(record.durable.size_bytes)) return false;
      checkerBinding(record.original_scratch_path, context.scratch);
      const durablePath = resolve(REPO, record.durable.path);
      const durableRoot = resolve(RUN, 'checkers', 'audits');
      if (!durablePath.startsWith(`${durableRoot}${sep}`) || !existsSync(durablePath)) return false;
      const durable = artifact(durablePath);
      if (canonicalJSON(durable) !== canonicalJSON(record.durable) ||
          durable.sha256 !== record.original_sha256 ||
          durable.size_bytes !== record.original_size_bytes) return false;
    }
    return true;
  } catch { return false; }
}

function completedIteration(id, arm, iteration) {
  const context = iterationContext(id, arm, iteration);
  if (!context.ok) return context;
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = receiptValidation(receiptPath(id, iteration), id, iteration, context.parentPath, context.parent);
    if (!receipt.valid) return { ok: false, status: receipt.error, error: receipt.error };
  }
  let bundle;
  try { bundle = buildRevisionPromptBundle(id, arm, iteration, context, receipt); }
  catch (error) { return { ok: false, status: 'INVALID_PROMPT_INPUT', error: String(error) }; }
  if (!validPromptMetadata(id, arm, iteration, context, receipt)) {
    return { ok: false, status: 'MISSING_OR_INVALID_PROMPT_METADATA' };
  }
  const path = revisionPath(id, arm, iteration);
  if (!existsSync(path)) return { ok: false, status: 'MISSING_REVISION' };
  let revision;
  try { revision = readJSON(path); } catch { return { ok: false, status: 'INVALID_REVISION_JSON' }; }
  if (!validateRevisionValue(revision, { id, arm, iteration, context, receipt })) {
    return { ok: false, status: 'INVALID_REVISION' };
  }
  const auditPath = revisionAuditPath(id, arm, iteration);
  const auditContext = auditContextForRevision(id, arm, iteration, revision);
  if (!validAudit(auditPath, auditContext)) return { ok: false, status: 'MISSING_OR_INVALID_REVISION_AUDIT' };
  const audit = readJSON(auditPath);
  const auditPromptText = auditPrompt({
    id, arm, iteration, parent: revision, parentPath: path,
    parentHash: auditContext.parentHash, stageName: 'REVISION_AUDIT', scratch: auditContext.scratch,
  });
  if (!validAuditMetadata(id, arm, iteration, audit, auditContext, auditPromptText)) {
    return { ok: false, status: 'MISSING_OR_INVALID_AUDIT_METADATA' };
  }
  return {
    ok: true, context, receipt, bundle, revisionPath: path, revision,
    revisionHash: sha256File(path), auditPath, audit, auditHash: sha256File(auditPath),
    assessment: assessIteration(
      id, context.parent, revision, audit, iteration,
      isWholeProofPromptMetadata(readJSON(promptMetadataPath(id, arm, iteration))),
    ),
  };
}

function iterationContext(id, arm, iteration) {
  if (iteration === 1) return baseContext(id);
  const previous = completedIteration(id, arm, iteration - 1);
  if (!previous.ok) return { ok: false, status: `PREVIOUS_${previous.status}`, error: previous.error };
  if (previous.assessment.terminal) {
    return { ok: false, status: 'ALREADY_TERMINAL', terminal: previous.assessment, previous };
  }
  return {
    ok: true, parentPath: previous.revisionPath, parent: previous.revision,
    parentHash: previous.revisionHash, auditPath: previous.auditPath,
    audit: previous.audit, auditHash: previous.auditHash,
  };
}

function parseCodexCost(bytes) {
  const text = bytes.toString('utf8');
  const tokens = [...text.matchAll(/tokens used\s*\r?\n\s*([0-9][0-9,]*)/gi)];
  const models = [...text.matchAll(/^model:\s*(\S.*?)\s*$/gmi)];
  const efforts = [...text.matchAll(/^reasoning effort:\s*(\S.*?)\s*$/gmi)];
  const last = (values) => values.length ? values[values.length - 1][1].trim() : null;
  const tokenText = last(tokens);
  return {
    tokens_used: tokenText === null ? null : Number(tokenText.replaceAll(',', '')),
    model: last(models), reasoning_effort: last(efforts),
  };
}

function cellFiles(stageName, id, arm = null, iteration = null) {
  const suffix = [id, arm, iteration === null ? null : `iter_${iteration}`]
    .filter((part) => part !== null).join('__');
  return {
    log: join(RUN, 'logs', stageName, `${suffix}.log`),
    state: join(RUN, 'states', `${suffix}__${stageName}.json`),
    lock: join(RUN, 'locks', `${suffix}__${stageName}.lock`),
  };
}

function acquireLock(path, payload) {
  mkdirSync(dirname(path), { recursive: true });
  try {
    const descriptor = openSync(path, 'wx', 0o644);
    try { writeFileSync(descriptor, JSON.stringify(payload, null, 2) + '\n'); }
    finally { closeSync(descriptor); }
    return true;
  } catch (error) {
    if (error?.code === 'EEXIST') return false;
    throw error;
  }
}

function runCodexCell({
  id, arm = null, iteration = null, stageName, out, schema, prompt, scratch,
  validate, prepareTemporary = null, stateExtra = {},
}) {
  if (validate(out)) return Promise.resolve({ id, arm, iteration, status: 'SKIP_VALID', tokens_used: 0 });
  if (existsSync(out)) return Promise.resolve({ id, arm, iteration, status: 'INVALID_EXISTING_OUTPUT', tokens_used: 0 });
  if (dryRun) return Promise.resolve({ id, arm, iteration, status: 'PLANNED', tokens_used: 0 });
  // Drain without touching canonical state. In-flight calls finish normally;
  // this check prevents every new model launch after the operator switch.
  if (stopRequested()) {
    return Promise.resolve({ id, arm, iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  mkdirSync(dirname(out), { recursive: true });
  mkdirSync(scratch, { recursive: true });
  const temporary = `${out}.tmp.${process.pid}`;
  rmSync(temporary, { force: true });
  const files = cellFiles(stageName, id, arm, iteration);
  const started = new Date().toISOString();
  const startMilliseconds = Date.now();
  if (!acquireLock(files.lock, {
    pid: process.pid, record_id: id, arm, iteration, stage: stageName, started_at: started,
  })) return Promise.resolve({ id, arm, iteration, status: 'LOCKED', tokens_used: 0 });
  mkdirSync(dirname(files.log), { recursive: true });
  const oldLogSize = existsSync(files.log) ? statSync(files.log).size : 0;
  const descriptor = openSync(files.log, 'a');
  atomicWrite(files.state, JSON.stringify({
    record_id: id, arm, iteration, stage: stageName, status: 'RUNNING',
    started_at: started, ...stateExtra,
  }, null, 2) + '\n');
  const args = [
    '-a', 'never', '-s', 'workspace-write', '-C', scratch,
    '-m', REQUESTED_MODEL, '-c', `model_reasoning_effort="${REQUESTED_REASONING_EFFORT}"`,
    'exec', '--skip-git-repo-check', '--ephemeral', '--output-schema', schema,
    '--output-last-message', temporary,
  ];
  return new Promise((resolvePromise) => {
    let settled = false;
    let descriptorOpen = true;
    let stdinError = null;
    const closeLog = () => {
      if (!descriptorOpen) return;
      descriptorOpen = false;
      closeSync(descriptor);
    };
    const finish = (status, error, cost) => {
      if (settled) return;
      settled = true;
      const durationSeconds = (Date.now() - startMilliseconds) / 1000;
      const result = { id, arm, iteration, status, error, duration_seconds: durationSeconds, ...cost };
      atomicWrite(files.state, JSON.stringify({
        record_id: id, arm, iteration, stage: stageName, status, started_at: started,
        ended_at: new Date().toISOString(), duration_seconds: durationSeconds,
        error, ...cost, ...stateExtra,
      }, null, 2) + '\n');
      rmSync(files.lock, { force: true });
      resolvePromise(result);
    };
    let child;
    try {
      child = spawn('codex', args, { cwd: scratch, stdio: ['pipe', descriptor, descriptor] });
    } catch (error) {
      closeLog();
      finish('SPAWN_FAILED', String(error), {
        tokens_used: null, model: null, reasoning_effort: null,
      });
      return;
    }
    child.on('error', (error) => {
      closeLog();
      finish('SPAWN_FAILED', String(error), { tokens_used: null, model: null, reasoning_effort: null });
    });
    child.on('exit', (code, signal) => {
      if (settled) return;
      closeLog();
      const log = readFileSync(files.log);
      const cost = parseCodexCost(log.subarray(Math.min(oldLogSize, log.length)));
      let resultStatus = 'FAILED';
      let error = null;
      try {
        if (code !== 0) throw new Error(`exit=${code} signal=${signal}`);
        if (stdinError !== null) throw new Error(`prompt stdin failed: ${stdinError}`);
        if (prepareTemporary) prepareTemporary(temporary);
        if (!validate(temporary)) throw new Error('strict wrapper validation failed');
        if (existsSync(out)) {
          if (!validate(out)) throw new Error('conflicting invalid final output appeared');
          rmSync(temporary, { force: true });
          resultStatus = 'RACE_SKIP_VALID';
        } else {
          renameSync(temporary, out);
          resultStatus = 'COMPLETE';
        }
      } catch (caught) { error = String(caught); }
      finish(resultStatus, error, cost);
    });
    child.stdin.on('error', (error) => {
      stdinError = String(error);
      if (child.exitCode === null && !child.killed) child.kill('SIGTERM');
    });
    try {
      child.stdin.end(prompt, 'utf8');
    } catch (error) {
      stdinError = String(error);
      if (child.exitCode === null && !child.killed) child.kill('SIGTERM');
    }
  });
}

function runBaseline(id) {
  const out = baselinePath(id);
  return runCodexCell({
    id, stageName: 'baseline', out, schema: ACTIVE_BASELINE_SCHEMA,
    prompt: baselinePrompt(id), scratch: scratchPath(id, 'baseline'),
    validate: (path) => validBaseline(path, id),
  });
}

function runAuditBaseline(id) {
  const parentPath = baselinePath(id);
  if (!validBaseline(parentPath, id)) return Promise.resolve({ id, status: 'MISSING_BASELINE', tokens_used: 0 });
  const parent = readJSON(parentPath);
  const parentHash = sha256File(parentPath);
  const scratch = scratchPath(id, 'audit-baseline');
  const context = { id, stageName: 'BASELINE_AUDIT', arm: 'neutral', iteration: 0, parentHash, parent, scratch };
  const prompt = auditPrompt({
    id, arm: 'neutral', iteration: 0, parent, parentPath, parentHash,
    stageName: 'BASELINE_AUDIT', scratch,
  });
  const out = baselineAuditPath(id);
  if (existsSync(out) && validAudit(out, context) &&
      !validAuditMetadata(id, 'neutral', 0, readJSON(out), context, prompt) && !dryRun) {
    ensureAuditMetadata(id, 'neutral', 0, readJSON(out), context, prompt);
  }
  const validate = (path) => {
    if (!validAudit(path, context)) return false;
    return path !== out || validAuditMetadata(id, 'neutral', 0, readJSON(path), context, prompt);
  };
  return runCodexCell({
    id, stageName: 'audit-baseline', out, schema: AUDIT_SCHEMA, prompt, scratch, validate,
    prepareTemporary: (temporary) => {
      const audit = readJSON(temporary);
      if (!validateAuditValue(audit, context)) throw new Error('invalid baseline audit');
      ensureAuditMetadata(id, 'neutral', 0, audit, context, prompt);
    },
    stateExtra: { parent_sha256: parentHash },
  });
}

function runReceipt(id, iteration) {
  const context = iterationContext(id, 'bugbank', iteration);
  if (!context.ok) return Promise.resolve({ id, arm: 'bugbank', iteration, status: context.status, tokens_used: 0 });
  const out = receiptPath(id, iteration);
  const existing = receiptValidation(out, id, iteration, context.parentPath, context.parent);
  if (existing.valid) return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'SKIP_VALID', tokens_used: 0 });
  if (existsSync(out)) return Promise.resolve({
    id, arm: 'bugbank', iteration, status: 'INVALID_EXISTING_RECEIPT', error: existing.error, tokens_used: 0,
  });
  if (dryRun) return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'PLANNED', tokens_used: 0 });
  // Retrieval is not a model call, but it is still a new treatment artifact.
  // Honor the same drain boundary before creating its lock, state, or process.
  if (stopRequested()) {
    return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  const files = cellFiles('receipt', id, 'bugbank', iteration);
  const started = new Date().toISOString();
  const startMilliseconds = Date.now();
  if (!acquireLock(files.lock, {
    pid: process.pid, record_id: id, arm: 'bugbank', iteration, stage: 'receipt', started_at: started,
  })) return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'LOCKED', tokens_used: 0 });
  mkdirSync(dirname(files.log), { recursive: true });
  const descriptor = openSync(files.log, 'a');
  atomicWrite(files.state, JSON.stringify({
    record_id: id, arm: 'bugbank', iteration, stage: 'receipt', status: 'RUNNING',
    started_at: started, parent_sha256: context.parentHash, retrieval_k: RETRIEVAL_K,
  }, null, 2) + '\n');
  const argumentsList = [
    ACTIVE_FEEDBACK_SCRIPT, '--parent-json', context.parentPath, '--record-id', id,
    '--iteration', String(iteration), '--out', out, '--k', String(RETRIEVAL_K), '--db', BUGBANK_DB,
  ];
  return new Promise((resolvePromise) => {
    let settled = false;
    let descriptorOpen = true;
    const closeLog = () => {
      if (!descriptorOpen) return;
      descriptorOpen = false;
      closeSync(descriptor);
    };
    const finish = (status, error) => {
      if (settled) return;
      settled = true;
      const durationSeconds = (Date.now() - startMilliseconds) / 1000;
      atomicWrite(files.state, JSON.stringify({
        record_id: id, arm: 'bugbank', iteration, stage: 'receipt', status,
        started_at: started, ended_at: new Date().toISOString(), duration_seconds: durationSeconds,
        error, parent_sha256: context.parentHash, retrieval_k: RETRIEVAL_K,
        tokens_used: 0, model: null, reasoning_effort: null,
      }, null, 2) + '\n');
      rmSync(files.lock, { force: true });
      resolvePromise({ id, arm: 'bugbank', iteration, status, error, duration_seconds: durationSeconds, tokens_used: 0 });
    };
    let child;
    try {
      child = spawn('python3', argumentsList, { cwd: REPO, stdio: ['ignore', descriptor, descriptor] });
    } catch (error) {
      closeLog();
      finish('SPAWN_FAILED', String(error));
      return;
    }
    child.on('error', (error) => { closeLog(); finish('SPAWN_FAILED', String(error)); });
    child.on('exit', (code, signal) => {
      if (settled) return;
      closeLog();
      const validation = receiptValidation(out, id, iteration, context.parentPath, context.parent);
      finish(code === 0 && validation.valid ? 'COMPLETE' : 'FAILED',
        code === 0 && validation.valid ? null : `exit=${code} signal=${signal} receipt=${validation.error}`);
    });
  });
}

function runRevision(id, arm, iteration) {
  const context = iterationContext(id, arm, iteration);
  if (!context.ok) return Promise.resolve({ id, arm, iteration, status: context.status, tokens_used: 0 });
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = receiptValidation(receiptPath(id, iteration), id, iteration, context.parentPath, context.parent);
    if (!receipt.valid) return Promise.resolve({ id, arm, iteration, status: receipt.error, tokens_used: 0 });
  }
  let bundle;
  let promptMetadata;
  try {
    bundle = buildRevisionPromptBundle(id, arm, iteration, context, receipt);
    const metadataPath = promptMetadataPath(id, arm, iteration);
    if (existsSync(metadataPath)) {
      if (!validPromptMetadata(id, arm, iteration, context, receipt)) {
        throw new Error('existing prompt metadata fails semantic exposure/lineage validation');
      }
      const stored = readJSON(metadataPath);
      bundle = { ...bundle, prompt: stored.prompt_text };
      promptMetadata = artifact(metadataPath);
    } else {
      promptMetadata = ensurePromptMetadata(id, arm, iteration, bundle, context, receipt);
    }
  } catch (error) {
    return Promise.resolve({
      id, arm, iteration, status: 'PROMPT_MATERIALIZATION_FAILED', error: String(error), tokens_used: 0,
    });
  }
  const out = revisionPath(id, arm, iteration);
  const validate = (path) => {
    if (!existsSync(path)) return false;
    try {
      return validPromptMetadata(id, arm, iteration, context, receipt) &&
        validateRevisionValue(readJSON(path), { id, arm, iteration, context, receipt });
    } catch { return false; }
  };
  return runCodexCell({
    id, arm, iteration, stageName: 'revision', out, schema: ACTIVE_REVISION_SCHEMA,
    prompt: bundle.prompt, scratch: bundle.scratch, validate,
    prepareTemporary: (temporary) => normalizeRevisionTemporary(
      temporary, { id, arm, iteration, context, receipt },
    ),
    stateExtra: {
      parent_sha256: context.parentHash, audit_sha256: context.auditHash,
      prompt_sha256: sha256Text(bundle.prompt),
      prompt_size_bytes: Buffer.byteLength(bundle.prompt, 'utf8'),
      prompt_metadata_sha256: promptMetadata.sha256,
      wrapper_computed_treatment_status: bundle.expectedMetadata.treatment_status,
      receipt_sha256: receipt?.file_sha256 ?? null,
      receipt_exposure_bytes: receipt?.size_bytes ?? 0,
    },
  });
}

function runAuditRevision(id, arm, iteration) {
  const context = iterationContext(id, arm, iteration);
  if (!context.ok) return Promise.resolve({ id, arm, iteration, status: context.status, tokens_used: 0 });
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = receiptValidation(receiptPath(id, iteration), id, iteration, context.parentPath, context.parent);
    if (!receipt.valid) return Promise.resolve({ id, arm, iteration, status: receipt.error, tokens_used: 0 });
  }
  if (!validPromptMetadata(id, arm, iteration, context, receipt)) {
    return Promise.resolve({ id, arm, iteration, status: 'MISSING_OR_INVALID_PROMPT_METADATA', tokens_used: 0 });
  }
  const parentPath = revisionPath(id, arm, iteration);
  if (!existsSync(parentPath)) return Promise.resolve({ id, arm, iteration, status: 'MISSING_REVISION', tokens_used: 0 });
  const revision = readJSON(parentPath);
  if (!validateRevisionValue(revision, { id, arm, iteration, context, receipt })) {
    return Promise.resolve({ id, arm, iteration, status: 'INVALID_REVISION', tokens_used: 0 });
  }
  const auditContext = auditContextForRevision(id, arm, iteration, revision);
  const prompt = auditPrompt({
    id, arm, iteration, parent: revision, parentPath,
    parentHash: auditContext.parentHash, stageName: 'REVISION_AUDIT', scratch: auditContext.scratch,
  });
  const out = revisionAuditPath(id, arm, iteration);
  if (existsSync(out) && validAudit(out, auditContext) &&
      !validAuditMetadata(id, arm, iteration, readJSON(out), auditContext, prompt) && !dryRun) {
    ensureAuditMetadata(id, arm, iteration, readJSON(out), auditContext, prompt);
  }
  const validate = (path) => {
    if (!validAudit(path, auditContext)) return false;
    return path !== out || validAuditMetadata(id, arm, iteration, readJSON(path), auditContext, prompt);
  };
  return runCodexCell({
    id, arm, iteration, stageName: 'audit-revision', out, schema: AUDIT_SCHEMA,
    prompt, scratch: auditContext.scratch, validate,
    prepareTemporary: (temporary) => {
      const audit = readJSON(temporary);
      if (!validateAuditValue(audit, auditContext)) throw new Error('invalid revision audit');
      ensureAuditMetadata(id, arm, iteration, audit, auditContext, prompt);
    },
    stateExtra: { parent_sha256: auditContext.parentHash },
  });
}

function processIsAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === 'EPERM';
  }
}

function processReferencesScratch(scratch) {
  let processDirectories;
  try { processDirectories = readdirSync('/proc').filter((name) => /^\d+$/.test(name)); }
  catch { throw new Error('cannot inspect /proc to prove absence of active children'); }
  for (const processDirectory of processDirectories) {
    const pid = Number(processDirectory);
    if (pid === process.pid) continue;
    try {
      const commandLine = readFileSync(`/proc/${pid}/cmdline`).toString('utf8').replaceAll('\0', ' ');
      if (commandLine.includes(scratch)) return true;
    } catch { /* process exited during the scan */ }
  }
  return false;
}

function forensicRoot() {
  return join(RUN, 'forensics', `revision_recovery_pids_${[...recoveryRunnerPids].sort((a, b) => a - b).join('_')}`);
}

function archiveExactFile(source, category, name = null) {
  if (!existsSync(source)) return null;
  const destination = join(forensicRoot(), category, name ?? source.slice(REPO.length + 1).replaceAll(sep, '__'));
  const bytes = readFileSync(source);
  writeExclusiveOrVerify(destination, bytes);
  return artifact(destination);
}

function revisionRecoveryContext(id, arm, iteration) {
  const context = iterationContext(id, arm, iteration);
  if (!context.ok) throw new Error(`cannot recover without valid context: ${context.status}`);
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = receiptValidation(receiptPath(id, iteration), id, iteration, context.parentPath, context.parent);
    if (!receipt.valid) throw new Error(`cannot recover without valid receipt: ${receipt.error}`);
  }
  if (!validPromptMetadata(id, arm, iteration, context, receipt)) {
    throw new Error('cannot recover without exact valid prompt metadata');
  }
  return { context, receipt };
}

function recoverOneRevisionLock(lockPath) {
  const lockBytes = readFileSync(lockPath);
  const lock = JSON.parse(lockBytes.toString('utf8'));
  const { record_id: id, arm, iteration, pid } = lock;
  if (!ids.includes(id) || !['plain', 'bugbank'].includes(arm) ||
      !Number.isInteger(iteration) || iteration < 1 || !recoveryRunnerPids.has(pid)) {
    return { id: id ?? null, arm: arm ?? null, iteration: iteration ?? null, status: 'SKIP_OUT_OF_SCOPE' };
  }
  if (processIsAlive(pid)) return { id, arm, iteration, status: 'SKIP_RUNNER_ALIVE', pid };
  const scratch = scratchPath(id, 'revision', arm, iteration);
  if (processReferencesScratch(scratch)) {
    return { id, arm, iteration, status: 'SKIP_ACTIVE_CHILD', pid, scratch };
  }
  const { context, receipt } = revisionRecoveryContext(id, arm, iteration);
  const finalPath = revisionPath(id, arm, iteration);
  const temporaryPath = `${finalPath}.tmp.${pid}`;
  const files = cellFiles('revision', id, arm, iteration);
  const forensicName = `${id}__${arm}__iter_${iteration}__pid_${pid}`;
  const archivedLock = archiveExactFile(lockPath, 'locks', `${forensicName}.lock.json`);
  const archivedState = archiveExactFile(files.state, 'states', `${forensicName}.state.json`);
  const archivedLog = archiveExactFile(files.log, 'logs', `${forensicName}.log`);
  const cost = archivedLog === null ? { tokens_used: null, model: null, reasoning_effort: null }
    : parseCodexCost(readFileSync(resolve(REPO, archivedLog.path)));
  let status;
  let archivedTemporary = null;
  let finalArtifact = null;
  let originalTemporarySha256 = null;
  let originalTemporarySizeBytes = null;
  if (existsSync(finalPath)) {
    if (!validateRevisionValue(readJSON(finalPath), { id, arm, iteration, context, receipt })) {
      return { id, arm, iteration, status: 'BLOCKED_INVALID_EXISTING_FINAL', pid };
    }
    status = 'FINAL_ALREADY_VALID';
    finalArtifact = artifact(finalPath);
    if (existsSync(temporaryPath)) {
      archivedTemporary = archiveExactFile(temporaryPath, 'revision_tmp', `${forensicName}.original.json`);
      originalTemporarySha256 = archivedTemporary.sha256;
      originalTemporarySizeBytes = archivedTemporary.size_bytes;
    }
  } else if (existsSync(temporaryPath)) {
    const originalBytes = readFileSync(temporaryPath);
    originalTemporarySha256 = sha256Bytes(originalBytes);
    originalTemporarySizeBytes = originalBytes.length;
    archivedTemporary = archiveExactFile(temporaryPath, 'revision_tmp', `${forensicName}.original.json`);
    const candidate = `${finalPath}.recovery.${process.pid}`;
    rmSync(candidate, { force: true });
    writeFileSync(candidate, originalBytes);
    try {
      normalizeRevisionTemporary(candidate, { id, arm, iteration, context, receipt });
      if (!validateRevisionValue(readJSON(candidate), { id, arm, iteration, context, receipt })) {
        throw new Error('normalized orphan failed exact revision validation');
      }
      if (existsSync(finalPath)) throw new Error('final appeared during recovery; refusing overwrite');
      renameSync(candidate, finalPath);
      finalArtifact = artifact(finalPath);
      status = 'RECOVERED_COMPLETE';
    } catch (error) {
      rmSync(candidate, { force: true });
      return {
        id, arm, iteration, status: 'SALVAGE_VALIDATION_FAILED', pid, error: String(error),
        original_temporary_sha256: originalTemporarySha256,
        archived_temporary: archivedTemporary,
      };
    }
  } else {
    status = 'READY_FOR_RELAUNCH';
  }
  const recovery = addPayloadHash({
    schema: 'open_frontier_paired_v2_revision_recovery_v1', run_id: RUN_ID,
    incident: 'e2big_sessions_44827_99576', record_id: id, arm, iteration,
    dead_runner_pid: pid, status, recovered_at: new Date().toISOString(),
    lineage: {
      parent: artifact(context.parentPath), audit: artifact(context.auditPath),
      prompt_metadata: artifact(promptMetadataPath(id, arm, iteration)),
      receipt: arm === 'bugbank' ? artifact(receiptPath(id, iteration)) : null,
    },
    original_temporary_sha256: originalTemporarySha256,
    original_temporary_size_bytes: originalTemporarySizeBytes,
    archived_temporary: archivedTemporary, archived_lock: archivedLock,
    archived_state: archivedState, archived_log: archivedLog,
    recovered_cost: cost, final: finalArtifact,
    safety_checks: {
      runner_pid_dead: true, no_process_references_exact_scratch: true,
      valid_final_never_overwritten: true, original_temporary_archived_before_normalization: true,
    },
  }, 'recovery_payload_sha256');
  const recoveryPath = join(RUN, 'recoveries', 'revisions', `${forensicName}.json`);
  writeExclusiveOrVerify(recoveryPath, Buffer.from(JSON.stringify(recovery, null, 2) + '\n'));
  atomicWrite(files.state, JSON.stringify({
    record_id: id, arm, iteration, stage: 'revision', status,
    recovered_at: recovery.recovered_at, recovery_path: repoPath(recoveryPath),
    recovery_sha256: sha256File(recoveryPath), tokens_used: cost.tokens_used,
    model: cost.model, reasoning_effort: cost.reasoning_effort,
    parent_sha256: context.parentHash, audit_sha256: context.auditHash,
  }, null, 2) + '\n');
  if (existsSync(temporaryPath)) rmSync(temporaryPath, { force: true });
  if (!readFileSync(lockPath).equals(lockBytes)) {
    throw new Error(`lock changed during recovery: ${lockPath}`);
  }
  rmSync(lockPath, { force: true });
  return {
    id, arm, iteration, status, pid, tokens_used: cost.tokens_used,
    original_temporary_sha256: originalTemporarySha256,
    final_sha256: finalArtifact?.sha256 ?? null,
    recovery_path: repoPath(recoveryPath),
  };
}

async function recoverRevisions() {
  const lockDirectory = join(RUN, 'locks');
  const locks = readdirSync(lockDirectory).filter((name) => name.endsWith('__revision.lock'))
    .map((name) => join(lockDirectory, name));
  const results = [];
  for (const lockPath of locks) {
    try { results.push(recoverOneRevisionLock(lockPath)); }
    catch (error) {
      results.push({ id: null, arm: null, status: 'RECOVERY_EXCEPTION', error: String(error) });
    }
  }
  for (const result of results) process.stdout.write(`${JSON.stringify(result)}\n`);
  return results;
}

function executionCosts(id, arm, terminalIteration) {
  const entries = [];
  for (let iteration = 1; iteration <= terminalIteration; iteration += 1) {
    const stagesForIteration = arm === 'bugbank' ? ['receipt', 'revision', 'audit-revision']
      : ['revision', 'audit-revision'];
    for (const stageName of stagesForIteration) {
      const path = cellFiles(stageName, id, arm, iteration).state;
      if (!existsSync(path)) {
        if (stageName === 'receipt' && existsSync(receiptPath(id, iteration))) {
          const receipt = readJSON(receiptPath(id, iteration));
          entries.push({
            stage: stageName, iteration, state_path: null, missing: false,
            status: receipt.status, tokens_used: 0,
            duration_seconds: receipt.timing?.duration_seconds ?? 0,
            model: null, reasoning_effort: null, prompt_size_bytes: null,
            receipt_exposure_bytes: statSync(receiptPath(id, iteration)).size,
          });
          continue;
        }
        entries.push({ stage: stageName, iteration, state_path: repoPath(path), missing: true });
        continue;
      }
      try {
        const value = readJSON(path);
        entries.push({
          stage: stageName, iteration, state_path: repoPath(path), missing: false,
          status: value.status, tokens_used: value.tokens_used ?? null,
          duration_seconds: value.duration_seconds ?? 0,
          model: value.model ?? null, reasoning_effort: value.reasoning_effort ?? null,
          prompt_size_bytes: value.prompt_size_bytes ?? null,
          receipt_exposure_bytes: value.receipt_exposure_bytes ?? null,
        });
      } catch {
        entries.push({ stage: stageName, iteration, state_path: repoPath(path), missing: true });
      }
    }
  }
  return {
    tokens_used: entries.reduce((sum, entry) => sum + (Number.isFinite(entry.tokens_used) ? entry.tokens_used : 0), 0),
    duration_seconds_sum: entries.reduce(
      (sum, entry) => sum + (Number.isFinite(entry.duration_seconds) ? entry.duration_seconds : 0), 0,
    ),
    missing_state_count: entries.filter((entry) => entry.missing).length,
    entries,
  };
}

function armProgress(id, arm) {
  const base = baseContext(id);
  if (!base.ok) return {
    arm, status: 'INCOMPLETE', terminal: false, terminal_reason: 'INCOMPLETE',
    iteration: null, reason: base.status, next_stage: base.status,
    revision_sha256: null, audit_sha256: null, claimed_resolution: null,
    target_verdict: null, audit_overall: null,
  };
  for (let iteration = 1; iteration <= maxIterations; iteration += 1) {
    const completed = completedIteration(id, arm, iteration);
    if (!completed.ok) return {
      arm, status: 'INCOMPLETE', terminal: false, terminal_reason: 'INCOMPLETE',
      iteration, reason: completed.status, next_stage: completed.status,
      revision_sha256: null, audit_sha256: null, claimed_resolution: null,
      target_verdict: null, audit_overall: null,
    };
    if (completed.assessment.terminal) {
      const modelCosts = auditableArmCost(id, arm, iteration);
      const auditCounts = Object.fromEntries(['VERIFIED', 'REFUTED', 'UNRESOLVED'].map((verdict) => [
        verdict.toLowerCase(), completed.audit.claims.filter((claim) => claim.verdict === verdict).length,
      ]));
      return {
        arm, status: completed.assessment.status, terminal: true,
        terminal_reason: completed.assessment.terminal_reason, iteration,
        reason: completed.assessment.reason, fixed_point: completed.assessment.fixed_point,
        ordered_claim_set_unchanged: completed.assessment.ordered_claim_set_unchanged,
        proof_state_unchanged: completed.assessment.proof_state_unchanged,
        parent_proof_state_sha256: completed.assessment.parent_proof_state_sha256,
        revision_proof_state_sha256: completed.assessment.revision_proof_state_sha256,
        bugbank_recheck_required: completed.assessment.bugbank_recheck_required,
        model_tokens_used: modelCosts.tokens_used,
        model_token_cost_auditable: modelCosts.auditable,
        token_budget_target: completed.assessment.token_budget_target,
        token_budget_used: completed.assessment.token_budget_used,
        token_budget_matched: completed.assessment.token_budget_matched,
        token_budget_auditable: completed.assessment.token_budget_auditable,
        token_budget_overshoot: arm === 'plain' &&
          Number.isInteger(completed.assessment.token_budget_used) &&
          Number.isInteger(completed.assessment.token_budget_target)
          ? completed.assessment.token_budget_used - completed.assessment.token_budget_target
          : null,
        every_claim_verified: completed.assessment.every_claim_verified,
        claim_count: completed.revision.results.length, audit_counts: auditCounts,
        claimed_resolution: completed.revision.claimed_resolution,
        target_verdict: completed.audit.target_verdict,
        claimed_resolution_verdict: completed.audit.claimed_resolution_verdict,
        audit_overall: completed.audit.overall,
        revision_sha256: completed.revisionHash, audit_sha256: completed.auditHash,
        parent: artifact(completed.context.parentPath), revision: artifact(completed.revisionPath),
        audit: artifact(completed.auditPath),
        prompt_metadata: artifact(promptMetadataPath(id, arm, iteration)),
        receipt: arm === 'bugbank' ? artifact(receiptPath(id, iteration)) : null,
        execution_costs: executionCosts(id, arm, iteration),
        ordered_claims_sha256: sha256Text(canonicalJSON(
          completed.revision.results.map((result) => result.claim),
        )),
      };
    }
    if (completed.assessment.waiting_for_bugbank_budget) return {
      arm, status: 'INCOMPLETE', terminal: false, terminal_reason: 'INCOMPLETE',
      iteration, reason: 'WAITING_FOR_BUGBANK_TOKEN_TARGET',
      next_stage: 'WAIT_FOR_BUGBANK_TERMINAL',
      revision_sha256: completed.revisionHash, audit_sha256: completed.auditHash,
      claimed_resolution: completed.revision.claimed_resolution,
      target_verdict: completed.audit.target_verdict,
      audit_overall: completed.audit.overall,
    };
  }
  return {
    arm, status: 'INCOMPLETE', terminal: false, terminal_reason: 'INCOMPLETE',
    iteration: null, reason: `NO_TERMINAL_PROOF_STATE_WITHIN_OPERATIONAL_LIMIT_${maxIterations}`,
    next_stage: 'EXTEND_OR_CONTINUE_ITERATIONS', revision_sha256: null,
    audit_sha256: null, claimed_resolution: null, target_verdict: null, audit_overall: null,
  };
}

function terminalValue(id) {
  const base = baseContext(id);
  const arms = { plain: armProgress(id, 'plain'), bugbank: armProgress(id, 'bugbank') };
  const proofEndpointsComplete = arms.plain.terminal && arms.bugbank.terminal;
  const tokensOf = (arm) => arms[arm].terminal && Number.isInteger(arms[arm].model_tokens_used)
    ? arms[arm].model_tokens_used : null;
  const plainTokens = tokensOf('plain');
  const bugbankTokens = tokensOf('bugbank');
  const plainSolved = arms.plain.terminal && arms.plain.status === 'VERIFIED_FULL';
  const tokenComparisonAuditable = plainTokens !== null && bugbankTokens !== null;
  const complete = proofEndpointsComplete && tokenComparisonAuditable;
  return addPayloadHash({
    schema: TERMINAL_SCHEMA, run_id: RUN_ID, record_id: id,
    stage: 'PAIR_TERMINAL', status: complete ? 'COMPLETE' : 'INCOMPLETE',
    pair_status: complete ? 'COMPLETE' : 'INCOMPLETE',
    max_iterations: maxIterations, retrieval_k: RETRIEVAL_K,
    treatment_contrast_valid: complete,
    proof_endpoints_complete: proofEndpointsComplete,
    token_comparison_auditable: tokenComparisonAuditable,
    solved_arms: ['bugbank', 'plain'].filter(
      (arm) => arms[arm].terminal && arms[arm].status === 'VERIFIED_FULL',
    ),
    bugbank_model_tokens_used: bugbankTokens,
    plain_model_tokens_used: plainTokens,
    plain_minus_bugbank_tokens: plainTokens !== null && bugbankTokens !== null
      ? plainTokens - bugbankTokens : null,
    plain_solved_with_fewer_tokens: plainSolved && plainTokens !== null && bugbankTokens !== null
      ? plainTokens < bugbankTokens : null,
    baseline: base.ok ? { draft: artifact(base.parentPath), independent_audit: artifact(base.auditPath) } : null,
    arms,
  }, 'terminal_payload_sha256');
}

function runTerminal(id) {
  try {
    const value = terminalValue(id);
    if (!dryRun) atomicWrite(join(RUN, 'pair_terminals', `${id}.json`), JSON.stringify(value, null, 2) + '\n');
    return Promise.resolve({
      id, status: value.status, plain: value.arms.plain.status,
      bugbank: value.arms.bugbank.status, tokens_used: 0,
    });
  } catch (error) {
    return Promise.resolve({ id, status: 'INCOMPLETE', error: String(error), tokens_used: 0 });
  }
}

async function pool(items, width, fn) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (true) {
      const index = next++;
      if (index >= items.length) return;
      try {
        results[index] = await fn(items[index]);
      } catch (error) {
        const item = items[index];
        const identity = typeof item === 'string' ? { id: item } : {
          id: item?.id ?? null, arm: item?.arm ?? null,
        };
        results[index] = {
          ...identity, status: 'WORKER_EXCEPTION', error: String(error), tokens_used: 0,
        };
      }
      process.stdout.write(`${JSON.stringify(results[index])}\n`);
    }
  }
  await Promise.all(Array.from({ length: Math.min(width, items.length) }, worker));
  return results;
}

function cellIsSelected(id, arm) {
  return selectedCells.size === 0 || selectedCells.has(`${id}:${arm}`);
}

let summarySequence = 0;
function writeSummary(stageName, results, startedAt, iteration = null) {
  const successes = new Set([
    'COMPLETE', 'SKIP_VALID', 'RACE_SKIP_VALID', 'PLANNED',
    'RECOVERED_COMPLETE', 'READY_FOR_RELAUNCH', 'FINAL_ALREADY_VALID', 'SKIP_OUT_OF_SCOPE',
    'ALREADY_TERMINAL',
  ]);
  const summary = {
    run: RUN_ID, stage: stageName, iteration, dry_run: dryRun,
    started_at: startedAt, ended_at: new Date().toISOString(), selected: results.length,
    complete: results.filter((result) => successes.has(result.status)).length,
    failed: results.filter((result) => !successes.has(result.status)).length,
    tokens_used: results.reduce((sum, result) => sum + (Number.isFinite(result.tokens_used) ? result.tokens_used : 0), 0),
    duration_seconds_sum: results.reduce(
      (sum, result) => sum + (Number.isFinite(result.duration_seconds) ? result.duration_seconds : 0), 0,
    ),
    results,
  };
  if (!dryRun && stageName !== 'validate') {
    summarySequence += 1;
    const safeTime = startedAt.replaceAll(':', '').replaceAll('.', '-');
    const directory = join(RUN, 'summaries', stageName);
    mkdirSync(directory, { recursive: true });
    const path = join(directory, `${safeTime}__pid_${process.pid}__${summarySequence}.json`);
    writeExclusiveOrVerify(path, Buffer.from(JSON.stringify(summary, null, 2) + '\n'));
  }
  return summary;
}

async function executeStage(stageName, items, fn, iteration = null) {
  const startedAt = new Date().toISOString();
  return writeSummary(stageName, await pool(items, concurrency, fn), startedAt, iteration);
}

function eligibleCells(iteration, arms = ['plain', 'bugbank']) {
  const cells = [];
  for (const id of ids) for (const arm of arms) {
    if (!cellIsSelected(id, arm)) continue;
    // Once an arm reaches a valid terminal audit, freeze it at that first
    // terminal iteration.  A lagging mate may continue, but must not cause an
    // already-terminal arm to receive extra treatment or revision calls.
    if (iteration > 1) {
      const previous = completedIteration(id, arm, iteration - 1);
      if (previous.ok && previous.assessment.terminal) continue;
      if (previous.ok && previous.assessment.waiting_for_bugbank_budget) continue;
    }
    if (iterationContext(id, arm, iteration).ok) cells.push({ id, arm });
  }
  return cells;
}

async function runAll() {
  const summaries = [];
  const materializeTerminalSnapshot = async () => {
    const terminalSummary = await executeStage('terminal', ids, runTerminal);
    summaries.push(terminalSummary);
    return {
      summaries,
      failed: terminalSummary.results.filter((result) => result.status !== 'COMPLETE').length,
    };
  };
  summaries.push(await executeStage('baseline', ids, runBaseline));
  if (stopRequested()) return materializeTerminalSnapshot();
  summaries.push(await executeStage('audit-baseline', ids, runAuditBaseline));
  if (stopRequested()) return materializeTerminalSnapshot();

  // Advance both arms independently. BugBank goes first within each round,
  // but plain is not blocked on BugBank's terminal: it may find and freeze a
  // correct solution first. A stable inconclusive plain proof waits only when
  // its still-unknown BugBank token target is the sole missing condition.
  const nextRunnable = (arm) => ids.flatMap((id) => {
    if (!cellIsSelected(id, arm)) return [];
    let progress = armProgress(id, arm);
    if (progress.terminal) return [];
    if (progress.next_stage === 'WAIT_FOR_BUGBANK_TERMINAL') {
      // `armProgress` normally recomputes this as soon as BugBank freezes its
      // endpoint. Re-evaluate defensively so a previously waiting plain arm
      // cannot remain stuck after its token target becomes available.
      if (!armProgress(id, 'bugbank').terminal) return [];
      progress = armProgress(id, arm);
      if (progress.terminal || progress.next_stage === 'WAIT_FOR_BUGBANK_TERMINAL') return [];
    }
    if (!Number.isInteger(progress.iteration)) return [];
    const context = iterationContext(id, arm, progress.iteration);
    return context.ok ? [{ id, arm, iteration: progress.iteration }] : [];
  });

  const runArmCycle = async (arm) => {
    if (stopRequested()) return { attempted: false, failed: false, drained: true };
    const cells = nextRunnable(arm);
    if (!cells.length) return { attempted: false, failed: false, drained: false };
    let failed = false;
    if (arm === 'bugbank') {
      const receiptSummary = await executeStage(
        'receipt', cells, (cell) => runReceipt(cell.id, cell.iteration), null,
      );
      summaries.push(receiptSummary);
      failed ||= receiptSummary.failed > 0;
      if (stopRequested()) return { attempted: true, failed, drained: true };
    }
    const revisionCells = cells.filter((cell) => {
      if (arm === 'plain') return true;
      const context = iterationContext(cell.id, arm, cell.iteration);
      return context.ok && receiptValidation(
        receiptPath(cell.id, cell.iteration), cell.id, cell.iteration,
        context.parentPath, context.parent,
      ).valid;
    });
    const revisionSummary = await executeStage(
      'revision', revisionCells,
      (cell) => runRevision(cell.id, arm, cell.iteration), null,
    );
    summaries.push(revisionSummary);
    failed ||= revisionSummary.failed > 0;
    if (stopRequested()) return { attempted: true, failed, drained: true };
    const auditCells = revisionCells.filter(
      (cell) => existsSync(revisionPath(cell.id, arm, cell.iteration)),
    );
    const auditSummary = await executeStage(
      'audit-revision', auditCells,
      (cell) => runAuditRevision(cell.id, arm, cell.iteration), null,
    );
    summaries.push(auditSummary);
    failed ||= auditSummary.failed > 0;
    return { attempted: true, failed, drained: stopRequested() };
  };

  for (let round = 0; round < 2 * maxIterations + 2; round += 1) {
    const bugbankCycle = await runArmCycle('bugbank');
    if (bugbankCycle.drained) break;
    const plainCycle = await runArmCycle('plain');
    if (bugbankCycle.failed || plainCycle.failed || plainCycle.drained) break;
    if (ids.every((id) =>
      (!cellIsSelected(id, 'bugbank') || armProgress(id, 'bugbank').terminal) &&
      (!cellIsSelected(id, 'plain') || armProgress(id, 'plain').terminal))) break;
    if (!bugbankCycle.attempted && !plainCycle.attempted) break;
  }
  return materializeTerminalSnapshot();
}

let finalFailureCount = 0;
if (stage === 'all') {
  finalFailureCount = (await runAll()).failed;
} else if (stage === 'recover-revisions') {
  const startedAt = new Date().toISOString();
  const results = await recoverRevisions();
  const summary = writeSummary('recover-revisions', results, startedAt);
  finalFailureCount = summary.failed;
} else if (stage === 'validate') {
  const results = ids.map((id) => {
    try {
      const value = terminalValue(id);
      return {
        id, status: value.status, plain: value.arms.plain.status,
        bugbank: value.arms.bugbank.status, tokens_used: 0,
      };
    } catch (error) { return { id, status: 'INCOMPLETE', error: String(error), tokens_used: 0 }; }
  });
  for (const result of results) process.stdout.write(`${JSON.stringify(result)}\n`);
  writeSummary('validate', results, new Date().toISOString());
  finalFailureCount = results.filter((result) => result.status !== 'COMPLETE').length;
} else {
  let items;
  let worker;
  if (stage === 'baseline') { items = ids; worker = runBaseline; }
  else if (stage === 'audit-baseline') { items = ids; worker = runAuditBaseline; }
  else if (stage === 'receipt') {
    items = ids; worker = (id) => runReceipt(id, requestedIteration);
  } else if (stage === 'revision') {
    items = ids.flatMap((id) => ['plain', 'bugbank'].filter((arm) => cellIsSelected(id, arm))
      .map((arm) => ({ id, arm })));
    worker = (cell) => runRevision(cell.id, cell.arm, requestedIteration);
  } else if (stage === 'audit-revision') {
    items = ids.flatMap((id) => ['plain', 'bugbank'].filter((arm) => cellIsSelected(id, arm))
      .map((arm) => ({ id, arm })));
    worker = (cell) => runAuditRevision(cell.id, cell.arm, requestedIteration);
  } else { items = ids; worker = runTerminal; }
  const summary = await executeStage(stage, items, worker, requestedIteration);
  finalFailureCount = stage === 'terminal'
    ? summary.results.filter((result) => result.status !== 'COMPLETE').length
    : summary.failed;
}

if (finalFailureCount) process.exitCode = 1;
