"""Stable human-readable Adapter CLI output."""

from __future__ import annotations

from forge_cli.adapters.diagnostics import AdapterDoctorResult, AdapterValidationResult
from forge_cli.adapters.plan import AdapterPlan


def plan_lines(plan: AdapterPlan) -> tuple[str, ...]:
    """Render a deterministic plan without adding CLI policy."""
    lines = [
        f"{operation.intent.value.upper()} {operation.ownership.value} {operation.path}"
        for operation in plan.operations
    ]
    lines.extend(f"WARN {limitation}" for limitation in plan.limitations)
    lines.extend(f"CONFLICT {conflict}" for conflict in plan.conflicts)
    return tuple(lines)


def validation_lines(result: AdapterValidationResult) -> tuple[str, ...]:
    return tuple(
        f"{finding.code}: {finding.message} — {finding.remediation}"
        for finding in result.findings
    )


def doctor_lines(result: AdapterDoctorResult) -> tuple[str, ...]:
    status = {"passed": "PASS", "failed": "FAIL", "warning": "WARN"}
    return tuple(
        f"{status[check.status]} {check.id}: {check.message} — {check.remediation}"
        for check in result.checks
    )
