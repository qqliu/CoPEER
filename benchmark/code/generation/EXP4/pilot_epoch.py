"""One approved CCL pilot epoch; receipt identity, never directory name, controls allowance.

No policy means the conservative lifetime allowance. This module never changes
costs, archives, or receipts. The accounting owner writes the activation ledger
under its experiment-wide lock immediately before a durable dispatch.

The lane registry is policy data (policy["lanes"]), never a module constant:
the anchor pins the registered list at the first dispatch, and the policy
forbids a further epoch, so every lane is registered before that dispatch.
The anchor pins the freeze of that first dispatch too: every lane, fresh or
already run, joins the activated epoch only under that one freeze.
"""
import json
from pathlib import Path

from common import safe, sha

POLICY_NAME = "ATTEMPT_EPOCH_POLICY.json"
ACTIVATION_NAME = "PILOT_EPOCH_ACTIVATION.json"
LOCK_NAME = ".pilot_epoch.lock"
SCHEMA = "ccl-attempt-epoch-policy/v1"
ACTIVATION_SCHEMA = "ccl-pilot-epoch-activation/v1"
EPOCH_ID = "ccl-v7-epoch4-20260922"   # epoch 4: follow-up root (EPOCH4_DECISION.md)
APPROVAL_SHA256 = "6c73e61adbe6062d7069efc728900dcfb7fc46aeaa23d1fa1f665d1a8d7b44d1"   # sha256 of EXP/EPOCH4_DECISION.md
ROSTER_SHA256 = "a369189619b9b6d19c5ca15eb28fd1c478adec77fce6dbd6dc5ccfcec10c4f59"
ORDER_SHA256 = "570a607f24717a03e1f0c5eb0fb81fcb6f3f214e2f2fcddf070b164ebd86160c"


class EpochPolicyError(RuntimeError):
    def __init__(self, reason, details=None):
        self.reason, self.details = reason, details
        super().__init__(reason + (": " + str(details) if details is not None else ""))


def require(condition, message):
    if not condition:
        raise EpochPolicyError("attempt_epoch_policy_invalid", message)


def read_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise EpochPolicyError("attempt_epoch_identity_unreadable", str(path)) from exc
    require(isinstance(value, dict), "not an object: " + str(path))
    return value


def receipt_sha(ticket):
    """Exact serialization used by lane_accounting.atomic_json."""
    return sha(json.dumps(ticket, indent=1, ensure_ascii=False))


