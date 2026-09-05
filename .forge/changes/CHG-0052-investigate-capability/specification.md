---
forge:
  artifact: specification
  schema: 1
change: CHG-0052
status: draft
---

# CHG-0052 · Specification

> **Change Contract**
>
> Esta Specification define a primeira Forge Capability concreta,
> `investigate`: uma competência de investigação técnica disciplinada,
> evidence-driven e hypothesis-driven, expressa como
> `capabilities/investigate/CAPABILITY.md` conforme o contrato existente
> em `capabilities/capability.md`, sem tocar a fundação nem introduzir
> qualquer mecanismo de execução, registry ou lifecycle novo.

## Overview

| | |
|---|---|
| **Change** | CHG-0052 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

`capabilities/investigate/CAPABILITY.md` SHALL existir e satisfazer
integralmente o contrato de `capabilities/capability.md`, sendo
carregável pelo `forge_cli.capabilities.loader` existente sem qualquer
mudança de código. Seu conteúdo SHALL definir uma competência de
diagnóstico que substitui `symptom -> plausible guess -> code change`
por um fluxo evidence-driven e hypothesis-driven, permite que a root
cause permaneça explicitamente não estabelecida, e permanece
estritamente diagnóstica (sem autoridade de implementação, aprovação,
Flow, Gate ou lifecycle).

## Classification

STANDARD. O comportamento é localizado a um novo diretório de
documentação (`capabilities/investigate/`) e a testes focados
(`tests/capabilities/test_investigate_capability.py`) — sem mudança de
Protocol integer, Change Schema, Gate semantics, `capabilities/README.md`
ou `capabilities/capability.md` (Discovery — Executive Summary).

## User Stories

Nenhuma se aplica. `investigate` é uma competência de tooling consumida
por qualquer agente/Harness que precise diagnosticar um problema
técnico, não um fluxo de um ator de domínio distinto; os Requirements
abaixo são autocontidos, conforme Protocol §41 (mesmo padrão adotado por
`CHG-0047`).

## Functional Requirements

### FR-001 · Conformant, loadable Capability definition
Origin: Discovery — o contrato existente já cobre o formato de `investigate`; teste real do arquivo real ainda não existe

#### Requirement
`capabilities/investigate/CAPABILITY.md` SHALL carregar frontmatter
`capability: investigate` e um `schema` inteiro, e SHALL conter as sete
seções `##` exigidas por `capabilities/capability.md` (Identity,
Purpose, Applicability, Inputs, Behavior, Outputs, Evidence
Expectations), cada uma com conteúdo substantivo e não vazio. O arquivo
SHALL ser carregável por `forge_cli.capabilities.loader.load_capability`
sem qualquer alteração em `loader.py`, `model.py`, ou
`capabilities/capability.md`.

#### Boundary
Este Requirement cobre apenas conformidade estrutural com o contrato
existente — o conteúdo semântico de cada seção é coberto por FR-002 a
FR-006.

#### Acceptance
AC-001 — `load_capability(Path("capabilities/investigate/CAPABILITY.md"))` retorna um `Capability` com `id == "investigate"`, `schema` inteiro, e as sete seções obrigatórias não vazias, sem que o diff desta Change toque `loader.py`, `model.py` ou `capabilities/capability.md`.

### FR-002 · Evidence-driven, hypothesis-driven investigation behavior
Origin: pedido original — "impedir symptom → plausible guess → code change"; Discovery — o fluxo cabe inteiramente em `## Behavior`

#### Requirement
A seção `## Behavior` de `investigate` SHALL descrever um fluxo que:
separa fatos, observações, hipóteses e inferências; tenta estabelecer
reprodução determinística quando aplicável; coleta evidence antes de
concluir causalidade; formula hipóteses concorrentes evitando fixação
prematura na primeira explicação plausível; testa as hipóteses contra
código, testes, runtime evidence, Git history e artifacts relevantes;
elimina hipóteses incompatíveis com a evidence; e só identifica root
cause quando a evidence a sustenta suficientemente. A seção `##
Behavior` SHALL declarar explicitamente a sequência
`problem -> establish facts -> reproduce when possible -> gather
evidence -> competing hypotheses -> test hypotheses -> isolate root
cause -> conclusion`, e SHALL declarar explicitamente que
`symptom -> plausible guess -> code change` é o padrão a evitar.

#### Boundary
Este Requirement cobre o texto normativo do comportamento; não impõe uma
ferramenta, comando, ou automação específica para executá-lo (Capability
Architecture — o "como" pertence a um Harness Adapter futuro, fora de
escopo aqui).

