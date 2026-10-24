#!/usr/bin/env node

/* Config-driven, fail-closed runner for a sealed paired open-problem run. */

import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  chmodSync, closeSync, constants, existsSync, fstatSync, fsyncSync, lstatSync, mkdirSync, openSync, readFileSync,
  readdirSync, realpathSync, renameSync, rmSync, statSync, writeFileSync, linkSync,
  mkdtempSync,
} from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir, tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const RUNNER_SCRIPT = fileURLToPath(import.meta.url);
const BASE = resolve(HERE, '..');
const REPO = resolve(BASE, '..');

if (process.argv.includes('--self-test')) {
  for (const raw of [
    '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}',
    '{"x":1e9999}', '{"x":-1e9999}', '{"x":9007199254740992}',
    '{"x":1,"x":2}', '{"nested":{"\\u0078":1,"x":2}}',
  ]) {
    let rejected = false;
    try { strictParseJSON(Buffer.from(raw), 'self-test adversarial JSON'); }
    catch { rejected = true; }
    if (!rejected) throw new Error(`strict JSON parser accepted ${raw}`);
  }
  const parsed = strictParseJSON(
    Buffer.from('{"x":9007199254740991,"y":[0.25,-1e-10]}'),
    'self-test valid JSON',
  );
  if (parsed.x !== Number.MAX_SAFE_INTEGER || parsed.y[0] !== 0.25) {
    throw new Error('strict JSON parser changed valid JSON');
  }
  let overflowRejected = false;
  try { checkedTokenAdd(Number.MAX_SAFE_INTEGER, 1, 'self-test token sum'); }
  catch { overflowRejected = true; }
  if (!overflowRejected) throw new Error('unsafe token sum was accepted');
  overflowRejected = false;
  try { checkedFiniteAdd(Number.MAX_VALUE, Number.MAX_VALUE, 'self-test duration sum'); }
  catch { overflowRejected = true; }
  if (!overflowRejected) throw new Error('non-finite duration sum was accepted');
  overflowRejected = false;
  try { stringifySafeJSON({ unsafe: Number.POSITIVE_INFINITY }); }
  catch { overflowRejected = true; }
  if (!overflowRejected) throw new Error('non-finite serialization was accepted');

  const root = mkdtempSync(join(tmpdir(), 'paired-bugbank-targeted-stress-runner-self-test-'));
  const publishedOutput = join(root, 'published-output.json');
  const publicationMetadata = join(root, 'published-output.metadata.json');
  const publishedBytes = Buffer.from('{"status":"ready"}\n');
  writeFileSync(publishedOutput, publishedBytes);
  const publicationOrder = [];
  finalizeAndValidatePublication(
    publishedOutput,
    publishedBytes,
    (path) => {
      publicationOrder.push('validate');
      return path === publishedOutput && existsSync(publicationMetadata);
    },
    (path) => {
      publicationOrder.push('finalize');
      if (path !== publishedOutput) throw new Error('publication callback received the wrong path');
      writeFileSync(publicationMetadata, '{}\n');
    },
  );
  if (publicationOrder.join(',') !== 'finalize,validate') {
    throw new Error('canonical publication was validated before its metadata was finalized');
  }
  const lock = join(root, 'operation.lock');
  const displaced = join(root, 'operation.lock.displaced');
  writeFileSync(lock, '');
  const descriptor = openSync(lock, constants.O_RDWR | constants.O_NOFOLLOW);
  try {
    verifyOrAcquireMutationLock(lock, descriptor, '/usr/bin/flock');
    renameSync(lock, displaced);
    writeFileSync(lock, '');
    let rejected = false;
    try { verifyOrAcquireMutationLock(lock, descriptor, '/usr/bin/flock'); }
    catch { rejected = true; }
    if (!rejected) throw new Error('replacement mutation-gate inode was accepted');
  } finally {
    closeSync(descriptor);
    rmSync(root, { recursive: true, force: true });
  }
  process.stdout.write('SELF_TEST_OK\n');
  process.exit(0);
}

function arg(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

function strictParseJSON(raw, label = 'JSON') {
  const bytes = Buffer.isBuffer(raw) ? raw : Buffer.from(raw, 'utf8');
  const cacheKey = `${bytes.length}:${createHash('sha256').update(bytes).digest('hex')}`;
  if (!strictParseJSON.cache) strictParseJSON.cache = new Map();
  let normalized = strictParseJSON.cache.get(cacheKey);
  if (normalized === undefined) {
    const program = String.raw`
import json, math, sys
MAX_SAFE = 9007199254740991
def pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value
def constant(token):
    raise ValueError(f"non-finite JSON number {token}")
def integer(token):
    value = int(token)
    if abs(value) > MAX_SAFE:
        raise ValueError(f"unsafe JSON integer {token}")
    return value
def floating(token):
    value = float(token)
    if not math.isfinite(value) or abs(value) > MAX_SAFE:
        raise ValueError(f"unsafe or non-finite JSON number {token}")
    return value
try:
    source = sys.stdin.buffer.read().decode("utf-8")
    value = json.loads(source, object_pairs_hook=pairs, parse_constant=constant,
                       parse_int=integer, parse_float=floating)
    output = json.dumps(value, ensure_ascii=False, allow_nan=False,
                        sort_keys=True, separators=(",", ":")).encode("utf-8")
except Exception as error:
    sys.stderr.write(f"{type(error).__name__}: {error}\n")
    raise SystemExit(2)
sys.stdout.buffer.write(output)
`;
    const safeEnvironment = {
      HOME: '<workspace-home>', CODEX_HOME: '<workspace-home>/.codex',
      USER: 'anonymous-user', LOGNAME: 'anonymous-user', PATH: '/usr/bin:/bin',
      LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8', TZ: 'UTC',
      PYTHONDONTWRITEBYTECODE: '1', PYTHONNOUSERSITE: '1', PYTHONHASHSEED: '0',
    };
    const python = realpathSync('/usr/bin/python3');
    const result = spawnSync(python, ['-I', '-c', program], {
      input: bytes, env: safeEnvironment, encoding: 'utf8',
      maxBuffer: 128 * 1024 * 1024,
    });
    if (result.status !== 0) {
      throw new Error(`${label} is not strict finite unique-key JSON: ${(result.stderr || '').trim()}`);
    }
    normalized = result.stdout;
    strictParseJSON.cache.set(cacheKey, normalized);
  }
  const value = JSON.parse(normalized);
  assertSafeJSONNumbers(value, label);
  return value;
}

function assertSafeJSONNumbers(value, label = 'JSON') {
  if (typeof value === 'number') {
    if (!Number.isFinite(value) || Math.abs(value) > Number.MAX_SAFE_INTEGER) {
      throw new Error(`${label} contains an unsafe or non-finite number`);
    }
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item) => assertSafeJSONNumbers(item, label));
  } else if (value !== null && typeof value === 'object') {
    Object.values(value).forEach((item) => assertSafeJSONNumbers(item, label));
  }
}

function stringifySafeJSON(value, replacer = null, space = null, label = 'JSON serialization') {
  assertSafeJSONNumbers(value, label);
  const encoded = JSON.stringify(value, replacer, space);
  if (typeof encoded !== 'string') throw new Error(`${label} did not produce JSON text`);
  return encoded;
}

function isSafeTokenCount(value) {
  return Number.isSafeInteger(value) && value >= 0;
}

function checkedTokenAdd(left, right, label = 'token sum') {
  if (!isSafeTokenCount(left) || !isSafeTokenCount(right) ||
      left > Number.MAX_SAFE_INTEGER - right) {
    throw new Error(`${label} is not a safe nonnegative integer`);
  }
  return left + right;
}

function checkedTokenSum(values, label = 'token sum') {
  return values.reduce((sum, value) => checkedTokenAdd(sum, value, label), 0);
}

function checkedFiniteAdd(left, right, label = 'numeric sum') {
  if (typeof left !== 'number' || typeof right !== 'number' ||
      !Number.isFinite(left) || !Number.isFinite(right) || left < 0 || right < 0) {
    throw new Error(`${label} has a non-finite or negative operand`);
  }
  const result = left + right;
  if (!Number.isFinite(result) || Math.abs(result) > Number.MAX_SAFE_INTEGER) {
    throw new Error(`${label} overflowed the safe finite range`);
  }
  return result;
}

function checkedFiniteSum(values, label = 'numeric sum') {
  return values.reduce((sum, value) => checkedFiniteAdd(sum, value, label), 0);
}

function isSafeDuration(value) {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 &&
    value <= Number.MAX_SAFE_INTEGER;
}

function checkedDuration(value, label = 'duration') {
  if (!isSafeDuration(value)) throw new Error(`${label} is outside the safe finite range`);
  return value;
}

function elapsedSeconds(startMilliseconds, label = 'elapsed duration') {
  if (!Number.isSafeInteger(startMilliseconds)) {
    throw new Error(`${label} start time is not a safe integer`);
  }
  return checkedDuration(Math.max(0, (Date.now() - startMilliseconds) / 1000), label);
}

function checkedTokenDifference(left, right, label = 'token difference') {
  if (!isSafeTokenCount(left) || !isSafeTokenCount(right)) {
    throw new Error(`${label} operands are not safe nonnegative integers`);
  }
  const result = left - right;
  if (!Number.isSafeInteger(result)) throw new Error(`${label} is not a safe integer`);
  return result;
}

const requestedRunRoot = arg('run-root', null);
if (!requestedRunRoot) throw new Error('--run-root is required');
const RUN = resolve(requestedRunRoot);
const ACTIVE_V2_RUN = join(BASE, 'runs', 'open_frontier_paired_v2_20260901');
if (RUN === resolve(ACTIVE_V2_RUN) || RUN.startsWith(`${resolve(ACTIVE_V2_RUN)}${sep}`)) {
  throw new Error('the generic fresh-run runner refuses the historical paired-v2 namespace');
}
const EXPECTED_RUN = join(BASE, 'runs', 'open_frontier_paired_targeted_stress_v2_20260904');
if (RUN !== resolve(EXPECTED_RUN)) {
  throw new Error('run root differs from the frozen BugBank-targeted stress namespace');
}
const RUNTIME_PREFLIGHT = join(HERE, 'paired_open_problem_targeted_stress_v2_runtime_seal.py');
const MANIFEST_PATH = join(RUN, 'RUN_MANIFEST.json');
const RUNTIME_SEAL_PATH = join(RUN, 'RUNTIME_SEAL.json');
const BOOTSTRAP_PYTHON = realpathSync('/usr/bin/python3');
const SAFE_RUNTIME_ENV = Object.freeze({
  HOME: '<workspace-home>', CODEX_HOME: '<workspace-home>/.codex',
  USER: 'anonymous-user', LOGNAME: 'anonymous-user', PATH: '/usr/bin:/bin',
  LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8', TZ: 'UTC',
});
const SAFE_PYTHON_ENV = Object.freeze({
  ...SAFE_RUNTIME_ENV, PYTHONDONTWRITEBYTECODE: '1', PYTHONNOUSERSITE: '1',
  PYTHONHASHSEED: '0',
});
function assertRuntimePreflight() {
  const check = spawnSync(BOOTSTRAP_PYTHON, [RUNTIME_PREFLIGHT, 'check', '--run-root', RUN, '--quiet'], {
    env: SAFE_PYTHON_ENV, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
  });
  if (check.status !== 0) {
    throw new Error(`runtime seal preflight failed: ${(check.stderr || check.stdout || '').trim()}`);
  }
}
assertRuntimePreflight();

const manifest = strictParseJSON(readFileSync(MANIFEST_PATH), 'run manifest');
const runtimeSeal = strictParseJSON(readFileSync(RUNTIME_SEAL_PATH), 'runtime seal');
const PYTHON_RUNTIME = resolve(runtimeSeal.python_interpreter.path);
const NODE_RUNTIME = resolve(runtimeSeal.node_runtime.path);
const MODEL_CLI = resolve(runtimeSeal.model_cli_version.path);
const MODEL_BUNDLE_ROOT = resolve(runtimeSeal.model_cli_version.native_bundle_root);
const BUBBLEWRAP = resolve(runtimeSeal.bubblewrap.path);
const FLOCK_RUNTIME = resolve(runtimeSeal.flock_runtime.path);
const SEALED_PERMISSION_PROFILE = {
  name: 'sealed', extends: ':workspace',
  filesystem: { '/run/codex-home/auth.json': 'deny' },
  network_enabled: false,
};
const ISOLATION_CONTRACT = {
  schema: 'paired_open_problem_bwrap_contract_v2',
  outer_namespaces: ['pid', 'ipc', 'uts'],
  outer_network_namespace: 'host_for_codex_transport_only',
  inner_codex_authorization: {
    sandbox_cli_flag: null,
    default_permissions: SEALED_PERMISSION_PROFILE.name,
    permission_profile: {
      extends: SEALED_PERMISSION_PROFILE.extends,
      filesystem: SEALED_PERMISSION_PROFILE.filesystem,
      network: { enabled: SEALED_PERMISSION_PROFILE.network_enabled },
    },
  },
  ignore_user_config: true,
  ignore_workspace_rules: true,
  web_search: 'disabled',
  model_tool_shell_environment: {
    inherit: 'none', exclude: ['*'],
    set: {
      PATH: '/runtime/vendor/codex-path:/usr/bin:/bin', HOME: 'exact_cell_scratch',
      TMPDIR: '/tmp', LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8',
    },
  },
  allow_login_shell: false,
  shell_snapshot: false,
  strict_config: true,
  fixed_mounts: [
    { kind: 'ro-bind', source: '/usr', destination: '/usr' },
    { kind: 'symlink', source: 'usr/bin', destination: '/bin' },
    { kind: 'symlink', source: 'usr/sbin', destination: '/sbin' },
    { kind: 'symlink', source: 'usr/lib', destination: '/lib' },
    { kind: 'symlink', source: 'usr/lib64', destination: '/lib64' },
    { kind: 'ro-bind', source: '/etc/pki', destination: '/etc/pki' },
    { kind: 'ro-bind', source: '/etc/ssl', destination: '/etc/ssl' },
    { kind: 'ro-bind', source: '/etc/resolv.conf', destination: '/etc/resolv.conf' },
    { kind: 'ro-bind', source: '/etc/hosts', destination: '/etc/hosts' },
    { kind: 'ro-bind', source: '/etc/nsswitch.conf', destination: '/etc/nsswitch.conf' },
    { kind: 'proc', destination: '/proc' }, { kind: 'dev', destination: '/dev' },
    { kind: 'tmpfs', destination: '/tmp' },
  ],
  dynamic_mounts: [
    { kind: 'ro-bind', source: 'sealed_native_bundle', destination: '/runtime/vendor' },
    { kind: 'dir', destination: '/isolated/home' },
    { kind: 'tmpfs', destination: '/run/codex-home' },
    { kind: 'file-from-fd-3', source: 'runtime_auth_json_unhashed', destination: '/run/codex-home/auth.json' },
    { kind: 'bind', source: 'exact_cell_scratch', destination: 'same_absolute_path' },
    { kind: 'ro-bind-each', source: 'exact_call_evidence', destination: 'same_absolute_path' },
  ],
  exact_call_evidence: [
    'bound_output_schema', 'bound_source_input', 'immediate_parent_draft_when_applicable',
    'immediate_parent_audit_for_revision', 'current_bugbank_receipt_for_treated_revision',
  ],
  outer_spawn_environment: {
    LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8',
    PATH: '/runtime/vendor/codex-path:/usr/bin:/bin',
  },
  sandbox_environment: {
    HOME: '/isolated/home', CODEX_HOME: '/run/codex-home',
    PATH: '/runtime/vendor/codex-path:/usr/bin:/bin',
    LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8', NO_COLOR: '1',
  },
  forbidden_mounts: ['repository_root', 'bugbank_database', 'other_arm', 'prior_run', 'user_home'],
  model_output_flow: 'model_writes_exact_scratch_then_host_validates_and_atomically_finalizes',
  scratch_retry_policy: 'exclusive_lock_then_empty_exact_cell_scratch_before_each_new_call',
  host_publication_temporary_policy:
    'private_external_scratch_same_filesystem_fsync_then_atomic_rename_or_link',
  auth_policy: 'bwrap_file_from_fd3_parent_cli_only_model_tools_denied_by_profile',
  auth_transport_fd_model_tool_access: 'closed',
};
const deepSort = (value) => Array.isArray(value) ? value.map(deepSort)
  : value && typeof value === 'object'
    ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, deepSort(value[key])])) : value;
