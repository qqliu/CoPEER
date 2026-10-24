#!/usr/bin/env python3
"""Resolve explicit correction receipts and score approved current populations.

No provider calls, response-directory discovery, legacy score.main(), historical
gold defaults, or success-based response selection. The command requires the
actual registry scientific/runtime gate; pure helpers are exposed for fixtures.
"""
import argparse
import ast
import collections
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import re
import types

SCHEMA = "corrected-ccl-resolved-results/v1"
COMPONENTS = ("measured_tokens", "unknown_attempts", "observed_lower_bound_tokens", "charged_tokens")
COMMON_FUNCTIONS = {"normalise_leading_zero_labels", "_last_candidates_object", "_last_candidates_array",
                    "parse_candidates_audit", "parse_candidates", "_token_count", "usage_summary"}
COMMON_CONSTANTS = {"MAX_OUTPUT", "PARSER_VERSION", "ARRAY_ONLY_PARSER_VERSION", "NORMALISATIONS"}
SCORE_FUNCTIONS = {"seed_for", "toks", "baselines", "attempt_class_of", "budget_evidence_source", "outcome",
                   "aggregate_usage", "aggregate_output_usage", "cost_components", "parser_fallback_report",
                   "boot", "boot_minus_best", "wilson", "summarise"}
SCORE_CONSTANTS = {"RESAMPLES", "ATTEMPT_CLASS_CAUSE", "STOP_REASON_CLASS", "BUDGET_EVIDENCE_SOURCES", "SYMBOLS"}
EPOCH_SETTING_EXCEPTIONS = {"attempt_epoch_id", "attempt_epoch_policy_sha256"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def vsha(value):
    return sha(canonical(value))


def lane_key(root_label, lane):
    return root_label + "__" + lane


def target_key(row):
    return row["root_label"], row["lane"], row["record_id"]


def bound_json(descriptor, reader):
    raw = reader(descriptor)
    need(sha(raw) == descriptor["sha256"], "Bound JSON hash drift")
    return json.loads(raw)


def extract_pure(source, names, constants, environment):
    """Compile only explicitly reviewed functions/constants; never module imports."""
    tree = ast.parse(source)
    nodes = []
    found = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            need(not node.decorator_list, "Unexpected pure-function decorator")
            nodes.append(node)
            found.add(node.name)
        elif isinstance(node, ast.Assign):
            targets = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if targets & constants:
                need(targets <= constants, "Unexpected grouped pure constant")
                nodes.append(node)
                found |= targets
    need(found == names | constants, "Frozen pure scoring/parser interface changed")
    result = dict(environment)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<bound-frozen-pure-functions>", "exec"), result)
    return result, vsha([ast.dump(node, include_attributes=False) for node in nodes])


def frozen_runtime(configuration, reader):
    files = {Path(d["path"]).name: d for d in configuration["frozen_design_files"]}
    need("common.py" in files and "score.py" in files, "Frozen parser/scorer descriptors missing")
    raw_common = reader(files["common.py"])
    raw_score = reader(files["score.py"])
    need(sha(raw_common) == files["common.py"]["sha256"] and sha(raw_score) == files["score.py"]["sha256"],
         "Frozen parser/scorer file drift")
    env = {"json": json, "re": re, "hashlib": hashlib, "math": math, "random": random,
           "collections": collections}
    common, parser_digest = extract_pure(raw_common, COMMON_FUNCTIONS, COMMON_CONSTANTS, env)
    scoring, scoring_digest = extract_pure(raw_score, SCORE_FUNCTIONS, SCORE_CONSTANTS, common)
    need(scoring["RESAMPLES"] == 10000, "Frozen bootstrap count changed")
    return types.SimpleNamespace(**scoring), {"parser_functions_sha256": parser_digest,
        "scoring_functions_sha256": scoring_digest, "common": files["common.py"], "score": files["score.py"]}


def validate_population(manifest, items):
    population = manifest["current_population_definition"]
    need(isinstance(population, dict), "No approved current population")
    need(manifest.get("population_definition_state") == "ALL_GATES_APPROVED", "Population not approved")
    ids = sorted(items)
    need(population["historical_record_ids"] == ids and population["historical_record_ids_sha256"] == vsha(ids),
         "Historical roster binding differs")
    masks = population["record_masks"]
    need(set(masks) == set(items) and population["record_masks_sha256"] == vsha(masks), "Population mask hash mismatch")
    role_groups = {"admitted": "admitted", "withdrawn_diagnostic": "withdrawn_diagnostic_only",
                   "evaluation_population": "evaluation_population", "pilot_population": "pilot_population",
                   "evaluation_scorable": "evaluation_scorable", "evaluation_primary": "evaluation_primary",
                   "pilot_scorable": "pilot_scorable"}
    for rid, item in items.items():
        roles = masks[rid]["roles"]
        nonblank = {label for label, text in item["lines"] if str(text).strip()}
        need(len({label for label, _ in item["lines"]}) == len(item["lines"]), "Duplicate source line label")
        need(set(item["gold"]) <= nonblank and bool(item["gold"]) != bool(item.get("unscorable")),
             "Reference gold/scorability invalid")
        admitted = roles["admitted"]
        need(type(admitted) is bool and roles["withdrawn_diagnostic_only"] is (not admitted), "Admission mask inconsistent")
        need(roles["split"] == item["split"] and item["split"] in {"pilot", "evaluation"}, "Split changed")
        need(roles["unscorable"] == bool(item.get("unscorable")), "Scorability mask differs")
        scorable = admitted and not item.get("unscorable")
        expected = {"evaluation_population": admitted and item["split"] == "evaluation",
                    "pilot_population": admitted and item["split"] == "pilot",
                    "evaluation_scorable": bool(scorable and item["split"] == "evaluation"),
                    "pilot_scorable": bool(scorable and item["split"] == "pilot"),
                    "evaluation_primary": bool(scorable and item["split"] == "evaluation" and
                                               item["n_nonblank_text"] >= 10 and not item.get("exclude_from_primary", False))}
        need(all(roles[key] == value for key, value in expected.items()), "Current role definition differs")
        need(masks[rid]["release_status"] == ("RETAINED" if admitted else "EXCLUDED"), "Admission/disposition differs")
    for group, role in role_groups.items():
        expected = sorted(rid for rid, row in masks.items() if row["roles"][role])
        need(population["record_ids"][group] == expected and population["record_ids_sha256"][group] == vsha(expected)
             and population["counts"][group] == len(expected), "Current population roster differs: " + group)
    return population


def fresh_path(descriptor, registry):
    """Fresh descriptors must name the registered namespace, even in pure fixtures."""
    p = Path(descriptor["path"])
    root = Path(registry["fresh_root"])
    need(not p.is_absolute() and ".." not in p.parts and p.is_relative_to(root), "Fresh artifact escapes correction root")


def receipt_costs(target, registry, registry_descriptor, freeze_sha256, runtime, reader):
    """One charge per physical dispatch; record aggregates are never added again."""
    dispatches = {}
    receipts = {}
    for descriptor in target["dispatch_receipts"]:
        fresh_path(descriptor, registry)
        ticket = bound_json(descriptor, reader)
        identity = ticket["ticket_id"]
        need(identity not in dispatches, "Duplicate dispatch identity")
        need(ticket["record_id"] == target["record_id"] and ticket["split"] == target["split"], "Dispatch target differs")
        need(ticket.get("correction_registry_sha256") == registry_descriptor["sha256"] and
             ticket.get("correction_manifest_sha256") == registry["manifest"]["sha256"] and
             ticket.get("correction_epoch_id") == registry["epoch_id"] and
             ticket.get("root_label") == target["root_label"] and ticket.get("freeze_sha256") == freeze_sha256,
             "Physical dispatch correction/freeze identity differs")
        need(ticket.get("requested_model") == target["lane"], "Physical dispatch model differs")
        need(type(ticket.get("dispatched_time_ns")) is int and ticket["dispatched_time_ns"] > 0 and
             type(ticket.get("reservation_tokens")) is int and 0 <= ticket["reservation_tokens"] <= 120000,
             "Invalid physical dispatch time/reservation")
        dispatches[identity] = (ticket, descriptor)
    need(len(dispatches) == target["physical_attempt_count"] and len(dispatches) <= 2, "Physical attempt count/cap differs")
    for descriptor in target["attempt_receipts"]:
        fresh_path(descriptor, registry)
        receipt = bound_json(descriptor, reader)
        identity = receipt["dispatch"]["ticket_id"]
        need(identity in dispatches and identity not in receipts, "Unpaired or duplicate attempt receipt")
        need(receipt["dispatch"] == dispatches[identity][0], "Attempt receipt dispatch drift")
        need(receipt["attempt"].get("correction_registry_sha256") == registry_descriptor["sha256"] and
             receipt["attempt"].get("correction_manifest_sha256") == registry["manifest"]["sha256"] and
             receipt["attempt"].get("correction_epoch_id") == registry["epoch_id"], "Physical attempt correction identity differs")
        usage = runtime.usage_summary({"attempts": [receipt["attempt"]]})
        need(receipt["accounting"] == usage, "Attempt accounting differs from frozen usage rules")
        receipts[identity] = (receipt["attempt"], descriptor)
    units = []
    ordered = sorted(dispatches.items(), key=lambda row: row[1][0]["dispatched_time_ns"])
    need(len({row[1][0]["dispatched_time_ns"] for row in ordered}) == len(ordered), "Ambiguous dispatch order")
    for identity, (ticket, descriptor) in ordered:
        if identity in receipts:
            attempt, attempt_descriptor = receipts[identity]
        else:
            # An unresolved physical dispatch is an unknown-cost orphan, never a successful answer.
            attempt = {"usage_known": False, "budget_charge_tokens": ticket["reservation_tokens"]}
            attempt_descriptor = None
        units.append({"unit_id": identity, "coverage_id": "dispatch:" + identity,
                      "dispatch": descriptor, "attempt_receipt": attempt_descriptor,
                      "attempt": attempt, "orphan": identity not in receipts,
                      "components": runtime.cost_components(runtime.aggregate_usage([{"attempts": [attempt]}]))})
    return units


def read_chosen(configuration, call, item, record_descriptor, answer_descriptor, registry, registry_descriptor, runtime, reader, fresh,
                expected_freeze=None):
    if fresh:
        fresh_path(record_descriptor, registry)
        fresh_path(answer_descriptor, registry)
    record = bound_json(record_descriptor, reader)
    raw_answer = reader(answer_descriptor)
    need(sha(raw_answer) == answer_descriptor["sha256"] == record.get("answer_sha256"), "Chosen answer hash differs")
    need(record.get("record_id") == item["record_id"] and record.get("split") == item["split"], "Chosen record identity differs")
    need(record.get("requested_model") == configuration["lane"], "Chosen model identity differs")
    need(record.get("freeze_sha256") == (expected_freeze or configuration["freeze_sha256"]), "Chosen original freeze differs")
    need(record.get("prompt_sha256") == call["new_user_prompt_sha256"], "Chosen source-only prompt differs")
    if record.get("system_prompt_sha256") is not None:
        need(record["system_prompt_sha256"] == call["new_system_prompt_sha256"], "Chosen system prompt differs")
    if record.get("stdin_sha256") is not None:
        need(record["stdin_sha256"] == call["new_agy_stdin_sha256"], "Chosen provider stdin differs")
    if fresh:
        need(record.get("current_roles") == call["current_roles"] and record.get("cost_bucket") == call["cost_bucket"],
             "Fresh record admission/cost role differs")
        need(record.get("correction_registry_sha256") == registry_descriptor["sha256"] and
             record.get("correction_manifest_sha256") == registry["manifest"]["sha256"] and
             record.get("correction_epoch_id") == registry["epoch_id"], "Fresh record correction bindings differ")
        need(record.get("attempt_epoch_id") == registry["epoch_id"] and
             record.get("attempt_epoch_policy_sha256") == registry["policy"]["sha256"], "Fresh attempt epoch differs")
        for key, value in call["historical"]["settings"].items():
            if key in EPOCH_SETTING_EXCEPTIONS:
                continue
            actual = vsha(record.get("environment_overrides")) if key == "environment_overrides_sha256" else record.get(key)
            need(actual == value, "Fresh frozen configuration setting differs: " + key)
    answer = raw_answer.decode("utf-8")
    visible = answer.split("</think>")[-1] if configuration["runner"] == "run_local.py" and "</think>" in answer else answer
    # The parser never receives the new reference gold or a witness/dossier.
    audit = runtime.parse_candidates_audit(visible, {"record_id": item["record_id"], "split": item["split"], "lines": item["lines"]})
    need(record.get("candidates") == audit["candidates"], "Recorded candidates differ from frozen parser replay")
    if "candidate_parse" in record:
        need(record["candidate_parse"] == audit, "Recorded parser audit differs from replay")
    parsed = copy.deepcopy(record)
    parsed["candidate_parse"] = audit
    return parsed, {"record": record_descriptor, "answer": answer_descriptor, "actual_freeze_sha256": record["freeze_sha256"],
                    "visible_answer_sha256": sha(visible.encode()),
                    "parser_replayed": True, "candidate_parse_sha256": vsha(audit)}


def resolve_physical_inputs(registry, registry_descriptor, manifest, terminal_index, reader):
    """Pure exact-index resolution. Caller must first run the real registry gate."""
    need(terminal_index.get("schema") == "corrected-ccl-terminal-index/v1", "Wrong terminal index schema")
    need(terminal_index.get("registry") == registry_descriptor and terminal_index.get("manifest") == registry["manifest"]
         and terminal_index.get("epoch_id") == registry["epoch_id"], "Terminal index binding differs")
    refs = bound_json(manifest["reference_items"], reader)["items"]
    items = {row["record_id"]: row for row in refs}
    need(len(items) == len(refs), "Duplicate reference ID")
    population = validate_population(manifest, items)
    configs = manifest["reported_configurations"]
    need(configs == registry["configurations"], "Registry configuration list differs")
    targets = {}
    for row in terminal_index["targets"]:
        key = target_key(row)
        need(key not in targets, "Duplicate terminal target")
        targets[key] = row
    wanted = {(c["root_label"], c["lane"], a["record_id"]) for c in configs for a in c["calls"] if a["fresh_call_required"]}
    need(set(targets) == wanted, "Terminal index omits or adds required fresh targets")
    resolved = {}; bindings = []; all_units = {}; problems = []; uncalled = []; runtime_bindings = {}; runtimes = {}
    for configuration in configs:
        need(configuration.get("scope", "active_lane") == "active_lane",
             "Joined/lifetime reporting scope needs an explicitly approved response-locator adapter")
        ck = lane_key(configuration["root_label"], configuration["lane"])
        need(ck not in resolved, "Duplicate configuration")
        runtime, runtime_binding = frozen_runtime(configuration, reader)
        runtimes[ck] = runtime; runtime_bindings[ck] = runtime_binding
        rows = {}; units = []
        need(len(configuration["calls"]) == len(items) and {c["record_id"] for c in configuration["calls"]} == set(items),
             "Configuration historical roster differs")
        for call in configuration["calls"]:
            rid = call["record_id"]; roles = population["record_masks"][rid]["roles"]
            need(call["current_roles"] == roles and call["current_benchmark_admitted"] is roles["admitted"], "Call/current mask differs")
            fresh = call["fresh_call_required"]
            expected_operation = "FRESH_RERUN_DIAGNOSTIC_ONLY" if not roles["admitted"] else (
                "FRESH_RERUN_REPLACE_UNCONDITIONALLY" if fresh else "RETAIN_EXACT_HISTORICAL_OUTCOME")
            need(call["operation"] == expected_operation and (roles["admitted"] or fresh), "Invalid replacement disposition")
            record = None; chosen = None; complete = True
            if fresh:
                target = targets[(configuration["root_label"], configuration["lane"], rid)]
                need(target["current_roles"] == roles and target["cost_bucket"] == call["cost_bucket"]
                     and target["split"] == call["split"], "Terminal target role/split differs")
                target_units = receipt_costs(target, registry, registry_descriptor, configuration["freeze_sha256"], runtime, reader)
                for unit in target_units:
                    unit.update(record_id=rid, configuration=ck, split=call["split"], cost_bucket=call["cost_bucket"])
                units.extend(target_units)
                physical_call = target["physical_attempt_count"] > 0
                need(target.get("physical_call_occurred") is physical_call, "Physical-call disclosure differs")
                if not physical_call:
                    uncalled.append({"configuration": ck, "record_id": rid, "state": target["completion_state"]})
                complete = (target["completion_state"] == "TERMINAL" and bool(target["record"]) and bool(target["answer"])
                            and not any(u["orphan"] for u in target_units))
                need(target["complete"] is bool(complete), "Terminal completion contradicts actual receipts")
                need(target["completion_state"] in {"MISSING", "TERMINAL", "ORPHAN_UNRESOLVED"}, "Unknown terminal state")
                if complete:
                    record, chosen = read_chosen(configuration, call, items[rid], target["record"], target["answer"],
                                                 registry, registry_descriptor, runtime, reader, True)
                    attempts = record.get("attempts")
                    need(isinstance(attempts, list) and len(attempts) == len(target_units), "Final attempt list differs from physical receipts")
                    need([vsha(a) for a in attempts] == [vsha(u["attempt"]) for u in target_units],
                         "Final attempts differ from exact receipt attempts")
                    if not physical_call:
                        usage = runtime.usage_summary(record)
                        need(runtime.attempt_class_of(record) == "SETUP_FAILURE" and record.get("valid_protocol") is False and
                             usage["usage_known"] is True and usage["total_attributable_tokens"] == 0 and usage["attempts_count"] == 0,
                             "Zero-dispatch terminal must be an explicit preflight setup failure")
                else:
                    problems.append({"configuration": ck, "record_id": rid, "state": target["completion_state"],
                                     "physical_attempt_count": target["physical_attempt_count"], "fallback_to_history": False})
            else:
                historical = call["historical"]
                need(historical["state"] == "PRESENT", "Unchanged historical result missing")
                record, chosen = read_chosen(configuration, call, items[rid], historical["record"], historical["answer"],
                                             registry, registry_descriptor, runtime, reader, False)
            rows[rid] = {"record": record, "roles": roles, "fresh": fresh, "complete": bool(complete),
                         "diagnostic_only": not roles["admitted"], "binding": chosen}
            bindings.append({"configuration": ck, "root_label": configuration["root_label"], "lane": configuration["lane"],
                             "record_id": rid, "operation": call["operation"], "current_roles": roles,
                             "reference_item_sha256": vsha(items[rid]), "chosen": chosen, "complete": bool(complete),
                             "historical": call["historical"].get("record"), "historical_fallback_used": False})
        resolved[ck] = rows; all_units[ck] = units
    need(terminal_index["complete"] is (not problems), "Overall terminal completeness differs")
    need(terminal_index.get("all_required_physical_calls_complete") is (not problems and not uncalled), "Overall physical-call disclosure differs")
    # Mixed roots must not silently change the statistic/usage/parser protocol.
    need(len({v["scoring_functions_sha256"] for v in runtime_bindings.values()}) == 1, "Cross-root scoring protocol differs")
    need(len({v["parser_functions_sha256"] for v in runtime_bindings.values()}) == 1, "Cross-root parser/usage protocol differs")
    unit_ids = [u["unit_id"] for units in all_units.values() for u in units]
    need(len(set(unit_ids)) == len(unit_ids), "Physical dispatch double counted across targets")
    return {"items": items, "population": population, "resolved": resolved, "bindings": bindings,
            "fresh_cost_units": all_units, "runtimes": runtimes, "runtime_bindings": runtime_bindings,
            "configuration_identifiers": {lane_key(c["root_label"], c["lane"]): {"root_label": c["root_label"], "lane": c["lane"]} for c in configs},
            "complete": not problems, "incomplete_targets": problems,
            "all_required_physical_calls_complete": not problems and not uncalled, "uncalled_targets": uncalled}


def resolve_inputs(registry, registry_descriptor, manifest, terminal_index, reader):
    """Resolve each physical execution once, then project the declared reporting views."""
    import registry as shared_gate
    reporting = manifest["reported_configurations"]
    need(registry.get("reporting_configurations", registry["configurations"]) == reporting, "Registry reporting views differ")
    physical = manifest.get("physical_configurations", reporting)
    need(registry["configurations"] == physical, "Registry physical configurations differ")
    if any(c.get("scope", "active_lane") != "active_lane" for c in reporting):
        need("physical_configurations" in manifest and (manifest.get("physical_reporting_map") or {}).get("policy_state") == "APPROVED_BOUND",
             "Joined/lifetime reporting scope needs an explicitly approved response-locator adapter")
    shared_gate.validate_physical_plan(manifest)
    donor_calls = {(c["root_label"], c["lane"], call["record_id"]): (c, call)
                   for c in physical for call in c["calls"] if call["fresh_call_required"]}
    terminal_targets = {target_key(t): t for t in terminal_index["targets"]}
    for identity, (configuration, call) in donor_calls.items():
        need(identity in terminal_targets, "Terminal index omits or adds a required physical target")
        target = terminal_targets[identity]
        key = dict(zip(("root_label", "lane", "record_id"), identity))
        need(target.get("physical_call_key", key) == key, "Terminal physical alias key differs")
        expected = call.get("reporting_aliases", [key])
        need(target.get("reporting_aliases", [key]) == expected, "Terminal reporting aliases differ")
    physical_manifest = {**manifest, "reported_configurations": physical}
    result = resolve_physical_inputs(registry, registry_descriptor, physical_manifest, terminal_index, reader)
    result["physical_resolved"] = result["resolved"]
    result["physical_configuration_identifiers"] = dict(result["configuration_identifiers"])
    result["joined_required_history"] = {}
    result["reporting_physical_calls"] = {}
    physical_bindings = {(b["root_label"], b["lane"], b["record_id"]): b for b in result["bindings"]}
    views = {}; bindings = []; inventory_seen = {}; parser_cache = {}
    mapping = manifest.get("physical_reporting_map") or {}
    shared_policy = mapping.get("shared_policy")
    if shared_policy:
        for descriptor in [shared_policy["receipt"], shared_policy["equivalence_evidence"], *shared_policy["approval_reports"]]:
            reader(descriptor)
    for configuration in reporting:
        ck = lane_key(configuration["root_label"], configuration["lane"])
        need(ck not in views, "Duplicate reporting view identity")
        runtime, runtime_binding = frozen_runtime(configuration, reader)
        result["runtimes"][ck] = runtime; result["runtime_bindings"][ck] = runtime_binding
        result["configuration_identifiers"][ck] = {"root_label": configuration["root_label"], "lane": configuration["lane"]}
        calls = configuration["calls"]
        need(len(calls) == len(result["items"]) and {a["record_id"] for a in calls} == set(result["items"]), "Reporting roster differs")
        joined = configuration.get("joined_source_policy") if configuration.get("scope") == "lifetime_evaluation" else None
        origin_counts = collections.Counter(); rows = {}; physical_keys = []
        if joined:
            need(joined.get("schema") == "exp5-joined-historical-source-bindings/v1", "Unknown joined-history contract")
            for name in ("policy", "carryover", "decision", "countersign", "historical_activation", "carried_pilot_gate"):
                reader(joined[name])
        for call in calls:
            rid = call["record_id"]; roles = result["population"]["record_masks"][rid]["roles"]
            need(call["current_roles"] == roles and call["current_benchmark_admitted"] is roles["admitted"], "Reporting role/admission differs")
            if call["fresh_call_required"]:
                default = {"root_label": configuration["root_label"], "lane": configuration["lane"], "record_id": rid}
                physical_key = call.get("physical_call_key", default)
                identity = target_key(physical_key)
                donor_config, donor_call = donor_calls[identity]
                need(call["current_roles"] == donor_call["current_roles"] and call["cost_bucket"] == donor_call["cost_bucket"]
                     and call["operation"] == donor_call["operation"] and call["split"] == donor_call["split"],
                     "Shared view changes physical call roles or disposition")
                dk = lane_key(donor_config["root_label"], donor_config["lane"])
                rows[rid] = result["physical_resolved"][dk][rid]
                binding = copy.deepcopy(physical_bindings[identity])
                binding.update(configuration=ck, root_label=configuration["root_label"], lane=configuration["lane"],
                               physical_call_key=physical_key, physical_execution_configuration=dk,
                               shared_physical_result=(configuration["root_label"], configuration["lane"]) != identity[:2],
                               historical=call["historical"].get("record"))
                physical_keys.append(physical_key)
            else:
                need(call.get("physical_call_key") is None, "Unchanged item unexpectedly aliases a fresh call")
                history = call["historical"]
                need(history["state"] == "PRESENT", "Selected unchanged historical result missing")
                expected_freeze = history.get("actual_freeze_sha256", configuration["freeze_sha256"])
                parser_runtime = runtime
                parser_binding = runtime_binding
                if joined:
                    provenance = history.get("parser_provenance") or {}
                    need(provenance.get("freeze_sha256") == expected_freeze and provenance.get("view_parser_equivalent") is True,
                         "Joined historical parser origin missing or mismatched")
                    freeze_record = bound_json(provenance["freeze"], reader)
                    need(freeze_record.get("freeze_sha256") == expected_freeze, "Joined parser freeze identity differs")
                    provenance_key = vsha(provenance)
                    if provenance_key not in parser_cache:
                        parser_cache[provenance_key] = frozen_runtime(provenance, reader)
                    parser_runtime, parser_binding = parser_cache[provenance_key]
                    need(parser_binding["parser_functions_sha256"] == runtime_binding["parser_functions_sha256"] and
                         parser_binding["scoring_functions_sha256"] == runtime_binding["scoring_functions_sha256"],
                         "Joined historical parser/scorer differs from reporting protocol")
                elif ck in result["physical_resolved"]:
                    rows[rid] = result["physical_resolved"][ck][rid]
                if rid not in rows:
                    record, chosen = read_chosen(configuration, call, result["items"][rid], history["record"], history["answer"],
                                                registry, registry_descriptor, parser_runtime, reader, False, expected_freeze)
                    rows[rid] = {"record": record, "roles": roles, "fresh": False, "complete": True,
                                 "diagnostic_only": not roles["admitted"], "binding": chosen}
                binding = {"configuration": ck, "root_label": configuration["root_label"], "lane": configuration["lane"],
                           "record_id": rid, "operation": call["operation"], "current_roles": roles,
                           "reference_item_sha256": vsha(result["items"][rid]), "chosen": rows[rid]["binding"],
                           "complete": rows[rid]["complete"], "historical": history["record"], "physical_call_key": None,
                           "historical_fallback_used": False, "historical_parser_binding": parser_binding}
            binding["reporting_scope"] = configuration.get("scope", "active_lane")
            binding["historical_view_freeze_sha256"] = call["historical"].get("actual_freeze_sha256", configuration["freeze_sha256"])
            if joined:
                origin = call["historical"]["origin"]
                expected_kind = "CONTINUATION_ACTIVE" if origin["continuation_eligible"] else (
                    "CARRIED_PILOT" if call["split"] == "pilot" else "HISTORICAL_EVALUATION")
                need(origin["kind"] == expected_kind and origin["record"] == call["historical"]["record"]
                     and origin["answer"] == call["historical"]["answer"] and origin["split"] == call["split"],
                     "Joined selected origin differs")
                expected = joined["active_freeze_sha256"] if origin["continuation_eligible"] else joined["origin_freeze_sha256"]
                need(origin["freeze_sha256"] == binding["historical_view_freeze_sha256"] == expected, "Joined original freeze incorrectly relabeled")
                need(not origin["continuation_eligible"] or call["split"] == "evaluation", "Continuation cannot replace a pilot")
                origin_counts[origin["kind"]] += 1
                binding["historical_origin"] = origin
            bindings.append(binding)
        result["reporting_physical_calls"][ck] = physical_keys
        if joined:
            need(dict(origin_counts) == joined["origin_counts"], "Joined origin counts differ")
            donor_keys = {lane_key(k["root_label"], k["lane"]) for k in physical_keys}
            need(len(donor_keys) == 1, "Joined view must have one declared physical donor configuration")
            donor_key = next(iter(donor_keys))
            required = result["joined_required_history"].setdefault(donor_key, {})
            inventory = joined["physical_attempt_inventory"]
            need(len(inventory) == joined["physical_attempt_count"], "Joined physical-history count differs")
            need(len({entry["coverage_id"] for entry in inventory}) == len(inventory), "Duplicate joined historical physical identity")
            for entry in inventory:
                coverage = "dispatch:" + entry["ticket_id"]
                need(entry["coverage_id"] == coverage, "Joined cost coverage ID differs from ticket")
                ticket = bound_json(entry["dispatch"], reader)
                need(all(ticket[k] == entry[k] for k in ("ticket_id", "record_id", "split", "freeze_sha256")), "Joined historical physical receipt differs")
                if entry["attempt"]:
                    attempt = bound_json(entry["attempt"], reader)
                    need(attempt["dispatch"] == ticket, "Joined historical attempt/dispatch differs")
                for alias in entry.get("aliases", []):
                    need(reader(alias) == reader(entry["dispatch"]), "Copied historical dispatch alias differs")
                digest = vsha({k: entry[k] for k in ("ticket_id", "record_id", "split", "freeze_sha256")})
                digest += entry["dispatch"]["sha256"] + (entry["attempt"] or {}).get("sha256", "")
                need(coverage not in inventory_seen or inventory_seen[coverage] == digest, "Conflicting historical physical aliases")
                inventory_seen[coverage] = digest; required[coverage] = entry
            for call in calls:
                expected = [entry for entry in inventory if entry["record_id"] == call["record_id"]]
                need(sorted(call["historical"]["physical_attempt_history"], key=lambda e: e["coverage_id"]) ==
                     sorted(expected, key=lambda e: e["coverage_id"]), "Per-item joined physical history differs")
        views[ck] = rows
    result["resolved"] = views; result["bindings"] = bindings
    need(len({v["parser_functions_sha256"] for v in result["runtime_bindings"].values()}) == 1 and
         len({v["scoring_functions_sha256"] for v in result["runtime_bindings"].values()}) == 1,
         "Reporting view parser/statistic protocol differs")
    return result


def add_components(rows):
    return {key: sum(row[key] for row in rows) for key in COMPONENTS}


def historical_components(configuration, report, reader):
    need(report.get("schema") == "corrected-ccl-historical-cost/v1" and report.get("configuration") == configuration,
         "Historical campaign cost report differs")
    need(report.get("no_double_counted_attempts") is True and bool(report.get("census_bindings")), "Historical census missing")
    for descriptor in report["census_bindings"]:
        reader(descriptor)
    coverage = set(); names = set(); components = []
    for unit in report["units"]:
        need(unit["unit_id"] not in names, "Duplicate historical cost unit")
        names.add(unit["unit_id"])
        ids = unit["coverage_ids"]
        need(ids and len(ids) == len(set(ids)) and not coverage.intersection(ids), "Overlapping historical cost coverage")
        coverage.update(ids)
        need(unit["evidence"], "Unbound historical cost unit")
        for descriptor in unit["evidence"]:
            reader(descriptor)
        values = unit["components"]
        need(set(values) == set(COMPONENTS) and all(type(n) is int and n >= 0 for n in values.values()), "Invalid cost components")
        need(values["charged_tokens"] >= max(values["measured_tokens"], values["observed_lower_bound_tokens"]), "Invalid conservative charge")
        need(values["observed_lower_bound_tokens"] >= values["measured_tokens"], "Observed cost omits measured tokens")
        components.append(values)
    total = add_components(components)
    need(total == report["components"], "Historical cost sum differs")
    return total, coverage


def account_costs(resolution, policy, reader):
    result = {}; all_coverage = set()
    physical_rows = resolution.get("physical_resolved", resolution["resolved"])
    need(set(policy["subject"]["configurations"]) == set(physical_rows), "Cost policy physical configuration set differs")
    for ck, rows in physical_rows.items():
        runtime = resolution["runtimes"][ck]
        policy_row = policy["subject"]["configurations"][ck]
        historical, coverage = historical_components(ck, bound_json(policy_row["historical_cost_report"], reader), reader)
        need(historical == policy_row["historical_components"] and policy_row["historical_cost_included_once"] is True,
             "Historical cost differs from approved budget policy")
        required_joined = set(resolution.get("joined_required_history", {}).get(ck, {}))
        need(required_joined <= coverage, "Physical donor campaign inventory omits joined continuation/history spending")
        fresh = resolution["fresh_cost_units"][ck]
        fresh_ids = {u["coverage_id"] for u in fresh}
        need(not coverage.intersection(fresh_ids) and not all_coverage.intersection(coverage | fresh_ids), "Historical/fresh campaign attempt overlap")
        all_coverage |= coverage | fresh_ids
        fresh_total = add_components([u["components"] for u in fresh])
        buckets = {bucket: add_components([u["components"] for u in fresh if u["cost_bucket"] == bucket])
                   for bucket in ("CURRENT_ADMITTED_RERUN", "WITHDRAWN_DIAGNOSTIC_RERUN")}
        need(add_components(list(buckets.values())) == fresh_total, "Unknown fresh cost role")
        subsets = {}
        for name, role in (("current_admitted_all", "admitted"), ("current_admitted_evaluation", "evaluation_population"),
                           ("current_admitted_pilot", "pilot_population"), ("current_primary", "evaluation_primary"),
                           ("current_secondary", "evaluation_scorable")):
            records = [row["record"] for row in rows.values() if row["roles"][role]]
            subsets[name] = {"usage": runtime.aggregate_usage(records), "output_usage": runtime.aggregate_output_usage(records)}
        result[ck] = {"historical_campaign_once": historical, "historical_cost_report": policy_row["historical_cost_report"],
                      "fresh_all_physical_attempts_once": fresh_total, "fresh_by_cost_bucket": buckets,
                      "fresh_by_split": {split: add_components([u["components"] for u in fresh if u["split"] == split])
                                         for split in ("pilot", "evaluation")},
                      "grand_cumulative_campaign": add_components([historical, fresh_total]),
                      "current_selected_cost_views_not_added_again": subsets,
                      "fresh_physical_attempts": len(fresh), "fresh_unresolved_orphans": sum(u["orphan"] for u in fresh),
                      "historical_coverage_ids_sha256": vsha(sorted(coverage)), "fresh_coverage_ids_sha256": vsha(sorted(fresh_ids)),
                      "joined_history_required_coverage_count": len(required_joined),
                      "joined_history_required_coverage_ids_sha256": vsha(sorted(required_joined)),
                      "budget_lane_cap": policy_row["lane_cap"]}
    views = {}
    for ck, rows in resolution["resolved"].items():
        runtime = resolution["runtimes"][ck]
        keys = resolution.get("reporting_physical_calls", {}).get(ck, [])
        identities = {(k["root_label"], k["lane"], k["record_id"]) for k in keys}
        selected_units = [u for dk, units in resolution["fresh_cost_units"].items() for u in units
                          if (resolution["physical_configuration_identifiers"][dk]["root_label"],
                              resolution["physical_configuration_identifiers"][dk]["lane"], u["record_id"]) in identities]
        views[ck] = {"overlapping_reporting_view_not_added_to_campaign_total": True,
                     "referenced_fresh_physical_components": add_components([u["components"] for u in selected_units]),
                     "referenced_fresh_by_cost_bucket": {bucket: add_components([u["components"] for u in selected_units if u["cost_bucket"] == bucket])
                         for bucket in ("CURRENT_ADMITTED_RERUN", "WITHDRAWN_DIAGNOSTIC_RERUN")},
                     "referenced_fresh_coverage_ids_sha256": vsha(sorted(u["coverage_id"] for u in selected_units)),
                     "current_selected_cost_views": {name: {
                         "usage": runtime.aggregate_usage([row["record"] for row in rows.values() if row["roles"][role]]),
                         "output_usage": runtime.aggregate_output_usage([row["record"] for row in rows.values() if row["roles"][role]])}
                         for name, role in (("current_admitted_all", "admitted"), ("current_admitted_evaluation", "evaluation_population"),
                                            ("current_admitted_pilot", "pilot_population"), ("current_primary", "evaluation_primary"),
                                            ("current_secondary", "evaluation_scorable"))}}
    return {"scope": "Historical campaign inventory once plus fresh physical dispatch inventory once. Current selected costs are overlapping views, never added to grand cumulative. Diagnostics are absent from all current metric/cost denominators.",
            "unknown_usage_is_zero": False, "charged_tokens_are_measured_tokens": False, "configurations": result,
            "reporting_views": views,
            "grand_cumulative_all_configurations": add_components([x["grand_cumulative_campaign"] for x in result.values()])}


def statistics(resolution):
    need(resolution["complete"], "Incomplete corrected execution: current aggregates prohibited; no historical fallback")
    need(resolution["all_required_physical_calls_complete"], "Mandatory physical calls missing: final aggregates prohibited")
    runtimes = resolution["runtimes"]
    need(runtimes, "No configurations")
    runtime = runtimes[sorted(runtimes)[0]]
    identities = resolution["configuration_identifiers"]
    lane_counts = collections.Counter(row["lane"] for row in identities.values())
    seed_lanes = {key: row["lane"] if lane_counts[row["lane"]] == 1 else key for key, row in identities.items()}
    result = {}
    for name, group in (("primary_ge10_lines", "evaluation_primary"), ("secondary_scorable", "evaluation_scorable"),
                        ("pilot_scorable", "pilot_scorable")):
        ids = resolution["population"]["record_ids"][group]
        items = [resolution["items"][rid] for rid in ids]
        # Retain original evaluation statistic tags; namespace the separate pilot report.
        tag = "all_items" if name == "secondary_scorable" else name
        pop = {"n_items": len(items), "record_ids_sha256": vsha(ids), "baselines": {}, "critics": {},
               "paired_hit1_differences": {}, "paired_hit3_differences": {}, "paired_cost_differences": {}}
        if not items:
            pop.update(best_baseline=None, empty_population=True)
            result[name] = pop
            continue
        base = [runtime.baselines(item) for item in items]
        for baseline in base[0]:
            values = [row[baseline] for row in base]
            pop["baselines"][baseline] = {"mean": round(sum(values) / len(values), 4),
                                           "ci95": runtime.boot(items, values, tag + baseline)}
        pop["best_baseline"] = max((b for b in base[0] if b != "random_line"), key=lambda b: pop["baselines"][b]["mean"])
        outcomes = {}; per_item_cost = {}
        for ck in sorted(resolution["resolved"]):
            own_runtime = runtimes[ck]
            records = [resolution["resolved"][ck][rid]["record"] for rid in ids]
            need(all(record is not None for record in records), "Current scored record missing")
            outs = [own_runtime.outcome(item, record) for item, record in zip(items, records)]
            critic = own_runtime.summarise(items, outs, base, tag + seed_lanes[ck])
            critic.update(complete=True, records_present=len(records), inference_usage=own_runtime.aggregate_usage(records),
                          output_usage=own_runtime.aggregate_output_usage(records), parser_fallbacks=own_runtime.parser_fallback_report(records))
            costs = [own_runtime.cost_components(own_runtime.aggregate_usage([record])) for record in records]
            per_item_cost[ck] = costs; outcomes[ck] = outs
            critic["cost_components_per_item"] = {component: {"mean": sum(row[component] for row in costs) / len(costs),
                "ci95": runtime.boot(items, [row[component] for row in costs], name + ck + component)} for component in COMPONENTS}
            hit1 = sum(row["hit1"] for row in outs)
            critic["charged_tokens_per_hit1"] = critic["inference_usage"]["budget_charge_tokens"] / hit1 if hit1 else None
            total = critic["inference_usage"]["total_attributable_tokens"]
            critic["known_total_tokens_per_hit1"] = total / hit1 if hit1 and total is not None else None
            pop["critics"][ck] = critic
        keys = sorted(outcomes)
        for i, left in enumerate(keys):
            for right in keys[i + 1:]:
                pair = left + " minus " + right
                for metric in ("hit1", "hit3"):
                    values = [a[metric] - b[metric] for a, b in zip(outcomes[left], outcomes[right])]
                    pop["paired_" + metric + "_differences"][pair] = {"mean": round(sum(values) / len(values), 4),
                        "ci95": runtime.boot(items, values, tag + seed_lanes[left] + seed_lanes[right] + ("" if metric == "hit1" else metric))}
                pop["paired_cost_differences"][pair] = {}
                for component in COMPONENTS:
                    values = [a[component] - b[component] for a, b in zip(per_item_cost[left], per_item_cost[right])]
                    pop["paired_cost_differences"][pair][component] = {"mean": sum(values) / len(values),
                        "ci95": runtime.boot(items, values, name + left + right + component)}
        result[name] = pop
    return {"resamples": 10000, "bootstrap": "Percentile, source-group-stratified merged problem clusters; best deterministic baseline reselected within each replicate.",
            "cost_component_interpretation": "Measured tokens include only known attempts; lower bounds and conservative charges are distinct. Component comparisons never impute missing native usage as measured zero.",
            "populations": result, "seed_lane_identifiers": seed_lanes,
            "historical_human_reference_audit_reused_as_current_validation": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--registry-sha256", required=True)
    parser.add_argument("--terminal-index", required=True)
    parser.add_argument("--terminal-index-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    import registry as gate
    registration, manifest = gate.verify_registry(args.registry, args.registry_sha256)
    registry_descriptor = gate.descriptor(args.registry)
    index_descriptor = gate.descriptor(args.terminal_index)
    need(index_descriptor["sha256"] == args.terminal_index_sha256, "Terminal index hash differs")
    need(gate.path(args.terminal_index) == gate.path(registration["fresh_root"]) / "TERMINALS.json", "Terminal index moved")
    policy = bound_json(registration["policy"], gate.bound)
    self_descriptor = gate.descriptor(__file__)
    need(self_descriptor in registration["runtime_files"], "Scorer code not in approved runtime freeze")
    used_descriptors = {}
    def tracked_reader(descriptor):
        need(descriptor["path"] not in used_descriptors or used_descriptors[descriptor["path"]]["sha256"] == descriptor["sha256"],
             "Conflicting descriptors for one artifact")
        used_descriptors[descriptor["path"]] = descriptor
        return gate.bound(descriptor)
    terminal_index = bound_json(index_descriptor, tracked_reader)
    resolution = resolve_inputs(registration, registry_descriptor, manifest, terminal_index, tracked_reader)
    costs = account_costs(resolution, policy, tracked_reader)
    need(resolution["complete"] and resolution["all_required_physical_calls_complete"],
         "Required corrected physical calls remain incomplete; no results or fallback written")
    metrics = statistics(resolution)
    # Recheck all authorization/runtime bindings after computation and before publication to a new local artifact.
    final_registration, final_manifest = gate.verify_registry(args.registry, args.registry_sha256)
    need(final_registration == registration and final_manifest == manifest, "Runtime/scientific bindings changed during scoring")
    for descriptor in used_descriptors.values():
        gate.bound(descriptor)
    destination = gate.path(args.output)
    need(destination.is_relative_to(gate.path(registration["fresh_root"])) and not destination.exists(), "Results output must be a new path inside fresh root")
    result = {"schema": SCHEMA, "status": "COMPLETE_APPROVED_CORRECTION_RESULTS", "registry": registry_descriptor,
              "terminal_index": index_descriptor, "manifest": registration["manifest"], "reference_items": manifest["reference_items"],
              "scorer": self_descriptor, "runtime_bindings": resolution["runtime_bindings"],
              "population_definition": resolution["population"], "resolved_inputs": resolution["bindings"],
              "cost_accounting": costs, "statistics": metrics, "all_corrected_required_calls_terminal": True,
              "all_required_physical_calls_complete": True,
              "historical_fallback_used": False, "model_calls_performed": 0}
    gate.write_new(destination, result)
    print(json.dumps(gate.descriptor(destination), sort_keys=True))


if __name__ == "__main__":
    main()
