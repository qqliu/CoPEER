#!/usr/bin/env node

/* Fail-closed runner for the separate post-fixed-point paired extension. */

import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  closeSync, constants as fsConstants, existsSync, fstatSync, fsyncSync, linkSync, lstatSync,
  mkdirSync, mkdtempSync, openSync, readdirSync,
  readFileSync, realpathSync, renameSync, rmSync, statSync, writeFileSync,
} from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const SCRIPT = fileURLToPath(import.meta.url);
const HERE = dirname(SCRIPT);
const BASE = resolve(HERE, '..');
const REPO = resolve(BASE, '..');
const ORIGINAL_RUN = resolve(BASE, 'runs', 'open_frontier_paired_v2_20260901');
const SEAL_UTILITY = join(HERE, 'paired_open_problem_extension_runtime_seal.py');
const FEEDBACK = join(HERE, 'paired_open_problem_extension_feedback.py');
const GIT = '/usr/bin/git';

function argument(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const nonempty = (value) => typeof value === 'string' && value.length > 0;
const shaPattern = /^[0-9a-f]{64}$/;
const safeIdPattern = /^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$/;
const shaBytes = (value) => createHash('sha256').update(value).digest('hex');
const shaText = (value) => shaBytes(Buffer.from(value, 'utf8'));
const shaFile = (path) => shaBytes(readFileSync(path));

function assertFiniteJSONNumbers(value, location = '$') {
  if (typeof value === 'number' && !Number.isFinite(value)) {
    throw new Error(`non-finite JSON number at ${location}`);
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertFiniteJSONNumbers(item, `${location}[${index}]`));
  } else if (isObject(value)) {
    for (const [key, item] of Object.entries(value)) {
      assertFiniteJSONNumbers(item, `${location}.${key}`);
    }
  }
  return value;
}

function assertNoDuplicateJSONKeys(raw) {
  const text = String(raw);
  let cursor = 0;
  const fail = () => { throw new Error(`invalid or duplicate-key JSON near byte ${cursor}`); };
  const whitespace = () => {
    while (cursor < text.length && /[\x20\t\r\n]/.test(text[cursor])) cursor += 1;
  };
  const stringToken = () => {
    if (text[cursor] !== '"') fail();
    const start = cursor;
    cursor += 1;
    while (cursor < text.length) {
      if (text[cursor] === '"') {
        cursor += 1;
        return text.slice(start, cursor);
      }
      if (text[cursor] === '\\') {
        cursor += 2;
      } else {
        cursor += 1;
      }
    }
    fail();
    return '';
  };
  const value = () => {
    whitespace();
    if (text[cursor] === '{') {
      cursor += 1;
      whitespace();
      const keys = new Set();
      if (text[cursor] === '}') { cursor += 1; return; }
      while (cursor < text.length) {
        const encodedKey = stringToken();
        const key = JSON.parse(encodedKey);
        if (keys.has(key)) throw new Error(`duplicate JSON key ${JSON.stringify(key)}`);
        keys.add(key);
        whitespace();
        if (text[cursor] !== ':') fail();
        cursor += 1;
        value();
        whitespace();
        if (text[cursor] === '}') { cursor += 1; return; }
        if (text[cursor] !== ',') fail();
        cursor += 1;
        whitespace();
      }
      fail();
    } else if (text[cursor] === '[') {
      cursor += 1;
      whitespace();
      if (text[cursor] === ']') { cursor += 1; return; }
      while (cursor < text.length) {
        value();
        whitespace();
        if (text[cursor] === ']') { cursor += 1; return; }
        if (text[cursor] !== ',') fail();
        cursor += 1;
      }
      fail();
    } else if (text[cursor] === '"') {
      stringToken();
    } else {
      const rest = text.slice(cursor);
      const token = /^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(rest);
      if (token === null) fail();
      cursor += token[0].length;
    }
  };
  value();
  whitespace();
  if (cursor !== text.length) fail();
}

const strictJSONParse = (raw) => {
  assertNoDuplicateJSONKeys(raw);
  return assertFiniteJSONNumbers(JSON.parse(raw));
};
const readJSON = (path) => strictJSONParse(readFileSync(path, 'utf8'));
const isTokenCount = (value) => Number.isSafeInteger(value) && value >= 0;

function checkedTokenSum(values) {
  let total = 0;
  for (const value of values) {
    if (!isTokenCount(value) || total > Number.MAX_SAFE_INTEGER - value) {
      throw new Error('model-token total exceeds exact JSON-integer accounting');
    }
    total += value;
  }
  return total;
}

function checkedTokenDifference(left, right) {
  if (!isTokenCount(left) || !isTokenCount(right)) {
    throw new Error('model-token difference has an inexact operand');
  }
  const difference = left - right;
  if (!Number.isSafeInteger(difference)) {
    throw new Error('model-token difference exceeds exact JSON-integer accounting');
  }
  return difference;
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (isObject(value)) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]));
  }
  return value;
}
const canonicalJSON = (value) => JSON.stringify(canonicalize(value));
const exactArray = (left, right) => Array.isArray(left) && Array.isArray(right) &&
  left.length === right.length && left.every((item, index) => item === right[index]);
const exactKeys = (value, keys) => isObject(value) &&
  Object.keys(value).length === keys.length && keys.every((key) => Object.hasOwn(value, key));
const scientificStartAllowed = (dryRunMode, stopFile) => dryRunMode || !existsSync(stopFile);

function lockChildStdio(descriptor) {
  const stdio = Array.from({ length: descriptor + 1 }, () => 'ignore');
  stdio[1] = 'pipe';
  stdio[2] = 'pipe';
  stdio[descriptor] = descriptor;
  return stdio;
}

function processStartTicks(pid) {
  try {
    const raw = readFileSync(`/proc/${pid}/stat`, 'utf8');
    const boundary = raw.lastIndexOf(') ');
    if (boundary < 0) return null;
    const fields = raw.slice(boundary + 2).trim().split(/\s+/);
    return /^[0-9]+$/.test(fields[19] ?? '') ? fields[19] : null;
  } catch { return null; }
}

function retryableLauncherIsLive(value) {
  return isObject(value) && Number.isInteger(value.launcher_pid) &&
    value.launcher_pid > 0 && /^[0-9]+$/.test(value.launcher_process_start_ticks ?? '') &&
    processStartTicks(value.launcher_pid) === value.launcher_process_start_ticks;
}

