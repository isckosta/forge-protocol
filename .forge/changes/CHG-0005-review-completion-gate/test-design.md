# Test Design — CHG-0005

Behavioral requirement: every canonical Flow completion gate must include `blocking_review_threads_resolved`.

Regression test: `tests/unit/test_review_completion_gate.py` loads FULL, STANDARD, and FAST flow definitions and requires that gate token in each `before_completion.require` list.

The Codex nested-resource cleanup is behavior-preserving: the existing rejection cases remain unchanged and a positive nested-relative case documents the accepted contract.