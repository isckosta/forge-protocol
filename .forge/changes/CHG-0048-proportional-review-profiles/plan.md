---
forge:
  artifact: plan
  schema: 1
change: CHG-0048
status: approved
---

# Plan — CHG-0048 Proportional Review Profiles

1. **[RED]** Escrever TDD-001 a TDD-009 (validação/schema) em `tests/unit/test_validation_review_profile.py` (novo arquivo) e `tests/contract/` (extensão de `test_protocol_contract.py` ou arquivo irmão) contra `_validate_review_profile_floor` e os quatro Schemas ainda não modificados, confirmando RED pela razão esperada (função inexistente / Schema ainda rejeita `profile`). (FR-008, FR-010, TDD-001–009)
2. **[GREEN]** Em `src/forge_cli/validation/__init__.py`: adicionar `_PROFILE_RANK` e `_validate_review_profile_floor`, e capturar/usar o retorno de `resolve_effective_flow` na linha onde hoje é descartado (`validate_project`), até TDD-001–003 e TDD-009 passarem. (FR-010)
3. **[GREEN]** Editar os quatro Schemas: `protocol/schemas/change-v2.schema.json`, `protocol/schemas/policy-review-v2.schema.json`, `protocol/schemas/project-flow.schema.json` (campo `profile` aditivo), `protocol/schemas/flow.schema.json` (substituir `const: true` de `strict`/`adversarial` por `boolean`, adicionar `profile` como `required`), até TDD-004–006 passarem. Confirmar `protocol/schemas/policy-review.schema.json` byte-idêntico (TDD-008).
4. Editar `protocol/flows/fast.yml` → `profile: focused, strict: false, adversarial: false`; `protocol/flows/standard.yml` → `profile: standard, strict: false, adversarial: false`; `protocol/flows/full.yml` → `profile: strict` (mantendo `strict: true, adversarial: true`); `protocol/versions/2/policies/review.yml` → `profile: strict` (piso de Protocol, com nota de que o valor efetivo por Change vem do Flow). Confirmar TDD-007 passa.
5. Editar `protocol/versions/2/contract/engineering.md`: C-022 e C-023 substituídos pelo texto de Specification FR-005 (verbatim); C-031 ganha a clarificação de FR-006. Não tocar `protocol/contract/engineering.md` (Protocol 1).
6. **[RED]** Escrever TDD-010 a TDD-012 (rendering) em `tests/unit/test_claude_code_projection.py`/`test_codex_projection.py` (ou arquivos equivalentes já existentes para essas projeções) contra a linha fixa atual, confirmando RED pela razão esperada. **[GREEN]** Em `src/forge_cli/adapters/claude_code/projection.py` e `codex/projection.py`: adicionar `_REVIEW_PROFILE_INSTRUCTION` (mapa `focused`/`standard`/`strict` → texto) e indexar `_gate_instructions()` por ele, lendo o profile do Flow canônico efetivo já disponível no ponto de chamada. Não tocar `review_independence.py`. Até TDD-010–012 passarem. (FR-002, FR-003, FR-004, FR-009)
7. **[RED]** Escrever TDD-013 em teste de `merge_readiness` existente, confirmando RED. **[GREEN]** Em `src/forge_cli/merge_readiness/evaluator.py`, linha do diagnóstico `MR-004`: trocar `"STRICT REVIEW NOT READY"` por `"REVIEW NOT READY"`, sem tocar a condição de disparo. (FR-013)
8. **[RED]** Escrever TDD-014 contra a implementação do item 6, confirmando que sem derivação fresca de `manifest.flow.current` o teste falharia (simular via dois manifests/estados). Confirmar GREEN já com a implementação do item 6 (nenhuma mudança de código adicional esperada — TDD-014 é uma prova de propriedade da mesma implementação, não um novo comportamento). (FR-012)
9. **[RED]** Escrever TDD-015 (amostra de todos os `manifest.yml` `state.current: complete` existentes) e confirmar RED apenas se algum regredir; GREEN esperado imediatamente dado que os Schemas de FR-008 são aditivos e `flow.schema.json`'s narrowing não afeta manifests históricos (só os três arquivos de Flow, editados nesta própria Change). (FR-011)
10. Documentação: adicionar entrada `### CHG-0048 — Proportional Review Profiles` a `protocol/compatibility.md` (padrão das entradas existentes); adicionar entrada em `CHANGELOG.md`'s `## Unreleased`. Nenhum ADR novo (RFC-0007 já cumpre F-008 para esta Change).
11. Executar a suíte completa (`pytest -q`), `forge validate`, e inspecionar o diff final confirmando: nenhuma ocorrência de `ReviewProfileEngine`/`ReviewProfileRegistry`/execução paralela; `protocol/contract/engineering.md` (Protocol 1), `protocol/schemas/policy-review.schema.json` (Protocol 1), e `src/forge_cli/adapters/review_independence.py` inalterados; `_validate_resolution_verification` e `_validate_protocol2_review_provenance` sem nenhum branch novo condicionado a `flow`/`profile`.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou explicitamente a continuação para Implementation na sessão ativa em 2026-08-25, via `AskUserQuestion`, após revisar o Architecture (incluindo DEC-001), o Test Strategy (15 TDD cases) e o resumo dos 11 itens deste Plan, selecionando explicitamente a opção "Aprovar e prosseguir".

<!-- forge:plan-approval-record -->
