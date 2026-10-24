"""Synthetic response fixtures only; no production results or approval created."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
spec = importlib.util.spec_from_file_location("corrected_score_under_test", HERE / "resolve_and_score_corrected.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
DESIGNS = [
    "designs/v4",
    "designs/v5",
]


class Fixture:
    def __init__(self, local=False, configurations=2, joined=False):
        self.files = {}
        self.items = [{"record_id": rid, "split": "pilot" if rid.startswith("P") else "evaluation",
                       "lines": [[i, "line " + str(i)] for i in range(1, 11)], "gold": [2],
                       "unscorable": False, "n_nonblank_text": 10, "exclude_from_primary": False,
                       "group": "example", "cluster_merged": rid}
                      for rid in ["A", "B", "C"] + ["P" + str(i) for i in range(20)]]
        self.population = self.make_population()
        self.manifest = {"current_population_definition": self.population, "population_definition_state": "ALL_GATES_APPROVED",
                         "reference_items": self.put("synthetic/reference.json", {"items": self.items}), "reported_configurations": []}
        for n in range(configurations):
            design = DESIGNS[n % len(DESIGNS)]
            lane = "local_mock" if local and n == 1 else "mock" + str(n)
            cfg = {"root_label": "EXP" + str(n + 1), "lane": lane, "runner": "run_local.py" if lane.startswith("local") else "run_critic.py",
                   "freeze_sha256": "frozen" + str(n), "calls": [], "frozen_design_files": []}
            cfg["scope"] = "active_lane"
            cfg["configuration_id"] = cfg["root_label"] + "/" + lane + "/active_lane"
            cfg["freeze"] = self.put("synthetic/" + cfg["root_label"] + "/FREEZE.json", {"fixture_freeze": n, "freeze_sha256": cfg["freeze_sha256"]})
            for name in ("common.py", "score.py"):
                path = design + "/" + name
                cfg["frozen_design_files"].append(self.put(path, (REPO / path).read_bytes()))
            runtime, _ = s.frozen_runtime(cfg, self.read)
            for item in self.items:
                rid = item["record_id"]
                record, answer = self.record(cfg, item, runtime, fresh=False)
                prefix = "synthetic/history/" + cfg["root_label"] + "/" + rid
                rd = self.put(prefix + "/record.json", record); ad = self.put(prefix + "/answer.txt", answer.encode())
                roles = self.population["record_masks"][rid]["roles"]
                fresh = rid in {"A", "C"}
                cfg["calls"].append({"record_id": rid, "split": item["split"], "fresh_call_required": fresh,
                    "current_roles": roles, "current_benchmark_admitted": roles["admitted"],
                    "operation": "FRESH_RERUN_DIAGNOSTIC_ONLY" if rid == "C" else "FRESH_RERUN_REPLACE_UNCONDITIONALLY" if fresh else "RETAIN_EXACT_HISTORICAL_OUTCOME",
                    "cost_bucket": "WITHDRAWN_DIAGNOSTIC_RERUN" if rid == "C" else "CURRENT_ADMITTED_RERUN" if fresh else "NO_FRESH_CALL",
                    "new_user_prompt_sha256": "prompt", "new_system_prompt_sha256": "system", "new_agy_stdin_sha256": None,
                    "new_logical_messages_sha256": "messages", "new_request_surface_sha256": "surface",
                    "historical": {"state": "PRESENT", "record": rd, "answer": ad, "settings": {"effort": "medium"}}})
            self.manifest["reported_configurations"].append(cfg)
        self.physical = list(self.manifest["reported_configurations"])
        if joined:
            self.add_joined_view()
        historical_policies = {}
        for cfg in self.physical:
            ck = s.lane_key(cfg["root_label"], cfg["lane"])
            evidence = self.put("synthetic/cost/" + ck + "/census.json", {"fixture_only": True})
            comps = dict(zip(s.COMPONENTS, [230, 0, 230, 230]))
            cost = {"schema": "corrected-ccl-historical-cost/v1", "configuration": ck, "no_double_counted_attempts": True,
                    "census_bindings": [evidence], "units": [{"unit_id": ck + "old", "coverage_ids": [ck + "old" + i["record_id"] for i in self.items],
                    "components": comps, "evidence": [evidence]}], "components": comps}
            if joined and cfg is self.physical[0]:
                inventory = self.joined["joined_source_policy"]["physical_attempt_inventory"]
                old = [e for e in inventory if e["freeze_sha256"] == cfg["freeze_sha256"]]
                active = [e for e in inventory if e["freeze_sha256"] != cfg["freeze_sha256"]]
                cost["units"][0]["coverage_ids"] = [e["coverage_id"] for e in old]
                extra = dict(zip(s.COMPONENTS, [30, 0, 30, 30]))
                cost["units"].append({"unit_id": ck + "continuation", "coverage_ids": [e["coverage_id"] for e in active],
                                      "components": extra, "evidence": [e["attempt"] for e in active]})
                comps = s.add_components([comps, extra]); cost["components"] = comps
            historical_policies[ck] = {"historical_cost_report": self.put("synthetic/cost/" + ck + "/cost.json", cost),
                                      "historical_components": comps, "historical_cost_included_once": True, "lane_cap": 1000000}
        self.policy = {"subject": {"configurations": historical_policies}}
        self.registry = {"manifest": self.put("synthetic/manifest.json", self.manifest),
                         "policy": self.put("synthetic/policy.json", self.policy), "epoch_id": "correction-fixture-only",
                         "fresh_root": "synthetic/fresh", "configurations": self.physical,
                         "reporting_configurations": self.manifest["reported_configurations"]}
        self.rd = self.put("synthetic/fresh/RUN_REGISTRY.json", self.registry)
        self.terminal = {"schema": "corrected-ccl-terminal-index/v1", "registry": self.rd, "manifest": self.registry["manifest"],
                         "epoch_id": self.registry["epoch_id"], "complete": True, "all_required_physical_calls_complete": True, "targets": []}
        for cfg in self.registry["configurations"]:
            runtime, _ = s.frozen_runtime(cfg, self.read)
            for call in cfg["calls"]:
                if not call["fresh_call_required"]:
                    continue
                item = next(i for i in self.items if i["record_id"] == call["record_id"])
                rid = item["record_id"]; prefix = "synthetic/fresh/configurations/" + s.lane_key(cfg["root_label"], cfg["lane"]) + "/runs/" + cfg["lane"] + "/" + rid
                record, answer = self.record(cfg, item, runtime, fresh=True)
                ticket = {"ticket_id": cfg["root_label"] + rid, "record_id": rid, "split": item["split"], "tag": "a1",
                          "reservation_tokens": 40000, "freeze_sha256": cfg["freeze_sha256"], "root_label": cfg["root_label"],
                          "requested_model": cfg["lane"], "dispatched_time_ns": 1,
                          **self.stamps()}
                attempt = record["attempts"][0]
                dispatch = self.put(prefix + "/DISPATCH_a1.json", ticket)
                receipt = self.put(prefix + "/ATTEMPT_a1.json", {"dispatch": ticket, "attempt": attempt,
                                   "accounting": runtime.usage_summary({"attempts": [attempt]})})
                self.terminal["targets"].append({"root_label": cfg["root_label"], "lane": cfg["lane"], "record_id": rid,
                    "split": item["split"], "current_roles": call["current_roles"], "cost_bucket": call["cost_bucket"],
                    "completion_state": "TERMINAL", "complete": True, "physical_attempt_count": 1,
                    "physical_call_occurred": True,
                    "record": self.put(prefix + "/record.json", record), "answer": self.put(prefix + "/answer.txt", answer.encode()),
                    "dispatch_receipts": [dispatch], "attempt_receipts": [receipt]})
                if joined:
                    self.terminal["targets"][-1].update(physical_call_key=call["physical_call_key"],
                                                        reporting_aliases=call["reporting_aliases"])

    def add_joined_view(self):
        """Synthetic one-continuation / twenty-carried-pilot source join, no real approval."""
        donor = self.physical[0]
        view = copy.deepcopy(donor)
        view.update(root_label="EXP5", scope="lifetime_evaluation", configuration_id="EXP5/" + donor["lane"] + "/lifetime_evaluation")
        view["freeze_sha256"] = "fixture-continuation-freeze"
        view["freeze"] = self.put("synthetic/EXP5/FREEZE.json", {"fixture_continuation": True, "freeze_sha256": view["freeze_sha256"]})
        inventory = []
        for cfg, call in [(donor, c) for c in donor["calls"]] + [(view, next(c for c in view["calls"] if c["record_id"] == "B"))]:
            rid = call["record_id"]; ticket_id = cfg["root_label"] + "old" + rid
            ticket = {"ticket_id": ticket_id, "record_id": rid, "split": call["split"], "freeze_sha256": cfg["freeze_sha256"]}
            prefix = "synthetic/oldreceipts/" + ticket_id
            inventory.append({**ticket, "coverage_id": "dispatch:" + ticket_id,
                "dispatch": self.put(prefix + "/DISPATCH_a1.json", ticket),
                "attempt": self.put(prefix + "/ATTEMPT_a1.json", {"dispatch": ticket, "attempt": {"fixture_only": True}}), "aliases": []})
        runtime, _ = s.frozen_runtime(view, self.read)
        for call in view["calls"]:
            rid = call["record_id"]; history = call["historical"]; active = rid == "B"
            origin_cfg = view if active else donor
            if active:
                item = next(i for i in self.items if i["record_id"] == rid)
                record, _ = self.record(view, item, runtime, fresh=False)
                answer = '{"candidates":[3]}'
                record.update(answer_sha256=s.sha(answer.encode()), candidates=[3], candidate_parse=runtime.parse_candidates_audit(answer, item))
                record["attempts"][0]["usage"]["total_attributable_tokens"] = 30
                history["record"] = self.put("synthetic/EXP5/history/B/record.json", record)
                history["answer"] = self.put("synthetic/EXP5/history/B/answer.txt", answer.encode())
            history["actual_freeze_sha256"] = origin_cfg["freeze_sha256"]
            history["parser_provenance"] = {k: copy.deepcopy(origin_cfg[k]) for k in ("configuration_id", "freeze", "freeze_sha256", "frozen_design_files")}
            history["parser_provenance"]["view_parser_equivalent"] = True
            history["origin"] = {"record": history["record"], "answer": history["answer"], "split": call["split"],
                "freeze_sha256": origin_cfg["freeze_sha256"], "continuation_eligible": active,
                "kind": "CONTINUATION_ACTIVE" if active else "CARRIED_PILOT" if call["split"] == "pilot" else "HISTORICAL_EVALUATION"}
            history["physical_attempt_history"] = [e for e in inventory if e["record_id"] == rid]
            if call["fresh_call_required"]:
                call["execution_equivalence"] = {"approval_bound": True, "actual_settings_equal": True,
                    "native_cli_version": "2.1.275", "donor_configuration_id": donor["configuration_id"], "execution_contract_sha256": "a" * 64}
        stub = self.put("synthetic/join-policy-fixture.json", {"fixture_only_not_an_approval": True})
        view["joined_source_policy"] = {"schema": "exp5-joined-historical-source-bindings/v1",
            **{k: stub for k in ("policy", "carryover", "decision", "countersign", "historical_activation", "carried_pilot_gate")},
            "origin_freeze_sha256": donor["freeze_sha256"], "active_freeze_sha256": view["freeze_sha256"],
            "origin_counts": {"CONTINUATION_ACTIVE": 1, "HISTORICAL_EVALUATION": 2, "CARRIED_PILOT": 20},
            "physical_attempt_inventory": inventory, "physical_attempt_count": len(inventory)}
        self.manifest["reported_configurations"].append(view)
        self.manifest["physical_configurations"] = self.physical
        self.manifest["physical_reporting_map"] = {"policy_state": "APPROVED_BOUND",
            "shared_policy": {"receipt": stub, "equivalence_evidence": stub, "approval_reports": [stub]}}
        for cfg in self.manifest["reported_configurations"]:
            for call in cfg["calls"]:
                if call["fresh_call_required"]:
                    call["physical_call_key"] = {"root_label": donor["root_label"] if cfg is view else cfg["root_label"],
                                                 "lane": cfg["lane"], "record_id": call["record_id"]}
                else:
                    call["physical_call_key"] = None
        for cfg in self.physical:
            for call in cfg["calls"]:
                if call["fresh_call_required"]:
                    call["reporting_aliases"] = [{"root_label": report["root_label"], "lane": report["lane"], "scope": report["scope"],
                        "configuration_id": report["configuration_id"], "record_id": other["record_id"]}
                        for report in self.manifest["reported_configurations"] for other in report["calls"]
                        if other.get("physical_call_key") == call["physical_call_key"]]
        self.joined = view

    def stamps(self):
        return {"correction_registry_sha256": self.rd["sha256"], "correction_manifest_sha256": self.registry["manifest"]["sha256"],
                "correction_epoch_id": self.registry["epoch_id"], "attempt_epoch_id": self.registry["epoch_id"],
                "attempt_epoch_policy_sha256": self.registry["policy"]["sha256"]}

    def record(self, cfg, item, runtime, fresh):
        answer = '{"candidates":[2]}'
        if cfg["runner"] == "run_local.py":
            answer = '{"candidates":[1]}</think>' + answer
        audit = runtime.parse_candidates_audit(answer.split("</think>")[-1], item)
        cls = "TRANSPORT_FAILURE" if fresh and item["record_id"] == "A" else "VALID_ANSWER"
        attempt = {"attempt_class": cls, "valid_protocol": cls == "VALID_ANSWER", "usage_known": True,
                   "usage": {"total_attributable_tokens": 20 if fresh else 10, "output_tokens": 4}}
        if fresh:
            attempt.update(self.stamps())
        record = {"record_id": item["record_id"], "split": item["split"], "freeze_sha256": cfg["freeze_sha256"],
                  "requested_model": cfg["lane"],
                  "prompt_sha256": "prompt", "effort": "medium", "answer_sha256": s.sha(answer.encode()),
                  "attempt_class": cls, "valid_protocol": cls == "VALID_ANSWER", "attempts": [attempt],
                  "candidates": audit["candidates"], "candidate_parse": audit}
        if fresh:
            record.update(self.stamps())
            record["current_roles"] = self.population["record_masks"][item["record_id"]]["roles"]
            record["cost_bucket"] = "WITHDRAWN_DIAGNOSTIC_RERUN" if item["record_id"] == "C" else "CURRENT_ADMITTED_RERUN"
        return record, answer

    def make_population(self):
        masks = {}
        for item in self.items:
            rid = item["record_id"]; admitted = rid != "C"; pilot = item["split"] == "pilot"
            roles = {"admitted": admitted, "withdrawn_diagnostic_only": not admitted, "split": item["split"], "unscorable": False,
                     "evaluation_population": admitted and not pilot, "pilot_population": admitted and pilot,
                     "evaluation_scorable": admitted and not pilot, "pilot_scorable": admitted and pilot,
                     "evaluation_primary": admitted and not pilot}
            masks[rid] = {"roles": roles, "release_status": "RETAINED" if admitted else "EXCLUDED"}
        groups = {k: sorted(rid for rid, row in masks.items() if row["roles"][role]) for k, role in {
            "admitted": "admitted", "withdrawn_diagnostic": "withdrawn_diagnostic_only", "evaluation_population": "evaluation_population",
            "pilot_population": "pilot_population", "evaluation_primary": "evaluation_primary", "evaluation_scorable": "evaluation_scorable",
            "pilot_scorable": "pilot_scorable"}.items()}
        return {"historical_record_ids": sorted(masks), "historical_record_ids_sha256": s.vsha(sorted(masks)),
                "record_masks": masks, "record_masks_sha256": s.vsha(masks), "record_ids": groups,
                "record_ids_sha256": {k: s.vsha(v) for k, v in groups.items()}, "counts": {k: len(v) for k, v in groups.items()}}

    def put(self, path, value):
        raw = value if isinstance(value, bytes) else s.canonical(value)
        self.files[path] = raw
        return {"path": path, "sha256": s.sha(raw), "bytes": len(raw)}

    def read(self, descriptor):
        raw = self.files[descriptor["path"]]
        s.need(s.sha(raw) == descriptor["sha256"] and len(raw) == descriptor.get("bytes", len(raw)), "fixture hash drift")
        return raw

    def replace(self, descriptor, value):
        descriptor.update(self.put(descriptor["path"], value))

    def resolve(self):
        return s.resolve_inputs(self.registry, self.rd, self.manifest, self.terminal, self.read)

    def update_masks(self):
        for item in self.items:
            rid = item["record_id"]; roles = self.population["record_masks"][rid]["roles"]
            roles["unscorable"] = bool(item.get("unscorable"))
            roles["evaluation_scorable"] = roles["evaluation_population"] and not roles["unscorable"]
            roles["pilot_scorable"] = roles["pilot_population"] and not roles["unscorable"]
            roles["evaluation_primary"] = roles["evaluation_scorable"] and not item.get("exclude_from_primary")
        self.population["record_masks_sha256"] = s.vsha(self.population["record_masks"])
        for group in ["evaluation_scorable", "pilot_scorable", "evaluation_primary"]:
            ids = sorted(rid for rid, row in self.population["record_masks"].items() if row["roles"][group])
            self.population["record_ids"][group] = ids; self.population["record_ids_sha256"][group] = s.vsha(ids)
            self.population["counts"][group] = len(ids)
        self.manifest["reference_items"] = self.put("synthetic/reference.json", {"items": self.items})
        # Build a consistent synthetic predeclared-reference variant, never modify a real run.
        for target in self.terminal["targets"]:
            record = json.loads(self.read(target["record"]))
            record["current_roles"] = self.population["record_masks"][target["record_id"]]["roles"]
            self.replace(target["record"], record)


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def test_failure_replaces_old_success_and_retains_twenty_pilots(self):
        r = self.f.resolve()
        self.assertTrue(r["complete"])
        for ck, rows in r["resolved"].items():
            self.assertEqual(r["runtimes"][ck].outcome(r["items"]["A"], rows["A"]["record"])["cause"], "transport_failure")
            self.assertEqual(len(r["population"]["record_ids"]["pilot_population"]), 20)
            self.assertTrue(rows["C"]["diagnostic_only"])

    def test_complete_statistics_and_costs_exclude_diagnostic(self):
        r = self.f.resolve(); metrics = s.statistics(r); costs = s.account_costs(r, self.f.policy, self.f.read)
        primary = metrics["populations"]["primary_ge10_lines"]
        self.assertEqual(primary["n_items"], 2)
        self.assertEqual(len(primary["baselines"]), 5)
        self.assertEqual(len(primary["paired_hit1_differences"]), 1)
        self.assertEqual(len(primary["paired_hit3_differences"]), 1)
        self.assertEqual(len(primary["paired_cost_differences"]), 1)
        for critic in primary["critics"].values():
            self.assertEqual(critic["hit1"]["mean"], .5)
            self.assertEqual(critic["rule_misses_by_cause"], {"transport_failure": 1})
        for cfg in costs["configurations"].values():
            self.assertEqual(cfg["fresh_all_physical_attempts_once"]["charged_tokens"], 40)
            self.assertEqual(cfg["fresh_by_cost_bucket"]["WITHDRAWN_DIAGNOSTIC_RERUN"]["charged_tokens"], 20)
            self.assertEqual(cfg["grand_cumulative_campaign"]["charged_tokens"], 270)
            self.assertEqual(cfg["current_selected_cost_views_not_added_again"]["current_admitted_evaluation"]["usage"]["budget_charge_tokens"], 30)

    def test_missing_fresh_never_falls_back_or_scores(self):
        t = self.f.terminal["targets"][0]
        t.update(completion_state="MISSING", complete=False, physical_attempt_count=0, record=None, answer=None,
                 dispatch_receipts=[], attempt_receipts=[], physical_call_occurred=False)
        self.f.terminal["complete"] = False
        self.f.terminal["all_required_physical_calls_complete"] = False
        r = self.f.resolve()
        self.assertIsNone(r["resolved"]["EXP1__mock0"]["A"]["record"])
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            s.statistics(r)

    def test_orphan_charge_once_and_no_metrics(self):
        t = self.f.terminal["targets"][0]
        t.update(completion_state="ORPHAN_UNRESOLVED", complete=False, record=None, answer=None, attempt_receipts=[])
        self.f.terminal["complete"] = False
        self.f.terminal["all_required_physical_calls_complete"] = False
        r = self.f.resolve(); cost = s.account_costs(r, self.f.policy, self.f.read)["configurations"]["EXP1__mock0"]
        self.assertEqual(cost["fresh_all_physical_attempts_once"]["charged_tokens"], 40020)
        self.assertEqual(cost["fresh_unresolved_orphans"], 1)
        self.assertFalse(r["all_required_physical_calls_complete"])

    def test_duplicate_target_rejected(self):
        self.f.terminal["targets"].append(copy.deepcopy(self.f.terminal["targets"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate terminal"):
            self.f.resolve()

    def test_omitted_diagnostic_target_rejected(self):
        self.f.terminal["targets"].pop()
        with self.assertRaisesRegex(ValueError, "omits or adds"):
            self.f.resolve()

    def test_duplicate_dispatch_rejected(self):
        t = self.f.terminal["targets"][0]
        t["dispatch_receipts"].append(t["dispatch_receipts"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate dispatch"):
            self.f.resolve()

    def test_fresh_record_wrong_freeze_rejected(self):
        d = self.f.terminal["targets"][0]["record"]; row = json.loads(self.f.read(d)); row["freeze_sha256"] = "other"
        self.f.replace(d, row)
        with self.assertRaisesRegex(ValueError, "freeze differs"):
            self.f.resolve()

    def test_record_usage_cannot_replace_receipt_usage(self):
        d = self.f.terminal["targets"][0]["record"]; row = json.loads(self.f.read(d)); row["attempts"][0]["usage"]["total_attributable_tokens"] = 1
        self.f.replace(d, row)
        with self.assertRaisesRegex(ValueError, "exact receipt"):
            self.f.resolve()

    def test_receipt_accounting_drift_rejected(self):
        d = self.f.terminal["targets"][0]["attempt_receipts"][0]; row = json.loads(self.f.read(d)); row["accounting"]["budget_charge_tokens"] = 1
        self.f.replace(d, row)
        with self.assertRaisesRegex(ValueError, "accounting differs"):
            self.f.resolve()

    def test_candidate_success_cannot_override_failure_or_parser(self):
        d = self.f.terminal["targets"][0]["record"]; row = json.loads(self.f.read(d)); row["candidates"] = [1]
        self.f.replace(d, row)
        with self.assertRaisesRegex(ValueError, "parser replay"):
            self.f.resolve()

    def test_local_visible_answer_convention(self):
        f = Fixture(local=True); r = f.resolve()
        self.assertEqual(r["resolved"]["EXP2__local_mock"]["B"]["record"]["candidates"], [2])

    def test_historical_cost_aggregate_child_overlap_rejected(self):
        d = self.f.policy["subject"]["configurations"]["EXP1__mock0"]["historical_cost_report"]
        cost = json.loads(self.f.read(d)); extra = copy.deepcopy(cost["units"][0]); extra["unit_id"] += "child"; cost["units"].append(extra)
        self.f.replace(d, cost)
        with self.assertRaisesRegex(ValueError, "Overlapping historical"):
            s.account_costs(self.f.resolve(), self.f.policy, self.f.read)

    def test_current_mask_cannot_re_admit_diagnostic(self):
        self.f.manifest["current_population_definition"]["record_masks"]["C"]["roles"]["admitted"] = True
        with self.assertRaisesRegex(ValueError, "mask hash"):
            self.f.resolve()

    def test_unknown_frozen_scorer_interface_rejected(self):
        cfg = self.f.registry["configurations"][0]
        descriptor = next(d for d in cfg["frozen_design_files"] if d["path"].endswith("score.py"))
        self.f.replace(descriptor, b"# missing pure functions\n")
        with self.assertRaisesRegex(ValueError, "interface changed"):
            self.f.resolve()

    def test_setup_terminal_is_accounted_but_physical_calls_remain_incomplete(self):
        t = self.f.terminal["targets"][0]
        t.update(complete=True, physical_attempt_count=0, dispatch_receipts=[], attempt_receipts=[], physical_call_occurred=False)
        self.f.terminal["all_required_physical_calls_complete"] = False
        record = json.loads(self.f.read(t["record"]))
        record.update(attempt_class="SETUP_FAILURE", valid_protocol=False, attempts=[], usage_origin="preflight_no_inference",
                      usage_known=True, total_attributable_tokens=0)
        self.f.replace(t["record"], record)
        r = self.f.resolve()
        self.assertTrue(r["complete"])
        self.assertFalse(r["all_required_physical_calls_complete"])
        with self.assertRaisesRegex(ValueError, "physical calls missing"):
            s.statistics(r)

    def test_fresh_output_outside_registered_root_rejected(self):
        t = self.f.terminal["targets"][0]
        t["record"] = self.f.registry["configurations"][0]["calls"][0]["historical"]["record"]
        with self.assertRaisesRegex(ValueError, "escapes correction"):
            self.f.resolve()

    def test_reference_gold_must_name_existing_nonblank_line(self):
        self.f.items[0]["gold"] = [999]
        self.f.manifest["reference_items"] = self.f.put("synthetic/reference.json", {"items": self.f.items})
        with self.assertRaisesRegex(ValueError, "gold/scorability"):
            self.f.resolve()

    def test_new_unscorable_reference_uses_current_mask_without_legacy_flag_change(self):
        self.f.items[0].update(gold=[], unscorable=True)
        self.f.update_masks()
        r = self.f.resolve()
        self.assertEqual(r["population"]["record_ids"]["evaluation_primary"], ["B"])
        self.assertFalse(r["items"]["A"]["exclude_from_primary"])
        self.assertIsNotNone(r["resolved"]["EXP1__mock0"]["A"]["record"])
        self.assertEqual(len(r["fresh_cost_units"]["EXP1__mock0"]), 2)

    def test_unknown_native_usage_stays_unknown_and_charged_once(self):
        target = self.f.terminal["targets"][0]; descriptor = target["attempt_receipts"][0]
        receipt = json.loads(self.f.read(descriptor)); attempt = receipt["attempt"]
        attempt.update(usage_known=False, budget_charge_tokens=50000)
        attempt["usage"].update(total_attributable_tokens=None, observed_lower_bound=7, output_tokens=None)
        cfg = self.f.registry["configurations"][0]; runtime, _ = s.frozen_runtime(cfg, self.f.read)
        receipt["accounting"] = runtime.usage_summary({"attempts": [attempt]})
        self.f.replace(descriptor, receipt)
        record = json.loads(self.f.read(target["record"])); record["attempts"] = [attempt]; self.f.replace(target["record"], record)
        r = self.f.resolve(); cost = s.account_costs(r, self.f.policy, self.f.read)["configurations"]["EXP1__mock0"]
        self.assertEqual(cost["fresh_all_physical_attempts_once"], dict(zip(s.COMPONENTS, [20, 1, 27, 50020])))
        usage = cost["current_selected_cost_views_not_added_again"]["current_admitted_evaluation"]["usage"]
        self.assertIsNone(usage["total_attributable_tokens"])
        self.assertEqual(usage["known_attributable_tokens"], 10)

    def test_ten_configurations_are_dynamic(self):
        r = Fixture(configurations=10).resolve()
        self.assertEqual(len(r["resolved"]), 10)
        self.assertEqual(len(r["bindings"]), 230)

    def test_historical_record_hash_drift_is_not_repaired_by_scan(self):
        d = self.f.registry["configurations"][0]["calls"][1]["historical"]["record"]
        self.f.files[d["path"]] += b" "
        with self.assertRaisesRegex(ValueError, "hash drift"):
            self.f.resolve()

    def test_empty_primary_population_is_explicit(self):
        for item in self.f.items:
            if item["split"] == "evaluation":
                item["exclude_from_primary"] = True
        self.f.update_masks()
        primary = s.statistics(self.f.resolve())["populations"]["primary_ge10_lines"]
        self.assertTrue(primary["empty_population"])
        self.assertEqual(primary["n_items"], 0)
        self.assertIsNone(primary["best_baseline"])

    def test_actual_terminal_index_producer_with_synthetic_receipts(self):
        import dispatch_corrected
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            for name, raw in self.f.files.items():
                path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            index = dispatch_corrected.terminal_index(self.f.registry, self.f.rd, repo)
            result = s.resolve_inputs(self.f.registry, self.f.rd, self.f.manifest, index, self.f.read)
        self.assertTrue(result["complete"])
        self.assertTrue(result["all_required_physical_calls_complete"])

    def test_actual_terminal_index_orphan_preserves_incomplete_cost_ledger(self):
        import dispatch_corrected
        target = self.f.terminal["targets"][0]
        for descriptor in [target["record"], target["answer"], *target["attempt_receipts"]]:
            del self.f.files[descriptor["path"]]
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            for name, raw in self.f.files.items():
                path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            index = dispatch_corrected.terminal_index(self.f.registry, self.f.rd, repo)
            self.assertTrue(all(t["physical_call_occurred"] for t in index["targets"]))
            self.assertFalse(index["complete"])
            self.assertFalse(index["all_required_physical_calls_complete"])
            result = s.resolve_inputs(self.f.registry, self.f.rd, self.f.manifest, index, self.f.read)
        self.assertFalse(result["complete"])
        self.assertFalse(result["all_required_physical_calls_complete"])
        self.assertEqual(result["uncalled_targets"], [])
        costs = s.account_costs(result, self.f.policy, self.f.read)["configurations"]["EXP1__mock0"]
        self.assertEqual(costs["fresh_unresolved_orphans"], 1)
        self.assertEqual(costs["fresh_all_physical_attempts_once"]["charged_tokens"], 40020)
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            s.statistics(result)

    def test_future_lifetime_scope_fails_closed(self):
        self.f.registry["configurations"][0]["scope"] = "lifetime_evaluation"
        with self.assertRaisesRegex(ValueError, "locator adapter"):
            self.f.resolve()

    def test_fresh_effort_cannot_change_frozen_configuration(self):
        descriptor = self.f.terminal["targets"][0]["record"]
        row = json.loads(self.f.read(descriptor)); row["effort"] = "high"
        self.f.replace(descriptor, row)
        with self.assertRaisesRegex(ValueError, "configuration setting"):
            self.f.resolve()

    def test_record_cannot_relabel_diagnostic_as_admitted(self):
        descriptor = self.f.terminal["targets"][1]["record"]
        row = json.loads(self.f.read(descriptor)); row["cost_bucket"] = "CURRENT_ADMITTED_RERUN"
        self.f.replace(descriptor, row)
        with self.assertRaisesRegex(ValueError, "admission/cost role"):
            self.f.resolve()

    def test_historical_inventory_cannot_also_cover_fresh_ticket(self):
        policy = self.f.policy["subject"]["configurations"]["EXP1__mock0"]
        descriptor = policy["historical_cost_report"]; cost = json.loads(self.f.read(descriptor))
        cost["units"][0]["coverage_ids"].append("dispatch:EXP1A")
        self.f.replace(descriptor, cost)
        with self.assertRaisesRegex(ValueError, "campaign attempt overlap"):
            s.account_costs(self.f.resolve(), self.f.policy, self.f.read)


class SharedViewTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture(joined=True)

    def test_shared_failure_replaces_both_views_without_relabeling_freeze(self):
        r = self.f.resolve()
        original = r["resolved"]["EXP1__mock0"]; joined = r["resolved"]["EXP5__mock0"]
        self.assertIs(original["A"]["record"], joined["A"]["record"])
        self.assertEqual(joined["A"]["record"]["attempt_class"], "TRANSPORT_FAILURE")
        self.assertEqual(joined["A"]["record"]["freeze_sha256"], self.f.physical[0]["freeze_sha256"])
        self.assertNotEqual(joined["A"]["record"]["freeze_sha256"], self.f.joined["freeze_sha256"])
        self.assertEqual(original["B"]["record"]["candidates"], [2])
        self.assertEqual(joined["B"]["record"]["candidates"], [3])
        self.assertEqual(joined["B"]["record"]["freeze_sha256"], self.f.joined["freeze_sha256"])
        self.assertEqual(joined["P0"]["record"]["freeze_sha256"], self.f.physical[0]["freeze_sha256"])
        self.assertEqual(len(r["fresh_cost_units"]["EXP1__mock0"]), 2)
        self.assertTrue(joined["C"]["diagnostic_only"])
        self.assertTrue(r["complete"] and r["all_required_physical_calls_complete"])

    def test_campaign_union_charged_once_and_view_costs_explicitly_overlap(self):
        r = self.f.resolve(); c = s.account_costs(r, self.f.policy, self.f.read)
        self.assertEqual(set(c["configurations"]), {"EXP1__mock0", "EXP2__mock1"})
        self.assertEqual(set(c["reporting_views"]), {"EXP1__mock0", "EXP2__mock1", "EXP5__mock0"})
        self.assertEqual(c["configurations"]["EXP1__mock0"]["historical_campaign_once"]["charged_tokens"], 260)
        self.assertEqual(c["configurations"]["EXP1__mock0"]["joined_history_required_coverage_count"], 24)
        self.assertEqual(c["grand_cumulative_all_configurations"]["charged_tokens"], 570)
        for key in ("EXP1__mock0", "EXP5__mock0"):
            view = c["reporting_views"][key]
            self.assertTrue(view["overlapping_reporting_view_not_added_to_campaign_total"])
            self.assertEqual(view["referenced_fresh_physical_components"]["charged_tokens"], 40)
            self.assertEqual(view["referenced_fresh_by_cost_bucket"]["WITHDRAWN_DIAGNOSTIC_RERUN"]["charged_tokens"], 20)
        self.assertEqual(c["reporting_views"]["EXP1__mock0"]["current_selected_cost_views"]["current_admitted_evaluation"]["usage"]["budget_charge_tokens"], 30)
        self.assertEqual(c["reporting_views"]["EXP5__mock0"]["current_selected_cost_views"]["current_admitted_evaluation"]["usage"]["budget_charge_tokens"], 50)

    def test_shared_statistics_use_each_view_and_preserve_pilot_population(self):
        metrics = s.statistics(self.f.resolve())
        primary = metrics["populations"]["primary_ge10_lines"]
        self.assertEqual(primary["n_items"], 2)
        self.assertEqual(primary["critics"]["EXP1__mock0"]["hit1"]["mean"], .5)
        self.assertEqual(primary["critics"]["EXP5__mock0"]["hit1"]["mean"], 0)
        self.assertEqual(len(primary["paired_hit1_differences"]), 3)
        self.assertEqual(metrics["populations"]["pilot_scorable"]["n_items"], 20)

    def test_missing_continuation_campaign_coverage_is_not_inferred_zero(self):
        descriptor = self.f.policy["subject"]["configurations"]["EXP1__mock0"]["historical_cost_report"]
        report = json.loads(self.f.read(descriptor))
        report["units"][-1]["coverage_ids"] = ["unrelated-history"]
        self.f.replace(descriptor, report)
        with self.assertRaisesRegex(ValueError, "omits joined continuation"):
            s.account_costs(self.f.resolve(), self.f.policy, self.f.read)

    def test_repeated_historical_alias_cannot_be_charged_twice(self):
        descriptor = self.f.policy["subject"]["configurations"]["EXP1__mock0"]["historical_cost_report"]
        report = json.loads(self.f.read(descriptor))
        report["units"][-1]["coverage_ids"].append(report["units"][0]["coverage_ids"][0])
        self.f.replace(descriptor, report)
        with self.assertRaisesRegex(ValueError, "Overlapping historical"):
            s.account_costs(self.f.resolve(), self.f.policy, self.f.read)

    def test_joined_orphan_remains_missing_in_both_views(self):
        target = self.f.terminal["targets"][0]
        target.update(completion_state="ORPHAN_UNRESOLVED", complete=False, record=None, answer=None, attempt_receipts=[])
        self.f.terminal.update(complete=False, all_required_physical_calls_complete=False)
        result = self.f.resolve()
        self.assertFalse(result["complete"] or result["all_required_physical_calls_complete"])
        self.assertIsNone(result["resolved"]["EXP1__mock0"]["A"]["record"])
        self.assertIsNone(result["resolved"]["EXP5__mock0"]["A"]["record"])
        costs = s.account_costs(result, self.f.policy, self.f.read)
        self.assertEqual(costs["configurations"]["EXP1__mock0"]["fresh_unresolved_orphans"], 1)
        self.assertEqual(costs["grand_cumulative_all_configurations"]["charged_tokens"], 40550)
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            s.statistics(result)

    def test_shared_source_and_native_contract_drift_rejected(self):
        for field, value, message in (("new_user_prompt_sha256", "drift", "source/request"),
                                       ("new_request_surface_sha256", "drift", "source/request")):
            with self.subTest(field=field):
                fixture = Fixture(joined=True); fixture.joined["calls"][0][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    fixture.resolve()
        self.f.joined["calls"][0]["execution_equivalence"]["native_cli_version"] = "2.1.280"
        with self.assertRaisesRegex(ValueError, "inference equivalence"):
            self.f.resolve()

    def test_scope_and_terminal_alias_drift_rejected(self):
        self.f.joined["scope"] = "unapproved_future_scope"
        with self.assertRaisesRegex(ValueError, "Unknown reporting view"):
            self.f.resolve()
        self.f.joined["scope"] = "lifetime_evaluation"
        self.f.terminal["targets"][0]["reporting_aliases"] = []
        with self.assertRaisesRegex(ValueError, "Terminal reporting aliases"):
            self.f.resolve()

    def test_shared_role_or_model_cannot_change(self):
        self.f.joined["calls"][0]["cost_bucket"] = "WITHDRAWN_DIAGNOSTIC_RERUN"
        with self.assertRaisesRegex(ValueError, "roles or disposition"):
            self.f.resolve()
        self.f.joined["calls"][0]["cost_bucket"] = "CURRENT_ADMITTED_RERUN"
        self.f.joined["lane"] = "different-model"
        with self.assertRaisesRegex(ValueError, "another model"):
            self.f.resolve()

    def test_historical_origin_and_parser_freeze_cannot_be_relabelled(self):
        history = next(c for c in self.f.joined["calls"] if c["record_id"] == "P0")["historical"]
        history["parser_provenance"]["freeze_sha256"] = self.f.joined["freeze_sha256"]
        with self.assertRaisesRegex(ValueError, "parser origin"):
            self.f.resolve()
        history["parser_provenance"]["freeze_sha256"] = self.f.physical[0]["freeze_sha256"]
        history["origin"]["freeze_sha256"] = self.f.joined["freeze_sha256"]
        with self.assertRaisesRegex(ValueError, "incorrectly relabeled"):
            self.f.resolve()

    def test_logical_freeze_identity_is_bound_inside_distinct_file_digest(self):
        history = next(c for c in self.f.joined["calls"] if c["record_id"] == "P0")["historical"]
        provenance = history["parser_provenance"]
        self.assertNotEqual(provenance["freeze"]["sha256"], provenance["freeze_sha256"])
        provenance["freeze"] = self.f.put("synthetic/bad-logical-freeze.json", {"freeze_sha256": "wrong"})
        with self.assertRaisesRegex(ValueError, "parser freeze identity"):
            self.f.resolve()

    def test_shared_setup_terminal_never_satisfies_required_physical_calls(self):
        target = self.f.terminal["targets"][0]
        target.update(complete=True, physical_attempt_count=0, dispatch_receipts=[], attempt_receipts=[], physical_call_occurred=False)
        self.f.terminal["all_required_physical_calls_complete"] = False
        record = json.loads(self.f.read(target["record"]))
        record.update(attempt_class="SETUP_FAILURE", valid_protocol=False, attempts=[], usage_origin="preflight_no_inference",
                      usage_known=True, total_attributable_tokens=0)
        self.f.replace(target["record"], record)
        result = self.f.resolve()
        self.assertTrue(result["complete"])
        self.assertFalse(result["all_required_physical_calls_complete"])
        self.assertEqual(result["resolved"]["EXP5__mock0"]["A"]["record"]["attempt_class"], "SETUP_FAILURE")
        with self.assertRaisesRegex(ValueError, "Mandatory physical calls"):
            s.statistics(result)

    def test_item_history_inventory_and_dispatch_alias_are_bound(self):
        history = self.f.joined["calls"][0]["historical"]
        history["physical_attempt_history"] = []
        with self.assertRaisesRegex(ValueError, "Per-item joined physical history"):
            self.f.resolve()
        f = Fixture(joined=True)
        entry = f.joined["joined_source_policy"]["physical_attempt_inventory"][0]
        entry["aliases"] = [f.put("synthetic/wrong-copy.json", {"wrong_copy": True})]
        with self.assertRaisesRegex(ValueError, "dispatch alias differs"):
            f.resolve()

    def test_real_terminal_producer_emits_shared_physical_target_once(self):
        import dispatch_corrected
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for name, raw in self.f.files.items():
                path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
            index = dispatch_corrected.terminal_index(self.f.registry, self.f.rd, repo)
            self.assertEqual(len(index["targets"]), 4)
            result = s.resolve_inputs(self.f.registry, self.f.rd, self.f.manifest, index, self.f.read)
        self.assertTrue(result["complete"] and result["all_required_physical_calls_complete"])
        self.assertEqual(len(result["resolved"]), 3)


if __name__ == "__main__":
    unittest.main()
