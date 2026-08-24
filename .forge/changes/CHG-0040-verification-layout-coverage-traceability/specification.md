---
forge:
  artifact: specification
  schema: 1
change: CHG-0040
status: draft
---

# CHG-0040 · Specification

> **Change Contract**
>
> Esta Specification define o novo layout de `verification.md`: um
> relatório de conformidade orientado a resultado, no qual a conclusão
> aparece imediatamente e toda afirmação de conformidade é rastreável até
> a evidência que a sustenta — elaborando, não substituindo, a guidance
> "Result-Before-Evidence" já normatizada (C-068).

## Overview

| | |
|---|---|
| **Change** | CHG-0040 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O scaffold SHALL gerar um `verification.md` com `Result` como primeira
seção substantiva (um de `PASS`/`FAIL`/`SKIPPED`/`NOT APPLICABLE`),
seguido por `Summary`, `Acceptance Coverage` (tabela compacta `AC-xxx →
Requirement → Result → Evidence`), `Requirement Coverage` condicional,
`Test Evidence`, `Forge Evidence`, `Manual Evidence` condicional,
`Compatibility and Limitations`, e `Conclusion` — preservando o `forge:`
front matter existente e sem introduzir enforcement de Markdown, novo
estado de resultado, ou nova versão de Protocol.

## Classification

STANDARD — mesmo Flow de `CHG-0037`/`CHG-0038`/`CHG-0039` e o default do
projeto (`.forge/forge.yml: flows.default`). O comportamento é
localizado ao renderer do scaffold (`src/forge_cli/change_scaffolding.py`)
e à guidance de documentação (`protocol/artifact-structure.md`); não há
mudança de Protocol integer, Change Schema, Gate semantics ou execução
de Harness Adapter.

## User Stories

Nenhuma se aplica. Change técnica de tooling/scaffolding sem ator de
domínio distinto; os Requirements abaixo são autocontidos, conforme
Protocol §41.

## Functional Requirements

### FR-001 · Verification structural core and identity heading
Origin: Discovery — o template atual (`change_scaffolding.py:286`) é um
esqueleto de cinco linhas sem cobertura rastreável, divergente do
exemplo canônico e da guidance já normatizada por C-068

#### Requirement
O `verification.md` gerado SHALL preservar o `forge:` front matter
existente e emitir, em inglês, as headings estruturais `Result`,
`Summary`, `Acceptance Coverage`, `Test Evidence`, `Forge Evidence`,
`Compatibility and Limitations`, e `Conclusion`, substituindo o
template mínimo atual (`Result`/`Summary`/`Test Evidence`/`Forge
Evidence`/`Conclusion` sem tabela).

#### Expected Behavior
A heading de identidade do artefato SHALL seguir o padrão já adotado por
`intent`/`specification`/`test_design`/`tasks` (`# CHG-XXXX ·
Verification`), em vez do padrão genérico anterior (`# Verification —
CHG-XXXX Title`).

#### Acceptance
AC-001 — Given um scaffold FAST, STANDARD ou FULL comportamental, When
`verification.md` é gerado, Then o front matter e as headings
estruturais listadas estão presentes, na ordem declarada, e o template
mínimo anterior está ausente.

### FR-002 · Result uses only recognized states
Origin: Discovery — `protocol/artifact-structure.md` §4 "Verification"
já reconhece exatamente quatro estados; `INCONCLUSIVE` e variantes não
têm precedente

#### Requirement
O placeholder de `Result` gerado pelo scaffold SHALL permanecer um
marcador de "ainda não executado" distinto dos quatro estados finais
reconhecidos (`PASS`, `FAIL`, `SKIPPED`, `NOT APPLICABLE`), renderizado
como texto em negrito — nunca como heading aninhado.

#### Boundary
Esta Change NÃO introduz um quinto estado de resultado nem altera o
vocabulário de `manifest.yml: verification.status`
(`pending`/`passed`), que permanece um campo distinto do `## Result` do
Markdown.

#### Acceptance
AC-002 — Given o `verification.md` gerado, When se lê a seção `Result`,
Then o valor renderizado é texto em negrito sob `## Result`, não uma
segunda heading `#`/`##` aninhada, e o texto do scaffold placeholder
(`PENDING`) é visivelmente distinto dos quatro estados finais.

### FR-003 · Acceptance Coverage traceable to Requirement and Evidence
Origin: Discovery — nenhum `verification.md` real usa `AC-xxx` hoje; a
guidance existente menciona a tabela mas o scaffold nunca a ofereceu