def load_policy(exp):
    path = Path(exp) / POLICY_NAME
    if not path.exists():
        require(not (Path(exp) / ACTIVATION_NAME).exists(), "activated policy is missing")
        # The anchor is not the only durable proof that this experiment used
        # the epoch. Losing both root files must not admit an unstamped retry;
        # setup-only records also carry the policy binding without a dispatch.
        roots = [Path(exp) / "runs", Path(exp) / "canary"] + sorted(
            p for p in Path(exp).glob("superseded_*") if p.is_dir())
        for root in roots:
            for pattern in ("DISPATCH_*.json", "ATTEMPT_*.json", "record.json"):
                for receipt in root.glob("**/" + pattern):
                    value = read_json(receipt)
                    saved_dispatch = value.get("dispatch")
                    for evidence in (value, saved_dispatch if isinstance(saved_dispatch, dict) else {}):
                        require("attempt_epoch_id" not in evidence and "attempt_epoch_policy_sha256" not in evidence,
                                "activated policy is missing; retained epoch evidence: " + str(receipt))
        return None, None
    policy = read_json(path)
    approval = policy.get("approval") or {}
    require(isinstance(approval, dict), "approval must be an object")
    require(policy.get("schema") == SCHEMA and policy.get("status") == "APPROVED", "policy is not approved")
    require(policy.get("epoch_id") == EPOCH_ID, "only the approved epoch is permitted")
    require(approval.get("task") == "TASK450" and approval.get("status") == "APPROVED"
            and approval.get("decision_sha256") == APPROVAL_SHA256, "scientific approval binding differs")
    # The registry is data: a sorted list of unique lane names, each with exactly one activation entry.
    # A lane name is its own directory name (safe(lane) == lane): whitespace, separators and other unsafe
    # characters are refused, so safe() images are unique; a letter-case variant of a registered name is refused too.
    # The current and parent directory names and names starting with "." (hidden entries) or "-" (option-like argv
    # words) are not lane directories either, although safe() leaves them unchanged.
    lanes = policy.get("lanes")
    require(isinstance(lanes, list) and bool(lanes)
            and all(isinstance(lane, str) and lane and safe(lane) == lane and lane not in (".", "..")
                    and not lane.startswith((".", "-")) for lane in lanes)
            and sorted(set(lanes)) == lanes and len({lane.casefold() for lane in lanes}) == len(lanes),
            "lane registry must be a non-empty sorted list of unique safe lane names")
    activation = policy.get("lane_activation")
    require(isinstance(activation, dict) and sorted(activation) == lanes
            and all(isinstance(status, str) and status for status in activation.values()),
            "lane_activation must name every registered lane exactly once")
    roster, order = policy.get("pilot_record_ids"), policy.get("pilot_order_record_ids")
    require(isinstance(roster, list) and len(roster) == 20 and all(isinstance(r, str) and r for r in roster)
            and sorted(set(roster)) == roster, "pilot roster must contain exactly 20 sorted unique IDs")
    require(sha("\n".join(roster)) == ROSTER_SHA256 == policy.get("pilot_roster_sha256"), "pilot roster changed")
    require(isinstance(order, list) and all(isinstance(r, str) for r in order)
            and sorted(order) == roster and sha("\n".join(order)) == ORDER_SHA256,
            "pilot order changed")
    require(type(policy.get("pilot_max_attempts_per_item")) is int and policy["pilot_max_attempts_per_item"] == 2
            and type(policy.get("evaluation_max_attempts_per_item_lifetime")) is int
            and policy["evaluation_max_attempts_per_item_lifetime"] == 2, "attempt caps must remain two")
    rows = policy.get("historical_dispatches")
    require(isinstance(rows, list), "historical dispatch census is missing")
    seen = set()
    for row in rows:
        require(isinstance(row, dict), "invalid historical dispatch")
        tid = row.get("ticket_id")
        require(isinstance(tid, str) and tid and tid not in seen, "duplicate/missing historical ticket identity")
        seen.add(tid)
        require(row.get("lane") in lanes, "historical dispatch lane is not registered: " + tid)
        require(isinstance(row.get("record_id"), str)
                and row.get("split") in ("pilot", "evaluation", "canary")
                and isinstance(row.get("tag"), str) and row["tag"]
                and isinstance(row.get("freeze_sha256"), str) and row["freeze_sha256"], "historical identity incomplete")
        require(type(row.get("exempt_from_epoch_count")) is bool, "historical exemption must be explicit")
        require(not row["exempt_from_epoch_count"] or
                (row["record_id"] in roster and row["split"] in ("pilot", "canary")), "only historical pilot dispatches may be exempt")
        for kind in ("dispatch", "attempt", "record"):
            require(kind + "_path" in row and kind + "_sha256" in row, "missing historical " + kind + " binding")
            name, digest = row.get(kind + "_path"), row.get(kind + "_sha256")
            require((name is None and digest is None and kind != "dispatch") or
                    (isinstance(name, str) and bool(name) and not Path(name).is_absolute() and ".." not in Path(name).parts
                     and isinstance(digest, str) and len(digest) == 64
                     and all(c in "0123456789abcdef" for c in digest)), "invalid historical " + kind + " binding")
    return policy, sha(path.read_bytes())


