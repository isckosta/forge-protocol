---
forge:
  artifact: specification
  schema: 1
change: CHG-0047
status: draft
---

# CHG-0047 · Specification

> **Change Contract**
>
> Esta Specification define a fundação mínima da Forge Capability Architecture: um contrato humano mínimo (`capability.md`), documentação canônica (`capabilities/README.md`), um modelo mínimo (`model.py`) e um carregamento determinístico (`loader.py`) para uma definição concreta futura de capability (`CAPABILITY.md`) — sem implementar nenhuma capability real, registry, executor ou novo lifecycle.

## Overview

| | |
|---|---|
| **Change** | CHG-0047 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O CLI SHALL ganhar um pacote `forge_cli.capabilities` capaz de carregar deterministicamente uma definição de capability (`CAPABILITY.md`) que satisfaça o contrato mínimo documentado em `capabilities/capability.md`, retornando um modelo de dados imutável. `capabilities/README.md` SHALL documentar o conceito, seus limites arquiteturais e a relação com Core/Flow/Harness Adapters/evidence. Nenhuma capability concreta, registry, executor, plugin system ou novo Gate é introduzido.

## Classification

STANDARD. O comportamento é localizado a dois documentos novos (`capabilities/README.md`, `capabilities/capability.md`), um pacote Python novo e pequeno (`src/forge_cli/capabilities/`) e seus testes focados — sem mudança de Protocol integer, Change Schema, Gate semantics, ou execução de Harness Adapter (Discovery, achado "Ausência do conceito no Protocol e no Contract").

## User Stories

Nenhuma se aplica. Esta é uma Change arquitetural de fundação de tooling, sem ator de domínio distinto além do próprio Forge Core/CLI; os Requirements abaixo são autocontidos, conforme Protocol §41.

## Functional Requirements

### FR-001 · Documented Capability concept and architectural boundaries
Origin: Discovery — ausência do conceito no Protocol/Contract; necessidade de limites explícitos

#### Requirement
`capabilities/README.md` SHALL documentar, de forma concisa: o que é uma Forge Capability; o que não é (incluindo a distinção explícita com `src/forge_cli/adapters/capabilities.py`, que representa Harness capability flags, um conceito diferente — Discovery); responsabilidades; limites arquiteturais (o que uma Capability não pode possuir ou redefinir: Protocol lifecycle, Flow selection, Change lifecycle, mandatory Gates, approval semantics, human authority, Protocol compatibility, enforcement pertencente a CLI/CI/hooks); a relação com Core, Flow, Harness Adapters e repository-native evidence; e como futuras capabilities concretas devem ser adicionadas (`capabilities/<nome>/CAPABILITY.md`).

#### Boundary
Este Requirement cobre apenas o texto documental; não introduz nenhuma validação mecânica do conteúdo do README.

#### Acceptance
AC-001 — `capabilities/README.md` existe e contém, no mínimo, uma seção respondendo a cada um dos seis pontos listados no Requirement, incluindo a desambiguação explícita com `adapters/capabilities.py`.

### FR-002 · Minimal human-readable Capability contract
Origin: Discovery — convenção de frontmatter estabelecida; pedido original de contrato mínimo sem JSON Schema

#### Requirement
`capabilities/capability.md` SHALL definir o contrato mínimo que uma definição concreta de capability (`CAPABILITY.md`) deve satisfazer, cobrindo no mínimo as seções: Identity, Purpose, Applicability, Inputs, Behavior, Outputs, Evidence Expectations. A representação SHALL ser humana e simples (texto Markdown com um frontmatter mínimo de identidade — `capability`, `schema` — e headings `##` por seção), SHALL NOT introduzir JSON Schema, e SHALL declarar explicitamente que uma Capability não é sinônimo de `SKILL.md` — um Harness Adapter futuro deriva uma representação de Harness (ex.: uma Claude Skill) a partir da Capability, mas a Capability permanece a fonte canônica.

#### Boundary
Este Requirement define o contrato; não define nem exemplifica uma capability concreta (`investigate` e as demais permanecem fora de escopo).

#### Acceptance
AC-002 — `capabilities/capability.md` lista as sete seções mínimas exigidas, descreve o propósito de cada uma, mostra o formato de frontmatter mínimo esperado, e declara explicitamente a distinção com `SKILL.md`.

### FR-003 · Minimal Capability model
Origin: Discovery — precedente real de dataclass congelado (`CapabilityRequirement`/`CapabilityEvidence`)

#### Requirement
`src/forge_cli/capabilities/model.py` SHALL definir um modelo mínimo e imutável (`@dataclass(frozen=True)`) representando uma capability carregada, com um campo por seção obrigatória do contrato (`identity`, `purpose`, `applicability`, `inputs`, `behavior`, `outputs`, `evidence_expectations`), um identificador (`id`), um inteiro de schema (`schema`), e o caminho de origem (`source_path`). O modelo SHALL NOT incluir campos de lifecycle, autoridade, Gate, execução, ou qualquer campo específico de um Harness (ex.: nada nomeado `claude_*` ou equivalente).

#### Boundary
Este Requirement não introduz hierarquia de classes, builder, ou qualquer abstração sem consumidor concreto nesta Change.

#### Acceptance
AC-003 — `Capability` é um `dataclass(frozen=True)` com exatamente os campos listados no Requirement; uma tentativa de mutação pós-construção levanta erro; nenhum campo do modelo referencia Claude, Codex, Cursor ou qualquer Harness específico.

### FR-004 · Deterministic Capability loading
Origin: Discovery — padrão de carregamento determinístico existente (`resolve_protocol_root`), sem a mesma necessidade de empacotamento

