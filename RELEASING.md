# Releasing Forge

This document is the manual checklist for cutting a real Forge release.
It exists so the first real release doesn't have to invent this process
under time pressure. **Following this checklist does not itself publish
anything** — every step here is either local/reversible or an explicit,
separate human action (pushing a tag, publishing a GitHub Release).
Nothing in this repository's own Change history has ever completed this
checklist for real.

## Version scheme

Forge CLI versions follow [PEP 440](https://peps.python.org/pep-0440/):
`0.1.0a1`, `0.1.0b1`, `1.0.0rc1`, `1.0.0` — not hyphenated forms like
`0.1.0-alpha.1`. PEP 440 is what `pip`/`build`/`hatchling` actually parse
and what PyPI displays and sorts by; a hyphenated string is not a valid
version identifier for this ecosystem.

Forge has four independent version axes (Protocol, Schema, CLI, Adapter).
See `protocol/compatibility.md` for the authoritative definition of each
— this document does not restate it.

`src/forge_cli/version.py`'s `CLI_VERSION` is the single source of truth
for the CLI/package version; `pyproject.toml` reads it dynamically via
`[tool.hatch.version]`. Bump `CLI_VERSION` there and nowhere else.

## Release progression

```
0.1.0a1  -> external real-world validation
0.1.0b1  -> stabilization and fixes
1.0.0rc1 -> contract freeze; blocker/major fixes only
1.0.0
```

Additional prereleases are evidence-driven, not deadline-driven
(`ROADMAP.md`).

## Checklist

1. Confirm `forge validate`, `forge doctor`, and `pytest -q` are clean on
   `main`.
2. Bump `CLI_VERSION` in `src/forge_cli/version.py`.
3. Rename `CHANGELOG.md`'s current `## Unreleased` heading to
   `## [<version>] - <YYYY-MM-DD>` and add a fresh empty `## Unreleased`
   above it.
4. Commit both changes.
5. Tag the commit: `git tag v<version>` (e.g. `git tag v0.1.0a1`), then
   `git push origin v<version>`.
6. Create a GitHub Release from that tag, with release notes drawn from
   the `CHANGELOG.md` section just cut.
7. Publishing the Release triggers `.github/workflows/publish.yml`,
   which builds the wheel and sdist, smoke-tests both offline, and
   publishes to PyPI via OIDC trusted publishing.

## Prerequisite (one-time, PyPI-side, not performed by this repository)

Before step 7 can ever succeed, this project must be registered as a
**trusted publisher** on PyPI (project settings → Publishing → GitHub
Actions), naming this repository and the `publish.yml` workflow. This is
a manual action on PyPI's own site — nothing in this repository can do
it, and `publish.yml` has no fallback token-based publish path by design
(no long-lived `PYPI_API_TOKEN` is stored anywhere).
