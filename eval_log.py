"""
Minimal eval logger. No infra, no dashboard, no dependencies beyond stdlib.

Usage pattern:

    from eval_log import log_run, grade, summary

    result = my_agent.run(task_input)
    log_run(
        case_id="logistics_os_route_planner_01",
        input=task_input,
        output=result,
        expected="should call route_optimizer then return ETA",
        tags=["logistics-os", "agent"],
    )

Then grade each logged case by hand (or with a grading fn) and call summary()
to get a pass-rate table across all cases, sliced by tag.

Everything lands in eval_runs.jsonl in this directory. One JSON object per
line. Append-only, human-readable, greppable, diffable in git.
"""

import json
import os
import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent / "eval_runs.jsonl"


def log_run(case_id: str, input, output, expected: str = "", tags: list = None, trajectory: list = None):
    """
    Append one eval case to the log.

    case_id: stable identifier so you can re-run the same case later and diff results.
    input: whatever you sent the agent (string, dict, whatever — must be JSON-serializable).
    output: what the agent returned.
    expected: plain-language description of what a correct answer/trajectory looks like.
    tags: free-form labels for slicing later (project name, agent name, task type).
    trajectory: optional list of steps/tool calls the agent took, if you're evaluating an agent
                and not just a final answer. Each item can be a dict like
                {"tool": "route_optimizer", "args": {...}, "result": "..."}.
    """
    record = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "case_id": case_id,
        "input": input,
        "output": output,
        "expected": expected,
        "tags": tags or [],
        "trajectory": trajectory or [],
        "grade": None,       # filled in later by grade()
        "grader_note": None,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def grade(case_id: str, passed: bool, note: str = ""):
    """
    Grade the most recent ungraded entry matching case_id.
    Rewrite-in-place: reads the whole file, patches the matching record, writes back.
    Fine at the scale this tool is meant for (hundreds, not millions, of rows).
    """
    if not LOG_PATH.exists():
        raise FileNotFoundError("No eval_runs.jsonl yet — log a run first.")

    lines = LOG_PATH.read_text().splitlines()
    records = [json.loads(line) for line in lines]

    target_idx = None
    for i in reversed(range(len(records))):
        if records[i]["case_id"] == case_id and records[i]["grade"] is None:
            target_idx = i
            break

    if target_idx is None:
        raise ValueError(f"No ungraded record found for case_id={case_id!r}")

    records[target_idx]["grade"] = "pass" if passed else "fail"
    records[target_idx]["grader_note"] = note

    with open(LOG_PATH, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    return records[target_idx]


def summary(tag_filter: str = None):
    """
    Print pass/fail counts overall and per-tag. Pass tag_filter to restrict
    to cases that include that tag.
    """
    if not LOG_PATH.exists():
        print("No eval runs logged yet.")
        return

    records = [json.loads(line) for line in LOG_PATH.read_text().splitlines()]
    if tag_filter:
        records = [r for r in records if tag_filter in r.get("tags", [])]

    graded = [r for r in records if r["grade"] is not None]
    ungraded = [r for r in records if r["grade"] is None]
    passed = [r for r in graded if r["grade"] == "pass"]
    failed = [r for r in graded if r["grade"] == "fail"]

    print(f"Total cases: {len(records)}  |  Graded: {len(graded)}  |  Ungraded: {len(ungraded)}")
    if graded:
        pass_rate = len(passed) / len(graded) * 100
        print(f"Pass rate: {len(passed)}/{len(graded)} ({pass_rate:.1f}%)")

    # breakdown by tag
    tag_buckets = {}
    for r in graded:
        for t in r.get("tags", []):
            tag_buckets.setdefault(t, {"pass": 0, "fail": 0})
            tag_buckets[t][r["grade"]] += 1

    if tag_buckets:
        print("\nBy tag:")
        for tag, counts in sorted(tag_buckets.items()):
            total = counts["pass"] + counts["fail"]
            rate = counts["pass"] / total * 100 if total else 0
            print(f"  {tag:30s} {counts['pass']:>3}/{total:<3} ({rate:.0f}%)")

    if failed:
        print("\nFailed cases:")
        for r in failed:
            print(f"  [{r['case_id']}] {r['grader_note'] or '(no note)'}")


if __name__ == "__main__":
    # quick smoke test
    log_run(
        case_id="demo_001",
        input={"task": "summarize this doc"},
        output="A two-sentence summary...",
        expected="concise, factually grounded summary under 50 words",
        tags=["demo"],
    )
    grade("demo_001", passed=True, note="concise and accurate")
    summary()
