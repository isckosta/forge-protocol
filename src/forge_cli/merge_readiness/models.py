from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Verdict = Literal["ready", "blocked", "operational"]
CheckStatus = Literal["pass", "fail"]


@dataclass(frozen=True)
class MergeReadinessRequest:
    base_revision: str
    head_revision: str


@dataclass(frozen=True)
class ReadinessDiagnostic:
    code: str
    message: str
    change_id: str | None = None
    artifact: str | None = None
    expected: str | None = None
    actual: str | None = None


@dataclass(frozen=True)
class ReadinessCheck:
    check_id: str
    status: CheckStatus
    change_id: str | None = None
    message: str = ""


@dataclass(frozen=True)
class MergeReadinessEvaluation:
    request: MergeReadinessRequest
    affected_changes: tuple[str, ...]
    checks: tuple[ReadinessCheck, ...]
    diagnostics: tuple[ReadinessDiagnostic, ...]
    verdict: Verdict
