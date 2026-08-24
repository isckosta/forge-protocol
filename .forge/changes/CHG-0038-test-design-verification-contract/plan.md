---
forge:
  artifact: plan
  schema: 1
change: CHG-0038
status: approved
---

# Plan — CHG-0038 Test Design Verification Contract

1. Em `src/forge_cli/change_scaffolding.py`, reescrever a entrada `"test_design"` do dicionário `sections` dentro de `_markdown()` para o novo layout de contrato de verificação: `## Overview`, `## Test Strategy`, `## Coverage Map`, um `### TD-001 ·` de exemplo com `Requirements:`/`Type:`/`Priority:` e subseções `#### Purpose`/`#### Preconditions`/`#### Scenario`/`#### Evidence`/`#### Failure Condition`/`#### Boundary`, guidance sobre `Manual Acceptance` e sobre RED válido/inválido, `## Requirement Coverage`, `## Coverage Gaps` e `## Test Design Gate`. Adicionar um caso especial em `_frontmatter()` para `artifact == "test_design"` produzindo `# {change_id} · Test Design`. Não alterar a entrada `"test_strategy"`.
2. Em `tests/unit/test_change_scaffolding.py`, adicionar testes focados espelhando `test_render_scaffold_specification_uses_traceable_contract_layout`/`test_render_scaffold_specification_explains_optional_user_stories`, cobrindo: heading/frontmatter novos; presença de `### TD-001 ·` e subseções críticas; ausência de `N/A` forçado e do template mínimo anterior; frase de Requirement-sem-Story; presença de `Manual Acceptance`; guidance de RED válido/inválido; e uma asserção de que o template `test_strategy` permanece byte-idêntico ao valor atual (proteção de regressão para FR-006/TD-006).
3. Em `protocol/artifact-structure.md` §4, dividir a entrada combinada "Test Design / Test Strategy" em duas entradas distintas: "Test Design" (nova forma TD-xxx/Layer/Coverage Map, com a razão da divergência da guidance anterior registrada) e "Test Strategy" (forma `TDD-xxx` existente, explicitamente inalterada). Atualizar `.forge/changes/CHG-0016-canonical-artifact-structure` NÃO é necessário (histórico preservado); apenas o documento vivo muda.
4. Executar `pytest tests/unit/test_change_scaffolding.py -q`, a suíte completa (`pytest -q`), `forge validate`, e inspecionar o diff final confirmando que nenhum arquivo sob `protocol/schemas/`, nenhum Protocol integer, e nenhum `test-design.md`/`test-strategy.md` histórico foi alterado.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou a continuação na sessão ativa em 2026-08-23, após revisar o Repository Truth Audit, a tensão com a guidance existente de `protocol/artifact-structure.md`, o boundary de compatibilidade e a estratégia de testes, com a ressalva explícita de remover o item do exemplo de domínio ERP (Customer Price Lists) do escopo desta Change.

<!-- forge:plan-approval-record -->
