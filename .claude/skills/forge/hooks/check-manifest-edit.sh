#!/bin/sh
set -eu

# Forge CHG-0018 FR-006 / CHG-0045 FR-006: illustrative PreToolUse
# enforcement hook. Denies mutation of Forge review-control metadata
# via Bash shell redirection/in-place editing, or via a direct
# Edit/Write tool call targeting the same three paths; never matches
# read-only or version-control commands (see SKILL.md). This remains
# a partial, illustrative guard, not a general security boundary:
# it does not see MCP filesystem tools, NotebookEdit, or (unverified)
# subagent-issued tool calls.
#
# Strict Review R001 (CHG-0018 Iteration 1): a naive whole-string
# substring match denied a plain git add/commit whenever an unrelated
# '>' happened to appear anywhere else in the same command line (e.g.
# inside a commit message, or an unrelated redirect earlier in a
# compound command). Fixed by requiring the mutation token and the
# protected path to be close together (bounded proximity, no shell
# separator such as && / || / ; / | between them), via a single grep -E
# check, instead of two independent whole-string case patterns.
input="$(cat)"
tool_name="$(printf '%s' "$input" | jq -r '.tool_name // empty')"

if [ "$tool_name" = "Edit" ] || [ "$tool_name" = "Write" ]; then
  file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"
  case "$file_path" in
    .forge/changes/*/manifest.yml|.forge/changes/*/provenance.yml|.forge/changes/*/review.md|*/.forge/changes/*/manifest.yml|*/.forge/changes/*/provenance.yml|*/.forge/changes/*/review.md)
      printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Forge review-control metadata (manifest.yml/provenance.yml/review.md) must not be mutated directly via Edit/Write; use the normal repository-native path so changes stay auditable (CHG-0018 FR-006, CHG-0045 FR-006)."}}'
      exit 0
      ;;
  esac
  exit 0
fi

command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

if printf '%s' "$command" | grep -Eq '(sed[[:space:]]+-i|perl[[:space:]]+-i|truncate|>{1,2})[[:space:]]*[^&|;]{0,80}\.forge/changes/[^[:space:]&|;]*(manifest\.yml|provenance\.yml|review\.md)'
then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Forge review-control metadata (manifest.yml/provenance.yml/review.md) must not be mutated via shell redirection or in-place editing; use the normal Write/Edit tool path so changes stay auditable (CHG-0018 FR-006)."}}'
  exit 0
fi
exit 0