function verifyOrAcquireMutationLock(expectedPath, descriptor, flockExecutable) {
  if (!Number.isInteger(descriptor) || descriptor < 3) {
    throw new Error('mutation-gate descriptor is invalid');
  }
  const targetInfo = lstatSync(expectedPath);
  if (!targetInfo.isFile() || targetInfo.isSymbolicLink()) {
    throw new Error('canonical operation lock is not a plain file');
  }
  const descriptorInfo = fstatSync(descriptor);
  if (!descriptorInfo.isFile() || realpathSync(`/proc/self/fd/${descriptor}`) !== realpathSync(expectedPath) ||
      descriptorInfo.dev !== targetInfo.dev || descriptorInfo.ino !== targetInfo.ino) {
    throw new Error('inherited mutation-gate descriptor does not name the canonical operation lock');
  }
  const cleanEnvironment = { LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8', PATH: '/usr/bin:/bin' };
  const acquired = spawnSync(flockExecutable, ['-n', String(descriptor)], {
    stdio: lockChildStdio(descriptor), env: cleanEnvironment, encoding: 'utf8',
  });
  if (acquired.status !== 0) {
    throw new Error(`could not acquire inherited mutation gate: ${(acquired.stderr || '').trim()}`);
  }
  let competitor = null;
  try {
    competitor = openSync(expectedPath, fsConstants.O_RDONLY | fsConstants.O_NOFOLLOW);
    const conflict = spawnSync(flockExecutable, ['-n', String(competitor)], {
      stdio: lockChildStdio(competitor), env: cleanEnvironment, encoding: 'utf8',
    });
    if (conflict.status !== 1) {
      throw new Error('mutation gate did not exclude a separately opened file description');
    }
  } finally {
    if (competitor !== null) closeSync(competitor);
  }
  return true;
}

function proofState(value) {
  return {
    claimed_resolution: value.claimed_resolution,
    results: value.results.map((row) => ({ claim: row.claim, proof_sketch: row.proof_sketch })),
    final_writeup: value.final_writeup,
  };
}
const proofStateHash = (value) => shaText(canonicalJSON(proofState(value)));

function pythonPayloadHash(raw, hashField) {
  const program = [
    'import hashlib,json,math,sys',
    'def reject(token):',
    '    raise ValueError(f"non-finite JSON number {token}")',
    'def unique(pairs):',
    '    value={}',
    '    for key,item in pairs:',
    '        if key in value: raise ValueError(f"duplicate JSON key {key!r}")',
    '        value[key]=item',
    '    return value',
    'def finite(token):',
    '    value=float(token)',
    '    return value if math.isfinite(value) else reject(token)',
    'x=json.loads(sys.stdin.buffer.read().decode("utf-8"),object_pairs_hook=unique,parse_constant=reject,parse_float=finite)',
    `x.pop(${JSON.stringify(hashField)},None)`,
    'b=json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":")).encode("utf-8")',
    'sys.stdout.write(hashlib.sha256(b).hexdigest())',
  ].join('\n');
  const result = spawnSync(PYTHON, ['-c', program], {
    input: raw, encoding: 'utf8', maxBuffer: 128 * 1024 * 1024,
    env: { ...earlySeal.execution.retrieval_spawn_environment },
  });
  if (result.status !== 0 || !shaPattern.test(result.stdout.trim())) {
    throw new Error('Python payload-hash recomputation failed');
  }
  return result.stdout.trim();
}

function expectedAuditOverall(claims) {
  if (claims.some((claim) => claim.verdict === 'REFUTED')) return 'REFUTED';
  if (claims.length > 0 && claims.every((claim) => claim.verdict === 'VERIFIED')) return 'VERIFIED';
  return 'INCONCLUSIVE';
}

function expectedResolutionVerdict(parent, targetVerdict) {
  const claimed = { NONE: 0, PARTIAL: 1, FULL: 2 }[parent.claimed_resolution];
  const target = {
    NO_VALID_PROGRESS: 0, OVERCLAIMED: 0, VALID_PARTIAL_PROGRESS: 1,
    FULLY_RESOLVES_TARGET: 2,
  }[targetVerdict];
  if (!Number.isInteger(claimed) || !Number.isInteger(target)) return null;
  if (claimed === target) return 'ACCURATE';
  return claimed > target ? 'OVERSTATED' : 'UNDERSTATED';
}

function validDraftCore(value) {
  return isObject(value) && ['FULL', 'PARTIAL', 'NONE'].includes(value.claimed_resolution) &&
    Array.isArray(value.results) && value.results.length > 0 &&
    value.results.every((row) => isObject(row) && nonempty(row.claim) && nonempty(row.proof_sketch)) &&
    nonempty(value.final_writeup) && Array.isArray(value.checks_performed) &&
    value.checks_performed.every(nonempty) && ['CONFIDENT', 'UNSURE'].includes(value.self_assessment);
}

function validAuditValue(value, { id, arm, attempt, parent, parentHash }) {
  const auditKeys = [
    'record_id', 'stage', 'arm', 'iteration', 'parent_sha256', 'complete', 'claims',
    'confirmed_refutations', 'target_verdict', 'claimed_resolution_verdict',
    'target_evidence', 'overall', 'checks_performed',
  ];
  const claimKeys = [
    'idx', 'claim', 'claim_sha256', 'verdict', 'evidence', 'witness',
    'search_method', 'checker_path',
  ];
  if (!exactKeys(value, auditKeys) || value.record_id !== id || value.arm !== arm ||
      value.parent_sha256 !== parentHash || value.complete !== true ||
      !Array.isArray(value.claims) || value.claims.length !== parent.results.length ||
      !Array.isArray(value.confirmed_refutations) || !Array.isArray(value.checks_performed) ||
      !value.checks_performed.every(nonempty) ||
      !['FULLY_RESOLVES_TARGET', 'VALID_PARTIAL_PROGRESS', 'NO_VALID_PROGRESS', 'OVERCLAIMED']
        .includes(value.target_verdict) ||
      !['ACCURATE', 'OVERSTATED', 'UNDERSTATED'].includes(value.claimed_resolution_verdict) ||
      value.claimed_resolution_verdict !== expectedResolutionVerdict(parent, value.target_verdict) ||
      !nonempty(value.target_evidence)) return false;
  if (attempt === 0) {
    if (!Number.isInteger(value.iteration) || value.iteration < 0 ||
        !['BASELINE_AUDIT', 'REVISION_AUDIT'].includes(value.stage)) return false;
  } else if (value.stage !== 'REVISION_AUDIT' || value.iteration !== attempt) return false;
  for (let index = 0; index < value.claims.length; index += 1) {
    const claim = value.claims[index];
    const expected = parent.results[index].claim;
    if (!exactKeys(claim, claimKeys) || claim.idx !== index || claim.claim !== expected ||
        claim.claim_sha256 !== shaText(expected) ||
        !['VERIFIED', 'REFUTED', 'UNRESOLVED'].includes(claim.verdict) ||
        !nonempty(claim.evidence) || !nonempty(claim.witness) ||
        !nonempty(claim.search_method) || !nonempty(claim.checker_path)) return false;
  }
  const refutations = value.claims.filter((claim) => claim.verdict === 'REFUTED')
    .map((claim) => claim.idx);
  return exactArray(value.confirmed_refutations, refutations) &&
    value.overall === expectedAuditOverall(value.claims);
}

function verifiedFull(revision, audit) {
  return validDraftCore(revision) && isObject(audit) && audit.complete === true &&
    revision.claimed_resolution === 'FULL' && audit.target_verdict === 'FULLY_RESOLVES_TARGET' &&
    audit.claimed_resolution_verdict === 'ACCURATE' && audit.overall === 'VERIFIED' &&
    audit.confirmed_refutations.length === 0 && audit.claims.length === revision.results.length &&
    audit.claims.length > 0 && audit.claims.every((claim) => claim.verdict === 'VERIFIED');
}

// A seal-free self-test exercises the two scientifically important ordering
// rules without opening a run directory.
if (process.argv.includes('--self-test')) {
  for (const token of ['1e9999', '-1e9999']) {
    let rejected = false;
    try { strictJSONParse(`{"nested":[${token}]}`); }
    catch { rejected = true; }
    if (!rejected) throw new Error(`non-finite JSON ${token} was accepted`);
  }
  for (const raw of ['{"a":1,"a":2}', '{"a":1,"\\u0061":2}', '{"x":{"b":1,"b":2}}']) {
    let rejected = false;
    try { strictJSONParse(raw); }
    catch { rejected = true; }
    if (!rejected) throw new Error('duplicate-key JSON was accepted');
  }
  if (isTokenCount(Number.MAX_SAFE_INTEGER + 1)) {
    throw new Error('unsafe model-token integer was accepted');
  }
  let tokenOverflowRejected = false;
  try { checkedTokenSum([Number.MAX_SAFE_INTEGER, 1]); }
  catch { tokenOverflowRejected = true; }
  if (!tokenOverflowRejected || checkedTokenSum([1, 2, 3]) !== 6) {
    throw new Error('checked model-token arithmetic self-test failed');
  }
  const selfStartTicks = processStartTicks(process.pid);
  if (!/^[0-9]+$/.test(selfStartTicks ?? '')) {
    throw new Error('process-start identity self-test failed');
  }
  if (!retryableLauncherIsLive({
    launcher_pid: process.pid, launcher_process_start_ticks: selfStartTicks,
  }) || retryableLauncherIsLive({
    launcher_pid: 2147483647, launcher_process_start_ticks: '1',
  })) throw new Error('retryable-launcher liveness self-test failed');
  const parent = {
    claimed_resolution: 'PARTIAL', results: [{ claim: 'c', proof_sketch: 'p' }],
    final_writeup: 'f', checks_performed: [], self_assessment: 'UNSURE',
  };
  const audit = {
    complete: true, claims: [{ verdict: 'VERIFIED' }], confirmed_refutations: [],
    target_verdict: 'VALID_PARTIAL_PROGRESS', claimed_resolution_verdict: 'ACCURATE', overall: 'VERIFIED',
  };
  if (verifiedFull(parent, audit)) throw new Error('partial work was misclassified as full');
  const full = { ...parent, claimed_resolution: 'FULL' };
  const fullAudit = { ...audit, target_verdict: 'FULLY_RESOLVES_TARGET' };
  if (!verifiedFull(full, fullAudit)) throw new Error('strict full rule self-test failed');
  const atomicRoot = mkdtempSync(join(tmpdir(), 'paired-extension-atomic-'));
  try {
    const source = join(atomicRoot, 'source.json');
    const output = join(atomicRoot, 'output.json');
    writeFileSync(source, '{"complete":true}\n');
    publishValidatedAbsent(source, output,
      (candidate) => readFileSync(candidate, 'utf8') === '{"complete":true}\n');
    if (!readFileSync(output).equals(readFileSync(source))) {
      throw new Error('atomic publish bytes changed');
    }
    const interrupted = join(atomicRoot, 'interrupted.json');
    writeFileSync(`${interrupted}.finalizing`, 'partial');
    let refused = false;
    try { publishValidatedAbsent(source, interrupted, () => true); }
    catch { refused = true; }
    if (!refused || existsSync(interrupted)) {
      throw new Error('interrupted staging was not rejected fail-closed');
    }
    const stopFile = join(atomicRoot, 'STOP_REQUESTED');
    const forbiddenArtifact = join(atomicRoot, 'must-not-start.json');
    writeFileSync(stopFile, 'drain\n');
    if (scientificStartAllowed(false, stopFile)) {
      writeFileSync(forbiddenArtifact, '{}\n');
    }
    if (existsSync(forbiddenArtifact) || !scientificStartAllowed(true, stopFile)) {
      throw new Error('STOP admission guard allowed a new scientific artifact');
    }
    const operationLock = join(atomicRoot, 'operation.lock');
    writeFileSync(operationLock, '');
    const operationDescriptor = openSync(
      operationLock, fsConstants.O_RDWR | fsConstants.O_NOFOLLOW,
    );
    try {
      if (!verifyOrAcquireMutationLock(operationLock, operationDescriptor, '/usr/bin/flock')) {
        throw new Error('mutation-gate self-test did not acquire the lock');
      }
    } finally {
      closeSync(operationDescriptor);
    }
    const checkerScratch = join(atomicRoot, 'checker-scratch');
    mkdirSync(checkerScratch);
    const checker = join(checkerScratch, 'check.py');
    writeFileSync(checker, 'assert 1 + 1 == 2\n');
    const auditOutput = join(atomicRoot, 'audit.json');
    writeFileSync(auditOutput, JSON.stringify({
      complete: true,
      claims: [{
        verdict: 'VERIFIED', evidence: 'direct check', witness: '1+1=2',
        search_method: 'exact arithmetic', checker_path: '/work/check.py',
      }],
      target_verdict: 'VALID_PARTIAL_PROGRESS', target_evidence: 'partial only',
      checks_performed: ['ran exact checker'],
    }));
    normalizeAudit(auditOutput, 'p', 'plain', 1, parent, '0'.repeat(64), checkerScratch);
    const normalizedAudit = readJSON(auditOutput);
    if (normalizedAudit.claims[0].checker_path !== realpathSync(checker) ||
        normalizedAudit.claims[0].claim !== 'c' ||
        normalizedAudit.claimed_resolution_verdict !== 'ACCURATE') {
      throw new Error('guest checker path was not deterministically normalized');
    }
  } finally {
    rmSync(atomicRoot, { recursive: true, force: true });
  }
  process.stdout.write('SELF_TEST_OK\n');
  process.exit(0);
}

const requestedRoot = argument('run-root');
if (!requestedRoot) throw new Error('--run-root is required');
const RUN = resolve(requestedRoot);
if (RUN === ORIGINAL_RUN || RUN.startsWith(`${ORIGINAL_RUN}${sep}`) ||
    ORIGINAL_RUN.startsWith(`${RUN}${sep}`)) {
  throw new Error('extension runner refuses the original paired-run namespace');
}
const MANIFEST_PATH = join(RUN, 'EXTENSION_MANIFEST.json');
const SEAL_PATH = join(RUN, 'RUNTIME_SEAL.json');
const dryRun = process.argv.includes('--dry-run');
const stage = argument('stage', 'all');
const concurrency = Number(argument('concurrency', '4'));
const attemptArgument = argument('attempt');
const requestedAttempt = attemptArgument === null ? null : Number(attemptArgument);
const only = new Set((argument('only', '') || '').split(',').filter(Boolean));
const selectedCells = new Set((argument('cells', '') || '').split(',').filter(Boolean));
const allowedStages = new Set(['receipt', 'revision', 'audit', 'terminal', 'all', 'validate']);
if (!allowedStages.has(stage)) throw new Error(`unsupported stage ${stage}`);
if (!Number.isInteger(concurrency) || concurrency < 1) throw new Error('concurrency must be positive');
if (['receipt', 'revision', 'audit'].includes(stage) &&
    (!Number.isInteger(requestedAttempt) || requestedAttempt < 1 || requestedAttempt > 50)) {
  throw new Error('--attempt in [1,50] is required for this stage');
}

const earlySeal = readJSON(SEAL_PATH);
function bootstrapOriginAnchor(paths) {
  const cleanEnvironment = { LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8', PATH: '/usr/bin:/bin' };
  const revisionResult = spawnSync(GIT, ['rev-parse', 'origin/main^{commit}'], {
    cwd: REPO, encoding: 'utf8', env: cleanEnvironment,
  });
  if (revisionResult.status !== 0 || !/^[0-9a-f]{40}\n?$/.test(revisionResult.stdout || '')) {
    throw new Error('cannot establish the bootstrap origin/main anchor');
  }
  const revision = revisionResult.stdout.trim();
  for (const path of paths) {
    const info = lstatSync(path);
    if (!info.isFile() || info.isSymbolicLink()) throw new Error(`launch anchor is not a plain file: ${path}`);
    const repositoryPath = relative(REPO, path).split(sep).join('/');
    if (!repositoryPath || repositoryPath.startsWith('../')) {
      throw new Error(`launch anchor is outside repository: ${path}`);
    }
    const committed = spawnSync(GIT, ['show', `${revision}:${repositoryPath}`], {
      cwd: REPO, encoding: null, env: cleanEnvironment, maxBuffer: 128 * 1024 * 1024,
    });
    if (committed.status !== 0 || !Buffer.isBuffer(committed.stdout) ||
        !committed.stdout.equals(readFileSync(path))) {
      throw new Error(`${path} is not byte-identical to local origin/main`);
    }
  }
  return revision;
}

bootstrapOriginAnchor([MANIFEST_PATH, SEAL_PATH]);
const earlyUnsignedSeal = structuredClone(earlySeal);
const earlyPayloadHash = earlyUnsignedSeal.runtime_payload_sha256;
delete earlyUnsignedSeal.runtime_payload_sha256;
if (earlyPayloadHash !== shaText(canonicalJSON(earlyUnsignedSeal))) {
  throw new Error('runtime seal payload hash mismatch before preflight');
}
const sealedSealUtility = earlySeal.seal_utility;
if (!isObject(sealedSealUtility) || realpathSync(SEAL_UTILITY) !== resolve(sealedSealUtility.path) ||
    lstatSync(SEAL_UTILITY).isSymbolicLink() || !lstatSync(SEAL_UTILITY).isFile() ||
    shaFile(SEAL_UTILITY) !== sealedSealUtility.sha256 ||
    statSync(SEAL_UTILITY).size !== sealedSealUtility.size_bytes) {
  throw new Error('preflight utility does not match the origin-anchored runtime seal');
}
if (!isObject(earlySeal.node_runtime) ||
    realpathSync(process.execPath) !== resolve(earlySeal.node_runtime.path) ||
    shaFile(realpathSync(process.execPath)) !== earlySeal.node_runtime.sha256 ||
    statSync(realpathSync(process.execPath)).size !== earlySeal.node_runtime.size_bytes) {
  throw new Error('runner is not executing under the sealed Node runtime');
}
if (!isObject(earlySeal.python_runtime) || !nonempty(earlySeal.python_runtime.path)) {
  throw new Error('runtime seal lacks exact Python interpreter binding');
}
const PYTHON = realpathSync(earlySeal.python_runtime.path);
if (PYTHON !== resolve(earlySeal.python_runtime.path) || !existsSync(PYTHON) ||
    shaFile(PYTHON) !== earlySeal.python_runtime.sha256 ||
    statSync(PYTHON).size !== earlySeal.python_runtime.size_bytes) {
  throw new Error('sealed Python interpreter bytes are unavailable');
}

let mutationGateActive = false;
function assertPreflight() {
  const result = spawnSync(PYTHON, [SEAL_UTILITY, 'check', '--run-root', RUN, '--quiet'], {
    encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
    env: { ...earlySeal.execution.retrieval_spawn_environment },
  });
  if (result.status !== 0) {
    throw new Error(`extension runtime preflight failed: ${(result.stderr || result.stdout).trim()}`);
  }
  if (mutationGateActive) assertMutationGateHeld();
}
assertPreflight();

const manifest = readJSON(MANIFEST_PATH);
const seal = earlySeal;
const RUN_ID = manifest.run_id;
const MODEL = manifest.execution.model;
const EFFORT = manifest.execution.reasoning_effort;
const MAX_ATTEMPTS = manifest.execution.max_attempts;
const FORCED_ATTEMPTS = manifest.protocol.inconclusive_min_valid_audited_attempts;
const K = manifest.bugbank.retrieval_k;
const DATABASE = resolve(seal.bugbank_database.path);
const MODEL_CLI = resolve(seal.model_cli_version.path);
const MODEL_RUNTIME_BUNDLE = resolve(seal.model_runtime_bundle.path);
const BWRAP = resolve(seal.os_isolation.bwrap.path);
const FLOCK = resolve(seal.mutation_gate.flock.path);
const CODEX_AUTH = resolve(process.env.PAIRED_EXTENSION_CODEX_AUTH ||
  join(process.env.HOME || '', '.codex', 'auth.json'));
if (MODEL_CLI !== join(MODEL_RUNTIME_BUNDLE, 'bin', 'codex')) {
  throw new Error('sealed native Codex path is not inside the sealed vendor bundle');
}
const SCRATCH = resolve(manifest.operations.scratch_root);
const STOP_FILE = resolve(manifest.operations.stop_file);
const REVISION_SCHEMA = resolve(RUN, manifest.schemas.revision.path);
const AUDIT_SCHEMA = resolve(RUN, manifest.schemas.audit.path);
const stopRequested = () => !scientificStartAllowed(dryRun, STOP_FILE);

if (manifest.schema !== 'paired_open_problem_extension_manifest_v1' ||
    manifest.protocol.id !== 'POST_FIXED_POINT_THREE_FORCED_V1' ||
    MODEL !== 'gpt-5.6-sol' || EFFORT !== 'max' || MAX_ATTEMPTS !== 50 ||
    FORCED_ATTEMPTS !== 3 || K !== 3) throw new Error('sealed extension contract mismatch');
if (!Array.isArray(manifest.protocol.neutral_lenses) || manifest.protocol.neutral_lenses.length !== 3 ||
    manifest.protocol.neutral_lenses.some((lens, index) => !isObject(lens) || lens.attempt !== index + 1 ||
      !nonempty(lens.name) || !nonempty(lens.instruction) ||
      lens.instruction_sha256 !== shaText(lens.instruction))) {
  throw new Error('three predeclared neutral lenses are required');
}
if (!Array.isArray(manifest.problem_ids) || !manifest.problem_ids.length ||
    new Set(manifest.problem_ids).size !== manifest.problem_ids.length ||
    manifest.problem_ids.some((id) => !safeIdPattern.test(id))) throw new Error('invalid roster');
const records = new Map(manifest.records.map((record) => [record.record_id, record]));
if (records.size !== manifest.problem_ids.length ||
    manifest.problem_ids.some((id) => !records.has(id))) throw new Error('record roster mismatch');
const ids = manifest.problem_ids.filter((id) => only.size === 0 || only.has(id));
if (!ids.length) throw new Error('no selected records');
if ([...selectedCells].some((cell) => !/^[A-Za-z0-9_.-]+:(plain|bugbank)$/.test(cell))) {
  throw new Error('invalid --cells value');
}

function requireMutationGate() {
  if (dryRun || stage === 'validate') return;
  const expectedPath = resolve(manifest.operations.ops_root, 'operation.lock');
  if (!isObject(seal.mutation_gate) || seal.mutation_gate.environment_variable !== 'PAIRED_OPERATION_LOCK_FD' ||
      seal.mutation_gate.required_fd !== 8 || seal.mutation_gate.operation_lock_path !== expectedPath ||
      seal.ops_namespace.operation_lock !== expectedPath ||
      process.env.PAIRED_OPERATION_LOCK_FD !== '8') {
    throw new Error('mutating extension runner requires the sealed PAIRED_OPERATION_LOCK_FD=8 gate');
  }
  verifyOrAcquireMutationLock(expectedPath, 8, FLOCK);
  mutationGateActive = true;
}
requireMutationGate();

function assertMutationGateHeld() {
  if (!mutationGateActive) throw new Error('mutating runner has no active mutation gate');
  verifyOrAcquireMutationLock(resolve(manifest.operations.ops_root, 'operation.lock'), 8, FLOCK);
}

function runPath(binding) {
  if (!isObject(binding) || !nonempty(binding.path) || resolve(RUN, binding.path).startsWith(`${RUN}${sep}`) === false) {
    throw new Error('unsafe run-relative binding');
  }
  return resolve(RUN, binding.path);
}
const record = (id) => records.get(id);
const inputPath = (id) => runPath(record(id).input);
const seedRevisionPath = (id, arm) => runPath(record(id).arms[arm].revision);
const seedAuditPath = (id, arm) => runPath(record(id).arms[arm].audit);
const attemptPath = (id, arm, attempt) => join(RUN, 'attempts', id, arm, `attempt_${attempt}.json`);
const auditPath = (id, arm, attempt) => join(RUN, 'audits', 'attempts', id, arm, `attempt_${attempt}.json`);
const receiptPath = (id, attempt) => join(RUN, 'retrievals', id, `attempt_${attempt}.json`);
const promptMetadataPath = (id, arm, attempt) =>
  join(RUN, 'prompts', `${id}__${arm}__attempt_${attempt}.json`);
const auditMetadataPath = (id, arm, attempt) =>
  join(RUN, 'prompts', 'audits', id, arm, `attempt_${attempt}.json`);

function scratchPath(id, stageName, arm, attempt) {
  return join(SCRATCH, id, stageName, arm, `attempt_${attempt}`);
}

function resetCellScratch(path, id, stageName, arm, attempt) {
  const expected = scratchPath(id, stageName, arm, attempt);
  if (resolve(path) !== resolve(expected) || !resolve(path).startsWith(`${SCRATCH}${sep}`)) {
    throw new Error('refusing to reset anything except the exact sealed cell scratch');
  }
  mkdirSync(SCRATCH, { recursive: true, mode: 0o700 });
  const rootInfo = lstatSync(SCRATCH);
  if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink()) {
    throw new Error('scratch root is not a plain directory');
  }
  mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
  const realRoot = realpathSync(SCRATCH);
  const realParent = realpathSync(dirname(path));
  if (realParent !== realRoot && !realParent.startsWith(`${realRoot}${sep}`)) {
    throw new Error('cell scratch parent escapes sealed scratch root');
  }
  if (existsSync(path)) {
    const info = lstatSync(path);
    if (!info.isDirectory() || info.isSymbolicLink()) {
      throw new Error('cell scratch is not a plain directory');
    }
    rmSync(path, { recursive: true, force: true });
  }
  mkdirSync(path, { mode: 0o700 });
}

function repoPath(path) {
  return relative(REPO, path).split(sep).join('/');
}

function artifact(path) {
  const bytes = readFileSync(path);
  return { path: repoPath(path), sha256: shaBytes(bytes), size_bytes: bytes.length };
}

function executionLogSegment(path, startOffset) {
  const bytes = readFileSync(path);
  if (!Number.isInteger(startOffset) || startOffset < 0 || startOffset > bytes.length) {
    throw new Error('execution log segment offset is invalid');
  }
  const segment = bytes.subarray(startOffset);
  return {
    path: repoPath(path), start_offset: startOffset,
    size_bytes: segment.length, sha256: shaBytes(segment),
  };
}

function executionLogPrefixSha(path, startOffset) {
  const bytes = readFileSync(path);
  if (!Number.isInteger(startOffset) || startOffset < 0 || startOffset > bytes.length) {
    throw new Error('execution log prefix offset is invalid');
  }
  return shaBytes(bytes.subarray(0, startOffset));
}

function runtimeEvidence() {
  return {
    extension_manifest_sha256: shaFile(MANIFEST_PATH), runtime_seal_sha256: shaFile(SEAL_PATH),
    runtime_payload_sha256: seal.runtime_payload_sha256, runner_sha256: shaFile(SCRIPT),
  };
}

let hostAtomicSequence = 0;
function hostAtomicTemporary(path, purpose) {
  const root = join(SCRATCH, '.host-atomic');
  mkdirSync(SCRATCH, { recursive: true, mode: 0o700 });
  const scratchInfo = lstatSync(SCRATCH);
  if (!scratchInfo.isDirectory() || scratchInfo.isSymbolicLink() ||
      (scratchInfo.mode & 0o077) !== 0) {
    throw new Error('external scratch root is unsafe');
  }
  mkdirSync(root, { recursive: true, mode: 0o700 });
  const rootInfo = lstatSync(root);
  if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink() ||
      (rootInfo.mode & 0o077) !== 0 ||
      !realpathSync(root).startsWith(`${realpathSync(SCRATCH)}${sep}`)) {
    throw new Error('external host-atomic staging root is unsafe');
  }
  hostAtomicSequence += 1;
  return join(root, `${purpose}__${shaText(resolve(path))}__pid_${process.pid}__${hostAtomicSequence}`);
}

