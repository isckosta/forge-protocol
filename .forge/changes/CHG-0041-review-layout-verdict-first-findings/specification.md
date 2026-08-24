---
forge:
  artifact: specification
  schema: 1
change: CHG-0041
status: draft
---

# CHG-0041 · Specification

> **Change Contract**
>
> Esta Specification define o novo layout de `review.md`: um registro
> auditável de decisão e findings no qual o estado atual (aggregate
> Verdict) é imediatamente visível, sem sacrificar o histórico completo
> de iterações — elaborando, não substituindo, a guidance "aggregate
> Verdict primeiro" já normatizada (C-068) e já demonstrada por
> `CHG-0016/review.md`.

## Overview

| | |
|---|---|
| **Change** | CHG-0041 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O scaffold SHALL gerar um `review.md` com `Verdict` como primeira
seção substantiva (`PASS` ou `REQUEST CHANGES`), seguido por `Review
Summary` (derivado dos campos já estruturados de `manifest.yml`),
`Current Subject`, `Open Findings` condicional, `Reviewer
Independence`, e a convenção real e inalterada `## Iteration N —
<verdict>` preservando findings `Rxxx` estruturados — sem introduzir
novo namespace de finding, nova severity, ou nova obrigação de Gate.

## Classification

STANDARD — mesmo Flow de `CHG-0037`/`38`/`39`/`40` e o default do
projeto. O comportamento é localizado ao renderer do scaffold
(`src/forge_cli/change_scaffolding.py`) e à guidance de documentação
(`protocol/artifact-structure.md`); não há mudança de Protocol
integer, Change Schema, severity model, ou reviewer/resolver
independence semantics.

## User Stories

Nenhuma se aplica. Change técnica de tooling/scaffolding sem ator de
domínio distinto; os Requirements abaixo são autocontidos, conforme
Protocol §41.

## Functional Requirements

### FR-001 · Review structural core and identity heading
Origin: Discovery — o template atual (`change_scaffolding.py:311`) é
um esqueleto de duas linhas, divergente do exemplo real
(`CHG-0016/review.md`) e da guidance já normatizada por C-068

#### Requirement
O `review.md` gerado SHALL preservar o `forge:` front matter existente
e emitir, em inglês, as headings estruturais `Verdict`, `Review
Summary`, `Current Subject`, `Reviewer Independence`, `Open Findings`,
seguidas pela convenção real de iteração já existente — substituindo o
template mínimo atual.

#### Expected Behavior
A heading de identidade do artefato SHALL seguir o padrão já adotado
por `intent`/`specification`/`test_design`/`tasks`/`verification`
(`# CHG-XXXX · Review`), em vez do padrão genérico anterior (`#
Strict Review — CHG-XXXX Title` / `# Review — CHG-XXXX Title`).

#### Acceptance
AC-001 — Given um scaffold FAST, STANDARD ou FULL, When `review.md` é
gerado, Then o front matter e as headings estruturais listadas estão
presentes, na ordem declarada, antes da primeira `## Iteration`
heading, e o template mínimo anterior está ausente.

### FR-002 · Verdict uses only recognized states
Origin: Discovery — levantamento real mostra apenas `PASS`/`REQUEST
CHANGES` como vocabulário atual estável; `FAIL`/`FAILED`/texto livre
são ruído histórico pré-`CHG-0016`, não autoridade

#### Requirement
O placeholder de `Verdict` gerado pelo scaffold SHALL permanecer um
marcador de "ainda não executado" (`PENDING`) distinto dos dois
estados finais reconhecidos (`PASS`, `REQUEST CHANGES`), renderizado
como texto em negrito — nunca como heading aninhado.

#### Boundary
Esta Change NÃO introduz um terceiro estado de verdict nem altera o
vocabulário de `manifest.yml: review.status`
(`pending|active|passed|failed`), que permanece um campo distinto do
`## Verdict` do Markdown.

#### Acceptance
AC-002 — Given o `review.md` gerado, When se lê a seção `Verdict`,
Then o valor renderizado é texto em negrito sob `## Verdict`, e o
texto do scaffold placeholder (`PENDING`) é visivelmente distinto de
`PASS`/`REQUEST CHANGES`.

### FR-003 · Review Summary is derived, not hand-counted
Origin: Discovery — `manifest.yml: review.{iteration,blockers,majors,minors,observations}`
já é a autoridade estruturada para exatamente essa contagem
(§41 do prompt original — Structured Authority)

#### Requirement
O scaffold SHALL oferecer uma seção `Review Summary` com guidance para
uma tabela compacta (`Iterations`, `Current Subject`, `Open
Blockers`, `Open Majors`, `Open Minors`, `Final Iteration`, `Result`)
instruindo que os valores sejam os mesmos já registrados em
`manifest.yml: review`, nunca uma contagem manual paralela que possa
divergir.