#### Acceptance
AC-002 — `## Behavior` menciona, em prosa verificável, cada elemento do
Requirement (separação fato/hipótese, reprodução, evidence antes de
causalidade, hipóteses concorrentes, teste contra evidence, eliminação
de hipóteses incompatíveis, root cause condicionada a evidence
suficiente) e contém a sequência de oito passos e o padrão antagonista
(`symptom -> plausible guess -> code change`) declarados explicitamente
como texto, não apenas implícitos.

### FR-003 · Explicit inconclusive outcome and evidence classes
Origin: pedido original — "nunca deve fabricar certeza para encerrar a investigação"

#### Requirement
`investigate` SHALL permitir e declarar explicitamente dois desfechos
de conclusão de causa: `ROOT CAUSE CONFIRMED` e
`ROOT CAUSE NOT ESTABLISHED` — o segundo sendo uma saída legítima, não
uma falha do processo. `## Evidence Expectations` SHALL declarar e
preservar a distinção `CONFIRMED` / `INFERRED` / `UNKNOWN` para toda
conclusão causal relevante, e SHALL declarar que repository-native
evidence é a fonte durável de verdade quando o resultado precisar
sobreviver à execução (Capability README — repository-native evidence
principle).

#### Boundary
Este Requirement não impõe um novo artifact de Change obrigatório para
acomodar essas classes — permanecer expressável em prosa dentro de
Outputs/Evidence Expectations é suficiente (pedido original —
"Não imponha um novo artifact obrigatório").

#### Acceptance
AC-003 — o texto de `investigate` contém literalmente as strings
`ROOT CAUSE CONFIRMED` e `ROOT CAUSE NOT ESTABLISHED`, e literalmente as
três palavras `CONFIRMED`, `INFERRED`, `UNKNOWN` na seção Evidence
Expectations (ou em Outputs, referenciada por ela), como marcadores de
conclusão distintos.

### FR-004 · Diagnostic-only boundary
Origin: pedido original — seção "Boundaries"; `capabilities/README.md` — Architectural boundaries

#### Requirement
`investigate` SHALL declarar explicitamente, em `## Applicability` e/ou
`## Behavior`/`## Outputs`, que é diagnóstico e não implementação, e
SHALL declarar que não: corrige automaticamente o problema investigado;
altera production behavior apenas para validar uma hipótese; aprova
Changes; seleciona ou redefine Flow; cria Gates; controla lifecycle;
substitui decisões humanas; transforma inferência em fato; redefine
Protocol ou Engineering Contract. `## Outputs` SHALL declarar que o
resultado é uma recomendação de próxima ação, sem assumir
automaticamente que uma implementação é necessária.

#### Boundary
Instrumentação ou experimentos temporários usados durante a
investigação SHALL ser permitidos apenas quando claramente identificados
como tal e não confundidos com a solução final — este Requirement não
proíbe investigação ativa (rodar testes, reproduzir, instrumentar
temporariamente), apenas proíbe que ela vire a correção definitiva sem
decisão humana e sem passar pelo Flow apropriado.

#### Acceptance
AC-004 — o texto de `investigate` nega explicitamente cada item da lista
de Boundaries do Requirement (não corrige, não altera production
behavior permanentemente, não aprova Changes, não seleciona/redefine
Flow, não cria Gates, não controla lifecycle, não substitui decisão
humana, não transforma inferência em fato, não redefine Protocol/
Contract), e declara a permissão condicionada de instrumentação/
experimentos temporários.

### FR-005 · Applicability scope
Origin: pedido original — seção "Applicability"

#### Requirement
`## Applicability` SHALL listar situações onde `investigate` se aplica
legitimamente (bugs, regressões, falhas de teste, comportamento
intermitente, diferenças entre ambientes, problemas de integração,
causas técnicas desconhecidas, sintomas cuja origem ainda precisa ser
demonstrada), e SHALL declarar explicitamente quando não se aplica:
quando a root cause já estiver estabelecida por evidence suficiente e o
trabalho restante for apenas implementação.

#### Acceptance
AC-005 — `## Applicability` cobre, em prosa verificável, cada categoria
de situação listada no Requirement, e contém a exclusão explícita para
causa já estabelecida.

### FR-006 · No new registry, executor, lifecycle, Gate, or Harness coupling (revised per specification-drift.md)
Origin: pedido original — seção "Architecture" (lista de proibições); Discovery — ausência de registry/executor hoje
Revision: `specification-drift.md` — a Codex review de PR #47 encontrou que a proibição literal abaixo tornava impossível corrigir uma alegação factualmente falsa que esta própria Change introduz em `capabilities/README.md`; a proibição é corrigida (superseded, não deletada) para preservar sua intenção real (não redesenhar a fundação, não introduzir os mecanismos listados) sem proibir uma correção de acurácia pontual e não-arquitetural.

