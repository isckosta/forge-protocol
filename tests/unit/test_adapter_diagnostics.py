from __future__ import annotations

from forge_cli.adapters.diagnostics import (
    AdapterCheck,
    diagnose_adapter,
    validate_adapter,
)


def test_diagnosis_uses_stable_check_order_and_validation_converts_failures() -> None:
    result = diagnose_adapter(
        (
            AdapterCheck(
                id="limitations",
                status="warning",
                code="W_FORGE_ADAPTER_LIMITATION",
                message="Capability limitation is represented for skill instructions.",
            ),
            AdapterCheck(
                id="installation",
                status="failed",
                code="E_FORGE_ADAPTER_NOT_INSTALLED",
                message="Adapter is not installed.",
                remediation="Run `forge adapter install codex`.",
            ),
            AdapterCheck(
                id="configuration",
                status="passed",
                code="OK",
                message="Configuration is valid.",
            ),
        )
    )

    validation = validate_adapter(result)

    assert [item.id for item in result.checks] == [
        "configuration",
        "installation",
        "limitations",
    ]
    assert result.passed is False
    assert validation.passed is False
    assert validation.findings[0].id == "installation"
    assert validation.findings[0].code == "E_FORGE_ADAPTER_NOT_INSTALLED"
    assert validation.findings[0].remediation == "Run `forge adapter install codex`."


def test_limitations_are_warnings_not_enforcement() -> None:
    result = diagnose_adapter(
        (
            AdapterCheck(
                id="limitations",
                status="warning",
                code="W_FORGE_ADAPTER_LIMITATION",
                message="Capability limitation is represented for skill instructions.",
            ),
        )
    )

    assert result.passed is True
    assert any(item.status == "warning" for item in result.checks)
    assert all(
        "enforced" not in item.message.lower()
        for item in result.checks
        if item.status == "warning"
    )
