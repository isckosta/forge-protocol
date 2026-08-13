"""Immutable, harness-agnostic Adapter diagnostic result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


AdapterCheckStatus = Literal["passed", "failed", "warning"]

_CHECK_ORDER = {
    "configuration": 0,
    "compatibility": 1,
    "target": 2,
    "installation": 3,
    "generated_drift": 4,
    "conformance": 5,
    "limitations": 6,
}


@dataclass(frozen=True)
class AdapterCheck:
    id: str
    status: AdapterCheckStatus
    code: str
    message: str
    remediation: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"passed", "failed", "warning"}:
            raise ValueError(f"Unsupported Adapter diagnostic status: {self.status!r}.")
        if self.status == "failed" and not self.remediation:
            raise ValueError("A failed Adapter diagnostic requires remediation.")


@dataclass(frozen=True)
class AdapterFinding:
    id: str
    code: str
    message: str
    remediation: str


@dataclass(frozen=True)
class AdapterValidationResult:
    passed: bool
    findings: tuple[AdapterFinding, ...]


@dataclass(frozen=True)
class AdapterDoctorResult:
    passed: bool
    checks: tuple[AdapterCheck, ...]


def diagnose_adapter(checks: Iterable[AdapterCheck]) -> AdapterDoctorResult:
    """Normalize independently observed checks into a stable Doctor result."""
    ordered = tuple(
        sorted(
            checks,
            key=lambda item: (_CHECK_ORDER.get(item.id, len(_CHECK_ORDER)), item.id),
        )
    )
    return AdapterDoctorResult(
        passed=all(item.status != "failed" for item in ordered),
        checks=ordered,
    )


def validate_adapter(result: AdapterDoctorResult) -> AdapterValidationResult:
    """Convert failed Doctor checks to CLI-serializable validation findings."""
    findings = tuple(
        AdapterFinding(
            id=item.id,
            code=item.code,
            message=item.message,
            remediation=item.remediation,
        )
        for item in result.checks
        if item.status == "failed"
    )
    return AdapterValidationResult(passed=not findings, findings=findings)