function atomicWrite(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  const temporary = hostAtomicTemporary(path, 'replace');
  try {
    writeExclusive(temporary, data);
    // rename is atomic; if scratch and the run are unexpectedly on different
    // filesystems, EXDEV fails before touching the canonical target.
    renameSync(temporary, path);
  } finally {
    rmSync(temporary, { force: true });
  }
}

function writeExclusiveOrVerify(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  const bytes = Buffer.from(data);
  if (existsSync(path)) {
    if (!readFileSync(path).equals(bytes)) throw new Error(`immutable artifact conflict: ${path}`);
    return;
  }
  const temporary = hostAtomicTemporary(path, 'exclusive');
  try {
    writeExclusive(temporary, bytes);
    linkSync(temporary, path);
  } catch (error) {
    if (error?.code !== 'EEXIST' || !existsSync(path) || !readFileSync(path).equals(bytes)) throw error;
  } finally {
    rmSync(temporary, { force: true });
  }
}

function writeExclusive(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  const descriptor = openSync(path, 'wx', 0o644);
  try { writeFileSync(descriptor, data); fsyncSync(descriptor); } finally { closeSync(descriptor); }
}

function publishValidatedAbsent(source, out, validate) {
  const staging = `${out}.finalizing`;
  if (existsSync(staging) || existsSync(out)) {
    throw new Error('canonical output or finalization staging path already exists');
  }
  let linked = false;
  const bytes = readFileSync(source);
  try {
    writeExclusive(staging, bytes);
    if (!validate(staging)) throw new Error('host-side staged output revalidation failed');
    // link(2) is an atomic publish-if-absent operation.  Unlike rename(2), it
    // cannot silently replace a canonical artifact created by another process.
    linkSync(staging, out);
    linked = true;
  } finally {
    // Once linked, both names designate the same already-fsynced inode.
    // On an ordinary caught failure, remove only our exact staging name.
    if (existsSync(staging)) rmSync(staging, { force: true });
  }
  if (!linked || !readFileSync(out).equals(bytes)) {
    throw new Error('canonical output publish validation failed');
  }
}

function exposureManifest({ source, parent, audit = null, schema, scratch }) {
  const evidence = [
    { role: 'source', guest_path: '/evidence/source.json', artifact: artifact(source) },
    { role: 'parent', guest_path: '/evidence/parent.json', artifact: artifact(parent) },
  ];
  if (audit !== null) {
    evidence.push({ role: 'prior_independent_audit', guest_path: '/evidence/audit.json', artifact: artifact(audit) });
  }
  return {
    schema: 'paired_open_problem_extension_os_exposure_v1', mechanism: 'bubblewrap',
    bwrap: { path: BWRAP, sha256: shaFile(BWRAP), size_bytes: statSync(BWRAP).size },
    bwrap_execution_profile_sha256: shaText(canonicalJSON(seal.os_isolation.execution_profile)),
    evidence_mounts: evidence,
    output_schema_mount: { guest_path: '/evidence/output.schema.json', artifact: artifact(schema) },
    writable_mount: {
      guest_path: '/work', host_path: scratch,
      initial_state: 'EMPTY_DIRECTORY_RESET_UNDER_CANONICAL_CELL_LOCK',
    },
    codex_home_guest_path: '/run/codex-home',
    operational_credential_injection: '/run/codex-home/auth.json (bwrap --file from inherited fd 3; host path not mounted)',
    credential_source_fd_lifecycle: 'CONSUMED_AND_CLOSED_BEFORE_CODEX_EXEC',
    credential_visibility_to_model_tools: 'DENIED_BY_CUSTOM_PERMISSION_PROFILE',
    model_cli_guest_path: '/runtime/vendor/bin/codex',
    model_runtime_bundle_mount: structuredClone(seal.model_runtime_bundle),
    repository_mounted: false, bugbank_database_mounted: false,
    host_home_mounted: false, network_namespace: 'HOST_SHARED_FOR_MODEL_API',
  };
}

function seedContext(id, arm) {
  const parentPath = seedRevisionPath(id, arm);
  const parent = readJSON(parentPath);
  if (!validDraftCore(parent) || parent.record_id !== id || parent.arm !== arm) {
    return { ok: false, status: 'INVALID_SEED_REVISION' };
  }
  const parentHash = shaFile(parentPath);
  const priorAuditPath = seedAuditPath(id, arm);
  const priorAudit = readJSON(priorAuditPath);
  if (!validAuditValue(priorAudit, { id, arm, attempt: 0, parent, parentHash })) {
    return { ok: false, status: 'INVALID_SEED_AUDIT' };
  }
  return {
    ok: true, parentPath, parent, parentHash, auditPath: priorAuditPath,
    audit: priorAudit, auditHash: shaFile(priorAuditPath), seed: true,
  };
}

function uniqueRetrieved(receipt) {
  const idsSeen = new Set();
  const result = [];
  for (const query of receipt.queries) for (const hit of query.hits) {
    if (!idsSeen.has(hit.entry_id)) { idsSeen.add(hit.entry_id); result.push(hit.entry_id); }
  }
  return result;
}

function validateReceipt(path, id, attempt, context) {
  if (!existsSync(path)) return { valid: false, error: 'MISSING_RECEIPT' };
  try {
    const raw = readFileSync(path);
    const value = strictJSONParse(raw.toString('utf8'));
    if (value.schema !== 'paired_open_problem_extension_bugbank_receipt_v1' ||
        value.run_id !== RUN_ID || value.record_id !== id || value.arm !== 'bugbank' ||
        value.attempt !== attempt || value.stage !== 'EXTENSION_BUGBANK_EXPOSURE' ||
        value.status !== 'COMPLETE' || value.parent.sha256 !== context.parentHash ||
        value.parent.size_bytes !== statSync(context.parentPath).size ||
        value.parent_claim_count !== context.parent.results.length ||
        value.receipt_payload_sha256 !== pythonPayloadHash(raw, 'receipt_payload_sha256') ||
        value.database.sha256 !== shaFile(DATABASE) || resolve(value.database.path) !== DATABASE ||
        value.script.sha256 !== shaFile(FEEDBACK) || resolve(value.script.path) !== resolve(FEEDBACK) ||
        value.parameters.k_per_claim !== K ||
        value.parameters.query_text_basis !== 'claim statement, two newlines, proof_sketch' ||
        !Array.isArray(value.queries) || value.queries.length !== context.parent.results.length) {
      return { valid: false, error: 'RECEIPT_CONTRACT_MISMATCH' };
    }
    for (let index = 0; index < value.queries.length; index += 1) {
      const row = context.parent.results[index];
      const query = value.queries[index];
      const queryText = `${row.claim}\n\n${row.proof_sketch}`;
      if (query.claim_index !== index || query.claim !== row.claim ||
          query.claim_sha256 !== shaText(row.claim) ||
          query.proof_sketch_sha256 !== shaText(row.proof_sketch) ||
          query.query_text_sha256 !== shaText(queryText) || !Array.isArray(query.hits) ||
          query.hit_count !== query.hits.length || query.hits.length > K) {
        return { valid: false, error: 'RECEIPT_QUERY_MISMATCH' };
      }
    }
    return { valid: true, value, raw: raw.toString('utf8'), sha256: shaBytes(raw), retrieved: uniqueRetrieved(value) };
  } catch (error) { return { valid: false, error: String(error) }; }
}

function validateTreatment(revision, arm, receipt) {
  if (!Array.isArray(revision.retrieved_entry_ids) || !Array.isArray(revision.acted_on_entry_ids) ||
      !Array.isArray(revision.dismissed_hits) || !Array.isArray(revision.audit_feedback_acted_on)) return false;
  if (arm === 'plain') {
    return revision.treatment_status === 'PLAIN_SELF_CRITIQUE' && revision.receipt_path === '' &&
      revision.receipt_sha256 === '' && exactArray(revision.retrieved_entry_ids, []) &&
      exactArray(revision.acted_on_entry_ids, []) && exactArray(revision.dismissed_hits, []);
  }
  if (!receipt?.valid || revision.treatment_status !== 'BUGBANK_RECEIPT_EXPOSED' ||
      revision.receipt_path !== repoPath(receiptPath(revision.record_id, revision.iteration)) ||
      revision.receipt_sha256 !== receipt.sha256 ||
      !exactArray(revision.retrieved_entry_ids, receipt.retrieved)) return false;
  const acted = revision.acted_on_entry_ids;
  if (!acted.every(nonempty) || new Set(acted).size !== acted.length ||
      !acted.every((id) => receipt.retrieved.includes(id))) return false;
  const dismissed = revision.dismissed_hits;
  if (!dismissed.every((row) => isObject(row) && nonempty(row.entry_id) && nonempty(row.reason)) ||
      new Set(dismissed.map((row) => row.entry_id)).size !== dismissed.length) return false;
  const actedSet = new Set(acted);
  return exactArray(acted, receipt.retrieved.filter((id) => actedSet.has(id))) &&
    exactArray(dismissed.map((row) => row.entry_id), receipt.retrieved.filter((id) => !actedSet.has(id)));
}

function validRevisionValue(value, { id, arm, attempt, context, receipt }) {
  const keys = [
    'record_id', 'stage', 'arm', 'iteration', 'parent_sha256', 'audit_sha256',
    'treatment_status', 'receipt_path', 'receipt_sha256', 'retrieved_entry_ids',
    'acted_on_entry_ids', 'dismissed_hits', 'claimed_resolution', 'results', 'final_writeup',
    'audit_feedback_acted_on', 'checks_performed', 'self_assessment',
  ];
  return exactKeys(value, keys) && validDraftCore(value) &&
    value.results.every((row) => exactKeys(row, ['claim', 'proof_sketch'])) &&
    value.dismissed_hits.every((row) => exactKeys(row, ['entry_id', 'reason'])) &&
    value.record_id === id && value.stage === 'REVISION' &&
    value.arm === arm && value.iteration === attempt && value.parent_sha256 === context.parentHash &&
    value.audit_sha256 === context.auditHash && validateTreatment(value, arm, receipt);
}

function lensFor(attempt) {
  return attempt <= FORCED_ATTEMPTS ? manifest.protocol.neutral_lenses[attempt - 1] : null;
}

function revisionPromptBundle(id, arm, attempt, context, receipt = null) {
  const sourceRaw = readFileSync(inputPath(id), 'utf8');
  const parentRaw = readFileSync(context.parentPath, 'utf8');
  const auditRaw = readFileSync(context.auditPath, 'utf8');
  const scratch = scratchPath(id, 'revision', arm, attempt);
  const lens = lensFor(attempt);
  const schedule = lens === null
    ? `This is an exact-closure attempt after the three scheduled search lenses. Concentrate on resolving the independent audit. If no material proof change is required, copy claimed_resolution, every claim and proof_sketch, and final_writeup from the parent exactly.`
    : `This is scheduled search attempt ${attempt} of 3. Apply this predeclared arm-neutral lens:\n\n${lens.name}: ${lens.instruction}\n\nThis valid attempt is required even if the parent is already a fixed point. If the lens and audit support no material proof change, copy claimed_resolution, every claim and proof_sketch, and final_writeup from the parent exactly.`;
  const common = `You are extending one independently audited open-problem draft in a sealed paired experiment.

Read only source /evidence/source.json, parent /evidence/parent.json, and independent audit /evidence/audit.json. Do not use the web, any prior-run file other than those exact sealed inputs, any other solution, or any verification report. You may create exact-arithmetic checks only under /work; do not modify files outside /work.

Parent SHA-256: ${context.parentHash}
Audit SHA-256: ${context.auditHash}

${schedule}

Address every REFUTED or UNRESOLVED claim and the audit's target-coverage judgment. Preserve correct progress. Repair, narrow, replace, or remove unsupported claims. Never call the open target solved without a complete proof at the requested strength. Put every load-bearing claim in a separate results item in proof order. There is no claim-count cap. The entire ordered proof is in scope. Keep final_writeup under 3,000 words and each proof_sketch under 500 words.

Complete independent audit:
--- BEGIN AUDIT ---
${auditRaw}--- END AUDIT ---

`;
  let prompt;
  if (arm === 'plain') {
    prompt = `${common}Use native adversarial self-critique only. Do not read or use any retrieval result, external memory, treatment receipt, or database. Return revision-schema JSON. Use treatment_status PLAIN_SELF_CRITIQUE and empty receipt_path, receipt_sha256, retrieved_entry_ids, acted_on_entry_ids, and dismissed_hits.`;
  } else {
    if (!receipt?.valid) throw new Error('valid BugBank receipt required');
    prompt = `${common}Use the following complete diagnostic-memory receipt as fallible warnings, not authority. Independently check every applicable item. Each unique retrieved ID must appear exactly once: either in acted_on_entry_ids if it materially changes this attempt's proof state, or in dismissed_hits with a specific reason. Preserve first-retrieval order. If the parent already addresses an item and no proof change is needed, dismiss it rather than calling it acted on. The wrapper owns identity and lineage fields.

--- BEGIN COMPLETE TREATMENT RECEIPT ---
${receipt.raw}--- END COMPLETE TREATMENT RECEIPT ---

Return revision-schema JSON. Use treatment_status BUGBANK_RECEIPT_EXPOSED. Exact unique retrieved_entry_ids:
${JSON.stringify(receipt.retrieved, null, 2)}`;
    if (prompt.split(receipt.raw).length !== 2) throw new Error('receipt must be embedded exactly once');
  }
  const metadata = {
    schema: 'paired_open_problem_extension_prompt_v1', run_id: RUN_ID,
    record_id: id, stage: 'EXTENSION_REVISION_PROMPT', arm, attempt,
    claim_coverage_policy: 'WHOLE_PROOF_UNCAPPED_V1',
    forced_neutral_lens: lens,
    phase: lens === null ? 'POST_LENS_CLOSURE' : 'FORCED_NEUTRAL_LENS',
    prompt_text: prompt, prompt_utf8_sha256: shaText(prompt),
    prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
    source: artifact(inputPath(id)), parent: artifact(context.parentPath), audit: artifact(context.auditPath),
    receipt: arm === 'bugbank' ? artifact(receiptPath(id, attempt)) : null,
    treatment_exposed: arm === 'bugbank',
    requested_execution: {
      model: MODEL, reasoning_effort: EFFORT, sandbox: 'outer-bwrap-read-isolated',
      inner_sandbox: 'custom-sealed-workspace', user_config: 'ignored',
      model_tool_network: 'denied-by-inner-sandbox',
      web_search: 'disabled', shell_environment_inheritance: 'none',
      working_directory: '/work', repository_writes_forbidden: true,
    },
    os_read_isolation: exposureManifest({
      source: inputPath(id), parent: context.parentPath, audit: context.auditPath,
      schema: REVISION_SCHEMA, scratch,
    }),
  };
  return { prompt, metadata, scratch, sourceRaw, parentRaw };
}

function metadataWithHash(value) {
  const unsigned = structuredClone(value);
  delete unsigned.metadata_payload_sha256;
  return { ...unsigned, metadata_payload_sha256: shaText(canonicalJSON(unsigned)) };
}

function validPromptMetadata(path, expected) {
  if (!existsSync(path)) return false;
  try {
    const value = readJSON(path);
    const unsigned = structuredClone(value);
    const recorded = unsigned.metadata_payload_sha256;
    delete unsigned.metadata_payload_sha256;
    const expectedUnsigned = structuredClone(expected);
    delete expectedUnsigned.created_at;
    const actualUnsigned = structuredClone(unsigned);
    delete actualUnsigned.created_at;
    return recorded === shaText(canonicalJSON(unsigned)) &&
      canonicalJSON(actualUnsigned) === canonicalJSON(expectedUnsigned);
  } catch { return false; }
}

function ensurePromptMetadata(id, arm, attempt, bundle) {
  const path = promptMetadataPath(id, arm, attempt);
  const expected = bundle.metadata;
  if (existsSync(path)) {
    if (!validPromptMetadata(path, expected)) throw new Error('existing prompt metadata mismatch');
    return { binding: artifact(path), created: false };
  }
  const value = metadataWithHash({ ...expected, created_at: new Date().toISOString() });
  writeExclusiveOrVerify(path, Buffer.from(JSON.stringify(value, null, 2) + '\n'));
  return { binding: artifact(path), created: true };
}

function auditPrompt(id, arm, attempt, revision, revisionFile, scratch) {
  const parentHash = shaFile(revisionFile);
  const bindings = revision.results.map((row, idx) => ({
    idx, claim: row.claim, claim_sha256: shaText(row.claim),
  }));
  return `You are the independent adversarial audit agent for extension attempt ${attempt} of the ${arm} arm.

Read only source /evidence/source.json and draft /evidence/parent.json. Do not read the revision prompt, retrieval database, treatment receipt, other arm, prior-run material, or any other solution. Do not use the web. Do not trust claimed_resolution or self_assessment.

Judge whether the draft proves the exact source target at the requested strength. FULLY_RESOLVES_TARGET requires a complete proof of the entire target. Use VALID_PARTIAL_PROGRESS for correct incomplete progress, NO_VALID_PROGRESS if nothing material survives, and OVERCLAIMED if the writeup claims coverage the proof does not establish. Separately label claimed_resolution ACCURATE, OVERSTATED, or UNDERSTATED.

Audit every listed claim from scratch. Look for missing cases, quantifier mistakes, statement/model mismatches, invalid reductions, and counterexamples. Write exact-arithmetic checks only under /work. Persist each checker there and return its /work/... path; otherwise use literal "none" where genuinely inapplicable. VERIFIED requires a rigorous complete proof. REFUTED requires a concrete reproducible flaw or counterexample. Otherwise use UNRESOLVED.

Parent SHA-256: ${parentHash}
Exact claim bindings:
${JSON.stringify(bindings, null, 2)}

Return record_id ${JSON.stringify(id)}, stage REVISION_AUDIT, arm ${arm}, iteration ${attempt}, and the exact parent_sha256. Preserve every idx, claim, and claim_sha256. confirmed_refutations is exactly the increasing list of REFUTED indices. overall is REFUTED if any claim is refuted, VERIFIED only if every claim is verified, and INCONCLUSIVE otherwise. Return audit-schema JSON and do not modify repository files.`;
}

