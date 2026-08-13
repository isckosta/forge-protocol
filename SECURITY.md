# Forge Security Policy

## Reporting vulnerabilities

Do not publicly disclose an unpatched vulnerability. Use the repository's configured private security reporting mechanism.

Include the affected version, reproduction details, expected impact, and suggested mitigation when available.

## Scope

Security issues may include unsafe command execution, arbitrary file overwrite, path traversal, malicious configuration execution, unsafe Adapter generation, supply-chain risks, credential disclosure, and validation bypasses with security consequences.

## Harness security

Forge defines engineering Policies. Forge does not automatically provide an execution sandbox.

Filesystem, network, process, and shell privileges depend on the selected coding Harness. Forge must not claim guarantees the Harness does not provide.

## Secrets

Forge Artifacts should not require committed secrets.

## Dependencies

New runtime dependencies require justification. The CLI should maintain a small dependency surface.

## Supported versions

During pre-1.0 development, security fixes target the latest development release unless maintainers state otherwise.