if (stringifySafeJSON(deepSort(runtimeSeal.isolation_contract)) !==
    stringifySafeJSON(deepSort(ISOLATION_CONTRACT))) {
  throw new Error('sealed OS-isolation mount contract differs from runner contract');
}
if (realpathSync(PYTHON_RUNTIME) !== BOOTSTRAP_PYTHON) {
  throw new Error('sealed Python differs from the trusted preflight interpreter');
}
if (realpathSync(process.execPath) !== realpathSync(NODE_RUNTIME)) {
  throw new Error(`runner must be invoked by sealed Node runtime ${NODE_RUNTIME}`);
}
const INPUTS = join(RUN, 'inputs');
const BASELINE_SCHEMA = join(RUN, manifest.schemas.baseline.path);
const AUDIT_SCHEMA = join(RUN, manifest.schemas.audit.path);
const AUDIT_SOLVER_SCHEMA = join(RUN, manifest.schemas.audit_solver.path);
const REVISION_SCHEMA = join(RUN, manifest.schemas.revision.path);
const PLAIN_REVISION_SOLVER_SCHEMA = join(RUN, manifest.schemas.revision_plain_solver.path);
const FEEDBACK_SCRIPT = join(HERE, 'paired_open_problem_feedback.py');
const STOCK_RETRIEVER = join(HERE, 'bugbank_retrieve.py');
const BUGBANK_DB = resolve(runtimeSeal.bugbank_database.path);
const STOP_FILE = resolve(manifest.operations.stop_file);
const stopRequested = () => !dryRun && existsSync(STOP_FILE);
const RUN_ID = manifest.run_id;
const RECEIPT_SCHEMA = 'paired_open_problem_bugbank_exposure_receipt_v1';
const CLAIM_COVERAGE_POLICY = 'WHOLE_PROOF_UNCAPPED_V1';
const MODEL_ISOLATION_POLICY = 'BWRAP_EXACT_EVIDENCE_SEALED_PROFILE_V2';
const JSON_NUMBER_POLICY = 'STRICT_UTF8_UNIQUE_KEYS_FINITE_SAFE_NUMBERS_V1';
const NUMERIC_ACCOUNTING_POLICY = 'CHECKED_SAFE_INTEGER_TOKENS_AND_FINITE_DURATIONS_V1';
const PROMPT_SCHEMA = 'paired_open_problem_prompt_exposure_v1';
const AUDIT_METADATA_SCHEMA = 'paired_open_problem_audit_metadata_v1';
const TERMINAL_SCHEMA = 'paired_open_problem_pair_terminal_v1';
const RETRIEVAL_K = manifest.bugbank.retrieval_k;
const PROTOCOL_MAX_ITERATIONS = manifest.execution.max_iterations;
const REQUESTED_MODEL = manifest.execution.model;
const REQUESTED_REASONING_EFFORT = manifest.execution.reasoning_effort;
const SCRATCH_ROOT = resolve(manifest.operations.scratch_root);
const HOST_ATOMIC_ROOT = join(SCRATCH_ROOT, '.host-atomic');
if (!isSafeTokenCount(PROTOCOL_MAX_ITERATIONS) || PROTOCOL_MAX_ITERATIONS < 1 ||
    !isSafeTokenCount(RETRIEVAL_K) || RETRIEVAL_K < 1) {
  throw new Error('sealed iteration and retrieval bounds must be positive safe integers');
}
if (runtimeSeal.execution.model_isolation_policy !== MODEL_ISOLATION_POLICY ||
    runtimeSeal.execution.audit_normalization_policy !== 'CLERICAL_BINDINGS_ONLY_V1' ||
    runtimeSeal.execution.execution_log_segment_policy !==
      'EXACT_CANONICAL_PREFIX_HASH_AND_SUFFIX_FROM_ADMISSION_OFFSET_V1' ||
    runtimeSeal.execution.json_number_policy !== JSON_NUMBER_POLICY ||
    runtimeSeal.execution.numeric_accounting_policy !== NUMERIC_ACCOUNTING_POLICY) {
  throw new Error('runtime seal lacks the required isolation/normalization policy');
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
if (!dryRun && stage !== 'validate') {
  const expectedEnvironment = {
    ...SAFE_RUNTIME_ENV, PAIRED_OPERATION_LOCK_FD: '8',
  };
  if (stringifySafeJSON(Object.keys(process.env).sort()) !==
        stringifySafeJSON(Object.keys(expectedEnvironment).sort()) ||
      Object.entries(expectedEnvironment).some(([key, value]) => process.env[key] !== value)) {
    throw new Error('mutating runner must start from the sealed exact environment allowlist');
  }
}
if (!Number.isSafeInteger(concurrency) || concurrency < 1) throw new Error('concurrency must be positive');
if (maxIterations !== PROTOCOL_MAX_ITERATIONS) {
  throw new Error(`max-iterations is sealed at ${PROTOCOL_MAX_ITERATIONS}`);
}
if (retrievalK !== RETRIEVAL_K) throw new Error(`retrieval depth is fixed at k=${RETRIEVAL_K}`);
if (['receipt', 'revision', 'audit-revision'].includes(stage) &&
    (!Number.isSafeInteger(requestedIteration) || requestedIteration < 1 || requestedIteration > maxIterations)) {
  throw new Error(`--iteration in [1, ${maxIterations}] is required for ${stage}`);
}
if ([...selectedCells].some((cell) => !/^[A-Za-z0-9_.-]+:(plain|bugbank)$/.test(cell))) {
  throw new Error('--cells must be a comma-separated list of record_id:plain|bugbank');
}
if (stage === 'recover-revisions' &&
    (!recoveryRunnerPids.size || [...recoveryRunnerPids].some((pid) => !Number.isSafeInteger(pid) || pid < 1))) {
  throw new Error('--recover-runner-pids is required for recover-revisions');
}

function lockChildStdio(descriptor) {
  const stdio = Array.from({ length: descriptor + 1 }, () => 'ignore');
  stdio[1] = 'pipe';
  stdio[2] = 'pipe';
  stdio[descriptor] = descriptor;
  return stdio;
}

function verifyOrAcquireMutationLock(expectedPath, descriptor, flockExecutable = FLOCK_RUNTIME) {
  if (!Number.isSafeInteger(descriptor) || descriptor < 3) {
    throw new Error('operation mutation-gate descriptor is invalid');
  }
  const pathInfo = lstatSync(expectedPath);
  if (!pathInfo.isFile() || pathInfo.isSymbolicLink()) {
    throw new Error('canonical operation mutation gate is not a plain file');
  }
  let descriptorTarget;
  let descriptorInfo;
  try {
    descriptorTarget = realpathSync(`/proc/self/fd/${descriptor}`);
    descriptorInfo = fstatSync(descriptor);
  } catch (error) {
    throw new Error(`operation mutation-gate fd ${descriptor} is invalid: ${error}`);
  }
  if (descriptorTarget !== realpathSync(expectedPath) || !descriptorInfo.isFile() ||
      descriptorInfo.dev !== pathInfo.dev || descriptorInfo.ino !== pathInfo.ino) {
    throw new Error('operation mutation-gate descriptor does not bind the exact plain lock file');
  }
  const environment = { PATH: '/usr/bin:/bin', LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8' };
  const acquired = spawnSync(flockExecutable, ['-n', String(descriptor)], {
    env: environment, encoding: 'utf8', stdio: lockChildStdio(descriptor),
  });
  if (acquired.status !== 0) {
    throw new Error(`could not acquire inherited operation mutation gate: ${(acquired.stderr || '').trim()}`);
  }
  let competitor = null;
  try {
    competitor = openSync(expectedPath, constants.O_RDONLY | constants.O_NOFOLLOW);
    const conflict = spawnSync(flockExecutable, ['-n', String(competitor)], {
      env: environment, encoding: 'utf8', stdio: lockChildStdio(competitor),
    });
    if (conflict.status !== 1) {
      throw new Error('operation mutation gate did not exclude a separately opened file description');
    }
  } finally {
    if (competitor !== null) closeSync(competitor);
  }
}

const allIds = manifest.problem_ids;
if (!Array.isArray(allIds) || !allIds.length) throw new Error('sealed roster is empty or invalid');
if (new Set(allIds).size !== allIds.length) throw new Error('duplicate source record IDs');
if (!allIds.every((id) => typeof id === 'string' && /^[A-Za-z0-9_.-]+$/.test(id))) {
  throw new Error('unsafe source record ID');
}
const ids = allIds.filter((id) => (only.size === 0 || only.has(id)) && !exclude.has(id));
if (!ids.length) throw new Error('no selected records');

const OPERATION_LOCK_FD = 8;
const OPERATION_LOCK = resolve(manifest.operations.ops_root, 'operation.lock');
function assertMutationGate() {
  if (dryRun || stage === 'validate') return;
  const operationLockFd = OPERATION_LOCK_FD;
  if (process.env.PAIRED_OPERATION_LOCK_FD !== String(operationLockFd)) {
    throw new Error('mutating execution requires PAIRED_OPERATION_LOCK_FD=8');
  }
  if (runtimeSeal.mutation_gate?.environment_variable !== 'PAIRED_OPERATION_LOCK_FD' ||
      runtimeSeal.mutation_gate?.required_fd !== operationLockFd ||
      runtimeSeal.mutation_gate?.lock_path !== OPERATION_LOCK) {
    throw new Error('runtime seal mutation-gate contract differs from this run');
  }
  verifyOrAcquireMutationLock(OPERATION_LOCK, operationLockFd);
}

function guardedMkdir(path, options) {
  assertMutationGate();
  return mkdirSync(path, options);
}

function guardedWriteFile(pathOrDescriptor, data, options = undefined) {
  assertMutationGate();
  return options === undefined
    ? writeFileSync(pathOrDescriptor, data)
    : writeFileSync(pathOrDescriptor, data, options);
}

function guardedRename(source, destination) {
  assertMutationGate();
  return renameSync(source, destination);
}

function guardedLink(source, destination) {
  assertMutationGate();
  return linkSync(source, destination);
}

function guardedRm(path, options) {
  assertMutationGate();
  return rmSync(path, options);
}

function guardedOpen(path, flags, mode = undefined) {
  assertMutationGate();
  return mode === undefined ? openSync(path, flags) : openSync(path, flags, mode);
}

function guardedChmod(path, mode) {
  assertMutationGate();
  return chmodSync(path, mode);
}

function guardedFsync(descriptor) {
  assertMutationGate();
  return fsyncSync(descriptor);
}

function ensureHostAtomicRoot() {
  guardedMkdir(SCRATCH_ROOT, { recursive: true, mode: 0o700 });
  let scratchInfo = lstatSync(SCRATCH_ROOT);
  if (!scratchInfo.isDirectory() || scratchInfo.isSymbolicLink() ||
      realpathSync(SCRATCH_ROOT) !== SCRATCH_ROOT) {
    throw new Error('external scratch root is not an exact plain directory');
  }
  if ((scratchInfo.mode & 0o077) !== 0) {
    guardedChmod(SCRATCH_ROOT, 0o700);
    scratchInfo = lstatSync(SCRATCH_ROOT);
  }
  guardedMkdir(HOST_ATOMIC_ROOT, { recursive: true, mode: 0o700 });
  let stagingInfo = lstatSync(HOST_ATOMIC_ROOT);
  if (!stagingInfo.isDirectory() || stagingInfo.isSymbolicLink() ||
      realpathSync(HOST_ATOMIC_ROOT) !== HOST_ATOMIC_ROOT ||
      !HOST_ATOMIC_ROOT.startsWith(`${SCRATCH_ROOT}${sep}`)) {
    throw new Error('external host-atomic staging root is not an exact plain directory');
  }
  if ((stagingInfo.mode & 0o077) !== 0) {
    guardedChmod(HOST_ATOMIC_ROOT, 0o700);
    stagingInfo = lstatSync(HOST_ATOMIC_ROOT);
  }
  if ((scratchInfo.mode & 0o077) !== 0 || (stagingInfo.mode & 0o077) !== 0) {
    throw new Error('external host-atomic staging directories are not private');
  }
  if (scratchInfo.dev !== statSync(RUN).dev || stagingInfo.dev !== scratchInfo.dev) {
    throw new Error('external host-atomic staging and the scientific run are on different filesystems');
  }
}

if (!dryRun && stage !== 'validate') {
  assertMutationGate();
  // Every publication temporary lives outside the closed-world run.  This
  // preflight also proves that rename/link publication is same-filesystem
  // before the runner creates any new in-run runtime directory or artifact.
  ensureHostAtomicRoot();
  for (const directory of [
    'baselines', 'audits/baseline', 'audits/iterations', 'audits/metadata/baseline',
    'audits/metadata/iterations', 'retrievals',
    'iterations', 'prompts',
    'pair_terminals', 'logs/baseline', 'logs/audit-baseline', 'logs/receipt',
    'logs/revision', 'logs/audit-revision', 'states', 'locks', 'summaries',
  ]) {
    guardedMkdir(join(RUN, directory), { recursive: true });
  }
}

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isNonemptyString = (value) => typeof value === 'string' && value.length > 0;
const isSha256 = (value) => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value);
const isWholeProofPromptMetadata = (value) =>
  isObject(value) && value.claim_coverage_policy === CLAIM_COVERAGE_POLICY;
const sha256Bytes = (value) => createHash('sha256').update(value).digest('hex');
const sha256Text = (value) => sha256Bytes(Buffer.from(value, 'utf8'));
const sha256File = (path) => sha256Bytes(readFileSync(path));
const readJSON = (path) => strictParseJSON(readFileSync(path), `JSON file ${path}`);

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (isObject(value)) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]));
  }
  return value;
}

const canonicalJSON = (value) => stringifySafeJSON(canonicalize(value), null, null, 'canonical JSON');
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

