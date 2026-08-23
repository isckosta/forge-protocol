---
forge:
  artifact: specification
  schema: 1
change: CHG-0038
status: draft
---

# CHG-0038 · Specification

> **Change Contract**
>
> Esta Specification define o novo layout de `test-design.md`: um contrato de verificação pré-Implementation, rastreável até Requirements e User Stories, distinto de Verification.

## Overview

| | |
|---|---|
| **Change** | CHG-0038 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O scaffold SHALL gerar um `test-design.md` com Overview, Test Strategy, Coverage Map, cenários `TD-xxx` autocontidos (Purpose, Preconditions, Scenario, Evidence, Failure Condition, Boundary), Requirement Coverage, Coverage Gaps e um Test Design Gate — preservando o front matter existente e sem introduzir enforcement de Markdown.

## Classification

STANDARD. O comportamento é localizado ao renderer do scaffold (`src/forge_cli/change_scaffolding.py`) e à guidance de documentação (`protocol/artifact-structure.md`); não há mudança de Protocol integer, Change Schema, Gate semantics ou execução de Harness Adapter.

## User Stories

Nenhuma se aplica. Esta é uma Change técnica de tooling/scaffolding sem ator de domínio distinto; os Requirements abaixo são autocontidos, conforme Protocol §41 ("Requirements remain the authoritative contract ... without a User Story").

## Functional Requirements

### FR-001 · Verification design contract scaffold layout
Origin: Discovery — achado sobre o template mínimo atual de `test_design`

#### Requirement
O `test-design.md` gerado SHALL preservar o `forge:` front matter existente e emitir, em inglês, as headings estruturais `Overview`, `Test Strategy`, `Coverage Map`, `Requirement Coverage`, `Coverage Gaps` e `Test Design Gate`, substituindo o template mínimo atual (`Objective`/`Strategy`/`TDD-001 — <behavior>`/`Completion Criteria`).

#### Expected Behavior
A heading de identidade do artefato SHALL seguir o padrão já adotado por `intent` e `specification` (`# CHG-XXXX · Test Design`), em vez do padrão genérico anterior (`# Test Design — CHG-XXXX Title`).

#### Acceptance
AC-001 — Given um scaffold STANDARD ou FAST comportamental, When `test-design.md` é gerado, Then o front matter e as headings estruturais listadas estão presentes e o template mínimo anterior está ausente.

### FR-002 · Self-contained TD-xxx scenario structure
Origin: Discovery — necessidade de rastreabilidade por cenário

#### Requirement
Cada cenário gerado como exemplo SHALL usar o identificador estável `### TD-001 · <scenario>` e suportar, como subseções, `Requirements`, `Stories` (opcional), `Type`, `Priority`, `#### Purpose`, `#### Preconditions`, `#### Scenario`, `#### Evidence`, `#### Failure Condition` e `#### Boundary`.

#### Expected Behavior
A guidance SHALL deixar explícito que nem toda subseção é obrigatória em todo cenário — uma subseção sem conteúdo material SHALL ser omitida, não preenchida com `N/A`.

#### Boundary
Este Requirement cobre a forma do scaffold gerado, não a qualidade do conteúdo que um autor humano ou agente vier a escrever dentro dela.

#### Acceptance
AC-002 — Um cenário de exemplo gerado contém `### TD-001 ·`, `#### Purpose` e `#### Scenario`; a heading solta `## TDD-001 — <behavior>` do template anterior está ausente.

### FR-003 · Requirement traceability with optional User Stories
Origin: Discovery — evolução equivalente à CHG-0037 para Specification

#### Requirement
A guidance SHALL descrever uma `Coverage Map` e uma `Requirement Coverage` que funcionem tanto com quanto sem User Stories, e SHALL declarar explicitamente que um Requirement sem User Story permanece válido.

#### Boundary
A Coverage Map é um índice; não substitui as referências `Requirements:`/`Stories:` registradas em cada cenário `TD-xxx`.

#### Acceptance
AC-003 — A guidance mostra a forma da tabela com coluna `User Story` e a forma sem essa coluna, e contém a frase equivalente a "a Requirement without a User Story is valid".

