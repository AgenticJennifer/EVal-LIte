# eval-lite

A JSONL eval logger for grading LLM and agent outputs. No dashboard, no
Docker, no dependencies beyond the Python standard library. Log a run,
grade it, get a pass-rate summary sliced by tag.

This exists for the gap between "eyeballing outputs in a notebook" and
"standing up Langfuse." If you're solo, prototyping, and your eval set is
in the dozens-to-low-hundreds of cases, a flat JSONL file you can grep,
diff in git, and read by hand is often the right tool — not a placeholder
until you get a real one.

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

# After reading the output yourself:
grade("case_001", passed=True, note="matches expected behavior")

summary()
```

Everything lands in `eval_runs.jsonl` — one JSON object per line,
append-only, human-readable, safe to commit to git if your inputs/outputs
aren't sensitive.

## Try the example

```bash
python run_example.py
```

This runs a deliberately flawed toy "summarizer" against three cases,
logs each one, grades it, and prints a tag-sliced summary. The point of
the example is the failure modes are real, not contrived — read
`example_agent.py` to see what's actually wrong with it before trusting
any eval tool's verdict on your own agent.

## Run tests

```bash
pip install pytest
pytest tests/ -v
```

## What this is not

This is not an observability platform. There's no dashboard, no tracing
UI, no alerting, no multi-user collaboration, no production monitoring.
If you need any of those — or your trace volume is high enough that a
flat file stops being skimmable — graduate to something like
[Langfuse](https://langfuse.com) (self-hostable, MIT-licensed, free) or
a paid platform once a team needs to look at the same dashboard.

The honest ceiling on this tool: it works because someone is reading
every failure by hand. The moment that stops being true, this tool stops
being enough.

## License

MIT