function executionLogSegment(path, startOffset) {
  requirePlainFile(path, 'canonical execution log');
  const bytes = readFileSync(path);
  if (!Number.isSafeInteger(startOffset) || startOffset < 0 || startOffset > bytes.length) {
    throw new Error('execution-log start offset is outside the canonical log');
  }
  const segment = bytes.subarray(startOffset);
  return {
    path: repoPath(path), start_offset: startOffset,
    size_bytes: segment.length, sha256: sha256Bytes(segment),
  };
}

function executionLogPrefixSha(path, startOffset) {
  requirePlainFile(path, 'canonical execution log');
  const bytes = readFileSync(path);
  if (!Number.isSafeInteger(startOffset) || startOffset < 0 || startOffset > bytes.length) {
    throw new Error('execution-log prefix offset is outside the canonical log');
  }
  return sha256Bytes(bytes.subarray(0, startOffset));
}

function runtimeEvidence() {
  return {
    run_manifest_sha256: sha256File(MANIFEST_PATH),
    runtime_seal_sha256: sha256File(RUNTIME_SEAL_PATH),
    runtime_seal_payload_sha256: runtimeSeal.runtime_payload_sha256,
    runner_sha256: sha256File(RUNNER_SCRIPT),
  };
}

function modelToolShellEnvironment(scratch) {
  return {
    inherit: 'none', exclude: ['*'],
    set: {
      PATH: '/runtime/vendor/codex-path:/usr/bin:/bin', HOME: resolve(scratch),
      TMPDIR: '/tmp', LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8',
    },
  };
}

function tomlInlineStringTable(value) {
  return `{${Object.entries(value).map(([key, item]) =>
    `${key}=${stringifySafeJSON(item)}`).join(',')}}`;
}

function requestedModelExecution(workingDirectory) {
  return {
    model: REQUESTED_MODEL,
    reasoning_effort: REQUESTED_REASONING_EFFORT,
    sandbox: 'outer-bwrap-read-isolated',
    inner_sandbox: 'custom-sealed-workspace',
    permission_profile: structuredClone(SEALED_PERMISSION_PROFILE),
    working_directory: workingDirectory,
    repository_writes_forbidden: true,
    outer_isolation_policy: MODEL_ISOLATION_POLICY,
    readable_evidence_policy: 'EXACT_CALL_INPUTS_ONLY',
    auth_file_model_tool_access: 'deny',
    auth_transport_fd_model_tool_access: 'closed',
    model_shell_network_access: false,
    isolation_contract_sha256: runtimeSeal.isolation_contract_sha256,
    ignore_user_config: true,
    ignore_workspace_rules: true,
    web_search: 'disabled',
    model_tool_shell_environment: modelToolShellEnvironment(workingDirectory),
    allow_login_shell: false,
    shell_snapshot: false,
    strict_config: true,
    outer_spawn_environment_keys: Object.keys(ISOLATION_CONTRACT.outer_spawn_environment).sort(),
    scratch_retry_policy: ISOLATION_CONTRACT.scratch_retry_policy,
    host_publication_temporary_policy: ISOLATION_CONTRACT.host_publication_temporary_policy,
  };
}

function modelIsolationEvidence(schema, readOnlyInputs, scratch) {
  return {
    isolation_contract_sha256: runtimeSeal.isolation_contract_sha256,
    inner_permission_profile: structuredClone(SEALED_PERMISSION_PROFILE),
    auth_file_model_tool_access: 'deny',
    auth_transport_fd_model_tool_access: 'closed',
    model_shell_network_access: false,
    ignore_user_config: true,
    ignore_workspace_rules: true,
    web_search: 'disabled',
    model_tool_shell_environment: modelToolShellEnvironment(scratch),
    allow_login_shell: false,
    shell_snapshot: false,
    strict_config: true,
    outer_spawn_environment_keys: Object.keys(ISOLATION_CONTRACT.outer_spawn_environment).sort(),
    scratch_retry_policy: ISOLATION_CONTRACT.scratch_retry_policy,
    host_publication_temporary_policy: ISOLATION_CONTRACT.host_publication_temporary_policy,
    isolated_read_only_evidence: [schema, ...readOnlyInputs].map((path) => artifact(path)),
    isolated_scratch_path: resolve(scratch),
  };
}

function atomicWrite(path, data) {
  guardedMkdir(dirname(path), { recursive: true });
  const temporary = hostAtomicTemporary(path, 'replace');
  try {
    writeExternalExclusive(temporary, data);
    guardedRename(temporary, path);
  } finally {
    guardedRm(temporary, { force: true });
  }
}

function writeExclusiveOrVerify(path, data) {
  guardedMkdir(dirname(path), { recursive: true });
  const bytes = Buffer.from(data);
  if (existsSync(path)) {
    requirePlainFile(path, 'existing immutable artifact');
    if (!readFileSync(path).equals(bytes)) {
      throw new Error(`immutable artifact conflicts with expected bytes: ${path}`);
    }
    return 'EXISTS_IDENTICAL';
  }
  const temporary = hostAtomicTemporary(path, 'exclusive');
  try {
    writeExternalExclusive(temporary, bytes);
    guardedLink(temporary, path);
    return 'CREATED';
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
    requirePlainFile(path, 'raced immutable artifact');
    if (!readFileSync(path).equals(bytes)) {
      throw new Error(`immutable artifact conflicts with expected bytes: ${path}`);
    }
    return 'EXISTS_IDENTICAL';
  } finally {
    guardedRm(temporary, { force: true });
  }
}

let hostAtomicSequence = 0;
function hostAtomicTemporary(destination, purpose) {
  ensureHostAtomicRoot();
  hostAtomicSequence = checkedTokenAdd(hostAtomicSequence, 1, 'host-atomic sequence');
  const destinationHash = createHash('sha256').update(resolve(destination)).digest('hex');
  return join(
    HOST_ATOMIC_ROOT,
    `${purpose}__${destinationHash}__pid_${process.pid}__${Date.now()}__${hostAtomicSequence}`,
  );
}

function writeExternalExclusive(path, data) {
  const descriptor = guardedOpen(
    path,
    constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW,
    0o644,
  );
  try {
    guardedWriteFile(descriptor, data);
    guardedFsync(descriptor);
  } finally {
    closeSync(descriptor);
  }
}

function finalizeAndValidatePublication(out, bytes, validate, afterFinalize = null) {
  if (afterFinalize !== null) afterFinalize(out);
  if (!readFileSync(out).equals(bytes) || !validate(out)) {
    throw new Error('canonical output publish validation failed');
  }
}

function publishValidatedAbsent(source, out, validate, afterFinalize = null) {
  if (existsSync(out)) throw new Error('canonical output already exists');
  const temporary = hostAtomicTemporary(out, 'validated-output');
  const bytes = readFileSync(source);
  let published = false;
  try {
    writeExternalExclusive(temporary, bytes);
    if (!validate(temporary)) throw new Error('host-staged output validation failed');
    guardedLink(temporary, out);
    published = true;
  } finally {
    guardedRm(temporary, { force: true });
  }
  if (!published) throw new Error('canonical output publish validation failed');
  finalizeAndValidatePublication(out, bytes, validate, afterFinalize);
}

function countOccurrences(text, needle) {
  if (!needle.length) return 0;
  let count = 0;
  let offset = 0;
  while ((offset = text.indexOf(needle, offset)) !== -1) {
    count = checkedTokenAdd(count, 1, 'text occurrence count');
    offset = checkedTokenAdd(offset, needle.length, 'text occurrence offset');
  }
  return count;
}

const inputPath = (id) => join(INPUTS, `${id}.json`);
const baselinePath = (id) => join(RUN, 'baselines', `${id}.json`);
const baselineAuditPath = (id) => join(RUN, 'audits', 'baseline', `${id}.json`);
const revisionPath = (id, arm, iteration) => join(RUN, 'iterations', id, arm, `iter_${iteration}.json`);
const revisionAuditPath = (id, arm, iteration) => join(RUN, 'audits', 'iterations', id, arm, `iter_${iteration}.json`);
const receiptPath = (id, iteration) => join(RUN, 'retrievals', `${id}__iter_${iteration}.json`);
const promptMetadataPath = (id, arm, iteration) =>
  join(RUN, 'prompts', `${id}__${arm}__iter_${iteration}.json`);
const auditMetadataPath = (id, arm, iteration) => arm === 'neutral'
  ? join(RUN, 'audits', 'metadata', 'baseline', `${id}.json`)
  : join(RUN, 'audits', 'metadata', 'iterations', id, arm, `iter_${iteration}.json`);