function checkerBinding(path, scratch) {
  if (path === 'none') return null;
  if (!nonempty(path) || !path.startsWith('/')) throw new Error('checker path must be absolute or none');
  const resolved = resolve(path);
  const root = resolve(scratch);
  if (!resolved.startsWith(`${root}${sep}`)) throw new Error('checker escapes exact scratch directory');
  const real = realpathSync(resolved);
  if (!real.startsWith(`${realpathSync(root)}${sep}`)) throw new Error('checker symlink escape');
  const info = lstatSync(real);
  if (!info.isFile() || info.isSymbolicLink()) throw new Error('checker is not a regular file');
  return { path: real, sha256: shaFile(real), size_bytes: info.size };
}

function auditMetadataBase(id, arm, attempt, revisionFile, auditValue, prompt, scratch) {
  const checkerArtifacts = [];
  for (let index = 0; index < auditValue.claims.length; index += 1) {
    const checker = checkerBinding(auditValue.claims[index].checker_path, scratch);
    if (checker === null) continue;
    const destination = join(RUN, 'checkers', id, arm, `attempt_${attempt}`,
      `claim_${index}__${checker.sha256}.checker`);
    const bytes = readFileSync(checker.path);
    writeExclusiveOrVerify(destination, bytes);
    checkerArtifacts.push({
      idx: index, original_path: checker.path, original_sha256: checker.sha256,
      original_size_bytes: checker.size_bytes, durable: artifact(destination),
    });
  }
  return metadataWithHash({
    schema: 'paired_open_problem_extension_audit_metadata_v1', run_id: RUN_ID,
    record_id: id, stage: 'REVISION_AUDIT', arm, attempt,
    source: artifact(inputPath(id)), parent: artifact(revisionFile),
    prompt_text: prompt, prompt_utf8_sha256: shaText(prompt),
    prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'), checker_artifacts: checkerArtifacts,
    requested_execution: {
      model: MODEL, reasoning_effort: EFFORT, sandbox: 'outer-bwrap-read-isolated',
      inner_sandbox: 'custom-sealed-workspace', user_config: 'ignored',
      model_tool_network: 'denied-by-inner-sandbox',
      web_search: 'disabled', shell_environment_inheritance: 'none',
      working_directory: '/work', repository_writes_forbidden: true,
    },
    os_read_isolation: exposureManifest({
      source: inputPath(id), parent: revisionFile, schema: AUDIT_SCHEMA, scratch,
    }),
  });
}

function validAuditMetadata(path, id, arm, attempt, revisionFile, auditValue, prompt) {
  if (!existsSync(path)) return false;
  try {
    const value = readJSON(path);
    const unsigned = structuredClone(value);
    const recorded = unsigned.metadata_payload_sha256;
    delete unsigned.metadata_payload_sha256;
    const expectedExposure = exposureManifest({
      source: inputPath(id), parent: revisionFile, schema: AUDIT_SCHEMA,
      scratch: scratchPath(id, 'audit', arm, attempt),
    });
    if (recorded !== shaText(canonicalJSON(unsigned)) ||
        value.schema !== 'paired_open_problem_extension_audit_metadata_v1' ||
        value.run_id !== RUN_ID || value.record_id !== id || value.arm !== arm || value.attempt !== attempt ||
        value.prompt_text !== prompt || value.prompt_utf8_sha256 !== shaText(prompt) ||
        canonicalJSON(value.source) !== canonicalJSON(artifact(inputPath(id))) ||
        canonicalJSON(value.parent) !== canonicalJSON(artifact(revisionFile)) ||
        canonicalJSON(value.requested_execution) !== canonicalJSON({
          model: MODEL, reasoning_effort: EFFORT, sandbox: 'outer-bwrap-read-isolated',
          inner_sandbox: 'custom-sealed-workspace', user_config: 'ignored',
          model_tool_network: 'denied-by-inner-sandbox',
          web_search: 'disabled', shell_environment_inheritance: 'none',
          working_directory: '/work', repository_writes_forbidden: true,
        }) || canonicalJSON(value.os_read_isolation) !== canonicalJSON(expectedExposure) ||
        !Array.isArray(value.checker_artifacts)) return false;
    const expectedIndices = auditValue.claims.map((claim, index) => claim.checker_path === 'none' ? null : index)
      .filter((index) => index !== null);
    if (!exactArray(value.checker_artifacts.map((row) => row.idx), expectedIndices)) return false;
    for (const row of value.checker_artifacts) {
      const durable = resolve(REPO, row.durable.path);
      if (!durable.startsWith(`${resolve(RUN, 'checkers')}${sep}`) || !existsSync(durable) ||
          row.durable.sha256 !== shaFile(durable) || row.durable.size_bytes !== statSync(durable).size ||
          row.original_sha256 !== row.durable.sha256 || row.original_size_bytes !== row.durable.size_bytes) return false;
    }
    return true;
  } catch { return false; }
}

function parseCodexCost(bytes) {
  const text = bytes.toString('utf8');
  const tokens = [...text.matchAll(/tokens used\s*\r?\n\s*([0-9][0-9,]*)/gi)];
  const models = [...text.matchAll(/^model:\s*(\S.*?)\s*$/gmi)];
  const efforts = [...text.matchAll(/^reasoning effort:\s*(\S.*?)\s*$/gmi)];
  const last = (rows) => rows.length ? rows[rows.length - 1][1].trim() : null;
  const token = last(tokens);
  let tokenCount = null;
  if (token !== null) {
    const exact = BigInt(token.replaceAll(',', ''));
    if (exact <= BigInt(Number.MAX_SAFE_INTEGER)) tokenCount = Number(exact);
  }
  return {
    tokens_used: tokenCount,
    model: last(models), reasoning_effort: last(efforts),
  };
}

function statePath(id, arm, attempt, stageName) {
  return join(RUN, 'states', `${id}__${arm}__attempt_${attempt}__${stageName}.json`);
}
function logPath(id, arm, attempt, stageName) {
  return join(RUN, 'logs', stageName, `${id}__${arm}__attempt_${attempt}.log`);
}
function lockPath(id, arm, attempt, stageName) {
  return join(RUN, 'locks', `${id}__${arm}__attempt_${attempt}__${stageName}.lock`);
}

function modelCosts(id, arm, throughAttempt) {
  const entries = [];
  for (let attempt = 1; attempt <= throughAttempt; attempt += 1) {
    for (const stageName of ['revision', 'audit']) {
      const path = statePath(id, arm, attempt, stageName);
      if (!existsSync(path)) { entries.push({ attempt, stage: stageName, missing: true }); continue; }
      try {
        const value = readJSON(path);
        entries.push({
          attempt, stage: stageName, missing: false, path: repoPath(path), status: value.status,
          tokens_used: value.tokens_used, model: value.model, reasoning_effort: value.reasoning_effort,
          duration_seconds: value.duration_seconds ?? 0,
          identity_valid: value.record_id === id && value.arm === arm && value.attempt === attempt &&
            value.stage === stageName && value.model === MODEL && value.reasoning_effort === EFFORT,
        });
      } catch { entries.push({ attempt, stage: stageName, missing: true }); }
    }
  }
  let auditable = entries.length === 2 * throughAttempt && entries.every((row) => !row.missing &&
    row.status === 'COMPLETE' && isTokenCount(row.tokens_used) &&
    row.tokens_used >= 0 && row.identity_valid);
  let tokensUsed = null;
  if (auditable) {
    try { tokensUsed = checkedTokenSum(entries.map((row) => row.tokens_used)); }
    catch { auditable = false; }
  }
  return {
    auditable, tokens_used: auditable ? tokensUsed : null,
    entries,
  };
}

function validCompleteModelState({
  id, arm, attempt, stageName, output, finalizedMetadata, expectedExtra,
}) {
  try {
    const value = readJSON(statePath(id, arm, attempt, stageName));
    const commonKeys = [
      'record_id', 'arm', 'attempt', 'stage', 'status', 'started_at', 'ended_at',
      'duration_seconds', 'error', 'tokens_used', 'model', 'reasoning_effort',
      'launcher_pid', 'launcher_process_start_ticks',
      'execution_log_start_offset', 'execution_log_prefix_sha256', 'execution_log_segment',
      'extension_manifest_sha256', 'runtime_seal_sha256', 'runtime_payload_sha256',
      'runner_sha256', ...Object.keys(expectedExtra), 'output', 'finalized_metadata',
    ];
    if (!exactKeys(value, commonKeys) || value.record_id !== id || value.arm !== arm ||
        value.attempt !== attempt || value.stage !== stageName || value.status !== 'COMPLETE' ||
        !isTokenCount(value.tokens_used) ||
        value.model !== MODEL || value.reasoning_effort !== EFFORT || value.error !== null ||
        !Number.isInteger(value.launcher_pid) || value.launcher_pid < 1 ||
        !/^[0-9]+$/.test(value.launcher_process_start_ticks ?? '') ||
        !nonempty(value.started_at) || !nonempty(value.ended_at) ||
        !Number.isFinite(value.duration_seconds) || value.duration_seconds < 0 ||
        !Number.isInteger(value.execution_log_start_offset) ||
        value.execution_log_start_offset < 0 ||
        value.extension_manifest_sha256 !== shaFile(MANIFEST_PATH) ||
        value.runtime_seal_sha256 !== shaFile(SEAL_PATH) ||
        value.runtime_payload_sha256 !== seal.runtime_payload_sha256 ||
        value.runner_sha256 !== shaFile(SCRIPT) ||
        canonicalJSON(value.output) !== canonicalJSON(artifact(output)) ||
        canonicalJSON(value.finalized_metadata) !== canonicalJSON(finalizedMetadata) ||
        !Object.entries(expectedExtra).every(([key, expected]) =>
          canonicalJSON(value[key]) === canonicalJSON(expected))) return false;
    const log = logPath(id, arm, attempt, stageName);
    if (canonicalJSON(value.execution_log_segment) !== canonicalJSON(
      executionLogSegment(log, value.execution_log_start_offset),
    ) || value.execution_log_prefix_sha256 !== executionLogPrefixSha(
      log, value.execution_log_start_offset,
    )) return false;
    const bytes = readFileSync(log);
    const logged = parseCodexCost(bytes.subarray(value.execution_log_start_offset));
    return logged.tokens_used === value.tokens_used && logged.model === MODEL &&
      logged.reasoning_effort === EFFORT;
  } catch { return false; }
}

function validCompleteReceiptState(id, attempt, context) {
  try {
    const arm = 'bugbank';
    const value = readJSON(statePath(id, arm, attempt, 'receipt'));
    const keys = [
      'record_id', 'arm', 'attempt', 'stage', 'status', 'started_at', 'ended_at',
      'duration_seconds', 'error', 'parent_sha256', 'retrieval_k', 'tokens_used',
      'model', 'reasoning_effort', 'extension_manifest_sha256', 'runtime_seal_sha256',
      'launcher_pid', 'launcher_process_start_ticks',
      'runtime_payload_sha256', 'runner_sha256', 'execution_log_start_offset',
      'execution_log_prefix_sha256', 'execution_log_segment', 'output',
    ];
    return exactKeys(value, keys) && value.record_id === id && value.arm === arm &&
      value.attempt === attempt && value.stage === 'receipt' && value.status === 'COMPLETE' &&
      value.parent_sha256 === context.parentHash && value.retrieval_k === K &&
      value.tokens_used === 0 && value.model === null && value.reasoning_effort === null &&
      Number.isInteger(value.launcher_pid) && value.launcher_pid >= 1 &&
      /^[0-9]+$/.test(value.launcher_process_start_ticks ?? '') &&
      value.error === null && nonempty(value.started_at) && nonempty(value.ended_at) &&
      Number.isFinite(value.duration_seconds) && value.duration_seconds >= 0 &&
      Number.isInteger(value.execution_log_start_offset) &&
      value.execution_log_start_offset >= 0 &&
      value.extension_manifest_sha256 === shaFile(MANIFEST_PATH) &&
      value.runtime_seal_sha256 === shaFile(SEAL_PATH) &&
      value.runtime_payload_sha256 === seal.runtime_payload_sha256 &&
      value.runner_sha256 === shaFile(SCRIPT) &&
      canonicalJSON(value.output) === canonicalJSON(artifact(receiptPath(id, attempt))) &&
      existsSync(logPath(id, arm, attempt, 'receipt')) &&
      lstatSync(logPath(id, arm, attempt, 'receipt')).isFile() &&
      !lstatSync(logPath(id, arm, attempt, 'receipt')).isSymbolicLink() &&
      canonicalJSON(value.execution_log_segment) === canonicalJSON(executionLogSegment(
        logPath(id, arm, attempt, 'receipt'), value.execution_log_start_offset,
      )) && value.execution_log_prefix_sha256 === executionLogPrefixSha(
        logPath(id, arm, attempt, 'receipt'), value.execution_log_start_offset,
      );
  } catch { return false; }
}

function assessment(id, arm, attempt, context, revision, audit) {
  const unchanged = canonicalJSON(proofState(context.parent)) === canonicalJSON(proofState(revision));
  const claimsUnchanged = exactArray(context.parent.results.map((row) => row.claim),
    revision.results.map((row) => row.claim));
  const strictFull = verifiedFull(revision, audit);
  const ownCost = modelCosts(id, arm, attempt);
  const auditSettled = audit.confirmed_refutations.length === 0 &&
    audit.claimed_resolution_verdict === 'ACCURATE' && audit.target_verdict !== 'OVERCLAIMED';
  const noActedHits = arm === 'plain' || revision.acted_on_entry_ids.length === 0;
  let budgetTarget = null;
  let budgetMatched = arm === 'bugbank' && ownCost.auditable;
  let budgetAuditable = arm === 'bugbank' && ownCost.auditable;
  if (arm === 'plain') {
    const treated = armProgress(id, 'bugbank');
    if (treated.terminal && isTokenCount(treated.incremental_model_tokens_used)) {
      budgetTarget = treated.incremental_model_tokens_used;
      budgetAuditable = ownCost.auditable && treated.incremental_token_cost_auditable;
      budgetMatched = budgetAuditable && ownCost.tokens_used >= budgetTarget;
    }
  }
  if (strictFull) return {
    status: 'VERIFIED_FULL', terminal: true,
    terminal_reason: 'FIRST_STRICT_INDEPENDENT_FULL_AUDIT', proof_state_unchanged: unchanged,
    ordered_claim_set_unchanged: claimsUnchanged, audit_settled: true, no_acted_hits: noActedHits,
    minimum_attempts_met: attempt >= FORCED_ATTEMPTS, token_budget_target: budgetTarget,
    token_budget_matched: budgetMatched, token_budget_auditable: budgetAuditable,
    reason: 'The first strict independent audit verified every claim and the complete exact target.',
  };
  const closure = attempt >= FORCED_ATTEMPTS && unchanged && auditSettled && noActedHits &&
    ownCost.auditable && budgetMatched;
  if (closure) return {
    status: 'INCONCLUSIVE_EXTENDED_FIXED_POINT', terminal: true,
    terminal_reason: 'AUDITED_POST_LENS_FIXED_POINT', proof_state_unchanged: true,
    ordered_claim_set_unchanged: claimsUnchanged, audit_settled: true, no_acted_hits: true,
    minimum_attempts_met: true, token_budget_target: budgetTarget,
    token_budget_matched: true, token_budget_auditable: true,
    reason: 'After all three scheduled lenses, the exact proof state closed under an independent audit and the extension budget condition.',
  };
  let reason = attempt < FORCED_ATTEMPTS
    ? `Attempt ${attempt} is valid, but all three predeclared neutral-lens attempts are required before an inconclusive stop.`
    : !unchanged ? 'The proof state changed and requires another complete audited attempt.'
      : !auditSettled ? 'The independent audit still reports a refutation or target/label mismatch.'
        : !noActedHits ? 'BugBank feedback changed the proof state and must be rechecked in a fresh retrieval cycle.'
          : !ownCost.auditable ? 'Extension model-call tokens are not fully auditable.'
            : arm === 'plain' && budgetTarget === null ? 'Plain is waiting for the BugBank extension endpoint.'
              : 'Plain has not yet matched the BugBank extension-token endpoint.';
  return {
    status: 'CONTINUE', terminal: false, terminal_reason: null,
    proof_state_unchanged: unchanged, ordered_claim_set_unchanged: claimsUnchanged,
    audit_settled: auditSettled, no_acted_hits: noActedHits,
    minimum_attempts_met: attempt >= FORCED_ATTEMPTS, token_budget_target: budgetTarget,
    token_budget_matched: budgetMatched, token_budget_auditable: budgetAuditable,
    waiting_for_bugbank_endpoint: arm === 'plain' && attempt >= FORCED_ATTEMPTS &&
      unchanged && auditSettled && ownCost.auditable && budgetTarget === null,
    reason,
  };
}