#### Requirement
Nenhum arquivo desta Change SHALL introduzir: `CapabilityRegistry`,
`CapabilityExecutor`, discovery automático, dependency graph,
composition runtime, estado próprio da capability, novo lifecycle, novo
Gate, novo Protocol version, um comando `/investigate`, um `SKILL.md`
específico de Claude/Codex/Cursor, ou qualquer adapter de Harness. Esta
Change SHALL NOT alterar o contrato arquitetural de
`capabilities/README.md` (suas seções "What a Forge Capability
is"/"is not", Responsibilities, Architectural boundaries, e o diagrama
de relação) nem `capabilities/capability.md` em nenhuma parte, e
SHALL NOT alterar `loader.py` ou `model.py`. Esta Change MAY corrigir,
no mínimo texto necessário, uma alegação de status factualmente
incorreta em `capabilities/README.md` que a própria entrega desta
Change torna falsa (o parágrafo introdutório que descreve `investigate`
como trabalho futuro) — uma correção de acurácia, não uma mudança de
contrato.

#### Acceptance
AC-006 — busca por `CapabilityRegistry`, `CapabilityExecutor`,
`/investigate`, `SKILL.md` relacionado a investigate, e qualquer menção
a Claude/Codex/Cursor no diff desta Change não retorna nenhuma
ocorrência fora deste próprio `specification.md`/`intent.md`/`plan.md`/
`specification-drift.md`; `capabilities/capability.md`, `loader.py` e
`model.py` permanecem byte-idênticos ao estado pré-Change; o diff de
`capabilities/README.md` é limitado ao parágrafo de status introdutório,
e todas as demais seções (What a Forge Capability is/is not,
Responsibilities, Architectural boundaries, o diagrama de relação, e
"Adding a future Capability") permanecem byte-idênticas.

## Non-functional Requirements

### NFR-001 · Harness- and repository-portability
`investigate` SHALL ser utilizável em qualquer Forge-enabled repository,
sem depender de nomes de arquivo, comandos, ou convenções específicas
deste repositório (`forge-protocol`) além do próprio contrato de
`capabilities/capability.md`.

## Constraints

### CON-001 · Scope boundary (revised per specification-drift.md)
Não alterar o contrato arquitetural de `capabilities/README.md` além do
parágrafo de status introdutório (correção de acurácia, FR-006); não
alterar `capabilities/capability.md` em nenhuma parte; não introduzir
nenhuma das classes/mecanismos listados em FR-006; não criar um
`SKILL.md` de `investigate`; não implementar qualquer correção
automática do problema que uma futura investigação real encontrar.

## Traceability Matrix

Índice apenas; as referências locais em cada Requirement permanecem
autoritativas.

| Discovery / Pedido original | Requirement | Acceptance |
|---|---|---|
| Contrato existente já cobre o formato | FR-001 | AC-001 |
| "impedir symptom → plausible guess → code change" | FR-002 | AC-002 |
| "nunca deve fabricar certeza para encerrar a investigação" | FR-003 | AC-003 |
| Seção "Boundaries" do pedido original | FR-004 | AC-004 |
| Seção "Applicability" do pedido original | FR-005 | AC-005 |
| Seção "Architecture" (lista de proibições) | FR-006 | AC-006 |

## Compatibility Statement (revisado per specification-drift.md)

Nenhum artefato de Change existente, Schema, Protocol integer, Flow
Gate, ou Harness Adapter é afetado. `capabilities/capability.md`
permanece inalterado; a fundação já antecipa esta Change textualmente
(`ADR-0019`, Consequences). `capabilities/README.md` recebe uma única
correção de acurácia (o parágrafo de status introdutório, que descrevia
`investigate` como trabalho futuro) — seu contrato arquitetural
permanece inalterado. O loader e o modelo existentes permanecem
inalterados — `investigate` é apenas um novo dado consumido por eles.

## Specification Gate

Esta Specification está completa: cada Requirement tem origem
rastreável na Discovery ou no pedido original, Acceptance verificável, e
Boundary explícito onde necessário; os limites do pedido original
(FR-004, FR-006) e o requisito central anti-certeza-fabricada (FR-003)
estão cobertos; nenhum Requirement introduz as classes/mecanismos
explicitamente fora de escopo.

## Out of Scope (revisado per specification-drift.md)

Qualquer mudança no contrato arquitetural de `capabilities/README.md`
além do parágrafo de status introdutório (correção de acurácia,
FR-006), ou qualquer mudança em `capabilities/capability.md`;
`CapabilityRegistry`, `CapabilityExecutor`, discovery automático,
dependency graph, composition runtime, estado próprio de capability,
novo lifecycle, novo Gate, nova versão de Protocol; `/investigate`;
`SKILL.md` de Claude/Codex/Cursor; adapters de Harness; qualquer
implementação de correção para o problema que uma futura investigação
real encontrar.
