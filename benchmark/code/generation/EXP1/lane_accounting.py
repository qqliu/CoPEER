"""Durable lane budgets and dispatch guards; no inference or provider imports."""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import threading
import time
import uuid

from common import MAX_OUTPUT, normalise_leading_zero_labels, safe, sha, usage_summary
import pilot_epoch

# v4: the mutually exclusive outcome classes every physical attempt records as `attempt_class`.
ATTEMPT_CLASSES = ("VALID_ANSWER", "BUDGET_EXHAUSTED", "CONTRACT_VIOLATION", "TRANSPORT_FAILURE", "SETUP_FAILURE")
MAX_PHYSICAL_ATTEMPTS = 2       # the original call plus the single transport retry; a DISPATCH receipt consumes one
TECHNICAL_GATE_LIMIT = 2        # technical-integrity failures tolerated in the 20-item pilot
HOLD_NAME = "HOLD.json"         # EXP/HOLD.json: anyone on the team stops every lane by creating it
CARRYOVER_NAME = "CARRYOVER.json"
CARRYOVER_SCHEMA = "ccl-carryover/v1"
# Kept separate everywhere (archive item, archive, lane, summary); a charge is never reported as a measurement.
CARRYOVER_COMPONENTS = ("measured_tokens", "unknown_attempts", "observed_lower_bound_tokens", "charged_tokens")
RECEIPT_PATTERNS = ("record.json", "DISPATCH_*.json", "ATTEMPT_*.json")
# Stops this class writes for an interruption. Only these are retired by an explicit reconciliation.
INTERRUPTION_STOPS = ("unreconciled_dispatch", "dispatch_interrupted", "runner_interrupted")


class LaneStopped(RuntimeError):
    pass