### FR-004 · Automated and Manual Acceptance are distinguished
Origin: Discovery — risco de tratar interação humana como automaticamente verificável

#### Requirement
A guidance SHALL nomear um `Type: Manual Acceptance` distinto de tipos automatizados (ex.: Unit, Integration, Domain Integration) e SHALL exigir, para esse tipo, Preconditions, instruções de operador, evidência observável e Failure Condition.

#### Boundary
Este Requirement não introduz execução real de aceitação manual nem qualquer tooling de coleta de evidência — apenas a guidance textual do scaffold.

#### Acceptance
AC-004 — A guidance contém a frase `Manual Acceptance` e declara que ela não deve ser confundida com verificação automática.

### FR-005 · Valid RED guidance excludes non-behavioral failure causes
Origin: Discovery — Protocol §19/§15 (RED deve falhar pela razão comportamental esperada)

#### Requirement
Quando TDD se aplica, a guidance SHALL descrever o que torna um RED válido (falha pela razão comportamental esperada) e SHALL listar causas que invalidam um RED como evidência (erro de sintaxe, import quebrado, fixture inválida, configuração ausente, infraestrutura indisponível sem relação com a regra testada).

#### Boundary
Esta Requirement não cria uma nova regra de Protocol; formaliza, na guidance do artefato, o que Protocol §15/§19 e Contract C-016 já exigem.

#### Acceptance
AC-005 — A guidance lista explicitamente pelo menos as quatro causas de RED inválido citadas acima.

### FR-006 · Compatibility and scope boundary
Origin: Discovery — achado de compatibilidade e separação Test Design/Test Strategy

#### Requirement
`test-design.md` históricos SHALL permanecer válidos sem reescrita; `forge validate` SHALL NOT passar a parsear ou impor a estrutura Markdown de `test-design.md`; o template e a guidance de `test-strategy.md` (Flow FULL) SHALL permanecer inalterados por esta Change.

#### Acceptance
AC-006 — Os testes de scaffold e de contrato existentes continuam passando; nenhum arquivo sob `protocol/schemas/` muda; o template `test_strategy` em `_markdown()` permanece byte-idêntico ao anterior.

## Non-functional Requirements

### NFR-001 · Plain-text readability
O Markdown gerado SHALL permanecer legível sem HTML específico de renderer, badges, emojis ou tooling externo obrigatório.

## Constraints

### CON-001 · Scope boundary
Não criar parser de Markdown, framework BDD, geração automática de testes, nova versão de Protocol, novo Schema, novo comando de lifecycle, exigência de User Story para todo Requirement, Story Points, ou cobertura de código. Não redesenhar `test-strategy.md`.

## Traceability Matrix

Índice apenas; as referências locais em cada Requirement permanecem autoritativas.

| Discovery | Requirement | Acceptance |
|---|---|---|
| Template mínimo atual de `test_design` | FR-001 | AC-001 |
| Necessidade de rastreabilidade por cenário | FR-002 | AC-002 |
| Evolução equivalente à CHG-0037 | FR-003 | AC-003 |
| Risco de aceitação manual disfarçada de automática | FR-004 | AC-004 |
| Protocol §19/§15 — RED válido | FR-005 | AC-005 |
| Compatibilidade e separação Test Design/Test Strategy | FR-006 | AC-006 |

## Compatibility Statement

O front matter existente, o Change Schema, os inteiros de Protocol, os Flow Gates, os `test-design.md` históricos, `test-strategy.md` e a semântica de Harness Adapter permanecem inalterados. A nova estrutura aplica-se apenas a `test-design.md` recém-gerados e à guidance correspondente.

## Specification Gate

Esta Specification está completa quando o comportamento do scaffold, a guidance canônica dividida (Test Design vs. Test Strategy), o exemplo de domínio ERP, a documentação e os testes focados estiverem atualizados sem introduzir enforcement semântico de Markdown.

## Out of Scope

Mudança de semântica de Protocol, mudança de Schema, parsing de Markdown por validador, execução de BDD, reescrita retroativa de artefatos históricos, e qualquer alteração em `test-strategy.md`.
