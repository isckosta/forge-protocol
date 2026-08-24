---
forge:
  artifact: specification
  schema: 1
change: CHG-0042
status: draft
---

# CHG-0042 · Specification

> **Change Contract**
>
> Esta Specification define a guidance elaborada para
> `specification-drift.md`: uma narrativa cronológica auditável de
> como um contrato previamente aceito revelou-se insuficiente, sem
> aplicar o princípio Result-Before-Evidence usado por
> Verification/Review — Final decision permanece a última seção.

## Overview

| | |
|---|---|
| **Change** | CHG-0042 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

`protocol/artifact-structure.md`'s seção "Specification Drift" SHALL
ser elaborada de três seções terse (Root Cause, Evidence, Final
decision) para uma narrativa cronológica proporcional (Context,
Trigger, Original Specification, Observed Conflict, Root Cause,
Evidence, Specification Correction, Impact Assessment, Affected
Artifacts, Re-verification, Final decision), preservando a exceção
deliberada a Result-Before-Evidence e sem introduzir scaffold, schema,
ou validação nova — este artefato não tem representação em código.

## Classification

STANDARD, não-comportamental — mesmo Flow default do projeto, sem
Test Design/TDD (não há código a testar; `specification_drift` não é
um stage de Flow nem tem renderer em `change_scaffolding.py`).

## User Stories

Nenhuma se aplica. Change técnica de documentação normativa sem ator
de domínio distinto.

## Functional Requirements

### FR-001 · Chronological narrative structure with Final decision last
Origin: Discovery — guidance atual tem apenas 3 seções; os 4 exemplos
reais (`CHG-0008/11/12/13`) divergem estruturalmente entre si por
falta de elaboração

#### Requirement
A guidance elaborada SHALL descrever a sequência cronológica `Context
→ Trigger → Original Specification → Observed Conflict → Root Cause →
Evidence → Specification Correction → Impact Assessment → Affected
Artifacts → Re-verification → Final decision`, preservando
explicitamente `## Final decision` (grafia real, "d" minúsculo,
confirmada em `CHG-0012`) como a última seção substantiva — uma
exceção deliberada a Result-Before-Evidence (C-068), não sua
aplicação.

#### Boundary
Nenhuma seção é obrigatória em toda ocorrência; a guidance elaborada
SHALL declarar proporcionalidade explicitamente (um drift simples usa
um subconjunto pequeno).

#### Acceptance
AC-001 — Given a seção "Specification Drift" elaborada, When lida,
Then ela lista as onze seções na ordem declarada, com `Final decision`
por último e uma frase explícita justificando essa exceção a
Result-Before-Evidence.

