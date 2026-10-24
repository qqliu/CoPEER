// Node runner for the browser-compatible checks in docs/assets/js/checks/.
// Usage: node tests/run_checks.mjs            (exit code 1 if any check fails)
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const dataDir = join(root, 'docs', 'data');
const checksDir = join(root, 'docs', 'assets', 'js', 'checks');

const sandbox = { window: {}, console, BigInt };
sandbox.window.window = sandbox.window;
sandbox.window.self = sandbox.window;
sandbox.self = sandbox.window;
const ctx = vm.createContext(sandbox);

for (const f of readdirSync(dataDir).filter((n) => n.endsWith('.js')).sort()) {
  vm.runInContext(readFileSync(join(dataDir, f), 'utf8'), ctx, { filename: f });
}
vm.runInContext(readFileSync(join(root, 'docs', 'assets', 'js', 'math', 'labs.js'), 'utf8'), ctx, { filename: 'labs.js' });
vm.runInContext(readFileSync(join(root, 'docs', 'tests', 'codex_review_fixtures.js'), 'utf8'), ctx, { filename: 'codex_review_fixtures.js' });
for (const f of readdirSync(checksDir).filter((n) => n.endsWith('.js')).sort()) {
  vm.runInContext(readFileSync(join(checksDir, f), 'utf8'), ctx, { filename: f });
}

const results = [];
const C = sandbox.window.COPEER_CHECKS;
if (C.runDataChecks) results.push(...C.runDataChecks(sandbox.window.COPEER_DATA));
if (C.runMathChecks) results.push(...C.runMathChecks());

let failed = 0;
for (const r of results) {
  if (!r.pass) failed += 1;
  console.log(`${r.pass ? 'PASS' : 'FAIL'}  ${r.name}${r.detail ? '  (' + r.detail + ')' : ''}`);
}
console.log(`\n${results.length - failed} passed, ${failed} failed, ${Object.keys(sandbox.window.COPEER_DATA || {}).length} data files loaded`);
process.exit(failed ? 1 : 0);