function scratchPath(id, stageName, arm = null, iteration = null) {
  const components = [SCRATCH_ROOT, id, stageName];
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
    return value.record_id === id && value.stage === 'BASELINE' &&
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
  if (!Number.isSafeInteger(claimedRank) || !Number.isSafeInteger(targetRank)) return null;
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

const AUDIT_NORMALIZATION_POLICY = 'CLERICAL_BINDINGS_ONLY_V1';

function normalizeAuditTemporary(path, context) {
  const value = readJSON(path);
  if (!isObject(value) || !Array.isArray(value.claims) ||
      value.claims.length !== context.parent.results.length) {
    throw new Error('audit output lacks the exact parent claim count');
  }
  // Normalize only deterministic clerical bindings.  In particular, preserve
  // each substantive verdict/evidence/witness/search result and preserve the
  // independent target_verdict and target_evidence exactly as generated.
  value.record_id = context.id;
  value.stage = context.stageName;
  value.arm = context.arm;
  value.iteration = context.iteration;
  value.parent_sha256 = context.parentHash;
  value.complete = true;
  value.claims = value.claims.map((claim, index) => ({
    ...claim, idx: index, claim: context.parent.results[index].claim,
    claim_sha256: sha256Text(context.parent.results[index].claim),
  }));
  value.confirmed_refutations = value.claims.flatMap(
    (claim, index) => claim.verdict === 'REFUTED' ? [index] : [],
  );
  value.overall = expectedAuditOverall(value.claims);
  value.claimed_resolution_verdict = expectedClaimedResolutionVerdict(
    context.parent, value.target_verdict,
  );
  guardedWriteFile(path, stringifySafeJSON(value, null, 2) + '\n');
}

function pythonReceiptPayloadHash(raw) {
  const program = String.raw`
import hashlib, json, math, sys
MAX_SAFE = 9007199254740991
def pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value
def constant(token):
    raise ValueError(f"non-finite JSON number {token}")
def integer(token):
    value = int(token)
    if abs(value) > MAX_SAFE:
        raise ValueError(f"unsafe JSON integer {token}")
    return value
def floating(token):
    value = float(token)
    if not math.isfinite(value) or abs(value) > MAX_SAFE:
        raise ValueError(f"unsafe or non-finite JSON number {token}")
    return value
try:
    x = json.loads(sys.stdin.buffer.read().decode("utf-8"),
                   object_pairs_hook=pairs, parse_constant=constant,
                   parse_int=integer, parse_float=floating)
    x.pop("receipt_payload_sha256", None)
    b = json.dumps(x, ensure_ascii=False, allow_nan=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
except Exception as error:
    sys.stderr.write(f"{type(error).__name__}: {error}\n")
    raise SystemExit(2)
sys.stdout.write(hashlib.sha256(b).hexdigest())
`;
  const result = spawnSync(PYTHON_RUNTIME, ['-I', '-c', program], {
    input: raw, env: SAFE_PYTHON_ENV, encoding: 'utf8',
    maxBuffer: 128 * 1024 * 1024,
  });
  if (result.status !== 0 || !isSha256(result.stdout.trim())) throw new Error('receipt hash recomputation failed');
  return result.stdout.trim();
}

const receiptValidationCache = new Map();
function receiptValidation(path, id, iteration, parentPath, parent) {
  if (!existsSync(path)) return { valid: false, error: 'MISSING_RECEIPT' };
  const signature = [id, iteration, path, statSync(path).size, statSync(path).mtimeMs,
    parentPath, statSync(parentPath).size, statSync(parentPath).mtimeMs,
    statSync(BUGBANK_DB).size, statSync(BUGBANK_DB).mtimeMs,
    statSync(FEEDBACK_SCRIPT).size, statSync(FEEDBACK_SCRIPT).mtimeMs,
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
    const value = strictParseJSON(rawBytes, `receipt ${path}`);
    if (value.schema !== RECEIPT_SCHEMA) return { valid: false, error: 'UNKNOWN_RECEIPT_SCHEMA' };
    const parentBytes = readFileSync(parentPath);
    const claims = parent.results.map((result, claimIndex) => {
      const queryText = `${result.claim}\n\n${result.proof_sketch}`;
      return {
        claim_index: claimIndex, claim: result.claim, claim_sha256: sha256Text(result.claim),
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
        value.parameters.query_text_basis !== 'claim statement, two newlines, proof_sketch' ||
        value.parameters.salient_term_tie_break !== 'first occurrence in query text' ||
        !isObject(value.invocation) || value.invocation.k !== RETRIEVAL_K ||
        value.invocation.run_id !== RUN_ID ||
        resolve(value.invocation.out) !== resolve(receiptPath(id, iteration)) ||
        resolve(value.invocation.parent_json) !== resolve(parentPath) ||
        resolve(value.invocation.db) !== resolve(BUGBANK_DB) ||
        value.invocation.db_sha256 !== manifest.bugbank.database_sha256 ||
        !isObject(value.database) || value.database.sha256 !== sha256File(BUGBANK_DB) ||
        resolve(value.database.path) !== resolve(BUGBANK_DB) ||
        !isObject(value.script) || value.script.sha256 !== sha256File(FEEDBACK_SCRIPT) ||
        resolve(value.script.path) !== resolve(FEEDBACK_SCRIPT) ||
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
      hitCount = checkedTokenAdd(hitCount, query.hits.length, 'receipt hit count');
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
  return `You are solving one research problem.

Read ONLY ${input}. Its "target" is the exact research problem; use "source_paper_text" only for definitions and results already proved there. Do not read any other file and do not use the web. You may create and run exact-arithmetic checks under ${scratch}, but do not modify files outside that directory.

Produce your strongest rigorous progress from scratch. A FULL result requires a complete proof of the recorded target. Otherwise give precisely scoped partial results, reductions, bounds, special cases, or a concrete counterexample to a natural conjecture. Put every load-bearing claim in its own results item, in proof order. There is no claim-count cap; do not omit a claim merely to keep the list short. Prefer sound claims to speculative breadth. Check finite assertions whenever practical, persist reusable checker programs under the scratch directory, and describe the checks in checks_performed.

Hard limits: final_writeup under 3,000 words and each proof_sketch under 500 words. Return JSON matching the schema, with record_id exactly ${stringifySafeJSON(id)} and stage exactly "BASELINE".`;
}

function auditPrompt({ id, arm, iteration, parent, parentPath, parentHash, stageName, scratch }) {
  const expected = parent.results.map((result, idx) => ({
    idx, claim: result.claim, claim_sha256: sha256Text(result.claim),
  }));
  return `You are independently checking a proposed solution to one research problem.

Read ONLY source input ${inputPath(id)} and draft ${parentPath}. Do not read any other file and do not use the web. Do not trust claimed_resolution or self_assessment.

First judge target coverage independently. Read the exact target, not merely the draft's claim list. target_verdict is FULLY_RESOLVES_TARGET only if the draft proves the entire requested target at the requested strength; VALID_PARTIAL_PROGRESS for correct but incomplete progress; NO_VALID_PROGRESS if nothing material survives; and OVERCLAIMED when the headline/final writeup asserts coverage not established by the claims. Separately judge whether claimed_resolution is ACCURATE, OVERSTATED, or UNDERSTATED. Explain this in target_evidence. A technically true but vacuous, much coarser, or mismatched result does not fully resolve a requested matching/tight classification.

Then audit every listed claim from scratch. Hunt for missing cases, quantifier errors, model or statement mismatches, invalid reductions, and counterexamples. For finite or computational claims, write and run exact-arithmetic checks under ${scratch}; never use floating point for a decision. Persist each checker program under that exact directory and return its absolute path in checker_path. Use literal "none" for witness, search_method, or checker_path only when genuinely inapplicable. A finite counterexample requires a concrete witness and persisted checker. VERIFIED requires a rigorous completed proof; REFUTED requires a concrete reproducible flaw or counterexample; otherwise use UNRESOLVED.

The parent SHA-256 is ${parentHash}. Return record_id ${stringifySafeJSON(id)}, stage ${stageName}, iteration ${iteration}, and parent_sha256 exactly as supplied. Exact claim bindings:
${stringifySafeJSON(expected, null, 2)}

Preserve every idx, claim, and claim_sha256 exactly. confirmed_refutations must be exactly the increasing idx list for REFUTED claims. overall is REFUTED if any claim is refuted, VERIFIED only if the nonempty list is entirely verified, and INCONCLUSIVE otherwise. Return schema-valid JSON. Do not modify repository files.`;
}

function baseContext(id) {
  const parentPath = baselinePath(id);
  if (!validBaseline(parentPath, id)) return { ok: false, status: 'MISSING_OR_INVALID_BASELINE' };
  if (!validBaselineCompletedState(id)) {
    return { ok: false, status: 'MISSING_OR_INVALID_BASELINE_STATE' };
  }
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
  if (!validAuditCompletedState(
    id, 'neutral', 0, parentPath, auditPromptText, auditContext.scratch,
  )) return { ok: false, status: 'MISSING_OR_INVALID_BASELINE_AUDIT_STATE' };
  return {
    ok: true, parentPath, parent, parentHash, auditPath,
    audit: readJSON(auditPath), auditHash: sha256File(auditPath),
  };
}

function validRevisionSubstantive(value) {
  return isObject(value) && ['FULL', 'PARTIAL', 'NONE'].includes(value.claimed_resolution) &&
    validResults(value.results) && isNonemptyString(value.final_writeup) &&
    Array.isArray(value.audit_feedback_acted_on) && value.audit_feedback_acted_on.every(isNonemptyString) &&
    Array.isArray(value.checks_performed) && value.checks_performed.every(isNonemptyString) &&
    ['CONFIDENT', 'UNSURE'].includes(value.self_assessment);
}

function validRevisionCore(value) {
  return validRevisionSubstantive(value) &&
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
  if (!validRevisionSubstantive(value)) throw new Error('revision output lacks substantive fields');
  if (arm === 'bugbank' &&
      (!Array.isArray(value.acted_on_entry_ids) || !Array.isArray(value.dismissed_hits))) {
    throw new Error('assisted revision output lacks required hit decisions');
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
  guardedWriteFile(path, stringifySafeJSON(normalized, null, 2) + '\n');
}

function buildRevisionPromptBundle(id, arm, iteration, context, receipt = null) {
  const sourceRaw = readFileSync(inputPath(id), 'utf8');
  const parentRaw = readFileSync(context.parentPath, 'utf8');
  const auditRaw = readFileSync(context.auditPath, 'utf8');
  const scratch = scratchPath(id, 'revision', arm, iteration);
  const closureInstruction = `
Proof-state closure is exact over claimed_resolution, every claim and proof_sketch in results, and final_writeup. If no material correction is required, copy those fields from the parent exactly; do not paraphrase or polish them. Bookkeeping fields may change independently.

`;
  const common = `You are revising one proposed solution to a research problem.

Read only source ${inputPath(id)}, exact parent ${context.parentPath}, and its independent audit ${context.auditPath}. The source defines the target. Parent SHA-256: ${context.parentHash}. Audit SHA-256: ${context.auditHash}. Do not read any other file and do not use the web. Write exact-arithmetic checks only under ${scratch}; do not modify files outside that directory.

Respond to every REFUTED or UNRESOLVED item and to the target-coverage and claimed-resolution judgments. Preserve correct progress; repair, narrow, replace, or remove unsupported claims. Do not call an open target solved without a complete proof at the requested strength. Keep exact claim wording when it remains correct; gratuitous rewording prevents a reproducible fixed point. Preserve every current load-bearing claim and add a separate results item for every new load-bearing claim when the proof expands. There is no claim-count cap. Keep final_writeup under 3,000 words and each proof_sketch under 500 words.

${closureInstruction}The complete independent audit follows verbatim:
--- BEGIN INDEPENDENT AUDIT ---
${auditRaw}--- END INDEPENDENT AUDIT ---

`;
  let prompt;
  let exposure;
  if (arm === 'plain') {
    const inputTokenCount = checkedTokenSum(
      [sourceRaw, parentRaw, auditRaw].map(
        (text) => (text.match(/bugbank/gi) || []).length,
      ),
      'plain-input treatment-name count',
    );
    prompt = `${common}Use your own adversarial self-critique and the independent audit. Return JSON matching the supplied schema. Fixed provenance fields are added by the wrapper after your response.`;
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
    const actionSemantics = ' In this closure protocol, list an ID in acted_on_entry_ids only when this iteration materially changes the proof state because of that record. If the parent already addresses the risk and no new proof change is needed, put the ID in dismissed_hits and state that reason.';
    const prefix = `${common}Use the following complete BugBank exposure receipt as diagnostic memory, not authority. Independently check every applicable counterexample and hypothesis warning. For every unique retrieved ID, either list it in acted_on_entry_ids or give a specific reason in dismissed_hits.${actionSemantics} Preserve first-retrieval order; the two lists must partition retrieved_entry_ids. The wrapper owns all lineage and exposure fields.

--- BEGIN COMPLETE BUGBANK EXPOSURE RECEIPT ---
`;
    const suffix = `--- END COMPLETE BUGBANK EXPOSURE RECEIPT ---

Return revision-schema JSON. Use treatment_status BUGBANK_RECEIPT_EXPOSED and receipt_path ${stringifySafeJSON(repoPath(receiptPath(id, iteration)))}. Exact unique retrieved_entry_ids in first-retrieval order:
${stringifySafeJSON(receipt.retrieved, null, 2)}`;
    prompt = `${prefix}${receipt.raw}${suffix}`;
    const occurrences = countOccurrences(prompt, receipt.raw);
    if (occurrences !== 1) throw new Error(`receipt verbatim occurrence count is ${occurrences}`);
    const characterOffset = prompt.indexOf(receipt.raw);
    const startByte = Buffer.byteLength(prompt.slice(0, characterOffset), 'utf8');
    exposure = {
      complete_receipt_payload_embedded: true, receipt_verbatim_occurrences: occurrences,
      receipt_start_byte: startByte,
      receipt_end_byte: checkedTokenAdd(startByte, receipt.size_bytes, 'receipt exposure end byte'),
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
    run_manifest: artifact(MANIFEST_PATH), runtime_seal: artifact(RUNTIME_SEAL_PATH),
    requested_execution: requestedModelExecution(scratch),
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
      canonicalJSON(value.run_manifest) !== canonicalJSON(artifact(MANIFEST_PATH)) ||
      canonicalJSON(value.runtime_seal) !== canonicalJSON(artifact(RUNTIME_SEAL_PATH)) ||
      !value.prompt_text.includes(readFileSync(context.auditPath, 'utf8')) ||
      !value.prompt_text.includes(inputPath(id)) || !value.prompt_text.includes(context.parentPath) ||
      canonicalJSON(value.requested_execution) !==
        canonicalJSON(requestedModelExecution(scratchPath(id, 'revision', arm, iteration)))) return false;
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
      value.exposure.receipt_end_byte !== checkedTokenAdd(
        receiptStartByte, receipt.size_bytes, 'receipt exposure end byte',
      ) ||
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
  const bytes = Buffer.from(stringifySafeJSON(value, null, 2) + '\n');
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
    const expected = buildRevisionPromptBundle(id, arm, iteration, context, receipt).expectedMetadata;
    const substantive = structuredClone(value);
    delete substantive.created_at;
    delete substantive.metadata_payload_sha256;
    return validatePromptMetadataValue(value, { id, arm, iteration, context, receipt }) &&
      canonicalJSON(substantive) === canonicalJSON(expected) &&
      value.claim_coverage_policy === CLAIM_COVERAGE_POLICY &&
      value.prompt_text.includes('There is no claim-count cap.') &&
      !value.prompt_text.includes('Use at most six claims');
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
  const expectedModelEntries = checkedTokenAdd(
    throughIteration, throughIteration, 'expected arm model-call count',
  );
  const auditable = costs.missing_state_count === 0 &&
    modelEntries.length === expectedModelEntries &&
    modelEntries.every((entry) => ['COMPLETE', 'RECOVERED_COMPLETE'].includes(entry.status) &&
      isSafeTokenCount(entry.tokens_used) &&
      stateIdentityAndExecutionAreExact(entry));
  const modelTokens = auditable
    ? checkedTokenSum(modelEntries.map((entry) => entry.tokens_used), 'arm model-token total')
    : null;
  // A partial sum must never be presented as an arm's completed-call total.
  // Receipt bookkeeping is deliberately excluded even though it is normally
  // zero: endpoint costs are revision and independent-audit model calls only.
  return { ...costs, tokens_used: modelTokens, auditable };
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
    tokenBudgetMatched = tokenBudgetAuditable && isSafeTokenCount(tokenBudgetTarget) &&
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
    run_manifest: artifact(MANIFEST_PATH), runtime_seal: artifact(RUNTIME_SEAL_PATH),
    prompt_text: prompt, prompt_utf8_sha256: sha256Bytes(promptBytes),
    prompt_size_bytes: promptBytes.length,
    requested_execution: requestedModelExecution(context.scratch),
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
  const bytes = Buffer.from(stringifySafeJSON(value, null, 2) + '\n');
  if (!dryRun) writeExclusiveOrVerify(path, bytes);
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
          !isSha256(record.original_sha256) || !Number.isSafeInteger(record.original_size_bytes) ||
          !isObject(record.durable) || !isSha256(record.durable.sha256) ||
          !Number.isSafeInteger(record.durable.size_bytes)) return false;
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
    if (!validReceiptCompletedState(id, iteration, context)) {
      return { ok: false, status: 'MISSING_OR_INVALID_RECEIPT_STATE' };
    }
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
  if (!validRevisionCompletedState(id, arm, iteration, context, receipt, bundle)) {
    return { ok: false, status: 'MISSING_OR_INVALID_REVISION_STATE' };
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
  if (!validAuditCompletedState(
    id, arm, iteration, path, auditPromptText, auditContext.scratch,
  )) return { ok: false, status: 'MISSING_OR_INVALID_REVISION_AUDIT_STATE' };
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
  const tokens = [...text.matchAll(
    /tokens used\s*\r?\n\s*([0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)\s*(?:\r?\n|$)/gi,
  )];
  const models = [...text.matchAll(/^model:\s*(\S.*?)\s*$/gmi)];
  const efforts = [...text.matchAll(/^reasoning effort:\s*(\S.*?)\s*$/gmi)];
  const last = (values) => values.length ? values[values.length - 1][1].trim() : null;
  const tokenText = last(tokens);
  let tokenCount = null;
  if (tokenText !== null) {
    if (!/^(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)$/.test(tokenText)) {
      throw new Error('model-call token telemetry has invalid digit grouping');
    }
    const digits = tokenText.replaceAll(',', '');
    tokenCount = Number(digits);
    if (!isSafeTokenCount(tokenCount)) {
      throw new Error('model-call token telemetry is not a safe nonnegative integer');
    }
  }
  return {
    tokens_used: tokenCount,
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

function exactValue(value, expected) {
  if ((Array.isArray(value) || isObject(value)) &&
      (Array.isArray(expected) || isObject(expected))) {
    return canonicalJSON(value) === canonicalJSON(expected);
  }
  return value === expected;
}

function validCompletedCellState({
  id, arm = null, iteration = null, stageName, out, modelCall,
  stateExtra = {}, schema = null, readOnlyInputs = [], scratch = null,
  allowRecovered = false,
}) {
  if (!existsSync(out)) return false;
  const files = cellFiles(stageName, id, arm, iteration);
  if (!existsSync(files.state)) return false;
  try {
    requirePlainFile(out, 'completed cell output');
    requirePlainFile(files.state, 'completed cell state');
    const value = readJSON(files.state);
    const status = value.status;
    if (status !== 'COMPLETE' && !(allowRecovered && stageName === 'revision' &&
        status === 'RECOVERED_COMPLETE')) return false;
    const isolationEvidence = modelCall
      ? modelIsolationEvidence(schema, readOnlyInputs, scratch) : {};
    const expectedBindings = {
      run_id: RUN_ID, record_id: id, arm, iteration, stage: stageName,
      ...runtimeEvidence(), ...stateExtra, ...isolationEvidence,
      finalized_output: artifact(out),
    };
    if (Object.entries(expectedBindings).some(([key, wanted]) =>
      !exactValue(value[key], wanted))) return false;
    if (modelCall) {
      if (!isSafeTokenCount(value.tokens_used) ||
          value.model !== REQUESTED_MODEL ||
          value.reasoning_effort !== REQUESTED_REASONING_EFFORT) return false;
    } else if (value.tokens_used !== 0 || value.model !== null ||
        value.reasoning_effort !== null) return false;
    if (!Number.isSafeInteger(value.execution_log_start_offset) ||
        value.execution_log_start_offset < 0 ||
        value.execution_log_prefix_sha256 !== executionLogPrefixSha(
          files.log, value.execution_log_start_offset,
        ) ||
        !exactValue(value.execution_log_segment, executionLogSegment(
          files.log, value.execution_log_start_offset,
        ))) return false;
    if (modelCall) {
      const bytes = readFileSync(files.log);
      const cost = parseCodexCost(bytes.subarray(value.execution_log_start_offset));
      if (cost.tokens_used !== value.tokens_used || cost.model !== value.model ||
          cost.reasoning_effort !== value.reasoning_effort) return false;
    }
    let commonKeys;
    if (status === 'COMPLETE') {
      if (!isNonemptyString(value.started_at) || !isNonemptyString(value.ended_at) ||
          typeof value.duration_seconds !== 'number' ||
          !isSafeDuration(value.duration_seconds) ||
          value.error !== null) return false;
      commonKeys = [
        'run_id', 'record_id', 'arm', 'iteration', 'stage', 'status',
        'started_at', 'ended_at', 'duration_seconds', 'error',
        'tokens_used', 'model', 'reasoning_effort',
        'execution_log_start_offset', 'execution_log_prefix_sha256',
        'execution_log_segment',
        'run_manifest_sha256', 'runtime_seal_sha256',
        'runtime_seal_payload_sha256', 'runner_sha256',
      ];
    } else {
      if (!isNonemptyString(value.recovered_at) ||
          !isNonemptyString(value.recovery_path) || !isSha256(value.recovery_sha256)) return false;
      const recovery = resolve(REPO, value.recovery_path);
      if (!recovery.startsWith(`${resolve(RUN, 'recoveries', 'revisions')}${sep}`) ||
          !existsSync(recovery) || sha256File(recovery) !== value.recovery_sha256) return false;
      commonKeys = [
        'run_id', 'record_id', 'arm', 'iteration', 'stage', 'status',
        'recovered_at', 'recovery_path', 'recovery_sha256',
        'tokens_used', 'model', 'reasoning_effort',
        'execution_log_start_offset', 'execution_log_prefix_sha256',
        'execution_log_segment',
        'run_manifest_sha256', 'runtime_seal_sha256',
        'runtime_seal_payload_sha256', 'runner_sha256',
      ];
    }
    const allowed = new Set([
      ...commonKeys, ...Object.keys(stateExtra), ...Object.keys(isolationEvidence),
      'finalized_output',
    ]);
    return Object.keys(value).length === allowed.size &&
      Object.keys(value).every((key) => allowed.has(key));
  } catch { return false; }
}

function validBaselineCompletedState(id) {
  const prompt = baselinePrompt(id);
  return validCompletedCellState({
    id, stageName: 'baseline', out: baselinePath(id), modelCall: true,
    schema: BASELINE_SCHEMA, readOnlyInputs: [inputPath(id)],
    scratch: scratchPath(id, 'baseline'),
    stateExtra: {
      source_sha256: sha256File(inputPath(id)), prompt_sha256: sha256Text(prompt),
      prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
    },
  });
}

function validAuditCompletedState(id, arm, iteration, parentPath, prompt, scratch) {
  const baseline = arm === 'neutral';
  return validCompletedCellState({
    id, arm: baseline ? null : arm, iteration: baseline ? null : iteration,
    stageName: baseline ? 'audit-baseline' : 'audit-revision',
    out: baseline ? baselineAuditPath(id) : revisionAuditPath(id, arm, iteration),
    modelCall: true, schema: AUDIT_SOLVER_SCHEMA,
    readOnlyInputs: [inputPath(id), parentPath], scratch,
    stateExtra: {
      parent_sha256: sha256File(parentPath), prompt_sha256: sha256Text(prompt),
      prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
      audit_normalization_policy: AUDIT_NORMALIZATION_POLICY,
    },
  });
}

function validReceiptCompletedState(id, iteration, context) {
  return validCompletedCellState({
    id, arm: 'bugbank', iteration, stageName: 'receipt',
    out: receiptPath(id, iteration), modelCall: false,
    stateExtra: { parent_sha256: context.parentHash, retrieval_k: RETRIEVAL_K },
  });
}

function revisionStateExtra(bundle, promptMetadata, context, receipt) {
  return {
    parent_sha256: context.parentHash, audit_sha256: context.auditHash,
    prompt_sha256: sha256Text(bundle.prompt),
    prompt_size_bytes: Buffer.byteLength(bundle.prompt, 'utf8'),
    prompt_metadata_sha256: promptMetadata.sha256,
    wrapper_computed_treatment_status: bundle.expectedMetadata.treatment_status,
    receipt_sha256: receipt?.file_sha256 ?? null,
    receipt_exposure_bytes: receipt?.size_bytes ?? 0,
  };
}

function validRevisionCompletedState(id, arm, iteration, context, receipt, bundle) {
  const metadata = promptMetadataPath(id, arm, iteration);
  if (!existsSync(metadata)) return false;
  return validCompletedCellState({
    id, arm, iteration, stageName: 'revision',
    out: revisionPath(id, arm, iteration), modelCall: true,
    schema: arm === 'plain' ? PLAIN_REVISION_SOLVER_SCHEMA : REVISION_SCHEMA,
    readOnlyInputs: [
      inputPath(id), context.parentPath, context.auditPath,
      ...(arm === 'bugbank' ? [receiptPath(id, iteration)] : []),
    ],
    scratch: bundle.scratch, allowRecovered: true,
    stateExtra: revisionStateExtra(bundle, artifact(metadata), context, receipt),
  });
}

function retryableCellStateMatches({
  value, id, arm, iteration, stageName, stateExtra, isolationEvidence = {},
  files, modelCall, runningAdmissions = [],
}) {
  if (!isObject(value) || !['RUNNING', 'FAILED', 'SPAWN_FAILED'].includes(value.status)) {
    return false;
  }
  const expected = {
    run_id: RUN_ID, record_id: id, arm, iteration, stage: stageName,
    status: value.status, started_at: value.started_at,
    ...runtimeEvidence(), ...stateExtra, ...isolationEvidence,
  };
  if (!isNonemptyString(value.started_at) ||
      !Number.isSafeInteger(value.execution_log_start_offset) ||
      value.execution_log_start_offset < 0) return false;
  const keys = new Set([
    ...Object.keys(expected), 'execution_log_start_offset',
    'execution_log_prefix_sha256',
    ...(value.status === 'RUNNING'
      ? ['runner_pid', 'runner_process_starttime']
      : [
        'ended_at', 'duration_seconds', 'error', 'tokens_used', 'model',
        'reasoning_effort', 'execution_log_segment',
      ]),
  ]);
  if (Object.keys(value).length !== keys.size ||
      Object.keys(value).some((key) => !keys.has(key)) ||
      Object.entries(expected).some(([key, wanted]) => !exactValue(value[key], wanted))) {
    return false;
  }
  if (!existsSync(files.log)) return false;
  let segment;
  try { segment = executionLogSegment(files.log, value.execution_log_start_offset); }
  catch { return false; }
  if (value.execution_log_prefix_sha256 !== executionLogPrefixSha(
    files.log, value.execution_log_start_offset,
  )) return false;
  if (value.status === 'RUNNING') {
    if (!Number.isSafeInteger(value.runner_pid) || value.runner_pid < 1 ||
        !isNonemptyString(value.runner_process_starttime)) return false;
    return runningAdmissions.some((admission) => admission !== null &&
      admission.pid === value.runner_pid &&
      admission.process_starttime === value.runner_process_starttime &&
      admission.started_at === value.started_at);
  }
  if (!isNonemptyString(value.ended_at) ||
      typeof value.duration_seconds !== 'number' ||
      !isSafeDuration(value.duration_seconds) ||
      !isNonemptyString(value.error) ||
      !exactValue(value.execution_log_segment, segment)) return false;
  if (!modelCall) {
    return value.tokens_used === 0 && value.model === null &&
      value.reasoning_effort === null;
  }
  const bytes = readFileSync(files.log);
  const cost = parseCodexCost(bytes.subarray(value.execution_log_start_offset));
  if (cost.tokens_used !== value.tokens_used || cost.model !== value.model ||
      cost.reasoning_effort !== value.reasoning_effort) return false;
  return (value.tokens_used === null ||
      isSafeTokenCount(value.tokens_used)) &&
    (value.model === null || value.model === REQUESTED_MODEL) &&
    (value.reasoning_effort === null ||
      value.reasoning_effort === REQUESTED_REASONING_EFFORT);
}

function recoverPublishedModelOutput({
  id, arm, iteration, stageName, out, files, runningAdmissions, stateExtra,
  schema, readOnlyInputs, scratch, validate, validateForRecovery, afterFinalize,
}) {
  if (!existsSync(files.state) || !existsSync(files.log) ||
      !validateForRecovery(out)) return null;
  try {
    const prior = readJSON(files.state);
    const isolationEvidence = modelIsolationEvidence(schema, readOnlyInputs, scratch);
    if (!retryableCellStateMatches({
      value: prior, id, arm, iteration, stageName, stateExtra,
      isolationEvidence, files, modelCall: true, runningAdmissions,
    })) return null;
    const log = readFileSync(files.log);
    const cost = parseCodexCost(log.subarray(prior.execution_log_start_offset));
    if (!isSafeTokenCount(cost.tokens_used) ||
        cost.model !== REQUESTED_MODEL ||
        cost.reasoning_effort !== REQUESTED_REASONING_EFFORT) return null;
    if (afterFinalize !== null) afterFinalize(out);
    if (!validate(out)) return null;
    const startedMilliseconds = Date.parse(prior.started_at);
    if (!Number.isFinite(startedMilliseconds)) return null;
    const durationSeconds = isSafeDuration(prior.duration_seconds)
      ? prior.duration_seconds : elapsedSeconds(startedMilliseconds, 'recovered model-call duration');
    atomicWrite(files.state, stringifySafeJSON({
      run_id: RUN_ID, record_id: id, arm, iteration, stage: stageName,
      status: 'COMPLETE', started_at: prior.started_at,
      ended_at: new Date().toISOString(), duration_seconds: durationSeconds,
      error: null, ...cost, ...runtimeEvidence(), ...stateExtra,
      ...isolationEvidence,
      execution_log_start_offset: prior.execution_log_start_offset,
      execution_log_prefix_sha256: prior.execution_log_prefix_sha256,
      execution_log_segment: executionLogSegment(
        files.log, prior.execution_log_start_offset,
      ),
      finalized_output: artifact(out),
    }, null, 2) + '\n');
    return { ...cost, duration_seconds: durationSeconds };
  } catch { return null; }
}

function recoverPublishedReceipt({
  id, iteration, out, files, runningAdmissions, stateExtra,
}) {
  if (!existsSync(files.state) || !existsSync(files.log)) return null;
  try {
    const prior = readJSON(files.state);
    if (!retryableCellStateMatches({
      value: prior, id, arm: 'bugbank', iteration, stageName: 'receipt',
      stateExtra, files, modelCall: false, runningAdmissions,
    })) return null;
    const startedMilliseconds = Date.parse(prior.started_at);
    if (!Number.isFinite(startedMilliseconds)) return null;
    const durationSeconds = isSafeDuration(prior.duration_seconds)
      ? prior.duration_seconds : elapsedSeconds(startedMilliseconds, 'recovered receipt duration');
    atomicWrite(files.state, stringifySafeJSON({
      run_id: RUN_ID, record_id: id, arm: 'bugbank', iteration, stage: 'receipt',
      status: 'COMPLETE', started_at: prior.started_at,
      ended_at: new Date().toISOString(), duration_seconds: durationSeconds,
      error: null, ...stateExtra, tokens_used: 0, model: null,
      reasoning_effort: null,
      execution_log_start_offset: prior.execution_log_start_offset,
      execution_log_prefix_sha256: prior.execution_log_prefix_sha256,
      execution_log_segment: executionLogSegment(
        files.log, prior.execution_log_start_offset,
      ),
      ...runtimeEvidence(), finalized_output: artifact(out),
    }, null, 2) + '\n');
    return { tokens_used: 0, duration_seconds: durationSeconds };
  } catch { return null; }
}

function processStarttime(pid) {
  try {
    const line = readFileSync(`/proc/${pid}/stat`, 'utf8');
    const marker = line.lastIndexOf(') ');
    if (marker < 0) return null;
    const fields = line.slice(marker + 2).trim().split(/\s+/);
    return /^\d+$/.test(fields[19] || '') ? fields[19] : null;
  } catch { return null; }
}

function exactLockPayload(value, identity) {
  const keys = new Set([
    'schema', 'run_id', 'pid', 'process_starttime', 'record_id', 'arm',
    'iteration', 'stage', 'started_at', 'runtime_seal_sha256', 'runner_sha256',
  ]);
  return isObject(value) && Object.keys(value).length === keys.size &&
    Object.keys(value).every((key) => keys.has(key)) &&
    value.schema === 'paired_open_problem_cell_lock_v1' &&
    value.run_id === RUN_ID && Number.isSafeInteger(value.pid) && value.pid > 0 &&
    isNonemptyString(value.process_starttime) &&
    value.record_id === identity.record_id && value.arm === identity.arm &&
    value.iteration === identity.iteration && value.stage === identity.stage &&
    isNonemptyString(value.started_at) &&
    value.runtime_seal_sha256 === sha256File(RUNTIME_SEAL_PATH) &&
    value.runner_sha256 === sha256File(RUNNER_SCRIPT);
}

function staleRunningAdmission(files) {
  if (!existsSync(files.state)) return null;
  try {
    requirePlainFile(files.state, 'retryable running state');
    const value = readJSON(files.state);
    if (value.status !== 'RUNNING' || !Number.isSafeInteger(value.runner_pid) ||
        value.runner_pid < 1 || !isNonemptyString(value.runner_process_starttime) ||
        !isNonemptyString(value.started_at) ||
        processStarttime(value.runner_pid) === value.runner_process_starttime) return null;
    return {
      pid: value.runner_pid, process_starttime: value.runner_process_starttime,
      started_at: value.started_at,
    };
  } catch { return null; }
}

function removeIncompleteTerminalForAdmission(id) {
  const path = join(RUN, 'pair_terminals', `${id}.json`);
  if (!existsSync(path)) return;
  requirePlainFile(path, 'derived pair terminal');
  const value = readJSON(path);
  const unsigned = structuredClone(value);
  const recordedHash = unsigned.terminal_payload_sha256;
  delete unsigned.terminal_payload_sha256;
  if (value.schema !== TERMINAL_SCHEMA || value.run_id !== RUN_ID ||
      value.record_id !== id || value.stage !== 'PAIR_TERMINAL' ||
      value.status !== 'INCOMPLETE' || value.pair_status !== 'INCOMPLETE' ||
      recordedHash !== sha256Text(canonicalJSON(unsigned))) {
    throw new Error(`refusing to remove noncanonical or complete pair terminal: ${path}`);
  }
  guardedRm(path, { force: true });
}

function clearStaleLockAfterCompletedCell(files, identity) {
  if (!existsSync(files.lock)) return 'CLEAR';
  try {
    requirePlainFile(files.lock, 'completed-cell lock');
    const value = readJSON(files.lock);
    if (!exactLockPayload(value, identity)) return 'INVALID';
    if (processStarttime(value.pid) === value.process_starttime) return 'ACTIVE';
    if (dryRun) return 'STALE';
    assertRuntimePreflight();
    guardedRm(files.lock, { force: true });
    return 'CLEARED';
  } catch { return 'INVALID'; }
}

function acquireLock(path, payload) {
  guardedMkdir(dirname(path), { recursive: true });
  const currentStarttime = processStarttime(process.pid);
  if (currentStarttime === null) throw new Error('cannot bind runner PID starttime');
  const value = {
    schema: 'paired_open_problem_cell_lock_v1', run_id: RUN_ID,
    ...payload, process_starttime: currentStarttime,
    runtime_seal_sha256: sha256File(RUNTIME_SEAL_PATH),
    runner_sha256: sha256File(RUNNER_SCRIPT),
  };
  let staleLock = null;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      const descriptor = guardedOpen(path, 'wx', 0o644);
      try { guardedWriteFile(descriptor, stringifySafeJSON(value, null, 2) + '\n'); }
      finally { closeSync(descriptor); }
      return { staleLock, lock: value };
    } catch (error) {
      if (error?.code !== 'EEXIST') throw error;
      requirePlainFile(path, 'existing cell lock');
      const existing = readJSON(path);
      if (!exactLockPayload(existing, payload)) {
        throw new Error(`existing cell lock has an invalid envelope: ${path}`);
      }
      if (processStarttime(existing.pid) === existing.process_starttime) return null;
      if (attempt > 0) throw new Error(`cell lock replacement raced recovery: ${path}`);
      staleLock = existing;
      guardedRm(path, { force: true });
    }
  }
  throw new Error(`could not acquire cell lock: ${path}`);
}

function requirePlainFile(path, label) {
  const info = lstatSync(path);
  if (!info.isFile() || info.isSymbolicLink()) throw new Error(`${label} is not a regular file: ${path}`);
}

function resetExactCellScratch(path) {
  const root = resolve(SCRATCH_ROOT);
  const target = resolve(path);
  if (!target.startsWith(`${root}${sep}`) || target === root) {
    throw new Error(`refusing to reset scratch outside an exact cell: ${target}`);
  }
  guardedMkdir(root, { recursive: true });
  if (realpathSync(root) !== root) throw new Error('scratch root traverses a symlink');
  if (existsSync(target)) {
    const info = lstatSync(target);
    if (!info.isDirectory() || info.isSymbolicLink() || realpathSync(target) !== target) {
      throw new Error(`cell scratch is not a real directory: ${target}`);
    }
    guardedRm(target, { recursive: true, force: true });
  }
  guardedMkdir(target, { recursive: true });
  if (realpathSync(target) !== target) throw new Error('new cell scratch traverses a symlink');
}

function modelTemporaryPath(scratch, stageName, pid = process.pid) {
  return join(scratch, `.model-output-${stageName}-${pid}.json`);
}

function mountParentArguments(paths) {
  const directories = new Set();
  for (const rawPath of paths) {
    let cursor = dirname(resolve(rawPath));
    while (cursor !== '/') {
      directories.add(cursor);
      cursor = dirname(cursor);
    }
  }
  return [...directories]
    .sort((left, right) => left.split(sep).length - right.split(sep).length || left.localeCompare(right))
    .flatMap((directory) => ['--dir', directory]);
}

function fixedIsolationMountArguments() {
  return ISOLATION_CONTRACT.fixed_mounts.flatMap((row) => {
    if (row.kind === 'ro-bind') return ['--ro-bind', row.source, row.destination];
    if (row.kind === 'symlink') return ['--symlink', row.source, row.destination];
    if (row.kind === 'proc') return ['--proc', row.destination];
    if (row.kind === 'dev') return ['--dev', row.destination];
    if (row.kind === 'tmpfs') return ['--tmpfs', row.destination];
    throw new Error(`unsupported sealed fixed mount kind: ${row.kind}`);
  });
}

function isolatedModelLaunch({ scratch, schema, readOnlyInputs, codexArguments }) {
  const evidence = [...new Set([schema, ...readOnlyInputs].map((path) => resolve(path)))];
  for (const path of evidence) requirePlainFile(path, 'isolated model input');
  if (realpathSync(scratch) !== resolve(scratch)) throw new Error('model scratch path traverses a symlink');
  const authRoot = resolve(process.env.CODEX_HOME || join(homedir(), '.codex'));
  const authPath = join(authRoot, 'auth.json');
  requirePlainFile(authPath, 'Codex authentication file');
  const bundleDestination = '/runtime/vendor';
  const nativeRelative = relative(MODEL_BUNDLE_ROOT, MODEL_CLI);
  if (!nativeRelative || nativeRelative.startsWith('..') || nativeRelative.startsWith(sep)) {
    throw new Error('native Codex binary escapes its sealed bundle');
  }
  const nativeInside = join(bundleDestination, nativeRelative);
  const directories = [
    scratch, ...evidence, bundleDestination, '/isolated/home',
    '/run/codex-home/auth.json', '/etc/resolv.conf',
  ];
  const argumentsList = [
    '--die-with-parent', '--new-session', '--unshare-pid', '--unshare-ipc', '--unshare-uts',
    '--dir', '/etc', ...fixedIsolationMountArguments(),
    ...mountParentArguments(directories),
    '--dir', '/isolated/home',
    '--ro-bind', MODEL_BUNDLE_ROOT, bundleDestination,
    '--tmpfs', '/run/codex-home', '--file', '3', '/run/codex-home/auth.json',
    '--bind', scratch, scratch,
    ...evidence.flatMap((path) => ['--ro-bind', path, path]),
    ...Object.entries(ISOLATION_CONTRACT.sandbox_environment)
      .flatMap(([key, value]) => ['--setenv', key, value]),
    '--chdir', scratch, nativeInside, ...codexArguments,
  ];
  // Never inherit the runner's environment.  In particular, API credentials
  // or scheduler variables must not enter a model-created shell process.
  const environment = { ...ISOLATION_CONTRACT.outer_spawn_environment };
  return { executable: BUBBLEWRAP, argumentsList, environment, authPath };
}

function runCodexCell({
  id, arm = null, iteration = null, stageName, out, schema, prompt, scratch,
  validate, readOnlyInputs, prepareTemporary = null, afterFinalize = null,
  stateExtra = {}, admit = null, validateForRecovery = validate,
}) {
  let admittedPrompt = prompt;
  let admittedStateExtra = stateExtra;
  const files = cellFiles(stageName, id, arm, iteration);
  const existingValid = validate(out);
  if (existingValid) {
    const stateMatches = validCompletedCellState({
      id, arm, iteration, stageName, out, modelCall: true, stateExtra,
      schema, readOnlyInputs, scratch, allowRecovered: stageName === 'revision',
    });
    if (stateMatches) return Promise.resolve({
      id, arm, iteration,
      status: ['CLEAR', 'CLEARED'].includes(clearStaleLockAfterCompletedCell(
        files, { record_id: id, arm, iteration, stage: stageName },
      )) ? 'SKIP_VALID' : 'LOCKED',
      tokens_used: 0,
    });
  }
  const existingRecoveryValid = existsSync(out) && validateForRecovery(out);
  if (existsSync(out) && !existingRecoveryValid) return Promise.resolve({
    id, arm, iteration, status: 'INVALID_EXISTING_OUTPUT', tokens_used: 0,
  });
  if (existsSync(files.state)) {
    try {
      if (['COMPLETE', 'RECOVERED_COMPLETE'].includes(readJSON(files.state).status)) {
        return Promise.resolve({
          id, arm, iteration, status: 'ORPHANED_EXISTING_STATE', tokens_used: 0,
        });
      }
    } catch { /* A malformed noncanonical failure state can be replaced under the cell lock. */ }
  }
  if (dryRun) return Promise.resolve({ id, arm, iteration, status: 'PLANNED', tokens_used: 0 });
  // Drain without touching canonical state. In-flight calls finish normally;
  // this check prevents every new model launch after the operator switch.
  if (stopRequested()) {
    return Promise.resolve({ id, arm, iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  try { assertRuntimePreflight(); }
  catch (error) {
    return Promise.resolve({
      id, arm, iteration, status: 'PREFLIGHT_FAILED', error: String(error), tokens_used: 0,
    });
  }
  const started = new Date().toISOString();
  const startMilliseconds = Date.now();
  let lockAdmission;
  try {
    lockAdmission = acquireLock(files.lock, {
      pid: process.pid, record_id: id, arm, iteration, stage: stageName, started_at: started,
    });
  } catch (error) {
    return Promise.resolve({
      id, arm, iteration, status: 'INVALID_EXISTING_LOCK', error: String(error), tokens_used: 0,
    });
  }
  if (lockAdmission === null) {
    return Promise.resolve({ id, arm, iteration, status: 'LOCKED', tokens_used: 0 });
  }
  // This is the scientific admission boundary.  Nothing except the exclusive
  // cell lock has been created yet.  Once this second STOP check passes, the
  // admitted call is treated as in flight and drains to completion.
  if (stopRequested()) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({ id, arm, iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  try { removeIncompleteTerminalForAdmission(id); }
  catch (error) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm, iteration, status: 'ADMISSION_FAILED', error: String(error), tokens_used: 0,
    });
  }
  if (existsSync(out)) {
    const recoveryAdmissions = [lockAdmission.staleLock, staleRunningAdmission(files)]
      .filter((value, index, values) => value !== null &&
        values.findIndex((candidate) => candidate !== null &&
          candidate.pid === value.pid && candidate.process_starttime === value.process_starttime &&
          candidate.started_at === value.started_at) === index);
    const recovered = recoverPublishedModelOutput({
      id, arm, iteration, stageName, out, files,
      runningAdmissions: recoveryAdmissions,
      stateExtra: admittedStateExtra, schema, readOnlyInputs, scratch,
      validate, validateForRecovery, afterFinalize,
    });
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm, iteration,
      status: recovered === null ? 'ORPHANED_EXISTING_OUTPUT' : 'RECOVERED_PUBLICATION',
      tokens_used: recovered?.tokens_used ?? 0,
      duration_seconds: recovered?.duration_seconds,
    });
  }
  guardedMkdir(dirname(out), { recursive: true });
  try { resetExactCellScratch(scratch); }
  catch (error) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm, iteration, status: 'SCRATCH_RESET_FAILED', error: String(error), tokens_used: 0,
    });
  }
  try {
    if (admit !== null) {
      const admitted = admit();
      if (!isObject(admitted) || !isNonemptyString(admitted.prompt) ||
          !isObject(admitted.stateExtra)) throw new Error('invalid cell admission result');
      admittedPrompt = admitted.prompt;
      admittedStateExtra = admitted.stateExtra;
    }
  } catch (error) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm, iteration, status: 'ADMISSION_FAILED', error: String(error), tokens_used: 0,
    });
  }
  const temporary = modelTemporaryPath(scratch, stageName);
  const isolationEvidence = modelIsolationEvidence(schema, readOnlyInputs, scratch);
  guardedMkdir(dirname(files.log), { recursive: true });
  const oldLogSize = existsSync(files.log) ? statSync(files.log).size : 0;
  const descriptor = guardedOpen(files.log, 'a');
  const oldLogSha256 = executionLogPrefixSha(files.log, oldLogSize);
  atomicWrite(files.state, stringifySafeJSON({
    run_id: RUN_ID, record_id: id, arm, iteration, stage: stageName, status: 'RUNNING',
    started_at: started, execution_log_start_offset: oldLogSize,
    execution_log_prefix_sha256: oldLogSha256,
    runner_pid: lockAdmission.lock.pid,
    runner_process_starttime: lockAdmission.lock.process_starttime,
    ...runtimeEvidence(), ...admittedStateExtra, ...isolationEvidence,
  }, null, 2) + '\n');
  const args = [
    '--strict-config', '-a', 'never', '-C', scratch,
    '-m', REQUESTED_MODEL, '-c', `model_reasoning_effort="${REQUESTED_REASONING_EFFORT}"`,
    '-c', 'web_search="disabled"',
    '-c', 'shell_environment_policy.inherit="none"',
    '-c', 'shell_environment_policy.exclude=["*"]',
    '-c', `shell_environment_policy.set=${tomlInlineStringTable(
      modelToolShellEnvironment(scratch).set
    )}`,
    '-c', 'allow_login_shell=false',
    '-c', 'features.shell_snapshot=false',
    '-c', `default_permissions="${SEALED_PERMISSION_PROFILE.name}"`,
    '-c', `permissions.${SEALED_PERMISSION_PROFILE.name}.extends="${SEALED_PERMISSION_PROFILE.extends}"`,
    '-c', `permissions.${SEALED_PERMISSION_PROFILE.name}.filesystem={"/run/codex-home/auth.json"="deny"}`,
    '-c', `permissions.${SEALED_PERMISSION_PROFILE.name}.network.enabled=false`,
    'exec', '--skip-git-repo-check', '--ephemeral',
    '--ignore-user-config', '--ignore-rules',
    '--output-schema', schema,
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
    const finish = (status, error, cost, finalizedOutput = null) => {
      if (settled) return;
      settled = true;
      if (status !== 'COMPLETE') guardedRm(temporary, { force: true });
      const durationSeconds = elapsedSeconds(startMilliseconds, 'model-call duration');
      const result = { id, arm, iteration, status, error, duration_seconds: durationSeconds, ...cost };
      atomicWrite(files.state, stringifySafeJSON({
        run_id: RUN_ID, record_id: id, arm, iteration, stage: stageName, status, started_at: started,
        ended_at: new Date().toISOString(), duration_seconds: durationSeconds,
        error, ...cost, execution_log_start_offset: oldLogSize,
        execution_log_prefix_sha256: oldLogSha256,
        execution_log_segment: executionLogSegment(files.log, oldLogSize),
        ...runtimeEvidence(), ...admittedStateExtra, ...isolationEvidence,
        ...(status === 'COMPLETE' ? { finalized_output: finalizedOutput } : {}),
      }, null, 2) + '\n');
      guardedRm(files.lock, { force: true });
      resolvePromise(result);
    };
    let child;
    try {
      assertRuntimePreflight();
      const launch = isolatedModelLaunch({
        scratch, schema, readOnlyInputs, codexArguments: args,
      });
      assertMutationGate();
      const authDescriptor = openSync(
        launch.authPath, constants.O_RDONLY | constants.O_NOFOLLOW,
      );
      try {
        if (!fstatSync(authDescriptor).isFile()) {
          throw new Error('opened Codex authentication descriptor is not a regular file');
        }
        child = spawn(launch.executable, launch.argumentsList, {
          cwd: scratch, env: launch.environment,
          stdio: ['pipe', descriptor, descriptor, authDescriptor],
        });
      } finally {
        closeSync(authDescriptor);
      }
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
      let cost = { tokens_used: null, model: null, reasoning_effort: null };
      let telemetryError = null;
      try { cost = parseCodexCost(log.subarray(Math.min(oldLogSize, log.length))); }
      catch (caught) { telemetryError = String(caught); }
      let resultStatus = 'FAILED';
      let error = null;
      let finalizedOutput = null;
      try {
        assertRuntimePreflight();
        if (telemetryError !== null) throw new Error(telemetryError);
        if (code !== 0) throw new Error(`exit=${code} signal=${signal}`);
        if (stdinError !== null) throw new Error(`prompt stdin failed: ${stdinError}`);
        if (!isSafeTokenCount(cost.tokens_used) ||
            cost.model !== REQUESTED_MODEL ||
            cost.reasoning_effort !== REQUESTED_REASONING_EFFORT) {
          throw new Error('model-call telemetry does not exactly match sealed tokens/model/effort');
        }
        if (prepareTemporary) prepareTemporary(temporary);
        if (!validate(temporary)) throw new Error('strict wrapper validation failed');
        if (existsSync(out)) {
          throw new Error('canonical final output appeared after the exclusive cell lock');
        }
        publishValidatedAbsent(temporary, out, validate, afterFinalize);
        guardedRm(temporary, { force: true });
        finalizedOutput = artifact(out);
        resultStatus = 'COMPLETE';
      } catch (caught) { error = String(caught); }
      finish(resultStatus, error, cost, finalizedOutput);
    });
    child.stdin.on('error', (error) => {
      stdinError = String(error);
      if (child.exitCode === null && !child.killed) child.kill('SIGTERM');
    });
    try {
      child.stdin.end(admittedPrompt, 'utf8');
    } catch (error) {
      stdinError = String(error);
      if (child.exitCode === null && !child.killed) child.kill('SIGTERM');
    }
  });
}