class LaneHeld(LaneStopped):
    """An experiment-level HOLD.json: removable, never persisted as a lane stop."""


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def exclusive_lock(path):
    """A process lock, intentionally nonblocking (including between CLI lanes)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise LaneStopped("another process owns " + str(path)) from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def output_cap_hit(record):
    """Legacy v2/v3 output-cap count; retained beside the v4 gate readout."""
    reasons = {"max_tokens", "length", "output_token_cap", "max_output_tokens", "output_budget_exhausted"}
    if record.get("stop_reason") in reasons or record.get("finish_reason") in reasons:
        return True
    if (record.get("hard_stop") or {}).get("reason") in reasons:
        return True
    for attempt in record.get("attempts", []):
        usage = attempt.get("usage") or {}
        if usage.get("stop_reason") in reasons or attempt.get("finish_reason") in reasons:
            return True
        if (attempt.get("hard_stop") or {}).get("reason") in reasons:
            return True
        if attempt.get("attempt_class") == "BUDGET_EXHAUSTED":
            return True
        if any(row.get("outputTokens", 0) >= MAX_OUTPUT for row in usage.get("per_model", {}).values()):
            return True
        if attempt.get("output_tokens", 0) >= MAX_OUTPUT:
            return True
    return record.get("output_tokens", 0) >= MAX_OUTPUT


def rule_miss(record):
    candidates = record.get("candidates")
    return (record.get("valid_protocol") is not True or not isinstance(candidates, list)
            or not candidates or candidates[0] is None)


def transport_failure(attempt):
    """A recorded v4 class decides; otherwise local attempts state this directly and CLI attempts retain stream evidence.

    (A CLI attempt killed at the output budget before any assistant message is
    BUDGET_EXHAUSTED, not a transport failure, although its stream shows neither event.)
    """
    if attempt.get("attempt_class") in ATTEMPT_CLASSES:
        return attempt["attempt_class"] == "TRANSPORT_FAILURE"
    if "transport_failure" in attempt:
        return attempt["transport_failure"] is True
    return (attempt.get("saw_assistant_message") is False
            and attempt.get("saw_result_event") is False)


def attempt_class(attempt):
    """The recorded v4 class, or None for a legacy/unclassified attempt."""
    value = attempt.get("attempt_class")
    return value if value in ATTEMPT_CLASSES else None


def derived_attempt_class(attempt):
    """The recorded class; for a v2/v3 attempt, the class its retained evidence implies."""
    recorded = attempt_class(attempt)
    if recorded is not None:
        return recorded
    if transport_failure(attempt):
        return "TRANSPORT_FAILURE"
    if output_cap_hit({"attempts": [attempt]}):
        return "BUDGET_EXHAUSTED"
    if attempt.get("valid_protocol") is False or attempt.get("hard_stop"):
        return "CONTRACT_VIOLATION"
    return "VALID_ANSWER"


def _string_end(text, start):
    pos = start + 1
    while pos < len(text):
        if text[pos] == "\\":
            pos += 2
        elif text[pos] == '"':
            return pos + 1
        else:
            pos += 1
    return len(text)


def _array_end(text, start):
    """Index after the bracket closing the array opened at start; None when unbalanced."""
    stack, pos = [], start
    while pos < len(text):
        char = text[pos]
        if char == '"':
            pos = _string_end(text, pos)
            continue
        if char in "[{":
            stack.append(char)
        elif char in "]}":
            if not stack or stack.pop() != ("[" if char == "]" else "{"):
                return None
            if not stack:
                return pos + 1
        pos += 1
    return None


def well_formed_candidates_array(answer):
    """Gate evidence only, never scoring: does the visible answer hold a decodable candidates array?

    A "candidates" KEY (text inside a quoted string is skipped whole) followed by a
    balanced array that decodes after the frozen leading-zero normalisation. The
    scanner mirrors common.normalise_leading_zero_labels; unescaped LaTeX in the
    unscored free-text fields therefore cannot hide a well-formed array.
    """
    text = answer or ""
    if "</think>" in text:
        text = text.split("</think>")[-1]
    pos = 0
    while pos < len(text):
        if text[pos] != '"':
            pos += 1
            continue
        end = _string_end(text, pos)
        try:
            key = json.loads(text[pos:end])
        except ValueError:
            pos = end
            continue
        pos = end
        while end < len(text) and text[end] in " \t\r\n":
            end += 1
        if key != "candidates" or end >= len(text) or text[end] != ":":
            continue
        end += 1
        while end < len(text) and text[end] in " \t\r\n":
            end += 1
        stop = _array_end(text, end) if end < len(text) and text[end] == "[" else None
        if stop is None:
            continue
        try:
            decoded = json.loads(normalise_leading_zero_labels('{"candidates": ' + text[end:stop] + "}"))
        except ValueError:
            decoded = None
        if isinstance(decoded, dict) and isinstance(decoded.get("candidates"), list):
            return True
        pos = stop
    return False


def technical_causes(record, answer=None):
    """Technical-integrity causes of one pilot record; empty for a model answer or a legitimate budget miss.

    `answer` is the saved answer text, needed only when a protocol-valid record has
    no parsed candidates list; an unreadable answer is counted, never waved through.
    """
    attempts = record.get("attempts") if isinstance(record.get("attempts"), list) else [record]
    classes = [derived_attempt_class(attempt) for attempt in attempts]
    causes = []
    if "CONTRACT_VIOLATION" in classes:
        causes.append("contract_violation")
    if not attempts or "SETUP_FAILURE" in classes:
        causes.append("setup_failure")
    if classes and classes[-1] == "TRANSPORT_FAILURE":
        causes.append("unresolved_transport_failure")
    if record.get("valid_protocol") is True and record.get("candidates") is None:
        if answer is None:
            causes.append("answer_unreadable")
        elif well_formed_candidates_array(answer):
            causes.append("unparseable_with_well_formed_candidates_array")
    return causes


def stop_file_reason(path):
    """A bare `touch STOP.json` is as binding as a written reason."""
    try:
        reason = json.loads(Path(path).read_text(encoding="utf-8"))["reason"]
    except (ValueError, KeyError, TypeError, OSError):
        reason = None
    return reason if isinstance(reason, str) and reason else "unreadable_stop_file"


def attempt_receipts(out_dir):
    """(tag, dispatch, saved ATTEMPT receipt or None) per DISPATCH of one item directory, oldest dispatch first."""
    rows = []
    for path in Path(out_dir).glob("DISPATCH_*.json"):
        dispatch = json.loads(path.read_text(encoding="utf-8"))
        attempt_path = path.with_name("ATTEMPT_" + path.name[len("DISPATCH_"):])
        saved = json.loads(attempt_path.read_text(encoding="utf-8")) if attempt_path.exists() else None
        if saved is not None and (not isinstance(saved, dict) or saved.get("dispatch") != dispatch
                                  or not isinstance(saved.get("attempt"), dict)):
            raise LaneStopped("attempt/dispatch identity mismatch: " + str(attempt_path))
        order = dispatch.get("dispatched_time_ns")
        rows.append((order if isinstance(order, int) else 0, path.name, dispatch, saved))
    return [(dispatch.get("tag"), dispatch, saved) for _, _, dispatch, saved in sorted(rows, key=lambda row: row[:2])]


def carryover_components(summary):
    """The four carryover quantities of one common.usage_summary result, names unchanged in meaning."""
    return {"measured_tokens": summary["known_attributable_tokens"],
            "unknown_attempts": summary["unknown_usage_attempts"],
            "observed_lower_bound_tokens": summary["observed_usage_lower_bound"],
            "charged_tokens": summary["budget_charge_tokens"]}


def zero_carryover():
    return {name: 0 for name in CARRYOVER_COMPONENTS}


def archive_census(exp):
    """Every preserved receipt below EXP/superseded_*: count and content hash per archive directory.

    CARRYOVER.json pins this census, so an archive added or changed after the build
    makes every lane refuse to run until build_carryover.py is run again.
    """
    census = {}
    for directory in sorted(Path(exp).glob("superseded_*")):
        if not directory.is_dir():
            continue
        paths = sorted({path for pattern in RECEIPT_PATTERNS for path in directory.glob("**/" + pattern)})
        rows = [[path.relative_to(directory).as_posix(), sha(path.read_bytes())] for path in paths]
        census[directory.name] = {"receipts": len(rows), "receipts_sha256": sha(json.dumps(rows))}
    return census


def carryover_sha256(document):
    """Canonical hash of everything except the hash field itself."""
    body = {key: value for key, value in document.items() if key != "content_sha256"}
    return sha(json.dumps(body, sort_keys=True, ensure_ascii=False))


def _count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def load_carryover(exp, path=None):
    """The validated carryover document, or LaneStopped. Never returns a partial reading.

    Checked: schema, content hash, non-negative integer components, every lane
    total equal to the sum of its archived items (a merged or hand-edited total
    is refused) and the pinned census of the archives that exist now.
    """
    path = Path(path) if path is not None else Path(exp) / CARRYOVER_NAME
    if not path.exists():
        raise LaneStopped("carryover missing: %s (build it with build_carryover.py; never assume zero)" % path)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise LaneStopped("carryover unreadable: %s (%s)" % (path, type(exc).__name__)) from exc
    if not isinstance(document, dict) or document.get("schema") != CARRYOVER_SCHEMA:
        raise LaneStopped("carryover has an unknown schema: " + str(path))
    if document.get("content_sha256") != carryover_sha256(document):
        raise LaneStopped("carryover content hash mismatch (edited after build_carryover.py wrote it): " + str(path))
    lanes = document.get("lanes")
    if not isinstance(lanes, dict):
        raise LaneStopped("carryover has no lanes table: " + str(path))
    for lane, entry in lanes.items():
        items = entry.get("items") if isinstance(entry, dict) else None
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise LaneStopped("carryover lane without archived items: " + lane)
        for item in items:
            if (not isinstance(item.get("record_id"), str) or not item["record_id"]
                    or item.get("split") not in ("pilot", "evaluation", "canary")
                    or not _count(item.get("attempts_count"))):
                raise LaneStopped("carryover item lacks physical-attempt identity/count: " + lane)
        if (not _count(entry.get("attempts_count"))
                or entry["attempts_count"] != sum(item["attempts_count"] for item in items)):
            raise LaneStopped("carryover lane attempt count differs from its archived items: " + lane)
        for name in CARRYOVER_COMPONENTS:
            if not _count(entry.get(name)) or not all(_count(item.get(name)) for item in items):
                raise LaneStopped("carryover component is not a non-negative integer: %s %s" % (lane, name))
            if entry[name] != sum(item[name] for item in items):
                raise LaneStopped("carryover lane total differs from its archived items: %s %s" % (lane, name))
    if document.get("archive_census") != archive_census(exp):
        raise LaneStopped("carryover is stale: the preserved archives differ from its census; rebuild with build_carryover.py")
    return document


def lane_carryover(document, model):
    """One lane's four components; zeros only when the VALIDATED archives hold nothing for it."""
    entry = document["lanes"].get(safe(model))
    result = {name: entry[name] for name in CARRYOVER_COMPONENTS} if entry else zero_carryover()
    result.update(archived_items=len(entry["items"]) if entry else 0, content_sha256=document["content_sha256"])
    return result


