---
forge:
  artifact: plan
  schema: 1
change: CHG-0039
status: approved
---

# Plan — CHG-0039 Tasks Layout Plan Grouping Traceability

1. Em `src/forge_cli/change_scaffolding.py`, reescrever a entrada `"tasks"` do dicionário `sections` dentro de `_markdown()` para o novo layout de checklist de execução agrupada: `## Overview` (tabela `Change`/`Flow`/`Status`), `## Execution` com um exemplo `### Plan 1 · <title>` contendo `- [ ] T-001 <work item>` e uma linha de metadata compacta (`` `Plan: 1` · `Requirements: FR-001` · `Test Design: TDD-001` ``), guidance explícita de que nenhuma referência é obrigatória em toda Task, e `## Status` como seção final (`No task has started.`). Adicionar um caso especial em `_frontmatter()` para `artifact == "tasks"` produzindo `# {change_id} · Tasks`. Não alterar as entradas `"plan"` ou `"test_strategy"`.
2. Em `tests/unit/test_change_scaffolding.py`, adicionar testes focados espelhando o padrão já usado para `specification`/`test_design` (`test_render_scaffold_specification_uses_traceable_contract_layout` e equivalentes de CHG-0038), cobrindo: heading/frontmatter novos (`# CHG-XXXX · Tasks`); presença de `### Plan 1 ·` e de `- [ ] T-001` sob essa heading; ausência da checklist plana anterior; presença de linha de metadata compacta usando `TDD-xxx` (não `TD-xxx`); frase de guidance de que referências não são obrigatórias em toda Task; tabela de `Overview` com `Change`/`Flow`; `## Status` como seção final contendo `No task has started.`; e uma asserção de que os templates `plan` e `test_strategy` permanecem byte-idênticos aos atuais (proteção de regressão para FR-006/TD-005).
3. Em `protocol/artifact-structure.md` §4, reescrever a entrada "Tasks" para descrever o novo layout recomendado (Overview, agrupamento por item de Plan, checklist `T-xxx` como fonte de estado de execução, metadata compacta opcional de Requirements/Stories/Test Design, Status simples) como guidance não vinculante que evolui — não substitui — a forma estável anterior, deixando explícito que: (a) isto não é uma nova obrigação de Gate; (b) Task concluída não implica Requirement verificado; (c) `tasks.md` históricos permanecem válidos sem qualquer exigência retroativa de agrupamento, Stories, Requirements ou Test Design.
4. Executar `pytest tests/unit/test_change_scaffolding.py -q`, a suíte completa (`pytest -q`), `forge validate`, e inspecionar o diff final confirmando que nenhum arquivo sob `protocol/schemas/`, nenhum Protocol integer, e nenhum `tasks.md`/`plan.md`/`test-strategy.md` histórico foi alterado.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou a continuação na sessão ativa em 2026-08-23, após revisar o Repository Truth Audit, o impacto normativo, o impacto de compatibilidade, os arquivos afetados, a estrutura final proposta e a estratégia de testes, confirmando explicitamente que o exemplo de domínio ERP (Customer Price Lists) não é necessário.

<!-- forge:plan-approval-record -->