#### Boundary
Esta Change não introduz nenhum mecanismo automático que gere essa
tabela a partir do manifest; a guidance apenas instrui o autor humano
a manter consistência entre os dois.

#### Acceptance
AC-003 — Given o `review.md` gerado, When a seção `Review Summary` é
inspecionada, Then ela contém guidance explícita instruindo que os
valores de contagem devem corresponder a `manifest.yml: review`, não a
uma contagem manual independente.

### FR-004 · Current Subject makes the reviewed revision explicit
Origin: Discovery — `provenance.yml`'s `subject_provenance`/`revision.commit`
já é a autoridade real para o subject congelado; o Markdown deve
apenas torná-la visível

#### Requirement
O scaffold SHALL oferecer uma seção `Current Subject` com guidance
para uma tabela compacta (`Subject SHA`, `Frozen`, `Iteration`)
referenciando o registro de provenance já existente por id, sem
reinventar um novo conceito de freeze.

#### Acceptance
AC-004 — Given o `review.md` gerado, When a seção `Current Subject` é
inspecionada, Then ela contém uma tabela com as três linhas
(`Subject SHA`/`Frozen`/`Iteration`) e guidance para referenciar
`provenance.yml` por id.

### FR-005 · Open Findings is conditional and omitted-when-empty is explicit
Origin: Discovery — §13 do prompt original; proporcionalidade (§2.5)

#### Requirement
O scaffold SHALL oferecer uma seção `Open Findings` com guidance para
uma tabela compacta (`Finding | Severity | Status | Iteration`)
listando apenas findings ainda abertos, e guidance explícita de que,
quando não houver findings abertos, a seção deve conter uma linha
curta (`No open findings.`) em vez de uma tabela vazia.

#### Boundary
Esta seção é um índice do estado atual; a fonte histórica de cada
finding permanece a Iteration que o produziu (FR-007), não é
duplicada ou movida para cá.

#### Acceptance
AC-005 — Given o `review.md` gerado, When a seção `Open Findings` é
inspecionada, Then ela contém a tabela com as colunas declaradas e
guidance explícita para usar `No open findings.` em vez de tabela
vazia quando aplicável.

### FR-006 · Findings remain first-class, evidence-bearing, and non-prescriptive
Origin: Discovery — `CHG-0016/review.md`'s real finding structure
(`### Rxxx — SEVERITY — <title>`, **Problem:**, evidência); C-025
(evidência obrigatória para BLOCKER/MAJOR); §16 do prompt original

#### Requirement
Findings dentro do histórico de iterações SHALL manter o prefixo
`Rxxx` já estabelecido (`CHG-0016` em diante — sem prefixo de Change),
com severidade reconhecida (`BLOCKER`/`MAJOR`/`MINOR`/`OBSERVATION`),
e guidance instruindo que a resolução exigida descreva a propriedade a
corrigir, não a implementação específica.

#### Boundary
Não introduz um novo namespace de finding nem confunde `Rxxx` (Strict
Review) com `SR-xxx` (Specification Review, artefato distinto, fora
de escopo).

#### Acceptance
AC-006 — Given o `review.md` gerado, When a seção de exemplo de
finding é inspecionada, Then o id segue o padrão `Rxxx` (sem prefixo
de Change), a severidade é uma das quatro reconhecidas, e a guidance
instrui descrever a propriedade exigida em vez de prescrever uma
implementação específica.

### FR-007 · Iteration History preserves the real, stable convention unchanged
Origin: Discovery — levantamento real 100% consistente de `##
Iteration N — <verdict>` em todo `review.md` desde `CHG-0016`;
`protocol/artifact-structure.md` já se compromete a preservá-la
"unchanged"

#### Requirement
A convenção real `## Iteration N — <verdict>` (heading nível 2,
travessão) SHALL permanecer exatamente como está — sem wrapper `##
Iteration History`, sem mudança de heading level, sem mudança de
separador. As novas seções (FR-001 a FR-005, FR-008) SHALL ser
inseridas entre `## Verdict` e a primeira `## Iteration N`.

#### Boundary
Esta Change delibera e diverge do texto ilustrativo do prompt
original (que sugere `## Iteration History` com `### Iteration N ·
<verdict>` aninhado) em favor da convenção real 100% consistente já
em uso — nenhuma Review real usa a forma ilustrada. Isso ainda atinge
o objetivo do prompt (estado atual visível antes do histórico), já
que as novas seções precedem a primeira `## Iteration N`.