function completedAttempt(id, arm, attempt) {
  const context = attemptContext(id, arm, attempt);
  if (!context.ok) return context;
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = validateReceipt(receiptPath(id, attempt), id, attempt, context);
    if (!receipt.valid) return { ok: false, status: receipt.error };
    if (!validCompleteReceiptState(id, attempt, context)) {
      return { ok: false, status: 'INVALID_RECEIPT_STATE' };
    }
  }
  let bundle;
  try { bundle = revisionPromptBundle(id, arm, attempt, context, receipt); }
  catch (error) { return { ok: false, status: 'INVALID_PROMPT_INPUT', error: String(error) }; }
  if (!validPromptMetadata(promptMetadataPath(id, arm, attempt), bundle.metadata)) {
    return { ok: false, status: 'MISSING_OR_INVALID_PROMPT_METADATA' };
  }
  const revisionFile = attemptPath(id, arm, attempt);
  if (!existsSync(revisionFile)) return { ok: false, status: 'MISSING_REVISION' };
  let revision;
  try { revision = readJSON(revisionFile); } catch { return { ok: false, status: 'INVALID_REVISION_JSON' }; }
  if (!validRevisionValue(revision, { id, arm, attempt, context, receipt })) {
    return { ok: false, status: 'INVALID_REVISION' };
  }
  const revisionExposure = bundle.metadata.os_read_isolation;
  if (!validCompleteModelState({
    id, arm, attempt, stageName: 'revision', output: revisionFile,
    finalizedMetadata: null,
    expectedExtra: {
      parent_sha256: context.parentHash, audit_sha256: context.auditHash,
      prompt_sha256: shaText(bundle.prompt),
      prompt_size_bytes: Buffer.byteLength(bundle.prompt, 'utf8'),
      prompt_metadata_sha256: shaFile(promptMetadataPath(id, arm, attempt)),
      os_read_isolation_sha256: shaText(canonicalJSON(revisionExposure)),
      neutral_lens_attempt: lensFor(attempt)?.attempt ?? null,
      receipt_sha256: receipt?.sha256 ?? null,
    },
  })) return { ok: false, status: 'INVALID_REVISION_STATE' };
  const auditFile = auditPath(id, arm, attempt);
  if (!existsSync(auditFile)) return { ok: false, status: 'MISSING_AUDIT' };
  let audit;
  try { audit = readJSON(auditFile); } catch { return { ok: false, status: 'INVALID_AUDIT_JSON' }; }
  const revisionHash = shaFile(revisionFile);
  if (!validAuditValue(audit, { id, arm, attempt, parent: revision, parentHash: revisionHash })) {
    return { ok: false, status: 'INVALID_AUDIT' };
  }
  const auditScratch = scratchPath(id, 'audit', arm, attempt);
  const expectedAuditPrompt = auditPrompt(id, arm, attempt, revision, revisionFile, auditScratch);
  if (!validAuditMetadata(auditMetadataPath(id, arm, attempt), id, arm, attempt,
    revisionFile, audit, expectedAuditPrompt)) {
    return { ok: false, status: 'MISSING_OR_INVALID_AUDIT_METADATA' };
  }
  const auditExposure = exposureManifest({
    source: inputPath(id), parent: revisionFile, schema: AUDIT_SCHEMA,
    scratch: auditScratch,
  });
  if (!validCompleteModelState({
    id, arm, attempt, stageName: 'audit', output: auditFile,
    finalizedMetadata: artifact(auditMetadataPath(id, arm, attempt)),
    expectedExtra: {
      parent_sha256: revisionHash, prompt_sha256: shaText(expectedAuditPrompt),
      prompt_size_bytes: Buffer.byteLength(expectedAuditPrompt, 'utf8'),
      os_read_isolation_sha256: shaText(canonicalJSON(auditExposure)),
      audit_output_normalizer: 'DERIVABLE_FIELDS_ONLY_V1',
    },
  })) return { ok: false, status: 'INVALID_AUDIT_STATE' };
  return {
    ok: true, context, receipt, bundle, revisionFile, revision,
    revisionHash, auditFile, audit, auditHash: shaFile(auditFile),
    assessment: assessment(id, arm, attempt, context, revision, audit),
  };
}

function attemptContext(id, arm, attempt) {
  if (attempt === 1) return seedContext(id, arm);
  const previous = completedAttempt(id, arm, attempt - 1);
  if (!previous.ok) return { ok: false, status: `PREVIOUS_${previous.status}` };
  if (previous.assessment.terminal) return {
    ok: false, status: 'ALREADY_TERMINAL', terminal: previous.assessment,
  };
  return {
    ok: true, parentPath: previous.revisionFile, parent: previous.revision,
    parentHash: previous.revisionHash, auditPath: previous.auditFile,
    audit: previous.audit, auditHash: previous.auditHash, seed: false,
  };
}

function seedLifetimeTokens(id, arm) {
  const value = record(id).arms[arm].seed_lifetime_model_tokens;
  if (!isTokenCount(value)) throw new Error(`invalid seed lifetime tokens for ${id}:${arm}`);
  return value;
}

function lifetimeModelTokens(seedTokens, costs) {
  return costs.auditable ? checkedTokenSum([seedTokens, costs.tokens_used]) : null;
}

function armProgress(id, arm) {
  const seed = seedContext(id, arm);
  if (!seed.ok) return {
    arm, status: 'INCOMPLETE', terminal: false, next_attempt: 1,
    reason: seed.status, incremental_model_tokens_used: null,
    incremental_token_cost_auditable: false,
    seed_lifetime_model_tokens: seedLifetimeTokens(id, arm), lifetime_model_tokens_used: null,
  };
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    const completed = completedAttempt(id, arm, attempt);
    if (!completed.ok) {
      const costs = modelCosts(id, arm, attempt - 1);
      const seedTokens = seedLifetimeTokens(id, arm);
      return {
        arm, status: 'INCOMPLETE', terminal: false, next_attempt: attempt,
        reason: completed.status, incremental_model_tokens_used: costs.tokens_used,
        incremental_token_cost_auditable: costs.auditable,
        seed_lifetime_model_tokens: seedTokens,
        lifetime_model_tokens_used: lifetimeModelTokens(seedTokens, costs),
      };
    }
    if (completed.assessment.terminal) {
      const costs = modelCosts(id, arm, attempt);
      const seedTokens = seedLifetimeTokens(id, arm);
      return {
        arm, status: completed.assessment.status, terminal: true, attempt,
        terminal_reason: completed.assessment.terminal_reason,
        reason: completed.assessment.reason,
        proof_state_unchanged: completed.assessment.proof_state_unchanged,
        ordered_claim_set_unchanged: completed.assessment.ordered_claim_set_unchanged,
        audit_settled: completed.assessment.audit_settled,
        no_acted_hits: completed.assessment.no_acted_hits,
        minimum_attempts_met: completed.assessment.minimum_attempts_met,
        token_budget_target: completed.assessment.token_budget_target,
        token_budget_matched: completed.assessment.token_budget_matched,
        token_budget_auditable: completed.assessment.token_budget_auditable,
        incremental_model_tokens_used: costs.tokens_used,
        incremental_token_cost_auditable: costs.auditable,
        seed_lifetime_model_tokens: seedTokens,
        lifetime_model_tokens_used: lifetimeModelTokens(seedTokens, costs),
        claimed_resolution: completed.revision.claimed_resolution,
        target_verdict: completed.audit.target_verdict,
        audit_overall: completed.audit.overall,
        claim_count: completed.revision.results.length,
        parent_proof_state_sha256: proofStateHash(completed.context.parent),
        revision_proof_state_sha256: proofStateHash(completed.revision),
        revision: artifact(completed.revisionFile), audit: artifact(completed.auditFile),
        prompt_metadata: artifact(promptMetadataPath(id, arm, attempt)),
        receipt: arm === 'bugbank' ? artifact(receiptPath(id, attempt)) : null,
        execution_costs: costs,
      };
    }
    if (completed.assessment.waiting_for_bugbank_endpoint) {
      const treated = armProgress(id, 'bugbank');
      if (treated.status.startsWith('INCOMPLETE_MAX_')) {
        const costs = modelCosts(id, arm, attempt);
        const seedTokens = seedLifetimeTokens(id, arm);
        return {
          arm, status: 'INCOMPLETE_BUGBANK_NO_ENDPOINT', terminal: false,
          max_attempts_reached: false, next_attempt: null,
          reason: 'BugBank exhausted 50 attempts without an endpoint, so the plain incremental target is undefined.',
          incremental_model_tokens_used: costs.tokens_used,
          incremental_token_cost_auditable: costs.auditable,
          seed_lifetime_model_tokens: seedTokens,
          lifetime_model_tokens_used: lifetimeModelTokens(seedTokens, costs),
        };
      }
      // Re-evaluate the completed attempt after BugBank obtains an endpoint.
      if (!treated.terminal) {
        const costs = modelCosts(id, arm, attempt);
        const seedTokens = seedLifetimeTokens(id, arm);
        return {
          arm, status: 'INCOMPLETE_WAITING_FOR_BUGBANK', terminal: false,
          next_attempt: null, reason: completed.assessment.reason,
          incremental_model_tokens_used: costs.tokens_used,
          incremental_token_cost_auditable: costs.auditable,
          seed_lifetime_model_tokens: seedTokens,
          lifetime_model_tokens_used: lifetimeModelTokens(seedTokens, costs),
        };
      }
      const reassessed = assessment(id, arm, attempt, completed.context, completed.revision, completed.audit);
      if (reassessed.terminal) return armProgress(id, arm);
    }
  }
  const costs = modelCosts(id, arm, MAX_ATTEMPTS);
  const seedTokens = seedLifetimeTokens(id, arm);
  return {
    arm, status: 'INCOMPLETE_MAX_ATTEMPTS', terminal: false, max_attempts_reached: true,
    next_attempt: null, reason: 'No valid terminal endpoint was reached within 50 extension attempts.',
    incremental_model_tokens_used: costs.tokens_used,
    incremental_token_cost_auditable: costs.auditable,
    seed_lifetime_model_tokens: seedTokens,
    lifetime_model_tokens_used: lifetimeModelTokens(seedTokens, costs),
  };
}

function terminalValue(id) {
  const arms = { bugbank: armProgress(id, 'bugbank'), plain: armProgress(id, 'plain') };
  const complete = arms.bugbank.terminal && arms.plain.terminal &&
    arms.bugbank.incremental_token_cost_auditable && arms.plain.incremental_token_cost_auditable;
  const incrementalDifference = isTokenCount(arms.plain.incremental_model_tokens_used) &&
    isTokenCount(arms.bugbank.incremental_model_tokens_used)
    ? checkedTokenDifference(arms.plain.incremental_model_tokens_used,
      arms.bugbank.incremental_model_tokens_used) : null;
  const lifetimeDifference = isTokenCount(arms.plain.lifetime_model_tokens_used) &&
    isTokenCount(arms.bugbank.lifetime_model_tokens_used)
    ? checkedTokenDifference(arms.plain.lifetime_model_tokens_used,
      arms.bugbank.lifetime_model_tokens_used) : null;
  const unsigned = {
    schema: 'paired_open_problem_extension_pair_terminal_v1', run_id: RUN_ID,
    record_id: id, stage: 'EXTENSION_PAIR_TERMINAL',
    status: complete ? 'COMPLETE' : 'INCOMPLETE', treatment_contrast_valid: complete,
    forced_audited_attempts: FORCED_ATTEMPTS, max_attempts: MAX_ATTEMPTS, retrieval_k: K,
    comparison_basis: 'EXTENSION_INCREMENTAL_MODEL_TOKENS',
    incremental_plain_minus_bugbank_tokens: incrementalDifference,
    lifetime_plain_minus_bugbank_tokens: lifetimeDifference,
    solved_arms: ['bugbank', 'plain'].filter((arm) => arms[arm].status === 'VERIFIED_FULL'),
    seed_pair_terminal: artifact(runPath(record(id).seed_pair_terminal)), arms,
  };
  return {
    ...unsigned,
    terminal_payload_sha256: pythonPayloadHash(JSON.stringify(unsigned), '__absent_terminal_hash__'),
  };
}

if (!dryRun && stage !== 'validate') {
  for (const directory of [
    'attempts', 'audits/attempts', 'retrievals', 'prompts',
    'checkers', 'states', 'logs/receipt', 'logs/revision', 'logs/audit',
    'locks', 'terminals', 'summaries',
  ]) mkdirSync(join(RUN, directory), { recursive: true });
}

function retireStaleCellLock(path, identity, canonicalOutput, allowOutput = false) {
  if (existsSync(path)) {
    const info = lstatSync(path);
    if (!info.isFile() || info.isSymbolicLink()) {
      throw new Error('canonical cell lock is not a plain file');
    }
    const prior = readJSON(path);
    if (!exactKeys(prior, ['pid', 'process_start_ticks', 'id', 'arm', 'attempt', 'stage', 'started_at']) ||
        !Number.isInteger(prior.pid) || prior.pid < 1 || !/^[0-9]+$/.test(prior.process_start_ticks) ||
        prior.id !== identity.id || prior.arm !== identity.arm || prior.attempt !== identity.attempt ||
        prior.stage !== identity.stage || !nonempty(prior.started_at)) {
      throw new Error('canonical cell lock has a malformed or mismatched identity');
    }
    if (processStartTicks(prior.pid) === prior.process_start_ticks) return false;
    assertMutationGateHeld();
    if (!allowOutput && (existsSync(canonicalOutput) || existsSync(`${canonicalOutput}.finalizing`))) {
      throw new Error('stale cell lock accompanies an orphaned published/staged output');
    }
    const priorStatePath = statePath(prior.id, prior.arm, prior.attempt, prior.stage);
    if (existsSync(priorStatePath)) {
      const priorState = readJSON(priorStatePath);
      if (priorState.record_id !== prior.id || priorState.arm !== prior.arm ||
          priorState.attempt !== prior.attempt || priorState.stage !== prior.stage ||
          !['RUNNING', 'FAILED', 'SPAWN_FAILED'].includes(priorState.status)) {
        throw new Error('stale cell lock is not paired with a retryable execution state');
      }
      if (priorState.started_at === prior.started_at &&
          (priorState.launcher_pid !== prior.pid ||
           priorState.launcher_process_start_ticks !== prior.process_start_ticks)) {
        throw new Error('stale same-admission lock does not match state launcher identity');
      }
      if (priorState.started_at !== prior.started_at &&
          processStartTicks(priorState.launcher_pid) === priorState.launcher_process_start_ticks) {
        throw new Error('replacement admission overlaps the exact live prior state owner');
      }
    }
    rmSync(path);
  }
  return true;
}

