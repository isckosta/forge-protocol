from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

from forge_cli.adapters.codex.projection import generate_codex_skill_bundle
from forge_cli.capabilities.model import Capability


@dataclass(frozen=True)
class GitHubCopilotProjectionResource:
    name: str
    content: str
    digest: str
    executable: bool = False


@dataclass(frozen=True)
class GitHubCopilotProjectionBundle:
    adapter_id: str
    flow_id: str
    resources: tuple[GitHubCopilotProjectionResource, ...]


def _resource(name: str, content: str, *, executable: bool = False) -> GitHubCopilotProjectionResource:
    normalized = content.rstrip() + "\n"
    return GitHubCopilotProjectionResource(
        name=name,
        content=normalized,
        digest=sha256(normalized.encode("utf-8")).hexdigest(),
        executable=executable,
    )


def _pointer() -> str:
    return "\n".join((
        "<!-- forge:begin -->",
        "## Forge",
        "",
        "This repository is Forge-governed. Use the `forge` Agent Skill at "
        "`.github/skills/forge/SKILL.md` to discover the effective workflow "
        "and repository-native references. This pointer intentionally does not "
        "restate Forge requirements.",
        "<!-- forge:end -->",
    ))


def _hook_config() -> str:
    return json.dumps({
        "version": 1,
        "hooks": {
            "preToolUse": [{
                "type": "command",
                "bash": ".github/hooks/forge-review-control.sh",
                "timeoutSec": 10,
            }],
        },
    }, indent=2)


def _hook_script() -> str:
    return """#!/bin/sh
set -eu

input=$(cat)
normalized=$(printf '%s' "$input" | sed \
  -e 's#\\\\/#/#g' \
  -e 's#\\\\/#/#g' \
  -e 's#\\\\/#/#g' \
  -e 's#\\\\u002[fF]#/#g' \
  -e 's#\\\\u002[fF]#/#g' \
  -e 's#\\\\u002[fF]#/#g' \
  -e 's#\\\\u002[eE]#.#g' \
  -e 's#\\\\u002[eE]#.#g' \
  -e 's#\\\\u002[eE]#.#g' \
  -e 's#\\\\u003[bB]#;#g' \
  -e 's#\\\\u003[bB]#;#g' \
  -e 's#\\\\u003[bB]#;#g' \
  -e 's#\\\\u0026#\\&#g' \
  -e 's#\\\\u007[cC]#|#g' \
  -e 's#\\\\u003[cC]#<#g' \
  -e 's#\\\\u003[eE]#>#g' \
  -e 's#\\\\u0060#`#g' \
  -e 's#\\\\u0024#$#g' \
  -e 's#\\\\u0028#(#g' \
  -e 's#\\\\u0029#)#g')
tool=$(printf '%s' "$input" | sed -n \
  's/.*"toolName"[[:space:]]*:[[:space:]]*"\\([^"]*\\)".*/\\1/p')
[ -n "$tool" ] || tool=$(printf '%s' "$input" | sed -n \
  's/.*"tool_name"[[:space:]]*:[[:space:]]*"\\([^"]*\\)".*/\\1/p')

change_dir='\\.forge/'
deny() {
  printf '%s\n' '{"permissionDecision":"deny","permissionDecisionReason":"Forge review-control metadata must remain repository-native and auditable; use the normal Forge Change workflow."}'
  exit 0
}
printf '%s' "$input" | grep -Eq '\\u[0-9A-Fa-f]{4}' && deny
printf '%s' "$input" | grep -Eq '\\\\n|\\\\r' && deny
printf '%s' "$input" | grep -Eq '\\\\' && deny
printf '%s' "$input" | grep -q "'" && deny
printf '%s' "$input" | grep -Eq '\\\\[-.]' && deny
if printf '%s' "$input" | grep -Eq \
  '"command"[[:space:]]*:[[:space:]]*"[^"]*[][?*{}]'; then
  deny
fi
case "$tool" in
  edit|write|Edit|Write)
    if printf '%s' "$normalized" | grep -Eq "$change_dir"; then
      deny
    fi
    ;;
  *)
    if printf '%s' "$normalized" | grep -Eq "$change_dir"; then
      printf '%s' "$normalized" | grep -Eq '[;&|<>`$()]' && deny
      printf '%s' "$normalized" | grep -Eiq \
        '(^|[[:space:]])(--output|-o|--ext-diff)' && deny
      if ! printf '%s' "$normalized" | grep -Eiq \
        '"command"[[:space:]]*:[[:space:]]*"git[[:space:]]+(-[^[:space:]]+[[:space:]]+)*(status|diff|show)([[:space:]]|")'; then
        deny
      fi
    fi
    ;;
esac
printf '%s\n' '{"permissionDecision":"allow"}'
"""


def _surface_limitations() -> str:
    return """## Copilot surface limitations

The workflow and Capability Skills are guidance and discovery projections; the
repository-native Forge artifacts remain authoritative. The review-control
hook is mechanical only where Copilot loads repository hooks on supported Unix
surfaces: Copilot CLI on Linux/macOS and Copilot cloud agent. Windows CLI
requires a PowerShell hook that this Adapter does not generate. IDE agent and
Copilot code review support are surface-dependent and must not be treated as
providing this hook guarantee.
TDD ordering and Strict Review remain represented guidance, not universal
runtime enforcement.
"""


def generate_github_copilot_skill_bundle(
    *,
    contract_content: str,
    flows: Iterable[tuple[str, str]],
    protocol_id: int = 1,
    artifact_structure_content: str = "",
    decision_rules_content: str = "",
    interaction_language: str = "",
    capabilities: tuple[Capability, ...] = (),
) -> GitHubCopilotProjectionBundle:
    effective_flows = tuple(flows)
    base = generate_codex_skill_bundle(
        contract_content=contract_content,
        flows=effective_flows,
        protocol_id=protocol_id,
        artifact_structure_content=artifact_structure_content,
        decision_rules_content=decision_rules_content,
        interaction_language=interaction_language,
        capabilities=capabilities,
    )
    resources: list[GitHubCopilotProjectionResource] = [
        _resource("copilot-instructions.md", _pointer()),
        _resource("hooks/forge-review-control.json", _hook_config()),
        _resource("hooks/forge-review-control.sh", _hook_script(), executable=True),
    ]
    for resource in base.resources:
        if resource.name == "SKILL.md":
            name = "skills/forge/SKILL.md"
            content = resource.content + "\n" + _surface_limitations()
        elif resource.name.startswith("references/"):
            name = "skills/forge/" + resource.name
            content = resource.content
        else:
            name = "skills/" + resource.name
            content = resource.content
        resources.append(_resource(name, content))
    flow_ids = tuple(sorted(flow_id for flow_id, _ in effective_flows))
    return GitHubCopilotProjectionBundle(
        adapter_id="github-copilot",
        flow_id=flow_ids[0] if flow_ids else "",
        resources=tuple(sorted(resources, key=lambda item: item.name)),
    )