#### Acceptance
AC-007 — Given o `review.md` gerado, When a estrutura é inspecionada,
Then `## Iteration 1 — PENDING` aparece exatamente como no template
anterior (mesmo heading level, mesmo separador), posicionada após
`Open Findings` e antes de `Conclusion`, e nenhuma heading `##
Iteration History` é introduzida.

### FR-008 · Reviewer Independence is presented, not asserted from scratch
Origin: Discovery — `protocol/policies/review.yml`'s
`reviewer_resolver_separation` já estrutura essas garantias;
`provenance.yml`'s `role: review` records já as registram

#### Requirement
O scaffold SHALL oferecer uma seção `Reviewer Independence` com
guidance instruindo que a declaração de independência (Execution e
Execution Context distintos do Implementation/Resolution sob revisão)
referencie o registro de provenance correspondente por id, em vez de
ser a única garantia.

#### Acceptance
AC-008 — Given o `review.md` gerado, When a seção `Reviewer
Independence` é inspecionada, Then ela contém guidance instruindo
referência a um registro de `provenance.yml` por id como evidência,
não apenas texto declarativo solto.

### FR-009 · Compatibility and scope boundary
Origin: Discovery — mesmo padrão de fechamento usado por
`CHG-0037`/`38`/`39`/`40`

#### Requirement
Esta Change SHALL preservar `review.md` de Changes históricas
inalterado, SHALL NOT alterar `manifest.yml: review` schema,
`execution-provenance-v2.schema.json`, `protocol/policies/review.yml`,
Protocol integer, Change Schema, `specification-review.md`/`SR-xxx`,
ou Harness Adapter behavior, e SHALL NOT introduzir validação
semântica de Markdown (C-067).

#### Acceptance
AC-009 — Given a suíte completa de testes e `forge validate` antes e
depois da Change, When executados, Then ambos permanecem verdes e
nenhum `review.md`/`specification-review.md` histórico é reescrito.

## Non-functional Requirements

### NFR-001 · Plain-text readability
O layout SHALL permanecer legível como texto plano (sem HTML, emoji,
ou cor dependente de renderer), consistente com §27/§32 da guidance
original — PASS é resultado auditável, não celebratório.

## Constraints

### CON-001 · Scope boundary
Esta Change está limitada a `src/forge_cli/change_scaffolding.py`
(template `review`), `protocol/artifact-structure.md` (seção
"Review"), e os testes de scaffold correspondentes. Não introduz novo
comando CLI, novo schema, ou novo validador. Não toca
`specification_review`.

## Traceability Matrix

| Discovery | Requirement | Acceptance |
| --- | --- | --- |
| Template mínimo sem Review Summary/Current Subject/Open Findings | FR-001 | AC-001 |
| Vocabulário real de verdict é só PASS/REQUEST CHANGES | FR-002 | AC-002 |
| manifest.yml já estrutura contagens | FR-003 | AC-003 |
| provenance.yml já estrutura subject congelado | FR-004 | AC-004 |
| Open Findings deve ser proporcional | FR-005 | AC-005 |
| CHG-0016/review.md demonstra estrutura real de finding | FR-006 | AC-006 |
| Convenção `## Iteration N — <verdict>` é real e estável | FR-007 | AC-007 |
| reviewer_resolver_separation já estruturado em policy/provenance | FR-008 | AC-008 |
| Compatibilidade retroativa e escopo | FR-009 | AC-009 |

## Compatibility Statement

Nenhum impacto retroativo: `review.md`/`specification-review.md`
históricos permanecem válidos e não são reescritos; nenhum Protocol
integer, Change Schema, ou schema JSON alterado; `forge validate` não
passa a interpretar conteúdo de `review.md` (C-067); severity model,
reviewer/resolver independence semantics, e frozen subject semantics
inalterados.

## Specification Gate

Requirements são independentes e verificáveis; Acceptance referencia
apenas ids já estabelecidos (`AC-xxx`, `FR-xxx`, `Rxxx`); nenhum
Requirement introduz obrigação de Gate nova (C-067 preservado
explicitamente por FR-009); FR-007 registra explicitamente e justifica
a única divergência deliberada do texto ilustrativo do prompt original
em favor de precedente real. Compatibility Statement confirma ausência
de impacto retroativo. Pronta para Plan.

## Out of Scope

Novo validador Markdown; novo campo de schema; novo estado de verdict
além dos dois reconhecidos; reescrita de `review.md` histórico;
mudanças em `specification-review.md`/`SR-xxx`; mudanças em reviewer/
resolver independence semantics, frozen subject semantics, ou severity
model; qualquer Harness Adapter; nova versão de Protocol; `##
Iteration History` wrapper (deliberadamente rejeitado, ver FR-007).