#### Requirement
O scaffold SHALL emitir uma seção `Acceptance Coverage` com uma tabela
`Acceptance | Requirement | Result | Evidence`, referenciando
identificadores já estabelecidos (`AC-xxx`, `FR-xxx`/`NFR-xxx`,
`TDD-xxx`/`TD-xxx` ou evidência equivalente) por id — nunca reproduzindo
o texto integral de um Acceptance Criterion.

#### Boundary
Não introduz um novo prefixo de identificador para Verification;
consome exclusivamente os ids já produzidos por Specification e Test
Design/Test Strategy.

#### Acceptance
AC-003 — Given uma Change com Acceptance Criteria (`AC-xxx`) declarados
na Specification, When `verification.md` é preenchido, Then a tabela
`Acceptance Coverage` referencia cada `AC-xxx` pelo id, com uma coluna
`Evidence` apontando para um id de evidência (`TDD-xxx`/`TD-xxx`/comando)
em vez de texto livre não rastreável.

### FR-004 · Requirement Coverage is conditional and non-duplicative
Origin: Discovery — Protocol §2.4 (Scanability) recomenda tabelas apenas
onde melhoram legibilidade; uma segunda tabela redundante com Acceptance
Coverage reduziria, não melhoraria, a leitura

#### Requirement
O scaffold SHALL oferecer uma seção `Requirement Coverage` opcional
(tabela `Requirement | Evidence | Result`) agregando por `FR-xxx`/
`NFR-xxx`, presente apenas quando agrega informação que a Acceptance
Coverage por si só não expressa (por exemplo, um Requirement coberto por
múltiplos Acceptance Criteria ou por verificação estática sem AC
associado).

#### Boundary
Uma Change pequena, com relação 1:1 entre Acceptance e Requirement, PODE
omitir esta seção sem violar a estrutura (proporcionalidade, §2.5).

#### Acceptance
AC-004 — Given uma Change onde `Acceptance Coverage` já expressa
integralmente a cobertura por Requirement, When `verification.md` é
preenchido, Then `Requirement Coverage` é omitida sem que isso seja
tratado como incompleto.

### FR-005 · Manual Evidence remains distinct from automated evidence
Origin: Discovery — Test Design já distingue `Type: Manual Acceptance`
de tipos automatizados; Verification precisa preservar essa distinção do
lado do resultado

#### Requirement
O scaffold SHALL oferecer uma seção `Manual Evidence` condicional,
distinta de `Test Evidence` e `Forge Evidence`, para verificações que
dependem de avaliação humana — presente apenas quando a Change tem
verificação manual real.

#### Boundary
Uma verificação manual NÃO PODE ser apresentada sob `Test Evidence` como
se fosse automatizada, nem `Manual Evidence` PODE ser sintetizada quando
nenhuma verificação manual ocorreu de fato.

#### Acceptance
AC-005 — Given uma Change sem verificação manual, When `verification.md`
é preenchido, Then a seção `Manual Evidence` está ausente (não vazia);
Given uma Change com verificação manual, Then `Manual Evidence` registra
o resultado distinto de `Test Evidence`.

### FR-006 · TDD RED→GREEN evidence is referenced, not renarrated
Origin: Discovery — `tdd-evidence.yml`/`protocol/schemas/tdd-evidence.schema.json`
já estruturam `red`/`intermediate_green`/`green` por ciclo `TDD-xxx`;
`CHG-0039/verification.md` já referencia por id na prática

#### Requirement
Quando TDD se aplica, o `Test Evidence` gerado SHALL orientar a
referência ao ciclo `TDD-xxx` correspondente (RED antes da falha
esperada, GREEN depois) por id, em vez de renarrar manualmente a
sequência quando `tdd-evidence.yml` já a registra.

#### Boundary
Esta Change não altera `tdd-evidence.schema.json` nem o formato de
`tdd-evidence.yml`; apenas orienta como `verification.md` referencia o
que já é autoridade estruturada existente.

#### Acceptance
AC-006 — Given uma Change com `tdd-evidence.yml` ativo, When
`verification.md` registra evidência TDD, Then a evidência referencia o
`TDD-xxx` correspondente por id em vez de reproduzir integralmente
comandos e outputs já capturados em `tdd-evidence.yml`.

