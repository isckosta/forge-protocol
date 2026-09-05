---
forge:
  artifact: plan
  schema: 1
change: CHG-0052
status: approved
---

# Plan — CHG-0052 Investigate Capability

1. **[RED]** Criar `tests/capabilities/test_investigate_capability.py` com um fixture de módulo que chama `load_capability(Path("capabilities/investigate/CAPABILITY.md"))` — este caminho ainda não existe — e os testes TD-001 a TD-006 (carregamento bem-sucedido com `id == "investigate"` e as sete seções não vazias; presença literal de `ROOT CAUSE CONFIRMED`/`ROOT CAUSE NOT ESTABLISHED`; presença de `CONFIRMED`/`INFERRED`/`UNKNOWN` em Evidence Expectations; ausência de vocabulário de Harness/mecanismos proibidos; presença das negações de Boundary; presença dos termos-chave do fluxo de oito passos e de `plausible guess`). Confirmar RED pela razão esperada: `CapabilityDefinitionError` (arquivo ausente). (TD-001–TD-006)
2. **[GREEN]** Criar `capabilities/investigate/CAPABILITY.md` com frontmatter `capability: investigate`, `schema: 1`, e as sete seções obrigatórias, cobrindo integralmente FR-001 a FR-006: `## Identity`/`## Purpose` framing a competência; `## Applicability` com as categorias do pedido original e a exclusão explícita para causa já estabelecida (FR-005); `## Inputs` descrevendo o que a investigação precisa antes de rodar (o problema relatado, acesso a código/testes/runtime/Git history/artifacts relevantes); `## Behavior` descrevendo o fluxo `problem -> establish facts -> reproduce when possible -> gather evidence -> competing hypotheses -> test hypotheses -> isolate root cause -> conclusion`, nomeando explicitamente `symptom -> plausible guess -> code change` como o antipadrão a evitar, e negando corrigir automaticamente/alterar production behavior permanentemente (FR-002, FR-004); `## Outputs` com o formato observável (`Problem`, `Observations`, `Reproduction Status`, `Evidence`, `Hypotheses Evaluated`, `Root Cause`, `Uncertainty`, `Recommended Next Action`), os marcadores literais `ROOT CAUSE CONFIRMED`/`ROOT CAUSE NOT ESTABLISHED`, e a recomendação de próxima ação sem presumir implementação (FR-003, FR-004); `## Evidence Expectations` com a distinção literal `CONFIRMED`/`INFERRED`/`UNKNOWN` e o repository-native evidence principle. Negar explicitamente, em Applicability/Behavior/Outputs, cada Boundary do pedido original (aprovar Changes, selecionar/redefinir Flow, criar Gates, controlar lifecycle, substituir decisão humana, redefinir Protocol/Contract) (FR-004). Nenhuma menção a Claude/Codex/Cursor, `CapabilityRegistry`, `CapabilityExecutor`, `/investigate`, ou `SKILL.md` (FR-006). Rodar os testes de (1) até todos passarem.
3. Executar `pytest tests/capabilities/ -q` e a suíte completa (`pytest -q`), confirmar `forge validate` limpo, e inspecionar o diff final confirmando que `capabilities/README.md`, `capabilities/capability.md`, `src/forge_cli/capabilities/loader.py` e `src/forge_cli/capabilities/model.py` permanecem byte-idênticos, e que nenhuma ocorrência de `CapabilityRegistry`/`CapabilityExecutor`/`/investigate`/`SKILL.md`/Claude/Codex/Cursor existe fora dos próprios Change Artifacts (`intent.md`, `discovery.md`, `specification.md`, `test-design.md`, `plan.md`) desta Change. (FR-006, AC-006)
4. Avaliar Documentation Impact: se `CHANGELOG.md` (seção `## Unreleased`) precisa de uma entrada anunciando a primeira Capability concreta — decisão registrada em `verification.md`/Review conforme o Gate `documentation_impact_evaluated`, não pré-julgada aqui.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou explicitamente a continuação para Implementation na sessão ativa em 2026-09-01, via `AskUserQuestion`, após revisar o Intent, a Discovery, a Specification (FR-001 a FR-006, NFR-001), o Test Design (TD-001 a TD-007) e o resumo dos 4 itens deste Plan, selecionando explicitamente a opção "Aprovar e prosseguir".

<!-- forge:plan-approval-record -->