function runBaseline(id) {
  if (stopRequested()) return Promise.resolve({ id, status: 'STOP_REQUESTED', tokens_used: 0 });
  const out = baselinePath(id);
  const prompt = baselinePrompt(id);
  return runCodexCell({
    id, stageName: 'baseline', out, schema: BASELINE_SCHEMA,
    prompt, scratch: scratchPath(id, 'baseline'),
    readOnlyInputs: [inputPath(id)],
    validate: (path) => validBaseline(path, id),
    stateExtra: {
      source_sha256: sha256File(inputPath(id)), prompt_sha256: sha256Text(prompt),
      prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
    },
  });
}

function runAuditBaseline(id) {
  if (stopRequested()) return Promise.resolve({ id, status: 'STOP_REQUESTED', tokens_used: 0 });
  const parentPath = baselinePath(id);
  if (!validBaseline(parentPath, id)) return Promise.resolve({ id, status: 'MISSING_BASELINE', tokens_used: 0 });
  if (!validBaselineCompletedState(id)) {
    return Promise.resolve({ id, status: 'MISSING_OR_INVALID_BASELINE_STATE', tokens_used: 0 });
  }
  const parent = readJSON(parentPath);
  const parentHash = sha256File(parentPath);
  const scratch = scratchPath(id, 'audit-baseline');
  const context = { id, stageName: 'BASELINE_AUDIT', arm: 'neutral', iteration: 0, parentHash, parent, scratch };
  const prompt = auditPrompt({
    id, arm: 'neutral', iteration: 0, parent, parentPath, parentHash,
    stageName: 'BASELINE_AUDIT', scratch,
  });
  const out = baselineAuditPath(id);
  const validate = (path) => {
    if (!validAudit(path, context)) return false;
    return path !== out || validAuditMetadata(id, 'neutral', 0, readJSON(path), context, prompt);
  };
  return runCodexCell({
    id, stageName: 'audit-baseline', out, schema: AUDIT_SOLVER_SCHEMA, prompt, scratch, validate,
    readOnlyInputs: [inputPath(id), parentPath],
    prepareTemporary: (temporary) => {
      normalizeAuditTemporary(temporary, context);
      const audit = readJSON(temporary);
      if (!validateAuditValue(audit, context)) throw new Error('invalid baseline audit');
    },
    afterFinalize: (finalPath) =>
      ensureAuditMetadata(id, 'neutral', 0, readJSON(finalPath), context, prompt),
    validateForRecovery: (path) => validAudit(path, context),
    stateExtra: {
      parent_sha256: parentHash, prompt_sha256: sha256Text(prompt),
      prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
      audit_normalization_policy: AUDIT_NORMALIZATION_POLICY,
    },
  });
}

