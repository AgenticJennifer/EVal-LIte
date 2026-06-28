import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import eval_log  # noqa: E402


def setup_function():
    """Each test gets a clean log file."""
    if eval_log.LOG_PATH.exists():
        eval_log.LOG_PATH.unlink()


def teardown_function():
    if eval_log.LOG_PATH.exists():
        eval_log.LOG_PATH.unlink()


def test_log_run_writes_valid_json():
    record = eval_log.log_run(
        case_id="t1", input="hello", output="world", expected="greeting", tags=["test"]
    )
    assert record["case_id"] == "t1"
    assert record["grade"] is None

    lines = eval_log.LOG_PATH.read_text().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["case_id"] == "t1"
    assert parsed["output"] == "world"


def test_grade_patches_correct_record():
    eval_log.log_run(case_id="t1", input="a", output="b")
    eval_log.log_run(case_id="t2", input="c", output="d")

    eval_log.grade("t1", passed=True, note="looks right")

    lines = [json.loads(line) for line in eval_log.LOG_PATH.read_text().splitlines()]
    t1 = next(r for r in lines if r["case_id"] == "t1")
    t2 = next(r for r in lines if r["case_id"] == "t2")

    assert t1["grade"] == "pass"
    assert t1["grader_note"] == "looks right"
    assert t2["grade"] is None  # untouched


def test_grade_raises_on_missing_case():
    eval_log.log_run(case_id="t1", input="a", output="b")
    try:
        eval_log.grade("nonexistent", passed=True)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_grade_only_matches_ungraded_entry():
    """If the same case_id is logged twice, grading should hit the most
    recent ungraded one, not silently re-grade an already-graded one."""
    eval_log.log_run(case_id="t1", input="a", output="b")
    eval_log.grade("t1", passed=True, note="first pass")
    eval_log.log_run(case_id="t1", input="a2", output="b2")
    eval_log.grade("t1", passed=False, note="second pass")

    lines = [json.loads(line) for line in eval_log.LOG_PATH.read_text().splitlines()]
    assert lines[0]["grade"] == "pass"
    assert lines[0]["grader_note"] == "first pass"
    assert lines[1]["grade"] == "fail"
    assert lines[1]["grader_note"] == "second pass"


def test_summary_does_not_crash_on_empty_log(capsys):
    eval_log.summary()
    captured = capsys.readouterr()
    assert "No eval runs logged yet" in captured.out


def test_summary_respects_tag_filter(capsys):
    eval_log.log_run(case_id="t1", input="a", output="b", tags=["alpha"])
    eval_log.log_run(case_id="t2", input="c", output="d", tags=["beta"])
    eval_log.grade("t1", passed=True)
    eval_log.grade("t2", passed=True)

    eval_log.summary(tag_filter="alpha")
    captured = capsys.readouterr()
    assert "Total cases: 1" in captured.out
