---
forge:
  artifact: intent
  schema: 1
change: CHG-0022
status: active
---

# Intent — Change Scaffolding CLI

## Summary

Add `forge change new <slug>` so a repository can begin a Forge Change from
the installed CLI with a deterministic, Flow-appropriate artifact scaffold.

## Problem

Forge currently has infrastructure commands and Adapter management, but no
command for creating a Change workspace. A developer must hand-copy an old
Change and edit its identifier, frontmatter, manifest, and artifact set. That
manual process is error-prone: it can select the wrong Flow artifacts, omit
required frontmatter, reuse an occupied Change number, or invent values that
do not satisfy the installed Protocol schemas. The external validation that
motivated roadmap item #2 demonstrated the practical cost of this gap.

## Desired Outcome

From an initialized Forge project, `forge change new <slug>` shows a complete
read-only creation plan, then creates the next available
`.forge/changes/CHG-NNNN-<slug>/` directory with schema-valid placeholder
artifacts for the project's active Flow. The command works offline and from
the installed wheel, and a collision or invalid request leaves the workspace
unchanged.

## Scope

- Add a `change` Typer sub-application and the `new` command.
- Resolve the active Flow from the project's configured default Flow and the
  canonical Flow resources packaged with Forge.
- Scan `.forge/changes/` at runtime to select the next free four-digit Change
  number; no number is reserved in source code.
- Generate the artifact set required by the active STANDARD or FULL Flow,
  including correct `forge:` frontmatter and useful placeholder sections.
- Generate an initially valid `forge/change@2` manifest with pending lifecycle
  state and only schema-valid prefilled values.
- Reuse the existing plan-before-mutation output convention, including
  `CREATE forge_owned <path>` lines before any filesystem mutation.
- Add offline CLI/unit/integration coverage and installed-wheel coverage.
- Update this Change's documentation impact and the roadmap status table.

## Out of Scope

- An interactive wizard or prompts for requirements, classification, or
  Decisions.
- Executing Specification, Implementation, Verification, Review, or
  Completion stages from the CLI.
- Changes to `protocol/schemas/*.json`, canonical Flow definitions, or the
  Engineering Contract.
- Roadmap remediation items #3–#10.
- Reserving Change numbers in a registry, database, or Git ref.

## Success Criteria

- A valid initialized project can scaffold a Change offline from the CLI and
  from a built wheel.
- The selected artifact filenames exactly follow the active canonical Flow's
  `stages:` requirements, with STANDARD and FULL distinguishable in tests.
- Every generated Markdown artifact has the required `forge:` frontmatter;
  the generated manifest passes the repository's current schema validation.
- The command prints all creation operations before writing any file.
- Existing Change directories cause deterministic next-number selection, and
  an invalid slug or destination collision causes no mutation.
- The full test suite, `forge validate`, and `forge doctor` remain green.