function runReceipt(id, iteration) {
  const context = iterationContext(id, 'bugbank', iteration);
  if (!context.ok) return Promise.resolve({ id, arm: 'bugbank', iteration, status: context.status, tokens_used: 0 });
  const out = receiptPath(id, iteration);
  const stateExtra = { parent_sha256: context.parentHash, retrieval_k: RETRIEVAL_K };
  const files = cellFiles('receipt', id, 'bugbank', iteration);
  const existing = receiptValidation(out, id, iteration, context.parentPath, context.parent);
  if (existing.valid) {
    const stateMatches = validCompletedCellState({
      id, arm: 'bugbank', iteration, stageName: 'receipt', out,
      modelCall: false, stateExtra,
    });
    if (stateMatches) return Promise.resolve({
      id, arm: 'bugbank', iteration,
      status: ['CLEAR', 'CLEARED'].includes(clearStaleLockAfterCompletedCell(
        files, { record_id: id, arm: 'bugbank', iteration, stage: 'receipt' },
      )) ? 'SKIP_VALID' : 'LOCKED',
      tokens_used: 0,
    });
  }
  if (existsSync(out) && !existing.valid) return Promise.resolve({
    id, arm: 'bugbank', iteration, status: 'INVALID_EXISTING_RECEIPT', error: existing.error, tokens_used: 0,
  });
  if (existsSync(files.state)) {
    try {
      if (readJSON(files.state).status === 'COMPLETE') {
        return Promise.resolve({
          id, arm: 'bugbank', iteration, status: 'ORPHANED_EXISTING_RECEIPT_STATE', tokens_used: 0,
        });
      }
    } catch { /* A malformed noncanonical failure state can be retried under lock. */ }
  }
  if (dryRun) return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'PLANNED', tokens_used: 0 });
  // Retrieval is not a model call, but it is still a new treatment artifact.
  // Honor the same drain boundary before creating its lock, state, or process.
  if (stopRequested()) {
    return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  try { assertRuntimePreflight(); }
  catch (error) {
    return Promise.resolve({
      id, arm: 'bugbank', iteration, status: 'PREFLIGHT_FAILED',
      error: String(error), tokens_used: 0,
    });
  }
  const receiptScratch = scratchPath(id, 'receipt', 'bugbank', iteration);
  const started = new Date().toISOString();
  const startMilliseconds = Date.now();
  let lockAdmission;
  try {
    lockAdmission = acquireLock(files.lock, {
      pid: process.pid, record_id: id, arm: 'bugbank', iteration,
      stage: 'receipt', started_at: started,
    });
  } catch (error) {
    return Promise.resolve({
      id, arm: 'bugbank', iteration, status: 'INVALID_EXISTING_LOCK',
      error: String(error), tokens_used: 0,
    });
  }
  if (lockAdmission === null) {
    return Promise.resolve({ id, arm: 'bugbank', iteration, status: 'LOCKED', tokens_used: 0 });
  }
  // Exact receipt admission boundary: no receipt, state, log, or scratch has
  // been materialized before this second STOP check under the cell lock.
  if (stopRequested()) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm: 'bugbank', iteration, status: 'STOP_REQUESTED', tokens_used: 0,
    });
  }
  try { removeIncompleteTerminalForAdmission(id); }
  catch (error) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm: 'bugbank', iteration, status: 'ADMISSION_FAILED',
      error: String(error), tokens_used: 0,
    });
  }
  if (existsSync(out)) {
    const recoveryAdmissions = [lockAdmission.staleLock, staleRunningAdmission(files)]
      .filter((value, index, values) => value !== null &&
        values.findIndex((candidate) => candidate !== null &&
          candidate.pid === value.pid && candidate.process_starttime === value.process_starttime &&
          candidate.started_at === value.started_at) === index);
    const recovered = recoverPublishedReceipt({
      id, iteration, out, files,
      runningAdmissions: recoveryAdmissions, stateExtra,
    });
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm: 'bugbank', iteration,
      status: recovered === null ? 'ORPHANED_EXISTING_RECEIPT' : 'RECOVERED_PUBLICATION',
      tokens_used: 0, duration_seconds: recovered?.duration_seconds,
    });
  }
  try { resetExactCellScratch(receiptScratch); }
  catch (error) {
    guardedRm(files.lock, { force: true });
    return Promise.resolve({
      id, arm: 'bugbank', iteration, status: 'SCRATCH_RESET_FAILED',
      error: String(error), tokens_used: 0,
    });
  }
  const temporary = join(receiptScratch, `.receipt-output-${process.pid}.json`);
  guardedMkdir(dirname(files.log), { recursive: true });
  const oldLogSize = existsSync(files.log) ? statSync(files.log).size : 0;
  const descriptor = guardedOpen(files.log, 'a');
  const oldLogSha256 = executionLogPrefixSha(files.log, oldLogSize);
  atomicWrite(files.state, stringifySafeJSON({
    run_id: RUN_ID, record_id: id, arm: 'bugbank', iteration, stage: 'receipt', status: 'RUNNING',
    started_at: started, execution_log_start_offset: oldLogSize, ...stateExtra,
    execution_log_prefix_sha256: oldLogSha256,
    runner_pid: lockAdmission.lock.pid,
    runner_process_starttime: lockAdmission.lock.process_starttime,
    ...runtimeEvidence(),
  }, null, 2) + '\n');
  const argumentsList = [
    FEEDBACK_SCRIPT, '--parent-json', context.parentPath, '--record-id', id,
    '--run-id', RUN_ID, '--iteration', String(iteration), '--out', temporary,
    '--canonical-out', out,
    '--k', String(RETRIEVAL_K), '--db', BUGBANK_DB,
    '--db-sha256', manifest.bugbank.database_sha256,
  ];
  return new Promise((resolvePromise) => {
    let settled = false;
    let descriptorOpen = true;
    const closeLog = () => {
      if (!descriptorOpen) return;
      descriptorOpen = false;
      closeSync(descriptor);
    };
    const finish = (status, error, finalizedOutput = null) => {
      if (settled) return;
      settled = true;
      if (status !== 'COMPLETE') guardedRm(temporary, { force: true });
      const durationSeconds = elapsedSeconds(startMilliseconds, 'receipt duration');
      atomicWrite(files.state, stringifySafeJSON({
        run_id: RUN_ID, record_id: id, arm: 'bugbank', iteration, stage: 'receipt', status,
        started_at: started, ended_at: new Date().toISOString(), duration_seconds: durationSeconds,
        error, ...stateExtra,
        tokens_used: 0, model: null, reasoning_effort: null,
        execution_log_start_offset: oldLogSize,
        execution_log_prefix_sha256: oldLogSha256,
        execution_log_segment: executionLogSegment(files.log, oldLogSize),
        ...runtimeEvidence(),
        ...(status === 'COMPLETE' ? { finalized_output: finalizedOutput } : {}),
      }, null, 2) + '\n');
      guardedRm(files.lock, { force: true });
      resolvePromise({ id, arm: 'bugbank', iteration, status, error, duration_seconds: durationSeconds, tokens_used: 0 });
    };
    let child;
    try {
      assertRuntimePreflight();
      assertMutationGate();
      child = spawn(PYTHON_RUNTIME, argumentsList, {
        cwd: REPO, env: SAFE_PYTHON_ENV,
        stdio: ['ignore', descriptor, descriptor],
      });
    } catch (error) {
      closeLog();
      finish('SPAWN_FAILED', String(error));
      return;
    }
    child.on('error', (error) => { closeLog(); finish('SPAWN_FAILED', String(error)); });
    child.on('exit', (code, signal) => {
      if (settled) return;
      closeLog();
      let validation;
      try {
        assertRuntimePreflight();
        validation = receiptValidation(temporary, id, iteration, context.parentPath, context.parent);
        if (code === 0 && validation.valid) {
          if (existsSync(out)) throw new Error('canonical receipt appeared during retrieval');
          publishValidatedAbsent(temporary, out, (candidate) => receiptValidation(
            candidate, id, iteration, context.parentPath, context.parent,
          ).valid);
          guardedRm(temporary, { force: true });
          validation = receiptValidation(out, id, iteration, context.parentPath, context.parent);
        }
      } catch (error) {
        validation = { valid: false, error: String(error) };
      }
      const completed = code === 0 && validation.valid;
      if (!completed) guardedRm(temporary, { force: true });
      finish(completed ? 'COMPLETE' : 'FAILED',
        completed ? null : `exit=${code} signal=${signal} receipt=${validation.error}`,
        completed ? artifact(out) : null);
    });
  });
}

