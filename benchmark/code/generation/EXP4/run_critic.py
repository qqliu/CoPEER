"""Shared pure generation helpers; extracted verbatim from the frozen driver."""
import time

def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def count(value):
    """A token count from the stream; anything a stream should never carry there is 0, not a crash."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < float("inf"): return 0
    return int(value)

def should_retry(attempt):
    """The single transport retry: only a TRANSPORT_FAILURE, never an observed answer/result, a spent budget or a violation."""
    if "attempt_class" in attempt:
        return attempt["attempt_class"] == "TRANSPORT_FAILURE"
    # A receipt older than v4 carries no class: the original predicate.
    return (not attempt["saw_assistant_message"] and not attempt["saw_result_event"]
            and (attempt["hard_stop"] is None or attempt["hard_stop"].get("reason") == "wall_clock_cap"))