function acquireLock(path, payload, canonicalOutput) {
  mkdirSync(dirname(path), { recursive: true });
  if (!/^[0-9]+$/.test(payload.process_start_ticks ?? '')) {
    throw new Error('could not bind the current process start time into the cell lock');
  }
  if (!retireStaleCellLock(path, payload, canonicalOutput)) return false;
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

function withdrawDerivedTerminal(id) {
  const path = join(RUN, 'terminals', `${id}.json`);
  if (!existsSync(path)) return;
  const value = readJSON(path);
  const raw = readFileSync(path);
  if (value.schema !== 'paired_open_problem_extension_pair_terminal_v1' ||
      value.run_id !== RUN_ID || value.record_id !== id || value.status !== 'INCOMPLETE' ||
      value.terminal_payload_sha256 !== pythonPayloadHash(raw, 'terminal_payload_sha256')) {
    throw new Error('refusing to withdraw a malformed or COMPLETE derived terminal');
  }
  assertMutationGateHeld();
  rmSync(path);
}

function recoverDeadCellLocks() {
  if (dryRun || stage === 'validate') return;
  const directory = join(RUN, 'locks');
  for (const name of readdirSync(directory)) {
    const match = /^(.+)__(plain|bugbank)__attempt_([1-9][0-9]*)__(receipt|revision|audit)\.lock$/.exec(name);
    if (!match) throw new Error(`noncanonical cell lock blocks recovery: ${name}`);
    const [, id, arm, rawAttempt, stageName] = match;
    const attempt = Number(rawAttempt);
    if (!records.has(id) || attempt > MAX_ATTEMPTS || (stageName === 'receipt' && arm !== 'bugbank')) {
      throw new Error(`cell lock identity is outside the sealed roster: ${name}`);
    }
    const path = join(directory, name);
    const pathInfo = lstatSync(path);
    if (!pathInfo.isFile() || pathInfo.isSymbolicLink()) {
      throw new Error(`non-plain cell lock blocks recovery: ${name}`);
    }
    const lock = readJSON(path);
    if (!exactKeys(lock, ['pid', 'process_start_ticks', 'id', 'arm', 'attempt', 'stage', 'started_at']) ||
        lock.id !== id || lock.arm !== arm || lock.attempt !== attempt || lock.stage !== stageName ||
        !Number.isInteger(lock.pid) || lock.pid < 1 || !/^[0-9]+$/.test(lock.process_start_ticks) ||
        !nonempty(lock.started_at)) throw new Error(`malformed cell lock blocks recovery: ${name}`);
    if (processStartTicks(lock.pid) === lock.process_start_ticks) continue;
    const output = stageName === 'receipt' ? receiptPath(id, attempt)
      : stageName === 'revision' ? attemptPath(id, arm, attempt)
        : auditPath(id, arm, attempt);
    const state = statePath(id, arm, attempt, stageName);
    if (!existsSync(state)) {
      if (existsSync(output) || existsSync(`${output}.finalizing`)) {
        throw new Error(`state-free stale lock has output bytes: ${name}`);
      }
      assertMutationGateHeld();
      rmSync(path);
      continue;
    }
    const value = readJSON(state);
    if (value.record_id !== id || value.arm !== arm || value.attempt !== attempt ||
        value.stage !== stageName) {
      throw new Error(`stale lock/state identity mismatch: ${name}`);
    }
    if (['RUNNING', 'FAILED', 'SPAWN_FAILED'].includes(value.status) &&
        !existsSync(output) && !existsSync(`${output}.finalizing`)) {
      if (!Number.isInteger(value.launcher_pid) || value.launcher_pid < 1 ||
          !/^[0-9]+$/.test(value.launcher_process_start_ticks ?? '')) {
        throw new Error(`retryable state lacks launcher process identity: ${name}`);
      }
      if (value.started_at === lock.started_at &&
          (value.launcher_pid !== lock.pid ||
           value.launcher_process_start_ticks !== lock.process_start_ticks)) {
        throw new Error(`same-admission lock/state process identity mismatch: ${name}`);
      }
      if (value.started_at !== lock.started_at &&
          (!nonempty(value.started_at) || lock.started_at <= value.started_at)) {
        throw new Error(`stale replacement lock does not postdate retryable state: ${name}`);
      }
      if (value.started_at !== lock.started_at &&
          processStartTicks(value.launcher_pid) === value.launcher_process_start_ticks) {
        throw new Error(`replacement lock overlaps the exact live prior owner: ${name}`);
      }
      assertMutationGateHeld();
      rmSync(path);
      continue;
    }
    if (value.status === 'COMPLETE' && value.started_at === lock.started_at &&
        value.launcher_pid === lock.pid &&
        value.launcher_process_start_ticks === lock.process_start_ticks &&
        existsSync(output) && isObject(value.output) &&
        canonicalJSON(value.output) === canonicalJSON(artifact(output))) {
      assertMutationGateHeld();
      rmSync(path);
    }
    // Retryable output/staging publication remains for its output-aware cell
    // recovery; anything else remains visible and fails closed downstream.
  }
}

recoverDeadCellLocks();

function retryableStateMatches(value, { id, arm, attempt, stageName, stateExtra }) {
  if (!isObject(value) || !['RUNNING', 'FAILED', 'SPAWN_FAILED'].includes(value.status)) return false;
  const baseKeys = [
    'record_id', 'arm', 'attempt', 'stage', 'status', 'started_at',
    'launcher_pid', 'launcher_process_start_ticks',
    'execution_log_start_offset',
    'execution_log_prefix_sha256',
    'extension_manifest_sha256', 'runtime_seal_sha256', 'runtime_payload_sha256',
    'runner_sha256', ...Object.keys(stateExtra),
  ];
  const finalKeys = [
    'ended_at', 'duration_seconds', 'error', 'tokens_used', 'model', 'reasoning_effort',
    'execution_log_segment',
  ];
  if (!exactKeys(value, value.status === 'RUNNING' ? baseKeys : [...baseKeys, ...finalKeys]) ||
      value.record_id !== id || value.arm !== arm || value.attempt !== attempt ||
      value.stage !== stageName || value.extension_manifest_sha256 !== shaFile(MANIFEST_PATH) ||
      value.runtime_seal_sha256 !== shaFile(SEAL_PATH) ||
      value.runtime_payload_sha256 !== seal.runtime_payload_sha256 ||
      value.runner_sha256 !== shaFile(SCRIPT) || !nonempty(value.started_at) ||
      !Number.isInteger(value.launcher_pid) || value.launcher_pid < 1 ||
      !/^[0-9]+$/.test(value.launcher_process_start_ticks ?? '') ||
      !Number.isInteger(value.execution_log_start_offset) || value.execution_log_start_offset < 0) return false;
  try {
    if (value.execution_log_prefix_sha256 !== executionLogPrefixSha(
      logPath(id, arm, attempt, stageName), value.execution_log_start_offset,
    )) return false;
  } catch { return false; }
  if (!Object.entries(stateExtra).every(([key, expected]) =>
    canonicalJSON(value[key]) === canonicalJSON(expected))) return false;
  if (value.status !== 'RUNNING') {
    try {
      if (canonicalJSON(value.execution_log_segment) !== canonicalJSON(executionLogSegment(
        logPath(id, arm, attempt, stageName), value.execution_log_start_offset,
      ))) return false;
    } catch { return false; }
  }
  return true;
}

function recoverPublishedModelState({
  id, arm, attempt, stageName, out, prompt, stateExtra,
}) {
  assertPreflight();
  const state = statePath(id, arm, attempt, stageName);
  const prior = readJSON(state);
  const prepared = typeof stateExtra === 'function'
    ? { binding: artifact(promptMetadataPath(id, arm, attempt)), created: false }
    : null;
  const resolvedExtra = typeof stateExtra === 'function' ? stateExtra(prepared) : stateExtra;
  if (!retryableStateMatches(prior, { id, arm, attempt, stageName, stateExtra: resolvedExtra })) {
    throw new Error('orphaned output lacks an exact retryable predecessor state');
  }
  if (retryableLauncherIsLive(prior)) {
    throw new Error('orphaned output still has its exact live predecessor process');
  }
  const lock = lockPath(id, arm, attempt, stageName);
  if (!retireStaleCellLock(lock, { id, arm, attempt, stage: stageName }, out, true)) {
    throw new Error('orphaned output is still owned by the exact live call process');
  }
  const staging = `${out}.finalizing`;
  if (existsSync(staging)) {
    if (lstatSync(staging).isSymbolicLink() || !lstatSync(staging).isFile() ||
        !readFileSync(staging).equals(readFileSync(out))) {
      throw new Error('orphaned output has a conflicting finalization staging file');
    }
    rmSync(staging);
  }
  const log = logPath(id, arm, attempt, stageName);
  if (!existsSync(log) || lstatSync(log).isSymbolicLink() || !lstatSync(log).isFile()) {
    throw new Error('orphaned output lacks a plain execution log');
  }
  const logBytes = readFileSync(log);
  if (prior.execution_log_start_offset > logBytes.length) {
    throw new Error('orphaned output log offset exceeds the canonical log');
  }
  const cost = parseCodexCost(logBytes.subarray(prior.execution_log_start_offset));
  if (!isTokenCount(cost.tokens_used) ||
      cost.model !== MODEL || cost.reasoning_effort !== EFFORT) {
    throw new Error('orphaned output lacks complete sealed model telemetry');
  }
  const finalizedMetadata = stageName === 'audit'
    ? artifact(auditMetadataPath(id, arm, attempt)) : null;
  const started = Date.parse(prior.started_at);
  const duration = Number.isFinite(prior.duration_seconds) && prior.duration_seconds >= 0
    ? prior.duration_seconds : Number.isFinite(started) ? Math.max(0, (Date.now() - started) / 1000) : 0;
  assertPreflight();
  withdrawDerivedTerminal(id);
  atomicWrite(state, JSON.stringify({
    record_id: id, arm, attempt, stage: stageName, status: 'COMPLETE',
    started_at: prior.started_at, ended_at: new Date().toISOString(),
    duration_seconds: duration, error: null, ...cost,
    launcher_pid: prior.launcher_pid,
    launcher_process_start_ticks: prior.launcher_process_start_ticks,
    execution_log_start_offset: prior.execution_log_start_offset,
    execution_log_prefix_sha256: prior.execution_log_prefix_sha256,
    execution_log_segment: executionLogSegment(log, prior.execution_log_start_offset),
    ...runtimeEvidence(), ...resolvedExtra,
    output: artifact(out), finalized_metadata: finalizedMetadata,
  }, null, 2) + '\n');
  return cost;
}

function recoverPublishedReceiptState({ id, attempt, out, parentHash }) {
  assertPreflight();
  const arm = 'bugbank';
  const stageName = 'receipt';
  const state = statePath(id, arm, attempt, stageName);
  const prior = readJSON(state);
  if (!retryableStateMatches(prior, {
    id, arm, attempt, stageName,
    stateExtra: { parent_sha256: parentHash, retrieval_k: K },
  })) throw new Error('orphaned receipt lacks an exact retryable predecessor state');
  if (retryableLauncherIsLive(prior)) {
    throw new Error('orphaned receipt still has its exact live predecessor process');
  }
  const lock = lockPath(id, arm, attempt, stageName);
  if (!retireStaleCellLock(lock, { id, arm, attempt, stage: stageName }, out, true)) {
    throw new Error('orphaned receipt is still owned by the exact live generator');
  }
  const staging = `${out}.finalizing`;
  if (existsSync(staging)) {
    if (lstatSync(staging).isSymbolicLink() || !lstatSync(staging).isFile() ||
        !readFileSync(staging).equals(readFileSync(out))) {
      throw new Error('orphaned receipt has a conflicting finalization staging file');
    }
    rmSync(staging);
  }
  const log = logPath(id, arm, attempt, stageName);
  if (!existsSync(log) || lstatSync(log).isSymbolicLink() || !lstatSync(log).isFile()) {
    throw new Error('orphaned receipt lacks its plain execution log');
  }
  const started = Date.parse(prior.started_at);
  const duration = Number.isFinite(prior.duration_seconds) && prior.duration_seconds >= 0
    ? prior.duration_seconds : Number.isFinite(started) ? Math.max(0, (Date.now() - started) / 1000) : 0;
  assertPreflight();
  withdrawDerivedTerminal(id);
  atomicWrite(state, JSON.stringify({
    record_id: id, arm, attempt, stage: stageName, status: 'COMPLETE',
    started_at: prior.started_at, ended_at: new Date().toISOString(),
    duration_seconds: duration, error: null,
    launcher_pid: prior.launcher_pid,
    launcher_process_start_ticks: prior.launcher_process_start_ticks,
    parent_sha256: parentHash, retrieval_k: K,
    tokens_used: 0, model: null, reasoning_effort: null, ...runtimeEvidence(),
    execution_log_start_offset: prior.execution_log_start_offset,
    execution_log_prefix_sha256: prior.execution_log_prefix_sha256,
    execution_log_segment: executionLogSegment(log, prior.execution_log_start_offset),
    output: artifact(out),
  }, null, 2) + '\n');
}

function recoverStagedModelOutput({
  id, arm, attempt, stageName, out, validate, afterFinalize, prompt, stateExtra,
}) {
  const staging = `${out}.finalizing`;
  if (!existsSync(staging) || existsSync(out) || !validate(staging)) {
    throw new Error('finalization staging bytes are absent, conflicting, or invalid');
  }
  const state = readJSON(statePath(id, arm, attempt, stageName));
  const prepared = typeof stateExtra === 'function'
    ? { binding: artifact(promptMetadataPath(id, arm, attempt)), created: false }
    : null;
  const resolvedExtra = typeof stateExtra === 'function' ? stateExtra(prepared) : stateExtra;
  if (!retryableStateMatches(state, {
    id, arm, attempt, stageName, stateExtra: resolvedExtra,
  })) throw new Error('staged output lacks its exact retryable call state');
  if (retryableLauncherIsLive(state)) {
    throw new Error('staged output still has its exact live predecessor process');
  }
  const stagedLog = readFileSync(logPath(id, arm, attempt, stageName));
  if (state.execution_log_start_offset > stagedLog.length) {
    throw new Error('staged output log offset exceeds the canonical log');
  }
  const cost = parseCodexCost(stagedLog.subarray(state.execution_log_start_offset));
  if (!isTokenCount(cost.tokens_used) ||
      cost.model !== MODEL || cost.reasoning_effort !== EFFORT) {
    throw new Error('staged output lacks complete sealed model telemetry');
  }
  if (!retireStaleCellLock(
    lockPath(id, arm, attempt, stageName),
    { id, arm, attempt, stage: stageName }, out, true,
  )) throw new Error('staged output is still owned by the exact live call process');
  assertPreflight();
  linkSync(staging, out);
  if (afterFinalize !== null) afterFinalize(out);
  if (!validate(out)) throw new Error('recovered canonical output failed complete validation');
  recoverPublishedModelState({ id, arm, attempt, stageName, out, prompt, stateExtra });
}

function runModel({ id, arm, attempt, stageName, out, schema, prompt, scratch, validate,
  isolation, normalize = null, afterFinalize = null, prepare = null, stateExtra = {} }) {
  if (!dryRun && existsSync(`${out}.finalizing`) && !existsSync(out)) {
    try {
      recoverStagedModelOutput({
        id, arm, attempt, stageName, out, validate, afterFinalize, prompt, stateExtra,
      });
      return Promise.resolve({
        id, arm, attempt, status: 'RECOVERED_COMPLETE', tokens_used: 0,
      });
    } catch (error) {
      return Promise.resolve({
        id, arm, attempt, status: 'ORPHANED_STAGED_OUTPUT',
        error: String(error), tokens_used: 0,
      });
    }
  }
  if (validate(out)) {
    const priorStatePath = statePath(id, arm, attempt, stageName);
    try {
      const priorState = readJSON(priorStatePath);
      if (priorState.status === 'COMPLETE' &&
          canonicalJSON(priorState.output) === canonicalJSON(artifact(out))) {
        return Promise.resolve({ id, arm, attempt, status: 'SKIP_VALID', tokens_used: 0 });
      }
    } catch { /* fail closed below */ }
    if (!dryRun) {
      try {
        recoverPublishedModelState({
          id, arm, attempt, stageName, out, prompt, stateExtra,
        });
        return Promise.resolve({
          id, arm, attempt, status: 'RECOVERED_COMPLETE', tokens_used: 0,
        });
      } catch (error) {
        return Promise.resolve({
          id, arm, attempt, status: 'ORPHANED_EXISTING_OUTPUT',
          error: String(error), tokens_used: 0,
        });
      }
    }
    return Promise.resolve({
      id, arm, attempt, status: 'ORPHANED_EXISTING_OUTPUT',
      error: 'valid canonical output lacks a matching COMPLETE state', tokens_used: 0,
    });
  }
  if (existsSync(out)) return Promise.resolve({ id, arm, attempt, status: 'INVALID_EXISTING_OUTPUT', tokens_used: 0 });
  if (dryRun) return Promise.resolve({ id, arm, attempt, status: 'PLANNED', tokens_used: 0 });
  if (stopRequested()) return Promise.resolve({ id, arm, attempt, status: 'STOP_REQUESTED', tokens_used: 0 });
  try { assertPreflight(); } catch (error) {
    return Promise.resolve({ id, arm, attempt, status: 'PREFLIGHT_FAILED', error: String(error), tokens_used: 0 });
  }
  const temporary = join(scratch, `.model-output-${stageName}-${process.pid}.json`);
  const lock = lockPath(id, arm, attempt, stageName);
  const startedAt = new Date().toISOString();
  const launcherPid = process.pid;
  const launcherProcessStartTicks = processStartTicks(launcherPid);
  try {
    // A terminal is a derived snapshot of the prefix.  Withdraw an older
    // INCOMPLETE snapshot before admitting any new scientific cell so a kill
    // can leave only a missing (never stale) terminal.
    withdrawDerivedTerminal(id);
  } catch (error) {
    return Promise.resolve({
      id, arm, attempt, status: 'TERMINAL_WITHDRAWAL_FAILED',
      error: String(error), tokens_used: 0,
    });
  }
  if (!acquireLock(lock, {
    pid: launcherPid, process_start_ticks: launcherProcessStartTicks,
    id, arm, attempt, stage: stageName, started_at: startedAt,
  }, out)) {
    return Promise.resolve({ id, arm, attempt, status: 'LOCKED', tokens_used: 0 });
  }
  try {
    assertPreflight();
    if (stopRequested()) {
      rmSync(lock, { force: true });
      return Promise.resolve({ id, arm, attempt, status: 'STOP_REQUESTED', tokens_used: 0 });
    }
  } catch (error) {
    rmSync(lock, { force: true });
    return Promise.resolve({
      id, arm, attempt, status: 'PREFLIGHT_FAILED', error: String(error), tokens_used: 0,
    });
  }
  try {
    resetCellScratch(scratch, id, stageName, arm, attempt);
    mkdirSync(dirname(out), { recursive: true });
  } catch (error) {
    rmSync(lock, { force: true });
    return Promise.resolve({
      id, arm, attempt, status: 'SCRATCH_RESET_FAILED', error: String(error), tokens_used: 0,
    });
  }
  let prepared = null;
  try { prepared = prepare === null ? null : prepare(); }
  catch (error) {
    rmSync(lock, { force: true });
    return Promise.resolve({
      id, arm, attempt, status: 'PREPARATION_FAILED', error: String(error), tokens_used: 0,
    });
  }
  const resolvedStateExtra = typeof stateExtra === 'function' ? stateExtra(prepared) : stateExtra;
  const log = logPath(id, arm, attempt, stageName);
  mkdirSync(dirname(log), { recursive: true });
  const previousLogSize = existsSync(log) ? statSync(log).size : 0;
  const previousLogSha = existsSync(log) ? shaFile(log) : shaBytes(Buffer.alloc(0));
  const descriptor = openSync(log, 'a');
  const state = statePath(id, arm, attempt, stageName);
  const startedMilliseconds = Date.now();
  atomicWrite(state, JSON.stringify({
    record_id: id, arm, attempt, stage: stageName, status: 'RUNNING', started_at: startedAt,
    launcher_pid: launcherPid, launcher_process_start_ticks: launcherProcessStartTicks,
    execution_log_start_offset: previousLogSize,
    execution_log_prefix_sha256: previousLogSha,
    ...runtimeEvidence(), ...resolvedStateExtra,
  }, null, 2) + '\n');
  const profile = seal.os_isolation.execution_profile;
  const substitutions = {
    '{cell_scratch}': scratch, '{source}': isolation.source, '{parent}': isolation.parent,
    '{prior_audit}': isolation.audit, '{output_schema}': schema,
    '{model_runtime_bundle}': MODEL_RUNTIME_BUNDLE,
    '{model}': MODEL, '{effort}': EFFORT,
    '{output_last_message}': `/work/${temporary.split(sep).at(-1)}`,
  };
  const render = (token) => Object.entries(substitutions).reduce(
    (value, [placeholder, replacement]) => value.replaceAll(placeholder, String(replacement)), token,
  );
  const args = profile.codex_argv_template.map(render);
  const bwrapArgs = [];
  for (const token of profile.bwrap_argv_template) {
    if (token === '{optional_prior_audit_mount}') {
      if (isolation.audit !== null) bwrapArgs.push(...profile.optional_prior_audit_mount.map(render));
    } else if (token === '{codex_argv}') {
      bwrapArgs.push(...args);
    } else {
      bwrapArgs.push(render(token));
    }
  }
  return new Promise((resolvePromise) => {
    let settled = false;
    let descriptorOpen = true;
    let stdinError = null;
    const closeLog = () => {
      if (descriptorOpen) { descriptorOpen = false; closeSync(descriptor); }
    };
    const finish = (status, error, cost, finalization = {}) => {
      if (settled) return;
      settled = true;
      const duration = (Date.now() - startedMilliseconds) / 1000;
      atomicWrite(state, JSON.stringify({
        record_id: id, arm, attempt, stage: stageName, status, started_at: startedAt,
        ended_at: new Date().toISOString(), duration_seconds: duration, error,
        launcher_pid: launcherPid, launcher_process_start_ticks: launcherProcessStartTicks,
        ...cost, execution_log_start_offset: previousLogSize,
        execution_log_prefix_sha256: previousLogSha,
        execution_log_segment: executionLogSegment(log, previousLogSize),
        ...runtimeEvidence(), ...resolvedStateExtra, ...finalization,
      }, null, 2) + '\n');
      rmSync(lock, { force: true });
      resolvePromise({ id, arm, attempt, status, error, duration_seconds: duration, ...cost });
    };
    let child;
    let authDescriptor = null;
    try {
      assertPreflight();
      try {
        const authInfo = lstatSync(CODEX_AUTH);
        if (!authInfo.isFile() || authInfo.isSymbolicLink() || (authInfo.mode & 0o077) !== 0) {
          throw new Error('unsafe credential mode/type');
        }
        authDescriptor = openSync(CODEX_AUTH, fsConstants.O_RDONLY | fsConstants.O_NOFOLLOW);
        if (!fstatSync(authDescriptor).isFile()) {
          throw new Error('not a regular file');
        }
      } catch {
        if (authDescriptor !== null) closeSync(authDescriptor);
        authDescriptor = null;
        throw new Error('operational credential could not be opened securely; set PAIRED_EXTENSION_CODEX_AUTH to a private plain file');
      }
      child = spawn(BWRAP, bwrapArgs, {
        cwd: scratch, stdio: ['pipe', descriptor, descriptor, authDescriptor],
        env: { ...profile.spawn_environment },
      });
      closeSync(authDescriptor);
      authDescriptor = null;
    } catch (error) {
      if (authDescriptor !== null) closeSync(authDescriptor);
      closeLog(); finish('SPAWN_FAILED', String(error), { tokens_used: null, model: null, reasoning_effort: null });
      return;
    }
    child.on('error', (error) => {
      closeLog(); finish('SPAWN_FAILED', String(error), { tokens_used: null, model: null, reasoning_effort: null });
    });
    child.on('exit', (code, signal) => {
      if (settled) return;
      closeLog();
      const bytes = readFileSync(log);
      const cost = parseCodexCost(bytes.subarray(Math.min(previousLogSize, bytes.length)));
      let status = 'FAILED';
      let error = null;
      let finalization = {};
      try {
        assertPreflight();
        if (code !== 0) throw new Error(`exit=${code} signal=${signal}`);
        if (stdinError !== null) throw new Error(`stdin failed: ${stdinError}`);
        if (!isTokenCount(cost.tokens_used) ||
            cost.model !== MODEL || cost.reasoning_effort !== EFFORT) {
          throw new Error('model telemetry does not match sealed execution identity');
        }
        if (normalize) normalize(temporary);
        if (!validate(temporary)) throw new Error('strict output validation failed');
        if (existsSync(out)) throw new Error('conflicting final output appeared despite canonical cell lock');
        publishValidatedAbsent(temporary, out, validate);
        rmSync(temporary, { force: true });
        const finalizedMetadata = afterFinalize ? afterFinalize(out) : null;
        finalization = {
          output: artifact(out), finalized_metadata: finalizedMetadata,
        };
        status = 'COMPLETE';
      } catch (caught) { error = String(caught); }
      finish(status, error, cost, finalization);
    });
    child.stdin.on('error', (error) => {
      stdinError = String(error);
      if (child.exitCode === null && !child.killed) child.kill('SIGTERM');
    });
    try { child.stdin.end(prompt, 'utf8'); }
    catch (error) {
      stdinError = String(error);
      if (child.exitCode === null && !child.killed) child.kill('SIGTERM');
    }
  });
}

function runReceipt(id, attempt) {
  const arm = 'bugbank';
  const context = attemptContext(id, arm, attempt);
  if (!context.ok) return Promise.resolve({ id, arm, attempt, status: context.status, tokens_used: 0 });
  const out = receiptPath(id, attempt);
  const staged = `${out}.finalizing`;
  if (!dryRun && existsSync(staged) && !existsSync(out)) {
    try {
      const state = readJSON(statePath(id, arm, attempt, 'receipt'));
      if (!validateReceipt(staged, id, attempt, context).valid ||
          !retryableStateMatches(state, {
            id, arm, attempt, stageName: 'receipt',
            stateExtra: { parent_sha256: context.parentHash, retrieval_k: K },
          })) throw new Error('staged receipt lacks exact valid bytes/state');
      if (retryableLauncherIsLive(state)) {
        throw new Error('staged receipt still has its exact live predecessor process');
      }
      if (!retireStaleCellLock(
        lockPath(id, arm, attempt, 'receipt'),
        { id, arm, attempt, stage: 'receipt' }, out, true,
      )) throw new Error('staged receipt is still owned by its exact live generator');
      assertPreflight();
      linkSync(staged, out);
      if (!validateReceipt(out, id, attempt, context).valid) {
        throw new Error('recovered receipt failed canonical validation');
      }
      recoverPublishedReceiptState({ id, attempt, out, parentHash: context.parentHash });
      return Promise.resolve({
        id, arm, attempt, status: 'RECOVERED_COMPLETE', tokens_used: 0,
      });
    } catch (error) {
      return Promise.resolve({
        id, arm, attempt, status: 'ORPHANED_STAGED_RECEIPT',
        error: String(error), tokens_used: 0,
      });
    }
  }
  const existing = validateReceipt(out, id, attempt, context);
  if (existing.valid) {
    try {
      const priorState = readJSON(statePath(id, arm, attempt, 'receipt'));
      if (priorState.status === 'COMPLETE' &&
          canonicalJSON(priorState.output) === canonicalJSON(artifact(out))) {
        return Promise.resolve({ id, arm, attempt, status: 'SKIP_VALID', tokens_used: 0 });
      }
    } catch { /* fail closed below */ }
    if (!dryRun) {
      try {
        recoverPublishedReceiptState({ id, attempt, out, parentHash: context.parentHash });
        return Promise.resolve({
          id, arm, attempt, status: 'RECOVERED_COMPLETE', tokens_used: 0,
        });
      } catch (error) {
        return Promise.resolve({
          id, arm, attempt, status: 'ORPHANED_EXISTING_RECEIPT',
          error: String(error), tokens_used: 0,
        });
      }
    }
    return Promise.resolve({
      id, arm, attempt, status: 'ORPHANED_EXISTING_RECEIPT',
      error: 'valid canonical receipt lacks a matching COMPLETE state', tokens_used: 0,
    });
  }
  if (existsSync(out)) return Promise.resolve({ id, arm, attempt, status: 'INVALID_EXISTING_RECEIPT', error: existing.error, tokens_used: 0 });
  if (dryRun) return Promise.resolve({ id, arm, attempt, status: 'PLANNED', tokens_used: 0 });
  if (stopRequested()) return Promise.resolve({ id, arm, attempt, status: 'STOP_REQUESTED', tokens_used: 0 });
  try { assertPreflight(); } catch (error) {
    return Promise.resolve({ id, arm, attempt, status: 'PREFLIGHT_FAILED', error: String(error), tokens_used: 0 });
  }
  const receiptScratch = scratchPath(id, 'receipt', arm, attempt);
  const temporary = join(receiptScratch, `.receipt-output-${process.pid}.json`);
  const stageName = 'receipt';
  const lock = lockPath(id, arm, attempt, stageName);
  const startedAt = new Date().toISOString();
  const launcherPid = process.pid;
  const launcherProcessStartTicks = processStartTicks(launcherPid);
  try {
    // See runModel: missing derived terminal state is restart-safe, whereas a
    // terminal from the prior prefix becomes stale as soon as this cell starts.
    withdrawDerivedTerminal(id);
  } catch (error) {
    return Promise.resolve({
      id, arm, attempt, status: 'TERMINAL_WITHDRAWAL_FAILED',
      error: String(error), tokens_used: 0,
    });
  }
  if (!acquireLock(lock, {
    pid: launcherPid, process_start_ticks: launcherProcessStartTicks,
    id, arm, attempt, stage: stageName, started_at: startedAt,
  }, out)) {
    return Promise.resolve({ id, arm, attempt, status: 'LOCKED', tokens_used: 0 });
  }
  try {
    assertPreflight();
    if (stopRequested()) {
      rmSync(lock, { force: true });
      return Promise.resolve({ id, arm, attempt, status: 'STOP_REQUESTED', tokens_used: 0 });
    }
  } catch (error) {
    rmSync(lock, { force: true });
    return Promise.resolve({
      id, arm, attempt, status: 'PREFLIGHT_FAILED', error: String(error), tokens_used: 0,
    });
  }
  try {
    resetCellScratch(receiptScratch, id, stageName, arm, attempt);
  } catch (error) {
    rmSync(lock, { force: true });
    return Promise.resolve({
      id, arm, attempt, status: 'SCRATCH_RESET_FAILED', error: String(error), tokens_used: 0,
    });
  }
  const log = logPath(id, arm, attempt, stageName);
  mkdirSync(dirname(log), { recursive: true });
  const previousLogSize = existsSync(log) ? statSync(log).size : 0;
  const previousLogSha = existsSync(log) ? shaFile(log) : shaBytes(Buffer.alloc(0));
  const descriptor = openSync(log, 'a');
  const state = statePath(id, arm, attempt, stageName);
  const startedMilliseconds = Date.now();
  atomicWrite(state, JSON.stringify({
    record_id: id, arm, attempt, stage: stageName, status: 'RUNNING', started_at: startedAt,
    launcher_pid: launcherPid, launcher_process_start_ticks: launcherProcessStartTicks,
    parent_sha256: context.parentHash, retrieval_k: K,
    execution_log_start_offset: previousLogSize,
    execution_log_prefix_sha256: previousLogSha, ...runtimeEvidence(),
  }, null, 2) + '\n');
  const args = [
    '-B', FEEDBACK, '--parent-json', context.parentPath, '--record-id', id, '--run-id', RUN_ID,
    '--arm', arm, '--attempt', String(attempt), '--out', temporary, '--k', String(K),
    '--db', DATABASE, '--db-sha256', manifest.bugbank.database_sha256,
  ];
  return new Promise((resolvePromise) => {
    let settled = false;
    let open = true;
    const closeLog = () => { if (open) { open = false; closeSync(descriptor); } };
    const finish = (status, error) => {
      if (settled) return;
      settled = true;
      const duration = (Date.now() - startedMilliseconds) / 1000;
      atomicWrite(state, JSON.stringify({
        record_id: id, arm, attempt, stage: stageName, status, started_at: startedAt,
        ended_at: new Date().toISOString(), duration_seconds: duration, error,
        launcher_pid: launcherPid, launcher_process_start_ticks: launcherProcessStartTicks,
        parent_sha256: context.parentHash, retrieval_k: K,
        tokens_used: 0, model: null, reasoning_effort: null,
        execution_log_start_offset: previousLogSize,
        execution_log_prefix_sha256: previousLogSha,
        execution_log_segment: executionLogSegment(log, previousLogSize),
        ...runtimeEvidence(),
        output: status === 'COMPLETE' ? artifact(out) : null,
      }, null, 2) + '\n');
      if (status !== 'COMPLETE') rmSync(temporary, { force: true });
      rmSync(lock, { force: true });
      resolvePromise({ id, arm, attempt, status, error, duration_seconds: duration, tokens_used: 0 });
    };
    let child;
    try {
      assertPreflight();
      child = spawn(PYTHON, args, {
        cwd: REPO, stdio: ['ignore', descriptor, descriptor],
        env: { ...seal.execution.retrieval_spawn_environment },
      });
    } catch (error) { closeLog(); finish('SPAWN_FAILED', String(error)); return; }
    child.on('error', (error) => { closeLog(); finish('SPAWN_FAILED', String(error)); });
    child.on('exit', (code, signal) => {
      if (settled) return;
      closeLog();
      let validation;
      try {
        assertPreflight();
        validation = validateReceipt(temporary, id, attempt, context);
        if (code === 0 && validation.valid) {
          publishValidatedAbsent(temporary, out,
            (candidate) => validateReceipt(candidate, id, attempt, context).valid);
          rmSync(temporary, { force: true });
          validation = validateReceipt(out, id, attempt, context);
        }
      }
      catch (error) { validation = { valid: false, error: String(error) }; }
      finish(code === 0 && validation.valid ? 'COMPLETE' : 'FAILED',
        code === 0 && validation.valid ? null : `exit=${code} signal=${signal} ${validation.error}`);
    });
  });
}

function normalizeRevision(path, id, arm, attempt, context, receipt) {
  const value = readJSON(path);
  if (!validDraftCore(value) || !Array.isArray(value.audit_feedback_acted_on) ||
      !Array.isArray(value.retrieved_entry_ids) || !Array.isArray(value.acted_on_entry_ids) ||
      !Array.isArray(value.dismissed_hits)) throw new Error('revision lacks required substantive fields');
  if (arm === 'plain' && (value.acted_on_entry_ids.length || value.dismissed_hits.length)) {
    throw new Error('plain output attempted treatment bookkeeping');
  }
  const wrapper = arm === 'plain' ? {
    treatment_status: 'PLAIN_SELF_CRITIQUE', receipt_path: '', receipt_sha256: '',
    retrieved_entry_ids: [], acted_on_entry_ids: [], dismissed_hits: [],
  } : {
    treatment_status: 'BUGBANK_RECEIPT_EXPOSED',
    receipt_path: repoPath(receiptPath(id, attempt)), receipt_sha256: receipt.sha256,
    retrieved_entry_ids: receipt.retrieved,
  };
  const normalized = {
    ...value, record_id: id, stage: 'REVISION', arm, iteration: attempt,
    parent_sha256: context.parentHash, audit_sha256: context.auditHash, ...wrapper,
  };
  if (!validRevisionValue(normalized, { id, arm, attempt, context, receipt })) {
    throw new Error('normalized revision violates extension contract');
  }
  writeFileSync(path, JSON.stringify(normalized, null, 2) + '\n');
}

function normalizeAudit(path, id, arm, attempt, revision, revisionHash, scratch) {
  const value = readJSON(path);
  if (!isObject(value) || value.complete !== true || !Array.isArray(value.claims) ||
      value.claims.length !== revision.results.length ||
      !['FULLY_RESOLVES_TARGET', 'VALID_PARTIAL_PROGRESS', 'NO_VALID_PROGRESS', 'OVERCLAIMED']
        .includes(value.target_verdict) || !nonempty(value.target_evidence) ||
      !Array.isArray(value.checks_performed) || !value.checks_performed.every(nonempty)) {
    throw new Error('audit lacks required substantive fields');
  }
  const claims = value.claims.map((claim, index) => {
    if (!isObject(claim) || !['VERIFIED', 'REFUTED', 'UNRESOLVED'].includes(claim.verdict) ||
        !nonempty(claim.evidence) || !nonempty(claim.witness) ||
        !nonempty(claim.search_method) || !nonempty(claim.checker_path)) {
      throw new Error(`audit claim ${index} lacks substantive verdict/evidence fields`);
    }
    let checkerPath = claim.checker_path;
    if (checkerPath !== 'none') {
      if (!checkerPath.startsWith('/work/') || checkerPath === '/work/') {
        throw new Error('audit checker path must be none or use the isolated /work mount');
      }
      const suffix = checkerPath.slice('/work/'.length);
      const translated = resolve(scratch, suffix);
      if (translated !== resolve(scratch) && !translated.startsWith(`${resolve(scratch)}${sep}`)) {
        throw new Error('audit checker path traversal');
      }
      const real = realpathSync(translated);
      const realScratch = realpathSync(scratch);
      if (!real.startsWith(`${realScratch}${sep}`) || !lstatSync(real).isFile()) {
        throw new Error('audit checker symlink/non-file escape');
      }
      checkerPath = real;
    }
    const exactClaim = revision.results[index].claim;
    return {
      ...claim, idx: index, claim: exactClaim, claim_sha256: shaText(exactClaim),
      checker_path: checkerPath,
    };
  });
  const confirmed = claims.filter((claim) => claim.verdict === 'REFUTED').map((claim) => claim.idx);
  const normalized = {
    ...value, record_id: id, stage: 'REVISION_AUDIT', arm, iteration: attempt,
    parent_sha256: revisionHash, claims, confirmed_refutations: confirmed,
    overall: expectedAuditOverall(claims),
    claimed_resolution_verdict: expectedResolutionVerdict(revision, value.target_verdict),
  };
  if (!validAuditValue(normalized, {
    id, arm, attempt, parent: revision, parentHash: revisionHash,
  })) throw new Error('normalized audit violates extension contract');
  writeFileSync(path, JSON.stringify(normalized, null, 2) + '\n');
}

function runRevision(id, arm, attempt) {
  const context = attemptContext(id, arm, attempt);
  if (!context.ok) return Promise.resolve({ id, arm, attempt, status: context.status, tokens_used: 0 });
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = validateReceipt(receiptPath(id, attempt), id, attempt, context);
    if (!receipt.valid) return Promise.resolve({ id, arm, attempt, status: receipt.error, tokens_used: 0 });
  }
  // Prompt metadata is a scientific exposure artifact. Do not materialize it
  // after the operator has requested a drain.
  if (!dryRun && stopRequested()) {
    return Promise.resolve({ id, arm, attempt, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  let bundle;
  try {
    bundle = revisionPromptBundle(id, arm, attempt, context, receipt);
    if (existsSync(promptMetadataPath(id, arm, attempt))) {
      if (!validPromptMetadata(promptMetadataPath(id, arm, attempt), bundle.metadata)) {
        throw new Error('existing prompt metadata mismatch');
      }
      // Use the persisted bytes, including its exact prompt, after a restart.
      bundle.prompt = readJSON(promptMetadataPath(id, arm, attempt)).prompt_text;
    }
  } catch (error) {
    return Promise.resolve({ id, arm, attempt, status: 'PROMPT_MATERIALIZATION_FAILED', error: String(error), tokens_used: 0 });
  }
  const out = attemptPath(id, arm, attempt);
  const validate = (path) => {
    if (!existsSync(path)) return false;
    try {
      return validPromptMetadata(promptMetadataPath(id, arm, attempt), bundle.metadata) &&
        validRevisionValue(readJSON(path), { id, arm, attempt, context, receipt });
    } catch { return false; }
  };
  return runModel({
    id, arm, attempt, stageName: 'revision', out, schema: REVISION_SCHEMA,
    prompt: bundle.prompt, scratch: bundle.scratch, validate,
    isolation: {
      source: inputPath(id), parent: context.parentPath, audit: context.auditPath,
    },
    prepare: () => ensurePromptMetadata(id, arm, attempt, bundle),
    normalize: (path) => normalizeRevision(path, id, arm, attempt, context, receipt),
    stateExtra: (prepared) => ({
      parent_sha256: context.parentHash, audit_sha256: context.auditHash,
      prompt_sha256: shaText(bundle.prompt), prompt_size_bytes: Buffer.byteLength(bundle.prompt, 'utf8'),
      prompt_metadata_sha256: prepared.binding.sha256,
      os_read_isolation_sha256: shaText(canonicalJSON(bundle.metadata.os_read_isolation)),
      neutral_lens_attempt: lensFor(attempt)?.attempt ?? null,
      receipt_sha256: receipt?.sha256 ?? null,
    }),
  });
}

function runAudit(id, arm, attempt) {
  const context = attemptContext(id, arm, attempt);
  if (!context.ok) return Promise.resolve({ id, arm, attempt, status: context.status, tokens_used: 0 });
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = validateReceipt(receiptPath(id, attempt), id, attempt, context);
    if (!receipt.valid) return Promise.resolve({ id, arm, attempt, status: receipt.error, tokens_used: 0 });
  }
  let bundle;
  try { bundle = revisionPromptBundle(id, arm, attempt, context, receipt); }
  catch (error) { return Promise.resolve({ id, arm, attempt, status: 'INVALID_PROMPT_INPUT', error: String(error), tokens_used: 0 }); }
  if (!validPromptMetadata(promptMetadataPath(id, arm, attempt), bundle.metadata)) {
    return Promise.resolve({ id, arm, attempt, status: 'MISSING_OR_INVALID_PROMPT_METADATA', tokens_used: 0 });
  }
  const revisionFile = attemptPath(id, arm, attempt);
  if (!existsSync(revisionFile)) return Promise.resolve({ id, arm, attempt, status: 'MISSING_REVISION', tokens_used: 0 });
  const revision = readJSON(revisionFile);
  if (!validRevisionValue(revision, { id, arm, attempt, context, receipt })) {
    return Promise.resolve({ id, arm, attempt, status: 'INVALID_REVISION', tokens_used: 0 });
  }
  const revisionHash = shaFile(revisionFile);
  const scratch = scratchPath(id, 'audit', arm, attempt);
  const prompt = auditPrompt(id, arm, attempt, revision, revisionFile, scratch);
  const auditExposure = exposureManifest({
    source: inputPath(id), parent: revisionFile, schema: AUDIT_SCHEMA, scratch,
  });
  const out = auditPath(id, arm, attempt);
  const metadataFile = auditMetadataPath(id, arm, attempt);
  if (!dryRun && existsSync(out) && !existsSync(metadataFile)) {
    try {
      const orphanAudit = readJSON(out);
      if (!validAuditValue(orphanAudit, {
        id, arm, attempt, parent: revision, parentHash: revisionHash,
      })) throw new Error('orphaned audit output is invalid');
      const orphanState = readJSON(statePath(id, arm, attempt, 'audit'));
      const orphanExtra = {
        parent_sha256: revisionHash, prompt_sha256: shaText(prompt),
        prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
        os_read_isolation_sha256: shaText(canonicalJSON(auditExposure)),
        audit_output_normalizer: 'DERIVABLE_FIELDS_ONLY_V1',
      };
      if (!retryableStateMatches(orphanState, {
        id, arm, attempt, stageName: 'audit', stateExtra: orphanExtra,
      })) throw new Error('orphaned audit output lacks its retryable state');
      if (retryableLauncherIsLive(orphanState)) {
        throw new Error('orphaned audit still has its exact live predecessor process');
      }
      const metadata = auditMetadataBase(
        id, arm, attempt, revisionFile, orphanAudit, prompt, scratch,
      );
      writeExclusiveOrVerify(
        metadataFile, Buffer.from(JSON.stringify(metadata, null, 2) + '\n'),
      );
    } catch (error) {
      return Promise.resolve({
        id, arm, attempt, status: 'AUDIT_METADATA_RECOVERY_FAILED',
        error: String(error), tokens_used: 0,
      });
    }
  }
  const validate = (path) => {
    if (!existsSync(path)) return false;
    try {
      const value = readJSON(path);
      if (!validAuditValue(value, { id, arm, attempt, parent: revision, parentHash: revisionHash })) return false;
      return path !== out || validAuditMetadata(metadataFile, id, arm,
        attempt, revisionFile, value, prompt);
    } catch { return false; }
  };
  return runModel({
    id, arm, attempt, stageName: 'audit', out, schema: AUDIT_SCHEMA, prompt, scratch, validate,
    isolation: { source: inputPath(id), parent: revisionFile, audit: null },
    normalize: (path) => normalizeAudit(
      path, id, arm, attempt, revision, revisionHash, scratch,
    ),
    afterFinalize: (finalPath) => {
      const metadata = auditMetadataBase(id, arm, attempt, revisionFile, readJSON(finalPath), prompt, scratch);
      const metadataPath = metadataFile;
      writeExclusiveOrVerify(metadataPath, Buffer.from(JSON.stringify(metadata, null, 2) + '\n'));
      return artifact(metadataPath);
    },
    stateExtra: {
      parent_sha256: revisionHash, prompt_sha256: shaText(prompt),
      prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
      os_read_isolation_sha256: shaText(canonicalJSON(auditExposure)),
      audit_output_normalizer: 'DERIVABLE_FIELDS_ONLY_V1',
    },
  });
}

function runTerminal(id) {
  try {
    const value = terminalValue(id);
    if (!dryRun) {
      assertMutationGateHeld();
      atomicWrite(join(RUN, 'terminals', `${id}.json`), JSON.stringify(value, null, 2) + '\n');
    }
    return Promise.resolve({
      id, status: value.status, bugbank: value.arms.bugbank.status,
      plain: value.arms.plain.status, tokens_used: 0,
    });
  } catch (error) {
    return Promise.resolve({ id, status: 'INCOMPLETE', error: String(error), tokens_used: 0 });
  }
}

async function pool(items, width, worker) {
  const results = new Array(items.length);
  let next = 0;
  async function oneWorker() {
    while (true) {
      const index = next++;
      if (index >= items.length) return;
      try { results[index] = await worker(items[index]); }
      catch (error) {
        const item = items[index];
        results[index] = {
          id: typeof item === 'string' ? item : item?.id ?? null,
          arm: typeof item === 'string' ? null : item?.arm ?? null,
          attempt: typeof item === 'string' ? null : item?.attempt ?? null,
          status: 'WORKER_EXCEPTION', error: String(error), tokens_used: 0,
        };
      }
      process.stdout.write(`${JSON.stringify(results[index])}\n`);
    }
  }
  await Promise.all(Array.from({ length: Math.min(width, Math.max(items.length, 1)) }, oneWorker));
  return results;
}

let summarySequence = 0;
async function executeStage(stageName, items, worker) {
  const startedAt = new Date().toISOString();
  const results = await pool(items, concurrency, worker);
  const successes = new Set([
    'COMPLETE', 'RECOVERED_COMPLETE', 'SKIP_VALID', 'PLANNED', 'ALREADY_TERMINAL',
  ]);
  const summary = {
    schema: 'paired_open_problem_extension_stage_summary_v1', run_id: RUN_ID,
    stage: stageName, dry_run: dryRun, started_at: startedAt, ended_at: new Date().toISOString(),
    selected: results.length, complete: results.filter((row) => successes.has(row.status)).length,
    failed: results.filter((row) => !successes.has(row.status)).length,
    tokens_used: checkedTokenSum(results.map((row) =>
      isTokenCount(row.tokens_used) ? row.tokens_used : 0)),
    results,
  };
  if (!dryRun && stageName !== 'validate') {
    assertMutationGateHeld();
    summarySequence += 1;
    const safeTime = startedAt.replaceAll(':', '').replaceAll('.', '-');
    writeExclusiveOrVerify(join(RUN, 'summaries', stageName,
      `${safeTime}__pid_${process.pid}__${summarySequence}.json`),
    Buffer.from(JSON.stringify(summary, null, 2) + '\n'));
  }
  return summary;
}

function cellSelected(id, arm) {
  return selectedCells.size === 0 || selectedCells.has(`${id}:${arm}`);
}

function nextRunnable(arm) {
  const result = [];
  for (const id of ids) {
    if (!cellSelected(id, arm)) continue;
    const progress = armProgress(id, arm);
    if (progress.terminal || progress.next_attempt === null ||
        progress.status === 'INCOMPLETE_WAITING_FOR_BUGBANK' ||
        progress.status === 'INCOMPLETE_BUGBANK_NO_ENDPOINT' ||
        progress.status === 'INCOMPLETE_MAX_ATTEMPTS') continue;
    if (Number.isInteger(progress.next_attempt) && attemptContext(id, arm, progress.next_attempt).ok) {
      result.push({ id, arm, attempt: progress.next_attempt });
    }
  }
  return result;
}

async function runArmCycle(arm, summaries) {
  if (stopRequested()) return { attempted: false, failed: false, drained: true };
  const cells = nextRunnable(arm);
  if (!cells.length) return { attempted: false, failed: false, drained: false };
  let failed = false;
  if (arm === 'bugbank') {
    const receiptSummary = await executeStage('receipt', cells,
      (cell) => runReceipt(cell.id, cell.attempt));
    summaries.push(receiptSummary);
    failed ||= receiptSummary.failed > 0;
    if (failed || stopRequested() || dryRun) return { attempted: true, failed, drained: stopRequested() };
  }
  const revisionCells = cells.filter((cell) => arm === 'plain' ||
    validateReceipt(receiptPath(cell.id, cell.attempt), cell.id, cell.attempt,
      attemptContext(cell.id, arm, cell.attempt)).valid);
  const revisionSummary = await executeStage('revision', revisionCells,
    (cell) => runRevision(cell.id, arm, cell.attempt));
  summaries.push(revisionSummary);
  failed ||= revisionSummary.failed > 0;
  if (failed || stopRequested() || dryRun) return { attempted: true, failed, drained: stopRequested() };
  const auditCells = revisionCells.filter((cell) => existsSync(attemptPath(cell.id, arm, cell.attempt)));
  const auditSummary = await executeStage('audit', auditCells,
    (cell) => runAudit(cell.id, arm, cell.attempt));
  summaries.push(auditSummary);
  failed ||= auditSummary.failed > 0;
  return { attempted: true, failed, drained: stopRequested() };
}

async function runAll() {
  const summaries = [];
  for (let round = 0; round < 2 * MAX_ATTEMPTS + 4; round += 1) {
    const bugbank = await runArmCycle('bugbank', summaries);
    if (bugbank.drained || bugbank.failed) break;
    const plain = await runArmCycle('plain', summaries);
    if (plain.drained || plain.failed) break;
    if (dryRun) break;
    if (ids.every((id) => ['bugbank', 'plain'].every((arm) => {
      if (!cellSelected(id, arm)) return true;
      const progress = armProgress(id, arm);
      return progress.terminal || progress.next_attempt === null;
    }))) break;
    if (!bugbank.attempted && !plain.attempted) break;
  }
  if (dryRun) return 0;
  const terminalSummary = await executeStage('terminal', ids, runTerminal);
  summaries.push(terminalSummary);
  return terminalSummary.results.filter((row) => row.status !== 'COMPLETE').length;
}

let failureCount = 0;
if (stage === 'all') {
  failureCount = await runAll();
} else if (stage === 'validate') {
  const results = ids.map((id) => {
    try {
      const value = terminalValue(id);
      return { id, status: value.status, bugbank: value.arms.bugbank.status, plain: value.arms.plain.status };
    } catch (error) { return { id, status: 'INCOMPLETE', error: String(error) }; }
  });
  for (const row of results) process.stdout.write(`${JSON.stringify(row)}\n`);
  failureCount = results.filter((row) => row.status !== 'COMPLETE').length;
} else if (stage === 'terminal') {
  const summary = await executeStage('terminal', ids, runTerminal);
  failureCount = summary.results.filter((row) => row.status !== 'COMPLETE').length;
} else {
  const cells = ids.flatMap((id) => ['bugbank', 'plain']
    .filter((arm) => cellSelected(id, arm)).map((arm) => ({ id, arm, attempt: requestedAttempt })));
  let summary;
  if (stage === 'receipt') {
    const treated = cells.filter((cell) => cell.arm === 'bugbank');
    summary = await executeStage('receipt', treated, (cell) => runReceipt(cell.id, cell.attempt));
  } else if (stage === 'revision') {
    summary = await executeStage('revision', cells, (cell) => runRevision(cell.id, cell.arm, cell.attempt));
  } else {
    summary = await executeStage('audit', cells, (cell) => runAudit(cell.id, cell.arm, cell.attempt));
  }
  failureCount = summary.failed;
}

if (failureCount) process.exitCode = 1;
