# Test Strategy — CHG-0018

## Objective

This Change is overwhelmingly executable (a new Adapter package, two Core
fixes, a new test suite) unlike `CHG-0016`/`CHG-0017`, which were mostly
prose. TDD applies fully. The ADR and one Contract rule are the only
non-executable deliverables (Protocol §19 `not_applicable`).

## Strategy

Four TDD cases:

## TDD-001 — Core-leak fixes are pure relocation/generalization

**Covers:** FR-001, FR-002, NFR-002.

**RED:** `from forge_cli.adapters.assessment import assess_invariant`
fails (`ModuleNotFoundError`) against the unmodified tree. A new test
asserting `AdapterConfiguration(adapter_id="claude-code",
target=".codex/anything")` no longer raises fails (it currently does).

**GREEN:** After relocation/generalization, both pass; the full
pre-existing Codex suite passes unchanged except the one intentionally-
updated `test_adapter_configuration.py` case.

**Expected Result:** Zero behavior change to Codex; `.codex` acceptance
widens at the generic layer only, still rejected at Codex's own layer.

## TDD-002 — Claude Code Adapter projects all three mechanisms correctly

**Covers:** FR-003–FR-006, AC-003, AC-004.

**RED:** Tests asserting `ClaudeCodeDriver().project(context)` produces
`.claude/skills/forge/SKILL.md` (+ references), `.claude/CLAUDE.md`
(pointer content, not full Contract text), and a `hooks:` frontmatter
block in `SKILL.md` plus a hook script artifact — fail today (module
doesn't exist).

**GREEN:** Implement `projection.py`/`driver.py`/`descriptor.py`/
`evidence.py`/`targets.py`. Assert: CLAUDE.md pointer does not contain the
full Contract text (INV-001); the hook script's pattern excludes `git
add`/`git commit`/`cat`/`ls`/`grep` (Specification Review SR-001) and
matches `sed -i`/`perl -i`/`truncate`/redirection against the three named
paths.

**Expected Result:** All three mechanisms present, content-correct,
`forge_owned`.

## TDD-003 — Shared conformance suite passes both drivers

**Covers:** FR-008, FR-009 (C-074), AC-006.

**RED:** The parametrized suite fails to collect/run against
`ClaudeCodeDriver()` before T-006/T-007 land (driver doesn't exist /
isn't registered).

**GREEN:** Both `CodexDriver()` and `ClaudeCodeDriver()` pass the same
assertions (manifest shape, protocol-compatibility checks, ownership/
drift/plan determinism, capability-limitation evaluation) via
`@pytest.mark.parametrize`.

**Expected Result:** Genuine driver-agnostic coverage, not two duplicated
Codex-only and Claude-Code-only suites with no shared assertions.

## TDD-004 — Repository-wide baseline unchanged

**Covers:** AC-007, CON-003.

**RED:** Baseline capture, not a failing assertion (matches every prior
Change's own TDD-00x baseline-capture precedent).

**GREEN:** `forge validate`/`forge doctor`/`pytest -q` report the
identical overall status against every historical Change after
Implementation, plus a successful result against `CHG-0018` itself.

**Baseline recorded before Implementation** (HEAD `023649a`, working tree
otherwise clean except this Change's own new, untracked planning
directory): `forge validate` reports **"Forge project is valid"** (exit
0); `forge doctor` reports all 7 checks `PASS`; `pytest -q` (full suite)
reports **437 passed**. Any regression against these exact figures during
Implementation is investigated before Verification proceeds.

## Non-mechanical Validation (Strict Review, not automated tests)

- `capabilities.yml`'s six evidence entries against the actual fetched
  `code.claude.com` pages (are the citations real and do they say what's
  claimed).
- The ADR against `docs/adr/`'s own style precedent and against DEC-001/
  002/003's actual Architecture-stage records.
- Whether the dogfooded Golden Path evidence (`examples/
  golden-path-claude-code/`) is genuine live-session output, not narrated.
- NFR-001 (no vendor-specific concept in the generic Core) — a repo-wide
  grep-based check, not just a unit test assertion, since the claim is
  about absence across the whole `adapters/*.py` surface.

## Completion Criteria

All of AC-001 through AC-010 satisfied; TDD-001–004 GREEN; Non-mechanical
Validation items reviewed and accepted at Strict Review; `tdd-evidence.yml`/
`traceability.yml` produced from real Implementation evidence.