def receipt_snapshot(exp, model, carryover=None, lanes=None):
    """Read active and preserved metadata, including legacy record-only attempts.

    A ticket copied to another directory is rejected, not counted as a new call.
    A moved ticket retains its ID and bytes. No answer content is read. Archived
    lane directories are recognised by the registered lanes when a policy is
    installed, else by this model and the carryover lanes.
    """
    exp = Path(exp)
    roots = [exp / "runs", exp / "canary"] + sorted(p for p in exp.glob("superseded_*") if p.is_dir())
    known = set(lanes or ()) | {model} | set((carryover or {}).get("lanes", {}))
    dispatches, legacy, records = {}, [], []
    for root in roots:
        directories = sorted({p.parent for pattern in ("DISPATCH_*.json", "record.json", "ATTEMPT_*.json")
                              for p in root.glob("**/" + pattern)})
        for directory in directories:
            record_path = directory / "record.json"
            record = read_json(record_path) if record_path.exists() else None
            paths = sorted(directory.glob("DISPATCH_*.json"))
            saved_paths = set(directory.glob("ATTEMPT_*.json"))
            expected_paths = {p.with_name("ATTEMPT_" + p.name[len("DISPATCH_"):]) for p in paths}
            require(saved_paths <= expected_paths, "attempt receipt without dispatch: " + str(directory))
            if record is not None:
                require(isinstance(record.get("requested_model"), str) and record["requested_model"], "record model is missing")
                require(all(isinstance(record.get(f), str) and record[f] for f in ("record_id", "split", "freeze_sha256")),
                        "record identity incomplete")
                records.append((record["requested_model"], record, record_path))
            if not paths:
                if record is not None:
                    attempts = record.get("attempts") if isinstance(record.get("attempts"), list) else [record]
                    require(not attempts or "attempt_epoch_id" not in record, "epoch record is missing its dispatch identities")
                    for i, attempt in enumerate(attempts):
                        legacy.append({"model": record["requested_model"], "record_id": record.get("record_id"),
                                       "split": record.get("split"), "attempt": attempt,
                                       "identity": str(record_path) + "#" + str(i)})
                continue
            for path in paths:
                ticket = read_json(path)
                tid = ticket.get("ticket_id")
                require(isinstance(tid, str) and tid and tid not in dispatches, "duplicate/missing physical dispatch ticket")
                for field in ("record_id", "split", "tag", "freeze_sha256"):
                    require(isinstance(ticket.get(field), str) and ticket[field], "dispatch identity missing: " + field)
                if root.name in ("runs", "canary"):
                    path_model = directory.relative_to(root).parts[0]
                else:
                    matches = {name for name in known if safe(name) in directory.relative_to(root).parts
                               or "lane_" + safe(name) in directory.relative_to(root).parts}
                    require(len(matches) <= 1, "ambiguous archived lane")
                    path_model = next(iter(matches), None)
                lane = ticket.get("requested_model") or (record or {}).get("requested_model") or path_model
                require(isinstance(lane, str) and lane and (path_model is None or safe(lane) == path_model), "dispatch lane identity differs")
                if record is not None:
                    require(record["requested_model"] == lane and all(record.get(f) == ticket[f]
                            for f in ("record_id", "split", "freeze_sha256")), "dispatch/record identity mismatch")
                saved_path = path.with_name("ATTEMPT_" + path.name[len("DISPATCH_"):])
                saved = read_json(saved_path) if saved_path.exists() else None
                if saved is not None:
                    require(saved.get("dispatch") == ticket and isinstance(saved.get("attempt"), dict), "attempt/dispatch identity mismatch")
                dispatches[tid] = {"ticket": ticket, "model": lane, "dispatch_sha256": sha(path.read_bytes()),
                                   "attempt_sha256": sha(saved_path.read_bytes()) if saved is not None else None,
                                   "record_sha256": sha(record_path.read_bytes()) if record is not None else None,
                                   "attempt": saved["attempt"] if saved is not None else None, "path": path}
    # The carryover builder's authenticated count must agree with retained metadata.
    for lane, entry in (carryover or {}).get("lanes", {}).items():
        for item in entry.get("items", []):
            directory = exp / item["directory"]
            count = sum(row["path"].parent == directory for row in dispatches.values())
            count += sum(row["identity"].startswith(str(directory / "record.json") + "#") for row in legacy)
            require(count == item["attempts_count"], "archived attempt identities/count differ")
    return dispatches, legacy, records