class LaneAccounting:
    """Single-process lane ownership plus thread-safe per-attempt reservations.

    Every dispatch is written before inference. An interrupted item without a final
    record halts subsequent invocations, even if a partial receipt exists. Recovery
    requires explicit reconciliation; this class never repeats an unknown call.
    The one unfinished state that resumes by itself is fully known: every dispatch
    receipted as a transport failure, so only the remaining allowance is left.

    v4: the lane cap is enforced against active cost PLUS the archived carryover.
    CARRYOVER.json is required whenever the experiment holds any superseded_*
    archive, and unconditionally with require_carryover=True, which is what the
    production runners should pass. Missing, unreadable, edited or stale: refuse.
    """
    def __init__(self, exp, model, freeze_sha256, lane_cap=10000000,
                 unknown_usage_charge=40000, per_attempt_reservation=120000,
                 transport_limit=10, carryover_path=None, require_carryover=None):
        self.exp, self.model = Path(exp), model
        self.freeze_sha256 = freeze_sha256
        self.lane = self.exp / "runs" / safe(model)
        self.canary = self.exp / "canary" / safe(model)
        self.lane_cap = lane_cap
        self.unknown_usage_charge = unknown_usage_charge
        self.per_attempt_reservation = per_attempt_reservation
        self.transport_limit = transport_limit
        self.carryover_path = Path(carryover_path) if carryover_path is not None else self.exp / CARRYOVER_NAME
        self.require_carryover = require_carryover
        self.condition = threading.Condition(threading.RLock())
        self.reservations = {}
        self.charge = 0
        self.carryover = dict(zero_carryover(), archived_items=0, content_sha256=None)
        self.archived_attempts = {}
        self.carryover_document = None
        self.attempt_epoch = None
        self.consecutive_transport = 0
        self.attempt_sequence = 0
        self.completed_records = 0
        self.stopped = None
        self.held = None
        self._entered = False

    def __enter__(self):
        self._lock = exclusive_lock(self.lane / ".lane.lock")
        self._lock.__enter__()
        try:
            self._restore()
        except BaseException:
            self._lock.__exit__(None, None, None)
            raise
        self._entered = True
        return self

    def __exit__(self, *args):
        self._entered = False
        return self._lock.__exit__(*args)

    def _records(self):
        return sorted(set(self.lane.glob("**/record.json")) | set(self.canary.glob("**/record.json")))

    def _load_carryover(self):
        self.archived_attempts = {}
        self.carryover_document = None
        # No file, no archive and no explicit requirement: a fresh experiment with nothing to carry.
        if not self.carryover_path.exists() and not self.require_carryover and not archive_census(self.exp):
            return dict(zero_carryover(), archived_items=0, content_sha256=None)
        document = load_carryover(self.exp, self.carryover_path)
        self.carryover_document = document
        for item in document["lanes"].get(safe(self.model), {}).get("items", []):
            identity = (item["split"], item["record_id"])
            self.archived_attempts[identity] = self.archived_attempts.get(identity, 0) + item["attempts_count"]
        return lane_carryover(document, self.model)

    def _restore(self):
        stop_path = self.lane / "STOP.json"
        if stop_path.exists():
            self.stopped = stop_file_reason(stop_path)
            raise LaneStopped("persisted lane stop: " + self.stopped)
        if (self.exp / HOLD_NAME).exists():
            self.held = str(self.exp / HOLD_NAME)
            raise LaneHeld("HOLD.json present: no new dispatch (%s)" % self.held)
        # A missing or unreadable carryover refuses this invocation and is not a lane stop:
        # nothing about the lane is wrong, so nothing is persisted against it.
        self.carryover = self._load_carryover()
        try:
            self.attempt_epoch = pilot_epoch.PilotEpoch(self.exp, self.model, self.freeze_sha256, self.carryover_document)
        except pilot_epoch.EpochPolicyError as exc:
            raise LaneStopped(str(exc)) from exc
        self.charge = self.carryover["charged_tokens"]
        self.consecutive_transport = self.attempt_sequence = self.completed_records = 0
        records = []
        for path in self._records():
            record = json.loads(path.read_text())
            is_canary = path.is_relative_to(self.canary)
            if record.get("requested_model") != self.model:
                self.stop("record_model_mismatch", {"path": str(path)})
                raise LaneStopped(self.stopped)
            if not is_canary and record.get("freeze_sha256") != self.freeze_sha256:
                self.stop("record_freeze_mismatch", {"path": str(path)})
                raise LaneStopped(self.stopped)
            # A completed record cannot hide a later orphan dispatch or replace
            # retained attempt usage with a smaller aggregate. Legacy records
            # without standalone receipts remain charged through the record.
            rows = attempt_receipts(path.parent)
            saved_paths = set(path.parent.glob("ATTEMPT_*.json"))
            expected_paths = {p.with_name("ATTEMPT_" + p.name[len("DISPATCH_"):])
                              for p in path.parent.glob("DISPATCH_*.json")}
            if (saved_paths != expected_paths
                    or any(saved is None or dispatch.get("record_id") != record.get("record_id")
                           or dispatch.get("split") != record.get("split")
                           or dispatch.get("freeze_sha256") != record.get("freeze_sha256")
                           for _, dispatch, saved in rows)):
                self.stop("record_attempt_receipts_mismatch", {"path": str(path)})
                raise LaneStopped(self.stopped)
            if rows and usage_summary(record, self.unknown_usage_charge) != usage_summary(
                    {"attempts": [saved["attempt"] for _, _, saved in rows]}, self.unknown_usage_charge):
                self.stop("record_attempt_usage_mismatch", {"path": str(path)})
                raise LaneStopped(self.stopped)
            self.charge += usage_summary(record, self.unknown_usage_charge)["budget_charge_tokens"]
            records.append(record)
        unfinished = sorted({path.parent for root in (self.lane, self.canary)
                             for path in root.glob("**/DISPATCH_*.json")
                             if not (path.parent / "record.json").exists()})
        consumed = []
        for directory in unfinished:
            rows = attempt_receipts(directory)
            # Resumable only when nothing is unknown and nothing can be lost: every dispatch is
            # receipted (an interrupted one through reconcile_interrupted) and every receipt is a
            # transport failure, which has no answer. A bare dispatch is an unknown call, and an
            # answered attempt without its record has lost its answer text: both halt the lane.
            if any(saved is None or derived_attempt_class(saved["attempt"]) != "TRANSPORT_FAILURE" for _, _, saved in rows):
                self.stop("unreconciled_dispatch", {"path": str(directory), "recovery": "recover receipts and reconcile explicitly; never rerun automatically"})
                raise LaneStopped(self.stopped)
            for _, dispatch, saved in rows:
                if not directory.is_relative_to(self.canary) and dispatch.get("freeze_sha256") != self.freeze_sha256:
                    self.stop("record_freeze_mismatch", {"path": str(directory)})
                    raise LaneStopped(self.stopped)
                # Consumed attempts of an unfinished item are charged now; once its record
                # exists they are charged through the record instead, never twice.
                self.charge += usage_summary({"attempts": [saved["attempt"]]}, self.unknown_usage_charge)["budget_charge_tokens"]
            consumed.append({"attempts": [saved["attempt"] for _, _, saved in rows]})
        self.completed_records = len(records)
        attempts = []
        for record in records + consumed:
            # Empty preflight records made no physical attempt and cannot reset a
            # failure streak. Legacy flat receipts remain a single attempt.
            rows = record.get("attempts") if isinstance(record.get("attempts"), list) else [record]
            for index, attempt in enumerate(rows):
                sequence = attempt.get("lane_attempt_sequence", 0)
                if isinstance(sequence, int) and not isinstance(sequence, bool) and sequence > 0:
                    self.attempt_sequence = max(self.attempt_sequence, sequence)
                    key = (1, sequence, "", 0)
                else:
                    key = (0, attempt.get("completed_time_ns", record.get("completed_time_ns", 0)),
                           record.get("finished_utc", ""), index)
                attempts.append((key, attempt))
        transport_limit_reached = False
        for _, attempt in sorted(attempts, key=lambda row: row[0]):
            if attempt.get("interrupted_by_operator") is True:
                continue  # Evidence about the operator, not the transport: neither extends nor resets a streak.
            self.consecutive_transport = self.consecutive_transport + 1 if transport_failure(attempt) else 0
            transport_limit_reached |= self.consecutive_transport >= self.transport_limit
        if self.charge >= self.lane_cap:
            self.stop("lane_token_cap", {"carryover_charged_tokens": self.carryover["charged_tokens"]})
        elif transport_limit_reached:
            self.stop("consecutive_transport_failures")
        if self.stopped:
            raise LaneStopped(self.stopped)
        self._persist()

    def summary(self):
        with self.condition:
            # budget_charge_tokens is what the lane cap sees: active cost plus archived carryover.
            return {"model": self.model, "freeze_sha256": self.freeze_sha256,
                    "budget_charge_tokens": self.charge,
                    "active_budget_charge_tokens": self.charge - self.carryover["charged_tokens"],
                    "carryover": dict(self.carryover),
                    "reserved_tokens": sum(self.reservations.values()),
                    "lane_cap": self.lane_cap, "completed_records": self.completed_records,
                    "completed_attempt_sequence": self.attempt_sequence,
                    "consecutive_transport": self.consecutive_transport, "stopped": self.stopped,
                    "held": self.held}

    def _persist(self):
        atomic_json(self.lane / "ACCOUNTING.json", self.summary())

    def stop(self, reason, details=None):
        with self.condition:
            if self.stopped is None:
                self.stopped = reason
                self.condition.notify_all()
                if not (self.lane / "STOP.json").exists():  # a teammate's STOP.json is never overwritten
                    atomic_json(self.lane / "STOP.json", {"reason": reason, "details": details,
                                "freeze_sha256": self.freeze_sha256, "time_ns": time.time_ns()})
            self._persist()
            self.condition.notify_all()

    def hold_reason(self):
        """Why no new dispatch may start now, or None; re-reads lane/STOP.json and EXP/HOLD.json.

        Never raises and never writes. A STOP.json made by someone else is adopted
        as this lane's stop; a HOLD.json is not a lane stop and lifts when removed.
        """
        with self.condition:
            stop_path = self.lane / "STOP.json"
            if self.stopped is None and stop_path.exists():
                self.stopped = stop_file_reason(stop_path)  # adopted, never rewritten
                self.condition.notify_all()
            if self.stopped:
                return "STOP.json present: " + self.stopped
            hold_path = self.exp / HOLD_NAME
            if hold_path.exists():
                self.held = str(hold_path)
                self.condition.notify_all()
                return "HOLD.json present: no new dispatch (%s)" % hold_path
            self.held = None
            return None

    def check_holds(self):
        """The raising form of hold_reason; called before EVERY reservation.

        A hold created while a loop is running therefore binds at the next dispatch.
        In-flight attempts are untouched: complete_attempt and write_record still
        settle and charge them.
        """
        with self.condition:
            reason = self.hold_reason()
            if self.stopped:
                raise LaneStopped(self.stopped)
            if reason:
                raise LaneHeld(reason)

    def reserve(self, out_dir, record_id, split, tag, reservation_tokens=None):
        amount = self.per_attempt_reservation if reservation_tokens is None else reservation_tokens
        if not isinstance(amount, int) or isinstance(amount, bool) or not 0 < amount <= self.per_attempt_reservation:
            raise ValueError("reservation must be positive and at most the per-attempt cap")
        with self.condition:
            while True:
                self.check_holds()
                if self.charge + sum(self.reservations.values()) + amount <= self.lane_cap:
                    break
                if self.reservations:
                    self.condition.wait()
                    continue
                self.stop("lane_token_cap", {"next_reservation": amount})
                raise LaneStopped(self.stopped)
            out_dir = Path(out_dir)
            if not (out_dir.resolve().is_relative_to(self.lane.resolve())
                    or out_dir.resolve().is_relative_to(self.canary.resolve())):
                raise LaneStopped("dispatch directory does not belong to this lane")
            if (out_dir / "record.json").exists():
                raise LaneStopped("record already completed: " + record_id)
            path = out_dir / ("DISPATCH_" + safe(tag) + ".json")
            if path.exists():
                self.stop("duplicate_dispatch", {"path": str(path)})
                raise LaneStopped(self.stopped)
            # A DISPATCH receipt consumes a physical attempt whatever happened afterwards.
            earlier = sorted(out_dir.glob("DISPATCH_*.json"))
            for dispatch in earlier:
                if not dispatch.with_name("ATTEMPT_" + dispatch.name[len("DISPATCH_"):]).exists():
                    self.stop("unreconciled_dispatch", {"path": str(dispatch), "recovery": "recover receipts and reconcile explicitly; never rerun automatically"})
                    raise LaneStopped(self.stopped)
            ticket = {"ticket_id": uuid.uuid4().hex, "record_id": record_id, "split": split,
                      "tag": tag, "reservation_tokens": amount, "freeze_sha256": self.freeze_sha256,
                      "out_dir": str(out_dir), "dispatched_time_ns": time.time_ns(), "requested_model": self.model}
            # The root ledger survives moving/archiving lane and canary directories.
            # Its lock covers every resumed model; no simultaneous first activation
            # can replace another lane's policy binding or consumed ticket.
            with exclusive_lock(self.exp / pilot_epoch.LOCK_NAME):
                try:
                    if self.attempt_epoch is None:
                        self.attempt_epoch = pilot_epoch.PilotEpoch(self.exp, self.model, self.freeze_sha256, self.carryover_document)
                    anchor = self.attempt_epoch.authorize(record_id, split)
                    ticket.update(self.attempt_epoch.stamp())
                    activation = self.attempt_epoch.activation(anchor, ticket)
                except pilot_epoch.EpochPolicyError as exc:
                    self.stop(exc.reason, exc.details)
                    raise LaneStopped(str(exc)) from exc
                if activation is not None:
                    # If interrupted between these writes, the missing dispatch
                    # fails closed against this retained consumed identity.
                    atomic_json(self.exp / pilot_epoch.ACTIVATION_NAME, activation)
                atomic_json(path, ticket)
            self.reservations[ticket["ticket_id"]] = amount
            self._persist()
            return ticket

    def consumed_attempts(self, out_dir):
        """[(tag, attempt)] already consumed by an unfinished item, oldest first; [] for a fresh item.

        The runner loop starts its record from these attempts and SKIPS their tags.
        A DISPATCH without an ATTEMPT receipt is an unknown call: LaneStopped.
        """
        rows = attempt_receipts(out_dir)
        bare = [tag for tag, _, saved in rows if saved is None]
        if bare:
            raise LaneStopped("unreconciled dispatch %s in %s" % (bare, out_dir))
        return [(tag, saved["attempt"]) for tag, _, saved in rows]

    def _retire_interruption_stop(self):
        """Once no dispatch is unreconciled, rename (never delete) a STOP written for the interruption."""
        stop_path = self.lane / "STOP.json"
        if not stop_path.exists() or stop_file_reason(stop_path) not in INTERRUPTION_STOPS:
            return None
        for root in (self.lane, self.canary):
            for path in root.glob("**/DISPATCH_*.json"):
                if (not (path.parent / "record.json").exists()
                        and not path.with_name("ATTEMPT_" + path.name[len("DISPATCH_"):]).exists()):
                    return None
        retired = self.lane / ("STOP_reconciled_%d.json" % time.time_ns())
        os.rename(stop_path, retired)
        if self.stopped in INTERRUPTION_STOPS:
            self.stopped = None
        return retired.name

    def reconcile_interrupted(self, out_dir, tag, evidence):
        """Explicit operator reconciliation of ONE interrupted dispatch; never a rerun.

        For a DISPATCH with no ATTEMPT and no record, writes ATTEMPT_<tag>.json as a
        TRANSPORT_FAILURE with interrupted_by_operator, usage unknown (null, never
        zero) and the RESERVATION as its charge, exactly like
        score.orphan_attempt_records. The original ticket is kept, nothing is
        deleted, and the consumed tag stays consumed: the item keeps only the
        allowance it had left. Usable without entering the lane, because a lane with
        an unreconciled dispatch cannot be entered; takes the lane lock itself then.
        """
        if not isinstance(evidence, dict) or not evidence:
            raise ValueError("reconciliation requires a non-empty evidence dict")
        json.dumps(evidence)  # must be recordable verbatim
        out_dir = Path(out_dir)
        if not (out_dir.is_relative_to(self.lane) or out_dir.is_relative_to(self.canary)):
            raise ValueError("directory does not belong to this lane: " + str(out_dir))
        lock = contextlib.nullcontext() if self._entered else exclusive_lock(self.lane / ".lane.lock")
        with lock, self.condition:
            dispatch_path = out_dir / ("DISPATCH_" + safe(tag) + ".json")
            attempt_path = out_dir / ("ATTEMPT_" + safe(tag) + ".json")
            if not dispatch_path.exists():
                raise ValueError("no dispatch to reconcile: " + str(dispatch_path))
            if attempt_path.exists() or (out_dir / "record.json").exists():
                raise LaneStopped("refusing to reconcile a dispatch that already has a receipt or a record: " + str(dispatch_path))
            ticket = json.loads(dispatch_path.read_text(encoding="utf-8"))
            reserved = ticket.get("reservation_tokens")
            if ticket.get("tag") != tag or not _count(reserved) or reserved == 0:
                raise ValueError("invalid dispatch receipt: " + str(dispatch_path))
            if not out_dir.is_relative_to(self.canary) and ticket.get("freeze_sha256") != self.freeze_sha256:
                raise LaneStopped("dispatch belongs to another freeze; archive it instead: " + str(dispatch_path))
            stop_path = self.lane / "STOP.json"
            attempt = {"tag": tag, "attempt_class": "TRANSPORT_FAILURE", "interrupted_by_operator": True,
                       "transport_failure": True, "saw_assistant_message": False, "saw_result_event": False,
                       "valid_protocol": False, "hard_stop": None, "usage_known": False,
                       "usage": {"total_attributable_tokens": None, "observed_lower_bound": 0},
                       "budget_charge_tokens": reserved,
                       "reconciliation": {"method": "LaneAccounting.reconcile_interrupted", "evidence": evidence,
                                          "lane_stop_at_reconciliation": stop_file_reason(stop_path) if stop_path.exists() else None},
                       "completed_time_ns": time.time_ns()}
            summary = usage_summary({"attempts": [attempt]}, self.unknown_usage_charge)
            atomic_json(attempt_path, {"dispatch": ticket, "attempt": attempt, "accounting": summary})
            self._retire_interruption_stop()
            if self._entered:
                self.reservations.pop(ticket.get("ticket_id"), None)
                self.charge += summary["budget_charge_tokens"]
                if self.charge >= self.lane_cap:
                    self.stop("lane_token_cap")
                self._persist()
                self.condition.notify_all()
            return attempt

    def complete_attempt(self, ticket, attempt):
        with self.condition:
            if ticket["ticket_id"] not in self.reservations:
                raise ValueError("attempt reservation is not active")
            amount = self.reservations[ticket["ticket_id"]]
            self.attempt_sequence += 1
            attempt["lane_attempt_sequence"] = self.attempt_sequence
            attempt["completed_time_ns"] = time.time_ns()
            summary = usage_summary({"attempts": [attempt]}, self.unknown_usage_charge)
            atomic_json(Path(ticket["out_dir"]) / ("ATTEMPT_" + safe(ticket["tag"]) + ".json"),
                        {"dispatch": ticket, "attempt": attempt, "accounting": summary})
            self.charge += summary["budget_charge_tokens"]
            del self.reservations[ticket["ticket_id"]]
            self.consecutive_transport = self.consecutive_transport + 1 if transport_failure(attempt) else 0
            if summary["budget_charge_tokens"] > amount:
                self.stop("attempt_exceeded_reservation", {"reserved": amount, "charged": summary["budget_charge_tokens"]})
            elif self.charge >= self.lane_cap:
                self.stop("lane_token_cap")
            elif self.consecutive_transport >= self.transport_limit:
                self.stop("consecutive_transport_failures")
            self._persist()
            self.condition.notify_all()

    def write_record(self, out_dir, record, answer):
        with self.condition:
            out_dir = Path(out_dir)
            if (out_dir / "record.json").exists():
                raise LaneStopped("refusing to overwrite completed record")
            record["freeze_sha256"] = self.freeze_sha256
            if self.attempt_epoch is not None:
                record.update(self.attempt_epoch.stamp())
            record["completed_time_ns"] = time.time_ns()
            record.update(usage_summary(record, self.unknown_usage_charge))
            out_dir.mkdir(parents=True, exist_ok=True)
            answer_path = out_dir / "answer.txt"
            with answer_path.open("w", encoding="utf-8") as handle:
                handle.write(answer)
                handle.flush()
                os.fsync(handle.fileno())
            atomic_json(out_dir / "record.json", record)
            self.completed_records += 1
            self._persist()

    def pilot_gate(self, items):
        """v4 technical-integrity gate, written beside the legacy v2/v3 counts.

        Passes iff all 20 records exist and at most TECHNICAL_GATE_LIMIT of them are
        contract violations, setup failures, unresolved transport failures or answers
        left unparsed although a well-formed candidates array is present. Budget
        exhaustion is a legitimate intention-to-treat miss: reported, never gated.
        A record whose attempts carry no attempt_class predates v4, so the v2/v3
        thresholds it was produced under still bind it: an old FAIL cannot be re-read
        as a v4 PASS.
        """
        if len(items) != 20 or len({item["record_id"] for item in items}) != 20:
            raise LaneStopped("pilot gate requires exactly 20 distinct frozen items")
        records, missing = [], []
        for item in items:
            path = self.lane / safe(item["record_id"]) / "record.json"
            if not path.exists():
                missing.append(item["record_id"])
                continue
            record = json.loads(path.read_text())
            if (record.get("freeze_sha256") != self.freeze_sha256 or record.get("record_id") != item["record_id"]
                    or record.get("split") != "pilot" or record.get("requested_model") != self.model):
                raise LaneStopped("pilot record identity/freeze mismatch: " + item["record_id"])
            records.append(record)
        by_cause, failed, exhausted, unclassified = {}, [], [], []
        for record in records:
            rid, answer = record["record_id"], None
            if record.get("valid_protocol") is True and record.get("candidates") is None:
                answer_path = self.lane / safe(rid) / "answer.txt"
                answer = answer_path.read_text(encoding="utf-8") if answer_path.exists() else None
            causes = technical_causes(record, answer)
            for cause in causes:
                by_cause.setdefault(cause, []).append(rid)
            if causes:
                failed.append(rid)  # one record counts once, whatever its causes
            attempts = record.get("attempts") if isinstance(record.get("attempts"), list) else [record]
            if any(derived_attempt_class(attempt) == "BUDGET_EXHAUSTED" for attempt in attempts):
                exhausted.append(rid)
            if any(attempt_class(attempt) is None for attempt in attempts):
                unclassified.append(rid)
        legacy = {"rule_misses": sum(map(rule_miss, records)), "output_cap_hits": sum(map(output_cap_hit, records)),
                  "thresholds": {"rule_misses": 2, "output_cap_hits": 1},
                  "binding": bool(unclassified), "unclassified_records": unclassified}
        legacy["passed"] = legacy["rule_misses"] <= 2 and legacy["output_cap_hits"] <= 1
        technical = {"threshold": TECHNICAL_GATE_LIMIT, "failed_records": len(failed), "record_ids": failed,
                     "by_cause": by_cause, "passed": len(failed) <= TECHNICAL_GATE_LIMIT}
        result = {"freeze_sha256": self.freeze_sha256, "expected": 20, "completed": len(records),
                  "missing": missing, "gate": "technical-integrity-v4",
                  "gate_disclosure": "OUTCOME-INFORMED amendment of the v2/v3 gate; the old thresholds and the actual v2/v3 gate FAILs stay on record",
                  "technical_integrity": technical,
                  "budget_exhausted": {"count": len(exhausted), "rate": round(len(exhausted) / len(records), 4) if records else None,
                                       "record_ids": exhausted, "part_of_gate": False},
                  "legacy_v2v3": legacy, "rule_misses": legacy["rule_misses"], "output_cap_hits": legacy["output_cap_hits"]}
        result["passed"] = not missing and technical["passed"] and (legacy["passed"] or not legacy["binding"])
        atomic_json(self.lane / "PILOT_GATE.json", result)
        if missing:
            raise LaneStopped("pilot incomplete; all 20 records are required")
        if not result["passed"]:
            self.stop("pilot_gate_failed", result)
            raise LaneStopped(self.stopped)
        return result