#### Requirement
`src/forge_cli/capabilities/loader.py` SHALL expor uma função que, dado o `Path` de um arquivo de definição, executa determinística e sequencialmente: localizar (validar que o arquivo existe), ler (UTF-8), parsear (frontmatter YAML + seções `##`), normalizar (remover espaço em branco supérfluo nas bordas de cada seção) e retornar o modelo `Capability` correspondente. Chamar a função duas vezes com o mesmo arquivo, sem alteração no conteúdo, SHALL produzir modelos iguais (determinismo). A função SHALL levantar um erro específico e explícito (não uma exceção genérica não tratada) quando: o arquivo não existir; o frontmatter estiver ausente ou não contiver `capability`/`schema` válidos; ou qualquer uma das sete seções obrigatórias estiver ausente ou vazia.

#### Boundary
Este Requirement cobre apenas o carregamento de uma definição individual dado um caminho explícito. SHALL NOT implementar descoberta/enumeração de múltiplas capabilities, registry, cache, composição, execução agentic, ou resolução de pacote/fallback empacotado (diferente de `resolve_protocol_root` — Discovery já estabelece que essa necessidade não existe para conteúdo repository-native).

#### Acceptance
AC-004 — Dado um `CAPABILITY.md` bem formado, o loader retorna um `Capability` com todos os campos populados e normalizados (sem espaço em branco de borda). Dado um arquivo inexistente, frontmatter ausente/inválido, ou uma seção obrigatória ausente/vazia, o loader levanta um erro específico do domínio de capabilities (não um `KeyError`/`AttributeError`/exceção genérica não tratada) com uma mensagem identificando o caminho e o problema.

### FR-005 · No coupling to Claude, no new registry, no new lifecycle
Origin: Discovery — ausência de registry/executor hoje; pedido original de limites arquiteturais

#### Requirement
Nenhum código, documento ou teste desta Change SHALL introduzir: uma capability concreta (`investigate`, `review`, `provenance`, `challenge` ou outra); uma classe `CapabilityRegistry`, `CapabilityExecutor`, `CapabilityPipeline`, `CapabilityGraph` ou `CapabilityProvider`; um novo comando de CLI (`forge capability ...`); um novo Gate de Flow; um novo campo em `manifest.yml`/Change Schema; uma dependência de nenhum Harness específico (Claude, Codex, Cursor); ou uma mudança em `pyproject.toml` (empacotamento não é necessário — Discovery).

#### Acceptance
AC-005 — Busca por `CapabilityRegistry`, `CapabilityExecutor`, `CapabilityPipeline`, `CapabilityGraph`, `CapabilityProvider` no diff desta Change não retorna nenhuma ocorrência; `pyproject.toml`, `protocol/`, `.claude/skills/forge/references/engineering-contract.md`, e `src/forge_cli/adapters/capabilities.py` permanecem inalterados por esta Change.

## Non-functional Requirements

### NFR-001 · Portability across Forge-enabled repositories
O `loader.py` SHALL operar sobre qualquer `Path` fornecido, sem depender de caminhos, arquivos ou convenções específicas do repositório `forge-protocol` — exceto `capabilities/capability.md` e `capabilities/README.md`, que são documentação canônica do próprio produto Forge e legitimamente vivem apenas neste repositório.

## Constraints

### CON-001 · Scope boundary
Não criar `capabilities/investigate/` ou qualquer outra capability concreta; não criar marketplace, package manager, plugin system, remote registry, capability registry extensível, capability composition runtime, dependency graph, confidence scoring, capability executor, orchestration paralela, adapters para múltiplos Harnesses, novo artifact obrigatório de Change, novo Gate, ou nova versão de Protocol. Não criar árvores vazias para Codex, Cursor, plugin registries ou outras integrações futuras.

## Traceability Matrix

Índice apenas; as referências locais em cada Requirement permanecem autoritativas.

| Discovery | Requirement | Acceptance |
|---|---|---|
| Ausência do conceito no Protocol/Contract; limites arquiteturais explícitos | FR-001 | AC-001 |
| Convenção de frontmatter; contrato mínimo sem JSON Schema | FR-002 | AC-002 |
| Precedente de dataclass congelado | FR-003 | AC-003 |
| Padrão de carregamento determinístico, sem empacotamento | FR-004 | AC-004 |
| Ausência de registry/executor hoje | FR-005 | AC-005 |

## Compatibility Statement

Nenhum artefato de Change existente, Schema, Protocol integer, Flow Gate, ou Harness Adapter é afetado. `src/forge_cli/adapters/capabilities.py` (Harness capability requirements) permanece inalterado e semanticamente distinto do novo `forge_cli.capabilities` (Forge Capability). `pyproject.toml` não muda — `capabilities/` não é empacotado no wheel do CLI, pelo mesmo motivo que `.forge/changes/` não é.

## Specification Gate

Esta Specification está completa: cada Requirement tem origem rastreável na Discovery, Acceptance verificável, e Boundary explícito onde necessário; os limites arquiteturais do pedido original (FR-001, FR-005) estão cobertos; e nenhum Requirement introduz as classes prematuras ou infraestrutura especulativa explicitamente fora de escopo.

## Out of Scope

Qualquer capability concreta; marketplace; package manager; plugin system; remote registry; capability registry extensível; capability composition runtime; dependency graph; confidence scoring; capability executor; orchestration paralela; adapters para múltiplos Harnesses; novo artifact obrigatório; novo Gate; nova versão de Protocol sem necessidade normativa comprovada; mudança em `pyproject.toml`.
