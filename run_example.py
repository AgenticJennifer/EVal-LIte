"""
Runs example_agent.summarize() against a few cases, logs each one, grades
it by hand (this is the point — read every failure before automating
anything), and prints a summary.

Run: python run_example.py
"""

from eval_log import log_run, grade, summary
from example_agent import summarize

CASES = [
    {
        "case_id": "short_input",
        "input": "The agent works fine on short text.",
        "expected": "returns the input unchanged, since it's already short",
    },
    {
        "case_id": "empty_input",
        "input": "",
        "expected": "should signal an error or empty-input case clearly, not silently return ''",
    },
    {
        "case_id": "long_input_loses_meaning",
        "input": (
            "The quarterly report shows revenue grew eight percent year over year, "
            "driven primarily by the logistics division, but operating costs also rose "
            "due to fuel price increases in the second half of the year, which the board "
            "flagged as the key risk going into next quarter."
        ),
        "expected": "should preserve the actual conclusion (revenue grew, but costs rose due to fuel), not just the first 12 words",
    },
]


def run():
    for case in CASES:
        output = summarize(case["input"])
        log_run(
            case_id=case["case_id"],
            input=case["input"],
            output=output,
            expected=case["expected"],
            tags=["example", "summarizer"],
        )
        print(f"\n[{case['case_id']}]")
        print(f"  input:    {case['input'][:60]!r}{'...' if len(case['input']) > 60 else ''}")
        print(f"  output:   {output!r}")
        print(f"  expected: {case['expected']}")

    # Grading happens after you've actually read the outputs above —
    # this is the manual step the eval-lite README argues you should not skip.
    grade("short_input", passed=True, note="unchanged, correct")
    grade("empty_input", passed=False, note="silently returns '' instead of signaling empty input")
    grade("long_input_loses_meaning", passed=False, note="truncates to first 12 words, drops the actual conclusion about costs/fuel")

    print("\n" + "=" * 50)
    summary(tag_filter="example")


if __name__ == "__main__":
    run()
