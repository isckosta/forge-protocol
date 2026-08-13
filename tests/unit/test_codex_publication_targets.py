from __future__ import annotations

try:
    from forge_cli.adapters.codex.targets import (
        PublicationTargetSource,
        resolve_publication_target,
    )
except ImportError:
    PublicationTargetSource = None
    resolve_publication_target = None


def _require_behavior() -> None:
    assert PublicationTargetSource is not None, "Codex publication target source is not implemented yet"
    assert resolve_publication_target is not None, "Codex publication target resolution is not implemented yet"


def test_no_target_is_invented_without_configuration_or_evidence() -> None:
    _require_behavior()
    assert resolve_publication_target() is None


def test_explicit_target_is_resolved_with_explicit_provenance() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/forge-codex.md")
    assert target is not None
    assert target.path == "tools/forge-codex.md"
    assert target.source is PublicationTargetSource.EXPLICIT


def test_evidence_backed_target_is_resolved_with_evidence_provenance() -> None:
    _require_behavior()
    target = resolve_publication_target(evidence_target="vendor/forge-codex.md")
    assert target is not None
    assert target.path == "vendor/forge-codex.md"
    assert target.source is PublicationTargetSource.EVIDENCE


def test_explicit_target_takes_precedence_over_packaged_evidence() -> None:
    _require_behavior()
    target = resolve_publication_target(
        explicit_target="project/codex.md",
        evidence_target="vendor/codex.md",
    )
    assert target is not None
    assert target.path == "project/codex.md"
    assert target.source is PublicationTargetSource.EXPLICIT


def test_unsafe_target_shape_is_rejected_before_generic_planning() -> None:
    _require_behavior()
    for path in ("", "/absolute.md", "../escape.md", "a/../escape.md", r"a\b.md"):
        try:
            resolve_publication_target(explicit_target=path)
        except ValueError:
            continue
        raise AssertionError(f"unsafe target accepted: {path!r}")