### FR-002 · Materiality boundary distinguishes Drift from Specification Review
Origin: Discovery — `CHG-0013/specification-drift.md` já demonstra
esse boundary real na prática ("No Drift... that is ordinary
Specification Review iteration, not Drift")

#### Requirement
A guidance elaborada SHALL declarar explicitamente que uma correção
de Specification descoberta *antes* de evidência de Implementation
(durante Specification Review adversarial) não é Drift, e que Drift
exige especificamente que evidência de Implementation invalide a
Specification (Protocol §13), citando o precedente real de `CHG-0013`.

#### Acceptance
AC-002 — Given a guidance elaborada, When lida, Then ela declara
explicitamente o boundary de materialidade entre Specification Review
e Specification Drift, referenciando Protocol §13.

### FR-003 · Distinction from Resolution and Decision is explicit
Origin: Discovery — `CHG-0012/specification-drift.md` demonstra a
relação real entre múltiplas Resolutions, Review Convergence
Non-Convergence, e a Decision final

#### Requirement
A guidance elaborada SHALL distinguir explicitamente: Resolution é o
trabalho (`role: resolution` em provenance) que uma Finding pode
exigir; Decision (`manifest.yml: decisions[]`, `DEC-xxx`) é o
mecanismo de escalação quando existe mais de uma semântica
normativa válida; Specification Drift é o registro de que uma
correção normativa foi necessária e o que ela produziu — não
substitui nenhum dos dois.

#### Acceptance
AC-003 — Given a guidance elaborada, When lida, Then ela distingue
Resolution, Decision, e Specification Drift em uma frase cada,
sem sugerir que um substitui o outro.

### FR-004 · The corrected Specification remains the sole authoritative contract
Origin: Discovery — §38 do prompt original ("Avoid Duplicate
Authority"); já implícito na guidance atual mas nunca dito
explicitamente

#### Requirement
A guidance elaborada SHALL declarar explicitamente que a correção
normativa deve ser aplicada a `specification.md` (ou ao Requirement
correspondente), e que `specification-drift.md` não deve se tornar
uma segunda fonte normativa — ele documenta a transição, não substitui
o contrato corrigido.

#### Acceptance
AC-004 — Given a guidance elaborada, When lida, Then a seção
"Specification Correction" declara explicitamente que a mudança deve
ser aplicada ao `specification.md` real, não apenas registrada neste
arquivo.

### FR-005 · Impact Assessment areas are guided, not mandated wholesale
Origin: Discovery — §20-27 do prompt original; proporcionalidade
(§2.5 de `artifact-structure.md`)

#### Requirement
A guidance elaborada SHALL orientar quais áreas tipicamente precisam
de avaliação de impacto quando aplicável (Plan, Tasks, Test
Design/Test Strategy, Verification, Review, Compatibility), incluindo
a declaração explícita de que uma Verification anterior pode deixar
de ser suficiente e que a correção da Specification não resolve
automaticamente a Finding que a revelou (nova Review independente
continua exigida).

#### Boundary
Não força uma tabela de impacto completa para todo drift; a guidance
SHALL declarar que apenas áreas realmente afetadas são listadas.

#### Acceptance
AC-005 — Given a guidance elaborada, When lida, Then ela lista as
áreas de impacto tipicamente relevantes, declara que "Verification
PASS anterior pode deixar de ser suficiente," e declara que a correção
da Specification não substitui uma nova Review independente.

### FR-006 · Unresolved drift and Decision escalation are represented honestly
Origin: Discovery — §30-31 do prompt original; C-054 ("Recommendation
is not Decision")

#### Requirement
A guidance elaborada SHALL declarar que, quando mais de uma semântica
normativa válida existir, o mecanismo de Decision existente deve ser
usado em vez de uma escolha silenciosa, e que um drift ainda não
decidido não deve apresentar uma `Final decision` fictícia — o estado
real (não decidido) deve ser registrado.

#### Acceptance
AC-006 — Given a guidance elaborada, When lida, Then ela declara
explicitamente que um `Final decision` não deve ser fabricado quando
a escolha normativa ainda não foi feita, e referencia o mecanismo de
Decision para trade-offs reais.

### FR-007 · Compatibility and scope boundary
Origin: Discovery — mesmo padrão de fechamento usado por
`CHG-0037`–`41`

#### Requirement
Esta Change SHALL preservar os quatro `specification-drift.md` reais
inalterados, SHALL NOT introduzir stage de scaffold, campo de schema,
validador, Protocol integer novo, ou mudança em Decision/Resolution/
frozen subject semantics, e SHALL NOT alterar
`specification-review.md`/`SR-xxx`.

#### Acceptance
AC-007 — Given o repositório antes e depois da Change, When
comparado, Then nenhum `specification-drift.md` histórico, nenhum
schema, e nenhum código-fonte foi alterado — apenas
`protocol/artifact-structure.md` e `CHANGELOG.md`.

## Non-functional Requirements

### NFR-001 · Plain-text readability
A guidance elaborada SHALL permanecer legível como texto plano, sem
HTML, emoji, ou elementos decorativos (§41 do prompt original).

## Constraints

### CON-001 · Scope boundary
Esta Change está limitada a `protocol/artifact-structure.md` (seção
"Specification Drift") e `CHANGELOG.md`. Nenhum código-fonte, schema,
Flow YAML, ou Contract rule é alterado.

## Traceability Matrix

| Discovery | Requirement | Acceptance |
| --- | --- | --- |
| Guidance atual é terse; exemplos reais divergem | FR-001 | AC-001 |
| CHG-0013 demonstra o boundary Review vs Drift | FR-002 | AC-002 |
| CHG-0012 demonstra Resolution/Decision/Drift | FR-003 | AC-003 |
| Duplicate Authority deve ser evitada | FR-004 | AC-004 |
| Áreas de impacto reais, proporcionais | FR-005 | AC-005 |
| Decision honesta, sem Final decision fictício | FR-006 | AC-006 |
| Compatibilidade retroativa e escopo | FR-007 | AC-007 |

## Compatibility Statement

Nenhum impacto retroativo: os quatro `specification-drift.md` reais
permanecem válidos e não são reescritos; nenhum Protocol integer,
Change Schema, ou schema JSON alterado; `forge validate` não passa a
interpretar conteúdo deste artefato (não interpretava antes, não
interpreta depois — C-067). `specification-review.md`/`SR-xxx`,
Decision mechanics, e frozen subject semantics inalterados.

## Specification Gate

Requirements são independentes e verificáveis por inspeção do texto
de guidance resultante; nenhum Requirement introduz obrigação de Gate
nova; Compatibility Statement confirma ausência de impacto
retroativo. Pronta para Plan.

## Out of Scope

Novo stage de scaffold para `specification_drift`; novo validador;
nova versão de Protocol; reescrita de `specification-drift.md`
histórico; mudanças em `specification-review.md`/`SR-xxx`, Decision
mechanics, Resolution semantics, ou frozen subject semantics; qualquer
Harness Adapter.
