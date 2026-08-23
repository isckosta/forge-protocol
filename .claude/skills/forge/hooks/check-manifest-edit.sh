#!/bin/sh
set -eu

# Forge CHG-0018 FR-006: illustrative PreToolUse enforcement hook.
# Denies in-place shell mutation of Forge review-control metadata;
# never matches read-only or version-control commands (see SKILL.md).
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
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

if printf '%s' "$command" | grep -Eq '(sed[[:space:]]+-i|perl[[:space:]]+-i|truncate|>{1,2})[[:space:]]*[^&|;]{0,80}\.forge/changes/[^[:space:]&|;]*(manifest\.yml|provenance\.yml|review\.md)'
then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Forge review-control metadata (manifest.yml/provenance.yml/review.md) must not be mutated via shell redirection or in-place editing; use the normal Write/Edit tool path so changes stay auditable (CHG-0018 FR-006)."}}'
  exit 0
fi
exit 0
