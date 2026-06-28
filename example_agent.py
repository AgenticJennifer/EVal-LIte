"""
A deliberately flawed toy agent so eval-lite has something real to grade.

It "summarizes" text by truncating it — which works fine for short input,
fails for long input (drops the actual point), and fails outright on empty
input. Three honest failure modes, not contrived ones.
"""


def summarize(text: str) -> str:
    if not text or not text.strip():
        return ""  # bug: should raise or return a clear error, silently fails instead

    words = text.split()
    if len(words) <= 12:
        return text.strip()

    # bug: truncating to the first 12 words loses the point of longer text
    return " ".join(words[:12]) + "..."