class PilotEpoch:
    def __init__(self, exp, model, freeze_sha256, carryover=None):
        self.exp, self.model, self.freeze = Path(exp), model, freeze_sha256
        self.carryover = carryover
        self.policy, self.policy_sha256 = load_policy(self.exp)
        if self.policy is not None:
            require(model in self.policy["lanes"], "lane is not registered for this epoch")
            self._state()  # refuse invalid policy/identity before any model can be loaded

    def _state(self):
        policy, digest = load_policy(self.exp)
        require(digest == self.policy_sha256, "policy changed during lane invocation")
        lanes = None if policy is None else policy["lanes"]
        # Epoch 4: the anchor is read BEFORE the receipt scan, so a dispatch activated during the scan can only make the
        # snapshot a superset of the ledger, never leave a ledger entry without its receipt (the epoch-2/3 start race).
        path = self.exp / ACTIVATION_NAME
        anchor = read_json(path) if path.exists() else None
        snapshot = receipt_snapshot(self.exp, self.model, self.carryover, lanes)
        if policy is None:
            return snapshot, None, set()
        if anchor is not None:
            require(anchor.get("schema") == ACTIVATION_SCHEMA and anchor.get("epoch_id") == EPOCH_ID
                    and anchor.get("policy_sha256") == digest and isinstance(anchor.get("dispatches"), dict),
                    "activation anchor differs; no new epoch or policy is allowed")
            require(anchor.get("lanes") == lanes and anchor.get("pilot_roster_sha256") == ROSTER_SHA256
                    and anchor.get("pilot_order_sha256") == ORDER_SHA256
                    and isinstance(anchor.get("first_freeze_sha256"), str) and anchor["first_freeze_sha256"]
                    and anchor.get("final_run_freeze_sha256") == anchor["first_freeze_sha256"],
                    "activation scope/freeze binding differs")
        ledger = anchor["dispatches"] if anchor else {}
        dispatches = snapshot[0]
        historical, exempt = set(), set()
        for row in policy["historical_dispatches"]:
            tid = row["ticket_id"]
            require(tid in dispatches, "historical dispatch is missing: " + tid)
            actual = dispatches[tid]
            # Epoch 2 (2026-09-22): a dispatch stamped by a PRIOR epoch (another epoch id, another policy digest) is history
            # like an unstamped one; only a dispatch of this epoch can never be re-labelled historical.
            require(actual["ticket"].get("attempt_epoch_id") != EPOCH_ID and actual["ticket"].get("attempt_epoch_policy_sha256") != digest,
                    "a new epoch dispatch cannot become historical: " + tid)
            require(actual["model"] == row["lane"] and all(actual["ticket"][f] == row[f]
                    for f in ("record_id", "split", "tag", "freeze_sha256")), "historical identity differs: " + tid)
            require(all(actual[kind + "_sha256"] == row.get(kind + "_sha256")
                        for kind in ("dispatch", "attempt", "record")), "historical receipt bytes differ: " + tid)
            historical.add(tid)
            if row["exempt_from_epoch_count"]:
                exempt.add(tid)
        for tid, value in ledger.items():
            require(isinstance(value, dict) and isinstance(value.get("ticket"), dict), "invalid activation dispatch ledger")
            ticket = value["ticket"]
            require(tid == ticket.get("ticket_id") and value.get("dispatch_sha256") == receipt_sha(ticket)
                    and ticket.get("attempt_epoch_id") == EPOCH_ID and ticket.get("attempt_epoch_policy_sha256") == digest,
                    "activation dispatch identity differs")
            require(ticket.get("freeze_sha256") == anchor["first_freeze_sha256"],
                    "activated dispatch freeze differs from the epoch freeze: " + tid)
            require(tid in dispatches and dispatches[tid]["ticket"] == ticket
                    and dispatches[tid]["dispatch_sha256"] == value["dispatch_sha256"], "activated dispatch is missing or altered: " + tid)
        # Every epoch-stamped receipt, and every receipt of a registered lane, is listed history or a ledger
        # entry: de-registering a lane or losing the anchor can never make an epoch dispatch invisible.
        for tid, row in dispatches.items():
            ticket = row["ticket"]
            stamped = "attempt_epoch_id" in ticket or "attempt_epoch_policy_sha256" in ticket
            stamped_here = ticket.get("attempt_epoch_id") == EPOCH_ID or ticket.get("attempt_epoch_policy_sha256") == digest
            if stamped_here:
                require(anchor is not None, "activation anchor is missing; retained epoch dispatch: " + tid)
            if stamped or row["model"] in lanes:
                require(tid in historical or tid in ledger, "unregistered dispatch identity: " + tid)
        # The anchor pins the freeze of the first dispatch: no lane, fresh or already run, joins it under another.
        if anchor is not None:
            require(self.freeze == anchor["first_freeze_sha256"], "invocation freeze differs from the activated epoch freeze")
        return snapshot, anchor, exempt

    def authorize(self, record_id, split):
        """Check allowance without mutation; caller holds lane + experiment locks."""
        (dispatches, legacy, records), anchor, exempt = self._state()
        if self.policy is not None:
            pilot = record_id in self.policy["pilot_record_ids"]
            require(split in ("pilot", "evaluation", "canary") and (split != "pilot" or pilot)
                    and (split != "evaluation" or not pilot), "split/approved pilot identity differs")
        else:
            pilot = False
        def matches(rid, other_split):
            return rid == record_id and (self.policy is not None or other_split == split
                                        or "canary" in (split, other_split))
        prior = [row for tid, row in dispatches.items() if row["model"] == self.model
                 and matches(row["ticket"]["record_id"], row["ticket"]["split"])
                 and not (pilot and tid in exempt)]
        old = [row for row in legacy if row["model"] == self.model and matches(row["record_id"], row["split"])]
        count = len(prior) + len(old)
        if count >= 2:
            raise EpochPolicyError("attempt_allowance_exhausted", {"record_id": record_id, "consumed_physical_attempts": count,
                                   "scope": "approved pilot epoch" if pilot else "lifetime"})
        if self.policy is not None:
            for row in prior + old:
                attempt = row["attempt"]
                if attempt is None:
                    raise EpochPolicyError("unreconciled_dispatch", record_id)
                transport = (attempt.get("attempt_class") == "TRANSPORT_FAILURE"
                             or ("attempt_class" not in attempt and attempt.get("transport_failure") is True))
                if (not transport or attempt.get("saw_assistant_message") is True or attempt.get("saw_result_event") is True):
                    raise EpochPolicyError("prior_attempt_not_retryable", record_id)
            for model, record, _ in records:
                if model == self.model and matches(record.get("record_id"), record.get("split")):
                    if (record.get("attempt_epoch_id") == EPOCH_ID and record.get("attempts") == []):
                        raise EpochPolicyError("prior_setup_failure_not_retryable", record_id)
        return anchor

    def historical_evaluation_exclusions(self):
        """Historical evaluation IDs that must be retained rather than dispatched.

        This is a scheduling view of authorize(), not a fresh allowance or an
        outcome selection rule. Transport-only histories remain eligible under
        the same two-attempt lifetime cap; observed answers and unresolved
        dispatches do not. No receipts, STOPs or activation state are written.
        """
        self._state()
        if self.policy is None:
            return {}
        ids = {row["record_id"] for row in self.policy["historical_dispatches"]
               if row["lane"] == self.model and row["split"] == "evaluation"
               and not row["exempt_from_epoch_count"]}
        excluded = {}
        for rid in sorted(ids):
            try:
                self.authorize(rid, "evaluation")
            except EpochPolicyError as exc:
                if exc.reason not in ("attempt_allowance_exhausted", "unreconciled_dispatch", "prior_attempt_not_retryable"):
                    raise
                excluded[rid] = exc.reason
        return excluded

    def stamp(self):
        if self.policy is None:
            return {}
        return {"attempt_epoch_id": EPOCH_ID, "attempt_epoch_policy_sha256": self.policy_sha256}

    def activation(self, anchor, ticket):
        """New durable ledger value. Never exempt an unlisted/new dispatch."""
        if self.policy is None:
            return None
        if anchor is None:
            # The registered list and the freeze are pinned here; a policy with other lanes is a different policy and is refused.
            anchor = {"schema": ACTIVATION_SCHEMA, "epoch_id": EPOCH_ID, "policy_sha256": self.policy_sha256,
                      "lanes": list(self.policy["lanes"]), "pilot_roster_sha256": ROSTER_SHA256, "pilot_order_sha256": ORDER_SHA256,
                      "first_freeze_sha256": self.freeze, "final_run_freeze_sha256": self.freeze, "dispatches": {}}
        # The ticket joins the activated epoch only under its freeze, whichever lane dispatches it.
        require(ticket.get("freeze_sha256") == self.freeze == anchor["first_freeze_sha256"],
                "dispatch freeze differs from the activated epoch freeze")
        anchor["dispatches"][ticket["ticket_id"]] = {"ticket": ticket, "dispatch_sha256": receipt_sha(ticket)}
        return anchor
