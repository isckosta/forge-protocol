---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0017
status: complete
---
# Knowledge Capture — CHG-0017

- **Manually deleting Adapter-generated files and re-running `forge
  adapter install` trips drift protection — this is the mechanism
  working as intended, not friction to route around.** While verifying
  the explicit-`interaction.language` case end-to-end, `rm -rf .agents`
  followed by `forge adapter install codex` failed with
  `E_FORGE_ADAPTER_DRIFT` (the on-disk installation record still expected
  the deleted files). The correct path to re-project changed output
  against an *existing* installation is `forge adapter update`, and even
  that refuses when the prior state was hand-mutated outside the CLI —
  it does not silently trust a directory that no longer matches its own
  record. The clean way to exercise both the `auto` and explicit-language
  cases end-to-end was two separate fresh scratch repositories, not one
  repository mutated twice by hand. General lesson: this Change's own
  C-072/C-073 argue Core cannot verify a Harness's actual behavior;
  Adapter drift protection is the same discipline applied one layer
  down — Core does not trust a working tree it did not itself produce
  and cannot revalidate that it still matches.

- **Directed exploration of a structurally similar prior Change before
  Architecture prevents the file-touch-point undercount `CHG-0016`'s own
  knowledge-capture recorded against itself.** `CHG-0016`'s Plan named
  only `projection.py` for its new field and discovered three more real
  touch points (`driver.py`, both `service.py` construction sites) only
  during Implementation. This Change's Discovery traced `CHG-0016`'s
  actual mechanism end-to-end first (all four files, by name and line)
  before Architecture was written, so this Change's own Plan/Architecture
  named all four touch points correctly from the start — confirmed by
  `verification.md`'s "What Required Correction During Implementation
  Itself" having nothing to report, unlike `CHG-0016`'s own. Worth
  recording as a positive confirmation, not only a failure mode: tracing
  a real precedent mechanism concretely is cheap relative to discovering
  its shape by trial during Implementation.

- **A schema and Contract edit landing in the same commit batch as the
  test-strategy that names them makes it easy to skip RED for the schema
  layer specifically, even while the primary executable-code TDD cycle
  stays disciplined.** `tdd-evidence.yml`'s TDD-001 notes this plainly:
  the four `test_project_configuration.py` companion cases were written
  after `protocol/schemas/project.schema.json`'s edit had already landed
  (T-001, batched with T-002–T-004's Contract/Specification/ADR text),
  so no RED was observed for them — unlike the genuine RED this Change's
  three projection-layer tests did produce. The declarative nature of a
  JSON Schema edit makes this easy to rationalize as harmless, but the
  honest record is a process gap, not a deliberate baseline-capture
  choice like `TDD-002`'s. General lesson: even a one-line, obviously-
  correct schema addition benefits from being sequenced after its own
  test, not batched ahead of it purely because it "obviously" belongs
  with the surrounding prose edits.