### FR-007 · Failure and Skipped/Not Applicable preserve structure and rationale
Origin: Discovery — a guidance atual não distingue como a estrutura se
comporta sob `FAIL`/`SKIPPED`/`NOT APPLICABLE`; o risco é uma Conclusion
que sugere Completion mesmo sob falha

#### Requirement
Quando `Result` for `FAIL`, a estrutura SHALL permanecer útil — Summary
e Acceptance Coverage identificam quais critérios falharam, e a
Conclusion NÃO PODE sugerir Completion. Quando `Result` for `SKIPPED` ou
`NOT APPLICABLE`, o scaffold SHALL orientar um rationale proporcional
explicando por que a Verificação não se aplica ou foi pulada.

#### Boundary
Esta Change não altera a semântica de quando `FAIL` é apropriado
(Contract já define isso via C-020/C-068); apenas garante que a
estrutura do artefato não mascare esse resultado.

#### Acceptance
AC-007 — Given `Result: FAIL`, When se lê `Conclusion`, Then o texto não
afirma ou implica que a Change está pronta para o próximo gate; Given
`Result: SKIPPED` ou `NOT APPLICABLE`, Then existe uma seção ou
parágrafo de rationale proporcional ao lado do Result.

### FR-008 · Compatibility and scope boundary
Origin: Discovery — mesmo padrão de fechamento usado por `CHG-0037`/
`CHG-0038`/`CHG-0039`

#### Requirement
Esta Change SHALL preservar `verification.md` de Changes históricas
inalterado, SHALL NOT alterar `manifest.yml: verification.status`,
`tdd-evidence.schema.json`, `traceability.schema.json`, Protocol
integer, Change Schema, ou Harness Adapter behavior, e SHALL NOT
introduzir validação semântica de Markdown (C-067).

#### Acceptance
AC-008 — Given a suíte completa de testes e `forge validate` antes e
depois da Change, When executados, Then ambos permanecem verdes e
nenhum `verification.md` histórico é reescrito.

## Non-functional Requirements

### NFR-001 · Plain-text readability
O layout SHALL permanecer legível como texto plano (sem HTML, emoji, ou
cor dependente de renderer), consistente com C-067/§32 da guidance
canônica (linguagem de status decorativa é explicitamente desencorajada).

## Constraints

### CON-001 · Scope boundary
Esta Change está limitada a `src/forge_cli/change_scaffolding.py`
(template `verification`), `protocol/artifact-structure.md` (seção
"Verification"), `examples/canonical-artifacts/verification.md` (quando
necessário para demonstrar a estrutura elaborada), e os testes de
scaffold correspondentes. Não introduz novo comando CLI, novo schema, ou
novo validador.

## Traceability Matrix

| Discovery | Requirement | Acceptance |
| --- | --- | --- |
| Template mínimo sem cobertura rastreável | FR-001 | AC-001 |
| Guidance já reconhece 4 estados, sem quinto estado | FR-002 | AC-002 |
| Nenhum precedente real usa `AC-xxx` | FR-003 | AC-003 |
| Redundância entre Acceptance e Requirement Coverage | FR-004 | AC-004 |
| Manual Evidence precisa permanecer distinta | FR-005 | AC-005 |
| `tdd-evidence.yml` já estrutura RED→GREEN | FR-006 | AC-006 |
| Conclusion pode mascarar FAIL | FR-007 | AC-007 |
| Compatibilidade retroativa e escopo | FR-008 | AC-008 |

## Compatibility Statement

Nenhum impacto retroativo: `verification.md` históricos permanecem
válidos e não são reescritos; `manifest.yml: verification.status`
inalterado; nenhum Protocol integer, Change Schema, ou schema JSON
alterado; `forge validate` não passa a interpretar conteúdo de
`verification.md` (C-067). `test-strategy.md`/`plan.md`/`tasks.md` e
demais artefatos não são tocados.

## Specification Gate

Requirements são independentes e verificáveis; Acceptance referencia
apenas ids já estabelecidos (`AC-xxx`, `FR-xxx`, `TDD-xxx`); nenhum
Requirement introduz obrigação de Gate nova (C-067 preservado
explicitamente por FR-008); Compatibility Statement confirma ausência de
impacto retroativo. Pronta para Plan.

## Out of Scope

Novo validador Markdown; novo campo de schema; novo estado de resultado
além dos quatro reconhecidos; reescrita de `verification.md` histórico;
integração automática com `traceability.yml`; mudanças em `review.md`,
`test-strategy.md`, `plan.md`, ou qualquer Harness Adapter; nova versão
de Protocol.
