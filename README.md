# Evalite

A JSONL eval logger for grading LLM and agent outputs. No dashboard, no Docker, no dependencies beyond the Python standard library. Log a run, grade it, get a pass-rate summary sliced by tag.

This exists for the gap between "eyeballing outputs in a notebook" and "standing up Langfuse." If you're solo, prototyping, and your eval set is in the dozens-to-low-hundreds of cases, a flat JSONL file you can grep, diff in git, and read by hand is often the right tool.

## Install

```bash
python -m pip install .
```

For local development:

```bash
python -m pip install -e ".[dev]"
```

## Quickstart

```python
from eval_log import log_run, grade, summary

result = my_agent.run("some input")

log_run(
    case_id="case_001",
    input="some input",
    output=result,
    expected="what a correct answer looks like, in plain language",
    tags=["my-project"],
)

grade("case_001", passed=True, note="matches expected behavior")
summary()
```

Everything lands in `eval_runs.jsonl`: one JSON object per line, append-only, human-readable, safe to commit to git if your inputs and outputs are not sensitive.

## One-Command Demo

```bash
python run_example.py
```

Expected output shape:

```text
Logged 3 example eval cases to eval_runs.jsonl
Summary by tag:
  toy-summarizer: 2 passed, 1 failed, 66.7% pass rate
```

This runs a deliberately flawed toy summarizer against three cases, logs each one, grades it, and prints a tag-sliced summary. Read `example_agent.py` to see the intentional failure mode before trusting any eval tool's verdict on your own agent.

## Run Tests

```bash
pip install pytest
pytest tests/ -v
```

## What This Is Not

This is not an observability platform. There's no dashboard, tracing UI, alerting, multi-user collaboration, or production monitoring. If you need those, graduate to something like [Langfuse](https://langfuse.com) or a paid platform once a team needs the same dashboard.

The honest ceiling on this tool: it works because someone is reading every failure by hand. The moment that stops being true, this tool stops being enough.

## License

MIT. See [LICENSE](LICENSE) for details.
