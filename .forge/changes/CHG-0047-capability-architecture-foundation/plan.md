---
forge:
  artifact: plan
  schema: 1
change: CHG-0047
status: approved
---

# Plan — CHG-0047 Capability Architecture Foundation

1. Criar `capabilities/README.md` documentando: o que é uma Forge Capability; o que não é (com a desambiguação explícita frente a `src/forge_cli/adapters/capabilities.py` — Discovery); responsabilidades; limites arquiteturais (o que uma Capability não pode possuir/redefinir: Protocol lifecycle, Flow selection, Change lifecycle, Gates obrigatórios, approval semantics, autoridade humana, Protocol compatibility, enforcement de CLI/CI/hooks); a relação com Core, Flow, Harness Adapters e repository-native evidence; e como adicionar uma futura capability concreta (`capabilities/<nome>/CAPABILITY.md`), incluindo a distinção explícita entre a Capability (fonte canônica) e uma futura representação de Harness derivada dela (ex.: `.claude/skills/forge-investigate/SKILL.md`), que não é sinônimo nem substituto. (FR-001)
2. Criar `capabilities/capability.md` definindo o contrato mínimo de uma definição de capability: frontmatter mínimo (`capability: <id>`, `schema: <int>`) e as sete seções obrigatórias (`## Identity`, `## Purpose`, `## Applicability`, `## Inputs`, `## Behavior`, `## Outputs`, `## Evidence Expectations`), cada uma com uma frase explicando seu propósito, sem introduzir JSON Schema ou formato rígido. Declarar explicitamente que uma Capability não é um `SKILL.md`. (FR-002)
3. **[RED]** Em `tests/capabilities/test_model.py`, escrever os testes de TD-001 (dataclass congelada, campos exatos, sem campo específico de Harness) contra o módulo `forge_cli.capabilities.model` ainda inexistente, e confirmar que a execução falha pela razão esperada (`ModuleNotFoundError`/`ImportError`).
4. **[GREEN]** Criar `src/forge_cli/capabilities/model.py` com a dataclass `Capability(id, schema, identity, purpose, applicability, inputs, behavior, outputs, evidence_expectations, source_path)`, `@dataclass(frozen=True)`, mínima, sem lógica adicional, até TD-001 passar. (FR-003)
5. **[RED]** Em `tests/capabilities/test_loader.py`, escrever os testes de TD-002 a TD-006 (carregamento completo e normalizado; determinismo; arquivo ausente; frontmatter ausente/inválido — parametrizado; seção obrigatória ausente/vazia — parametrizado pelas sete seções) contra `forge_cli.capabilities.loader` ainda inexistente, e confirmar RED pela razão esperada.
6. **[GREEN]** Criar `src/forge_cli/capabilities/loader.py` com `CapabilityDefinitionError(ValueError)`, a constante `REQUIRED_SECTIONS` (as sete seções), e `load_capability(path: Path) -> Capability` implementando locate → read → parse (frontmatter YAML via `yaml.safe_load` + seções `##` via regex) → normalize (strip por seção) → return, com mensagens de erro específicas identificando o caminho e o problema (arquivo ausente, frontmatter ausente/inválido, seção ausente/vazia), até TD-002 a TD-006 passarem. Sem lógica de resolução de pacote/fallback empacotado (Discovery/NFR-001), sem descoberta/enumeração, sem registry, sem execução. (FR-004, FR-005, NFR-001)
7. Criar `src/forge_cli/capabilities/__init__.py` reexportando `Capability`, `load_capability`, `CapabilityDefinitionError` como a superfície pública mínima do pacote.
8. Executar `pytest tests/capabilities/ -q`, a suíte completa (`pytest -q`), `forge validate`, e inspecionar o diff final confirmando: nenhuma ocorrência de `CapabilityRegistry`/`CapabilityExecutor`/`CapabilityPipeline`/`CapabilityGraph`/`CapabilityProvider`; `pyproject.toml`, `protocol/`, `.claude/skills/forge/references/engineering-contract.md` e `src/forge_cli/adapters/capabilities.py` inalterados; nenhum diretório vazio criado para Codex/Cursor/plugin registries. (FR-005, AC-005)

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou explicitamente a continuação para Implementation na sessão ativa em 2026-08-25, via `AskUserQuestion`, após revisar o Repository Truth Audit (Discovery), a Specification (FR-001 a FR-005, NFR-001), o Test Design (TD-001 a TD-007) e o resumo dos 8 itens deste Plan, selecionando explicitamente a opção "Aprovar e prosseguir".

<!-- forge:plan-approval-record -->