function runRevision(id, arm, iteration) {
  // Prompt metadata is itself treatment evidence.  Observe the drain switch
  // before deriving or materializing it, not only later in runCodexCell.
  if (stopRequested()) {
    return Promise.resolve({ id, arm, iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  const context = iterationContext(id, arm, iteration);
  if (!context.ok) return Promise.resolve({ id, arm, iteration, status: context.status, tokens_used: 0 });
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = receiptValidation(receiptPath(id, iteration), id, iteration, context.parentPath, context.parent);
    if (!receipt.valid) return Promise.resolve({ id, arm, iteration, status: receipt.error, tokens_used: 0 });
    if (!validReceiptCompletedState(id, iteration, context)) {
      return Promise.resolve({
        id, arm, iteration, status: 'MISSING_OR_INVALID_RECEIPT_STATE', tokens_used: 0,
      });
    }
  }
  let bundle;
  let promptMetadata = null;
  try {
    bundle = buildRevisionPromptBundle(id, arm, iteration, context, receipt);
    if (stopRequested()) {
      return Promise.resolve({ id, arm, iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
    }
    const metadataPath = promptMetadataPath(id, arm, iteration);
    if (existsSync(metadataPath)) {
      if (!validPromptMetadata(id, arm, iteration, context, receipt)) {
        throw new Error('existing prompt metadata fails semantic exposure/lineage validation');
      }
      const stored = readJSON(metadataPath);
      bundle = { ...bundle, prompt: stored.prompt_text };
      promptMetadata = artifact(metadataPath);
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
    id, arm, iteration, stageName: 'revision', out,
    schema: arm === 'plain' ? PLAIN_REVISION_SOLVER_SCHEMA : REVISION_SCHEMA,
    prompt: bundle.prompt, scratch: bundle.scratch, validate,
    readOnlyInputs: [
      inputPath(id), context.parentPath, context.auditPath,
      ...(arm === 'bugbank' ? [receiptPath(id, iteration)] : []),
    ],
    prepareTemporary: (temporary) => normalizeRevisionTemporary(
      temporary, { id, arm, iteration, context, receipt },
    ),
    stateExtra: promptMetadata === null ? {} :
      revisionStateExtra(bundle, promptMetadata, context, receipt),
    admit: promptMetadata === null ? () => {
      ensurePromptMetadata(id, arm, iteration, bundle, context, receipt);
      if (!validPromptMetadata(id, arm, iteration, context, receipt)) {
        throw new Error('new prompt metadata failed exact reconstruction');
      }
      promptMetadata = artifact(promptMetadataPath(id, arm, iteration));
      return {
        prompt: bundle.prompt,
        stateExtra: revisionStateExtra(bundle, promptMetadata, context, receipt),
      };
    } : null,
  });
}

function runAuditRevision(id, arm, iteration) {
  if (stopRequested()) {
    return Promise.resolve({ id, arm, iteration, status: 'STOP_REQUESTED', tokens_used: 0 });
  }
  const context = iterationContext(id, arm, iteration);
  if (!context.ok) return Promise.resolve({ id, arm, iteration, status: context.status, tokens_used: 0 });
  let receipt = null;
  if (arm === 'bugbank') {
    receipt = receiptValidation(receiptPath(id, iteration), id, iteration, context.parentPath, context.parent);
    if (!receipt.valid) return Promise.resolve({ id, arm, iteration, status: receipt.error, tokens_used: 0 });
    if (!validReceiptCompletedState(id, iteration, context)) {
      return Promise.resolve({
        id, arm, iteration, status: 'MISSING_OR_INVALID_RECEIPT_STATE', tokens_used: 0,
      });
    }
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
  let revisionBundle;
  try { revisionBundle = buildRevisionPromptBundle(id, arm, iteration, context, receipt); }
  catch (error) {
    return Promise.resolve({
      id, arm, iteration, status: 'INVALID_PROMPT_INPUT', error: String(error), tokens_used: 0,
    });
  }
  if (!validRevisionCompletedState(
    id, arm, iteration, context, receipt, revisionBundle,
  )) return Promise.resolve({
    id, arm, iteration, status: 'MISSING_OR_INVALID_REVISION_STATE', tokens_used: 0,
  });
  const auditContext = auditContextForRevision(id, arm, iteration, revision);
  const prompt = auditPrompt({
    id, arm, iteration, parent: revision, parentPath,
    parentHash: auditContext.parentHash, stageName: 'REVISION_AUDIT', scratch: auditContext.scratch,
  });
  const out = revisionAuditPath(id, arm, iteration);
  const validate = (path) => {
    if (!validAudit(path, auditContext)) return false;
    return path !== out || validAuditMetadata(id, arm, iteration, readJSON(path), auditContext, prompt);
  };
  return runCodexCell({
    id, arm, iteration, stageName: 'audit-revision', out, schema: AUDIT_SOLVER_SCHEMA,
    prompt, scratch: auditContext.scratch, validate,
    readOnlyInputs: [inputPath(id), parentPath],
    prepareTemporary: (temporary) => {
      normalizeAuditTemporary(temporary, auditContext);
      const audit = readJSON(temporary);
      if (!validateAuditValue(audit, auditContext)) throw new Error('invalid revision audit');
    },
    afterFinalize: (finalPath) =>
      ensureAuditMetadata(id, arm, iteration, readJSON(finalPath), auditContext, prompt),
    validateForRecovery: (path) => validAudit(path, auditContext),
    stateExtra: {
      parent_sha256: auditContext.parentHash, prompt_sha256: sha256Text(prompt),
      prompt_size_bytes: Buffer.byteLength(prompt, 'utf8'),
      audit_normalization_policy: AUDIT_NORMALIZATION_POLICY,
    },
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
  const metadataPath = promptMetadataPath(id, arm, iteration);
  return { context, receipt, promptMetadata: artifact(metadataPath), promptValue: readJSON(metadataPath) };
}

function recoverOneRevisionLock(lockPath) {
  requirePlainFile(lockPath, 'revision-recovery lock');
  const lockBytes = readFileSync(lockPath);
  const lock = strictParseJSON(lockBytes, `revision recovery lock ${lockPath}`);
  const { record_id: id, arm, iteration, pid } = lock;
  if (!ids.includes(id) || !['plain', 'bugbank'].includes(arm) ||
      !Number.isSafeInteger(iteration) || iteration < 1 || !recoveryRunnerPids.has(pid)) {
    return { id: id ?? null, arm: arm ?? null, iteration: iteration ?? null, status: 'SKIP_OUT_OF_SCOPE' };
  }
  if (!exactLockPayload(lock, {
    record_id: id, arm, iteration, stage: 'revision',
  })) return { id, arm, iteration, status: 'INVALID_LOCK_ENVELOPE', pid };
  if (processStarttime(pid) === lock.process_starttime) {
    return { id, arm, iteration, status: 'SKIP_RUNNER_ALIVE', pid };
  }
  const scratch = scratchPath(id, 'revision', arm, iteration);
  if (processReferencesScratch(scratch)) {
    return { id, arm, iteration, status: 'SKIP_ACTIVE_CHILD', pid, scratch };
  }
  const { context, receipt, promptMetadata, promptValue } = revisionRecoveryContext(id, arm, iteration);
  const finalPath = revisionPath(id, arm, iteration);
  const temporaryPath = modelTemporaryPath(scratch, 'revision', pid);
  const files = cellFiles('revision', id, arm, iteration);
  if (!existsSync(files.state) || !existsSync(files.log)) {
    return { id, arm, iteration, status: 'MISSING_RETRYABLE_STATE_OR_LOG', pid };
  }
  const recoveryStateExtra = {
    parent_sha256: context.parentHash, audit_sha256: context.auditHash,
    prompt_sha256: promptValue.prompt_utf8_sha256,
    prompt_size_bytes: promptValue.prompt_size_bytes,
    prompt_metadata_sha256: promptMetadata.sha256,
    wrapper_computed_treatment_status: promptValue.treatment_status,
    receipt_sha256: receipt?.file_sha256 ?? null,
    receipt_exposure_bytes: receipt?.size_bytes ?? 0,
  };
  const recoveryIsolationEvidence = modelIsolationEvidence(
    arm === 'plain' ? PLAIN_REVISION_SOLVER_SCHEMA : REVISION_SCHEMA,
    [
      inputPath(id), context.parentPath, context.auditPath,
      ...(arm === 'bugbank' ? [receiptPath(id, iteration)] : []),
    ],
    scratch,
  );
  const priorState = readJSON(files.state);
  if (!retryableCellStateMatches({
    value: priorState, id, arm, iteration, stageName: 'revision',
    stateExtra: recoveryStateExtra, isolationEvidence: recoveryIsolationEvidence,
    files, modelCall: true, runningAdmissions: [lock],
  })) return { id, arm, iteration, status: 'INVALID_RETRYABLE_STATE', pid };
  const forensicName = `${id}__${arm}__iter_${iteration}__pid_${pid}`;
  const archivedLock = archiveExactFile(lockPath, 'locks', `${forensicName}.lock.json`);
  const archivedState = archiveExactFile(files.state, 'states', `${forensicName}.state.json`);
  const archivedLog = archiveExactFile(files.log, 'logs', `${forensicName}.log`);
  const cost = parseCodexCost(
    readFileSync(files.log).subarray(priorState.execution_log_start_offset),
  );
  let status;
  let archivedTemporary = null;
  let finalArtifact = null;
  let originalTemporarySha256 = null;
  let originalTemporarySizeBytes = null;
  if (existsSync(finalPath)) {
    // Never replace a canonical state (and therefore never replace its token
    // evidence) merely because a stale duplicate lock was discovered.
    return { id, arm, iteration, status: 'BLOCKED_FINAL_ALREADY_EXISTS', pid };
  } else if (existsSync(temporaryPath)) {
    const originalBytes = readFileSync(temporaryPath);
    originalTemporarySha256 = sha256Bytes(originalBytes);
    originalTemporarySizeBytes = originalBytes.length;
    archivedTemporary = archiveExactFile(temporaryPath, 'revision_tmp', `${forensicName}.original.json`);
    const candidate = hostAtomicTemporary(finalPath, 'revision-recovery');
    try {
      writeExternalExclusive(candidate, originalBytes);
      normalizeRevisionTemporary(candidate, { id, arm, iteration, context, receipt });
      if (!validateRevisionValue(readJSON(candidate), { id, arm, iteration, context, receipt })) {
        throw new Error('normalized orphan failed exact revision validation');
      }
      if (!isSafeTokenCount(cost.tokens_used) ||
          cost.model !== REQUESTED_MODEL ||
          cost.reasoning_effort !== REQUESTED_REASONING_EFFORT) {
        throw new Error('orphan call lacks complete telemetry in its exact log segment');
      }
      if (existsSync(finalPath)) throw new Error('final appeared during recovery; refusing overwrite');
      publishValidatedAbsent(candidate, finalPath, (path) =>
        validateRevisionValue(readJSON(path), { id, arm, iteration, context, receipt }));
      finalArtifact = artifact(finalPath);
      status = 'RECOVERED_COMPLETE';
    } catch (error) {
      return {
        id, arm, iteration, status: 'SALVAGE_VALIDATION_FAILED', pid, error: String(error),
        original_temporary_sha256: originalTemporarySha256,
        archived_temporary: archivedTemporary,
      };
    } finally {
      guardedRm(candidate, { force: true });
    }
  } else {
    status = 'READY_FOR_RELAUNCH';
  }
  const recovery = addPayloadHash({
    schema: 'paired_open_problem_revision_recovery_v1', run_id: RUN_ID,
    incident: 'orphaned_revision_model_call', record_id: id, arm, iteration,
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
  writeExclusiveOrVerify(recoveryPath, Buffer.from(stringifySafeJSON(recovery, null, 2) + '\n'));
  atomicWrite(files.state, stringifySafeJSON({
    run_id: RUN_ID, record_id: id, arm, iteration, stage: 'revision', status,
    recovered_at: recovery.recovered_at, recovery_path: repoPath(recoveryPath),
    recovery_sha256: sha256File(recoveryPath), tokens_used: cost.tokens_used,
    model: cost.model, reasoning_effort: cost.reasoning_effort,
    parent_sha256: context.parentHash, audit_sha256: context.auditHash,
    prompt_sha256: promptValue.prompt_utf8_sha256,
    prompt_size_bytes: promptValue.prompt_size_bytes,
    prompt_metadata_sha256: promptMetadata.sha256,
    wrapper_computed_treatment_status: promptValue.treatment_status,
    receipt_sha256: receipt?.file_sha256 ?? null,
    receipt_exposure_bytes: receipt?.size_bytes ?? 0,
    execution_log_start_offset: priorState.execution_log_start_offset,
    execution_log_prefix_sha256: priorState.execution_log_prefix_sha256,
    execution_log_segment: executionLogSegment(
      files.log, priorState.execution_log_start_offset,
    ),
    ...(status === 'RECOVERED_COMPLETE' ? { finalized_output: finalArtifact } : {}),
    ...runtimeEvidence(), ...recoveryIsolationEvidence,
  }, null, 2) + '\n');
  if (existsSync(temporaryPath)) guardedRm(temporaryPath, { force: true });
  if (!readFileSync(lockPath).equals(lockBytes)) {
    throw new Error(`lock changed during recovery: ${lockPath}`);
  }
  guardedRm(lockPath, { force: true });
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
  for (const result of results) process.stdout.write(`${stringifySafeJSON(result)}\n`);
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
    tokens_used: checkedTokenSum(
      entries.map((entry) => entry.tokens_used ?? 0), 'execution-state token total',
    ),
    duration_seconds_sum: checkedFiniteSum(
      entries.map((entry) => entry.duration_seconds ?? 0),
      'execution-state duration total',
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
          isSafeTokenCount(completed.assessment.token_budget_used) &&
          isSafeTokenCount(completed.assessment.token_budget_target)
          ? checkedTokenDifference(
            completed.assessment.token_budget_used,
            completed.assessment.token_budget_target,
            'plain token-budget overshoot',
          )
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

function incompleteTerminalArm(arm) {
  // Incomplete terminal snapshots are deliberately informational only.  Keep
  // their entire arm envelope deterministic and independent of whatever
  // partially written cell happened to be observed at checkpoint time; the
  // validator derives scientific progress from the canonical cells instead.
  return {
    arm, status: 'INCOMPLETE', terminal: false, terminal_reason: 'INCOMPLETE',
    iteration: null, reason: 'VALID_ENDPOINT_NOT_AVAILABLE',
    next_stage: 'CONTINUE_PROTOCOL', revision_sha256: null, audit_sha256: null,
    claimed_resolution: null, target_verdict: null, audit_overall: null,
  };
}

function terminalValue(id) {
  const base = baseContext(id);
  const progress = { plain: armProgress(id, 'plain'), bugbank: armProgress(id, 'bugbank') };
  const arms = Object.fromEntries(['plain', 'bugbank'].map((arm) => [
    arm, progress[arm].terminal ? progress[arm] : incompleteTerminalArm(arm),
  ]));
  const proofEndpointsComplete = arms.plain.terminal && arms.bugbank.terminal;
  const tokensOf = (arm) => arms[arm].terminal && isSafeTokenCount(arms[arm].model_tokens_used)
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
      ? checkedTokenDifference(plainTokens, bugbankTokens, 'paired token difference') : null,
    plain_solved_with_fewer_tokens: plainSolved && plainTokens !== null && bugbankTokens !== null
      ? plainTokens < bugbankTokens : null,
    baseline: base.ok ? { draft: artifact(base.parentPath), independent_audit: artifact(base.auditPath) } : null,
    arms,
  }, 'terminal_payload_sha256');
}

function runTerminal(id) {
  try {
    const value = terminalValue(id);
    if (!dryRun) atomicWrite(
      join(RUN, 'pair_terminals', `${id}.json`), stringifySafeJSON(value, null, 2) + '\n',
    );
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
      process.stdout.write(`${stringifySafeJSON(results[index])}\n`);
    }
  }
  await Promise.all(Array.from({ length: Math.min(width, items.length) }, worker));
  return results;
}

function cellIsSelected(id, arm) {
  return selectedCells.size === 0 || selectedCells.has(`${id}:${arm}`);
}

let summarySequence = 0;
const WRITABLE_SUMMARY_STAGES = new Set([
  'baseline', 'audit-baseline', 'receipt', 'revision',
  'audit-revision', 'terminal', 'recover-revisions',
]);
function writeSummary(stageName, results, startedAt, iteration = null) {
  const successes = new Set([
    'COMPLETE', 'SKIP_VALID', 'PLANNED',
    'RECOVERED_COMPLETE', 'RECOVERED_PUBLICATION', 'READY_FOR_RELAUNCH',
    'FINAL_ALREADY_VALID', 'SKIP_OUT_OF_SCOPE',
    'ALREADY_TERMINAL',
  ]);
  const summary = {
    run: RUN_ID, stage: stageName, iteration, dry_run: dryRun,
    started_at: startedAt, ended_at: new Date().toISOString(), selected: results.length,
    complete: results.filter((result) => successes.has(result.status)).length,
    failed: results.filter((result) => !successes.has(result.status)).length,
    tokens_used: checkedTokenSum(
      results.map((result) => result.tokens_used ?? 0), 'stage-summary token total',
    ),
    duration_seconds_sum: checkedFiniteSum(
      results.map((result) => result.duration_seconds ?? 0),
      'stage-summary duration total',
    ),
    results,
  };
  if (!dryRun && stageName !== 'validate') {
    if (!WRITABLE_SUMMARY_STAGES.has(stageName)) {
      throw new Error(`refusing to write summary for unknown stage: ${stageName}`);
    }
    summarySequence = checkedTokenAdd(summarySequence, 1, 'stage-summary sequence');
    const safeTime = startedAt.replaceAll(':', '').replaceAll('.', '-');
    const directory = join(RUN, 'summaries', stageName);
    guardedMkdir(directory, { recursive: true });
    const path = join(directory, `${safeTime}__pid_${process.pid}__${summarySequence}.json`);
    writeExclusiveOrVerify(path, Buffer.from(stringifySafeJSON(summary, null, 2) + '\n'));
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
    if (!Number.isSafeInteger(progress.iteration)) return [];
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

  const maximumRounds = checkedTokenAdd(
    checkedTokenAdd(maxIterations, maxIterations, 'all-stage round bound'),
    2,
    'all-stage round bound',
  );
  for (let round = 0; round < maximumRounds; round += 1) {
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
  for (const result of results) process.stdout.write(`${stringifySafeJSON(result)}\n`);
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
