---
forge:
  artifact: specification
  schema: 1
change: CHG-0048
status: draft
---

# CHG-0048 · Specification

> **Change Contract**
>
> Esta Specification define os três Review Profiles canônicos (`focused`/FAST, `standard`/STANDARD, `strict`/FULL), o texto revisado de C-022/C-023/C-031, as mudanças aditivas de Schema, o comportamento (inalterado) de validação de independência/evidence/severities/convergence, e a propagação profile-aware para Adapters — sob RFC-0007 (aceito, Protocol 2).

## Overview

| | |
|---|---|
| **Change** | CHG-0048 |
| **Flow** | FULL |
| **Status** | Draft |

## Summary

O Forge SHALL passar a associar um Review Profile (`focused | standard | strict`) a cada Flow canônico, preservando um único lifecycle de Review, um único vocabulário de Finding/evidence/severity, e os mecanismos existentes de Resolution, Resolution Verification, Convergence Limit e provenance (C-026) inalterados e aplicados identicamente aos três profiles. `strict` (FULL) SHALL permanecer byte-idêntico em comportamento ao Strict Review adversarial de hoje. A mudança é normativa (Contract), estrutural (Flow files, Schemas) e de projeção (Adapters/CLI), fundamentada em RFC-0007.

## Classification

FULL. Esta Change altera texto normativo do Contract (C-022, C-023, nota em C-031), as três definições de Flow, três Schemas de Protocol 2 (`change-v2`, `flow`, `policy-review-v2`), código de validação, e as duas projeções de Harness Adapter shipped (Claude Code, Codex) — corresponde diretamente aos disqualifiers de FAST (`architectural_change`, `major_public_contract_change`) e exige RFC (F-008), já satisfeito por RFC-0007 (aceito).

## User Stories

Nenhuma se aplica. Esta é uma Change técnica de Protocol/tooling sem ator de domínio distinto; os Requirements abaixo são autocontidos, conforme Protocol §41.

## Functional Requirements

### FR-001 · Canonical Review Profile per Flow
Origin: Discovery — as três Flows declaram `review:` idêntico hoje; RFC-0007 item 1

#### Requirement
Cada Flow canônico SHALL declarar um campo `profile` em seu bloco `review:` (`protocol/flows/fast.yml` → `focused`, `standard.yml` → `standard`, `full.yml` → `strict`), e `protocol/versions/2/policies/review.yml` SHALL declarar o mesmo mapeamento como sua fonte canônica de política. `required: true` SHALL permanecer incondicional nos três Flows — Review nunca é opcional.

#### Boundary
Este Requirement define apenas o campo e seu valor canônico por Flow; não define o comportamento de cada profile (FR-002–FR-004) nem a validação de piso de configuração (FR-010).

#### Acceptance
AC-001 — `fast.yml`, `standard.yml`, `full.yml` e `protocol/versions/2/policies/review.yml` declaram, cada um, `profile` com o valor canônico correto; `full.yml`'s demais campos de `review:` (`required`, `strict`, `adversarial`) permanecem exatamente como hoje.

### FR-002 · `focused` Review Profile (FAST)
Origin: RFC-0007 item 2

#### Requirement
Sob o profile `focused`, Review SHALL ser escopada ao diff real da Change, regressões que ele possa introduzir, o(s) Requirement(s) que ele visa, e qualquer Finding material que o Reviewer efetivamente observe — SHALL NOT exigir busca adversarial irrestrita por qualquer motivo concebível de rejeição fora desse escopo.

#### Expected Behavior
Um Finding material observado sob `focused` SHALL ter a mesma autoridade de bloqueio (BLOCKER/MAJOR conforme C-027) que teria sob `strict` — `focused` reduz o escopo da busca, não a autoridade do resultado.

#### Acceptance
AC-002 — A instrução de Review projetada para FAST (Adapter) descreve o escopo `focused` acima; nenhuma mudança na severidade ou no bloqueio de Completion por Finding material ocorre quando o profile é `focused`.

### FR-003 · `standard` Review Profile (STANDARD)
Origin: RFC-0007 item 3

#### Requirement
Sob o profile `standard`, Review SHALL avaliar compliance com a Specification, correctness e qualidade da implementação com escrutínio genuíno e baseado em evidência, SHALL NOT exigir a obrigação adicional de `strict` de buscar exaustivamente motivos adversariais além do escopo e da evidência que a própria Change declara.

#### Acceptance
AC-003 — A instrução de Review projetada para STANDARD (Adapter) descreve o escopo `standard` acima, distinto tanto de `focused` (mais amplo: cobre compliance/correctness/qualidade, não só diff/regressão) quanto de `strict` (sem a obrigação de busca adversarial irrestrita).

### FR-004 · `strict` Review Profile (FULL) — comportamento preservado
Origin: RFC-0007 item 4; Discovery

#### Requirement
Sob o profile `strict`, Strict Review SHALL permanecer inteiramente adversarial, buscando ativamente motivos de rejeição, exatamente como C-023 define hoje — sem nenhuma regressão de comportamento para Changes FULL.

#### Acceptance
AC-004 — Nenhuma Change FULL, histórica ou futura, observa qualquer mudança de comportamento de Review atribuível a esta Change; a instrução de Review projetada para FULL é idêntica em substância à instrução hoje existente.

### FR-005 · Contract C-022 e C-023 revisados
Origin: RFC-0007 item 5; Discovery — Questão normativa resolvida

#### Requirement
C-022 SHALL ser revisado para desacoplar "Review é obrigatória" de "Review é estritamente adversarial": *"Every Change MUST undergo Review, at the rigor and posture defined by its Flow's Review Profile. `focused` and `standard` remain genuine Review with real rejection authority — never a rubber stamp, diff-only inspection, or passing-tests-only sufficiency."* C-023 SHALL ser revisado para escopar a obrigação adversarial ao profile `strict`, preservando a obrigação de rejeição em `focused`/`standard` sobre qualquer Finding material efetivamente identificado.

#### Boundary
Este Requirement altera apenas C-022/C-023 no Contract canônico de Protocol 2 (`protocol/versions/2/contract/engineering.md`). O Contract de Protocol 1 (`protocol/contract/engineering.md`) permanece inalterado — profiles são um conceito de Protocol 2 apenas (FR-009's Boundary).

#### Acceptance
AC-005 — `protocol/versions/2/contract/engineering.md`'s C-022/C-023 refletem o texto acima (ou equivalente semântico aprovado em Specification Review); `protocol/contract/engineering.md` (Protocol 1) permanece byte-idêntico.

### FR-006 · C-031 clarificado
Origin: RFC-0007 item 7

#### Requirement
C-031 SHALL ser clarificado para declarar explicitamente que o profile `focused` de FAST não remove a autoridade de Review de bloquear sobre um Finding real, apenas restringe sua obrigação de busca: *"FAST's Review Profile (`focused`) MUST NOT remove applicable TDD, Verification, Review, or Documentation Impact evaluation — it narrows Review's search obligation, not its authority to block on a real Finding."*

#### Acceptance
AC-006 — C-031 em `protocol/versions/2/contract/engineering.md` reflete a clarificação acima.

### FR-007 · Invariantes preservados sem alteração
Origin: RFC-0007 item 6; Constraint explícita do pedido original

#### Requirement
C-024, C-025, C-026, C-027, C-047, C-048, C-049, C-050, C-059, C-067, C-068 SHALL permanecer textualmente inalterados. Independência Reviewer/Resolver (execution/context separation, revision binding), requisitos de evidence para BLOCKER/MAJOR, severities (BLOCKER/MAJOR/MINOR/observation), Resolution, Resolution Verification, o Convergence Limit (2), e repository-native provenance SHALL ser aplicados de forma idêntica nos três profiles — nenhum desses mecanismos SHALL ser condicionado a `profile` em código ou em Contract.

#### Boundary
Este Requirement é uma restrição negativa: nenhuma nova lógica condicional por profile SHALL ser introduzida em nenhum desses mecanismos.

#### Acceptance
AC-007 — Diff desta Change não modifica o texto de C-024/C-025/C-026/C-027/C-047–C-050/C-059/C-067–C-068; `_validate_resolution_verification` e `_validate_protocol2_review_provenance` (`src/forge_cli/validation/__init__.py`) permanecem sem nenhum branch condicionado a `manifest.flow` ou a `profile` para independência, evidence, severities ou convergence.

### FR-008 · Mudanças de Schema, com default `strict` retroativo
Origin: RFC-0007 items 8–9 (revisado); Discovery — catálogo de Schemas; Specification Review SR-002/SR-003

#### Requirement
`protocol/schemas/change-v2.schema.json`'s objeto `review`, `protocol/schemas/policy-review-v2.schema.json`, e `protocol/schemas/project-flow.schema.json`'s objeto `review` (o mecanismo já existente e já consumido — via `resolve_effective_flow`, chamado por `forge validate` — de override de Flow por projeto, `.forge/flows/<flow_id>.yml`, `schema: forge/project-flow@1`; distinto e mais preciso que `.forge/forge.yml`'s bloco `review.strict` global, hoje não lido por nenhum código de CLI) SHALL ganhar um campo `profile` (enum `focused | standard | strict`) opcional, aditivo. Um manifest, política ou configuração de projeto que omita `profile` SHALL ser interpretado como `strict`. Separadamente, `protocol/schemas/flow.schema.json`'s sub-schema `review` SHALL substituir seus `const: true` fixos de `strict`/`adversarial` por um enum `profile` (preservando `required: true` como constante) — esta substituição SHALL ser tratada como a codificação direta em Schema da decisão de Contract já resolvida em FR-005 (RFC-0007, questão normativa resolvida), não como uma decisão aditiva independente: o `const: true` existia apenas para impor a obrigação hoje incondicional de C-022/C-023. `protocol/schemas/policy-review.schema.json` (Protocol 1) SHALL permanecer inalterado.

#### Boundary
Nenhuma Change histórica cujo `manifest.yml`/`provenance.yml` já validou contra os Schemas atuais SHALL deixar de validar após esta mudança nos três Schemas cujo campo é aditivo (`change-v2`, `policy-review-v2`, `project`). `flow.schema.json`'s narrowing não tem instâncias históricas análogas para invalidar — só três arquivos canônicos vivos, editados nesta própria Change — mas é registrado explicitamente como uma redução de garantia mecânica, não uma reivindicação puramente aditiva.

#### Acceptance
AC-008 — Os quatro Schemas de Protocol 2 tocados aceitam `profile` quando presente; os três com campo aditivo continuam aceitando manifests/políticas/configuração que o omitem; `policy-review.schema.json` (Protocol 1) é byte-idêntico ao anterior; uma suíte de manifests históricos representativos (amostra de `.forge/changes/*/manifest.yml` já completos) continua validando sem erro; qualquer `.forge/flows/<flow_id>.yml` de projeto existente que já valide contra `project-flow.schema.json` continua validando após a mudança.

### FR-009 · Adapter projections profile-aware; independência permanece compartilhada
Origin: RFC-0007 item 11; Discovery — `review_independence.py`, `claude_code/projection.py`, `codex/projection.py`

#### Requirement
`claude_code/projection.py` e `codex/projection.py`'s geração de instrução de gate por Flow SHALL substituir a linha fixa "Completion requires Strict Review to pass." por uma instrução profile-specific (`focused`/`standard`/`strict`) coerente com FR-002–FR-004. O bloco de independência Reviewer/Resolver (`review_independence.py`) SHALL permanecer compartilhado e Flow-invariante, sem reintroduzir a repetição por Flow que o CHG-0045 removeu.

#### Boundary
Este Requirement não reabre a arquitetura de consolidação do CHG-0045 além da linha de instrução de review — o restante da seção de gate obligations por Flow permanece como está.

#### Acceptance
AC-009 — O `SKILL.md` gerado para Claude Code e Codex mostra, para cada seção `### Flow` (FAST/STANDARD/FULL), uma instrução de review distinta e correspondente ao profile daquele Flow; o bloco de independência permanece único, compartilhado, e idêntico ao atual.

### FR-010 · Piso de profile por Flow; configuração de projeto pode só reforçar
Origin: RFC-0007 item 12; Constraint 11 do pedido original

#### Requirement
A configuração efetiva de um projeto (`.forge/flows/<flow_id>.yml`, mesclada com o Flow canônico via `resolve_effective_flow`, per FR-008) MAY declarar, em seu bloco `review.profile`, um profile mais rigoroso que o piso canônico daquele Flow (ex.: forçar `strict` em `.forge/flows/fast.yml`), mas MUST NOT declarar um profile mais fraco que esse piso. `forge validate` SHALL falhar fechado (Finding explícito) quando a configuração efetiva de um projeto declarar um profile abaixo do piso canônico do Flow aplicável — esta checagem SHALL usar o resultado já retornado por `resolve_effective_flow` (já chamado por `validate_project` para cada `.forge/flows/*.yml`), sem introduzir um segundo mecanismo de leitura de Flow.

#### Acceptance
AC-010 — Um teste demonstra que uma configuração de projeto declarando `profile: focused` para um Change classificado FULL (piso `strict`) produz um Finding de `forge validate`, enquanto declarar `profile: strict` para uma Change FAST (piso `focused`, reforçando) não produz Finding algum.

### FR-011 · Compatibilidade retroativa
Origin: Constraint 12 do pedido original; C-045

#### Requirement
Nenhuma Change histórica completa SHALL ser invalidada por esta mudança. `forge validate` aplicado a qualquer manifest histórico já `state.current: complete` SHALL continuar retornando válido, interpretando a ausência de `profile` como `strict` (FR-008).

#### Acceptance
AC-011 — Reexecutar `forge validate` contra o estado atual do repositório (todas as Changes completas existentes) após esta mudança não introduz nenhum Finding novo.

### FR-012 · Review Profile derivado do Flow efetivo; escalação C-005 propaga o profile
Origin: RFC-0007 item 13; Specification Review SR-006

#### Requirement
O Review Profile aplicável a um Review Iteration SHALL ser derivado de `manifest.flow.current` (o Flow efetivo da Change) no momento em que aquele Iteration efetivamente ocorre — nunca fixado no momento de Specification ou de Plan. Uma Change que escalar de Flow sob C-005 no meio de sua execução SHALL escalar seu Review Profile junto, para qualquer Review Iteration registrado após a escalação.

#### Boundary
Um Review Iteration já registrado antes de uma escalação NÃO é invalidado retroativamente (C-045) — permanece evidência válida sob o profile que se aplicava quando ocorreu.

#### Acceptance
AC-012 — Um teste demonstra que uma Change com `flow.escalations` não-vazio tem, para um Review Iteration cujo `revision` é posterior (em histórico Git) ao commit de escalação, o profile do Flow `current` (pós-escalação) refletido na instrução do Reviewer; um Iteration anterior à escalação permanece válido sem exigir re-review.

### FR-013 · Rótulo profile-neutro em Merge Readiness
Origin: RFC-0007 item 14; Specification Review SR-007

#### Requirement
`src/forge_cli/merge_readiness/evaluator.py`'s diagnóstico `MR-004` (hoje rotulado `"STRICT REVIEW NOT READY"`) SHALL ser renomeado para um rótulo profile-neutro (ex.: `"REVIEW NOT READY"`). Este Requirement é puramente cosmético — a condição de disparo e a semântica de bloqueio de `MR-004` SHALL permanecer inalteradas.

#### Acceptance
AC-013 — `MR-004`'s texto de diagnóstico não contém mais a string "Strict Review"; nenhum teste existente de `merge_readiness` que dependa da condição de disparo (não do texto) quebra.

## Non-functional Requirements

### NFR-001 · F-010 Foundation simplicity
Nenhum novo lifecycle, engine ou workflow de Review SHALL ser introduzido. Um único vocabulário de Finding/evidence/severity/provenance permanece a única fonte de verdade para os três profiles.

### NFR-002 · F-011 Deterministic validation
A checagem de piso de profile (FR-010) SHALL ser determinística e mecanicamente verificável por `forge validate`, sem depender de julgamento humano ou de heurística não determinística.

## Constraints

### CON-001 · Escopo de Schema
`protocol/schemas/policy-review.schema.json` (Protocol 1) não é alterado. Nenhuma classe `ReviewProfileEngine`/`ReviewProfileRegistry`/execução paralela é introduzida.

### CON-002 · Escopo do Contract
Apenas C-022, C-023 e a clarificação de C-031 são alterados textualmente. C-024–C-027, C-047–C-050, C-059, C-067–C-068 permanecem textualmente idênticos (FR-007).

### CON-003 · Risco residual aceito e reconhecido explicitamente
Os profiles `focused`/`standard` mudam a instrução dada ao Reviewer, não uma propriedade mecanicamente verificável do resultado — não há, e esta Change não introduz, um jeito de distinguir mecanicamente "Reviewer buscou dentro do escopo correto e não achou nada" de "Reviewer não buscou o suficiente". Isso é uma limitação deliberada e reconhecida (Specification Review SR-004), não uma omissão: o piso não-negociável por Flow (FR-010) e a autoridade de rejeição idêntica sobre qualquer Finding material efetivamente observado (FR-002–FR-003) são a mitigação aceita, não uma auditoria mecânica de exaustividade de busca — que exigiria o tipo de scoring/engine que esta Change explicitamente rejeita introduzir (Alternatives rejected, RFC-0007).

## Traceability Matrix

Índice apenas; as referências locais em cada Requirement permanecem autoritativas.

| Discovery / RFC-0007 | Requirement | Acceptance |
|---|---|---|
| Flows idênticos hoje; RFC-0007 item 1 | FR-001 | AC-001 |
| RFC-0007 item 2 | FR-002 | AC-002 |
| RFC-0007 item 3 | FR-003 | AC-003 |
| RFC-0007 item 4; preservação de comportamento FULL | FR-004 | AC-004 |
| Questão normativa resolvida; RFC-0007 item 5 | FR-005 | AC-005 |
| RFC-0007 item 7 | FR-006 | AC-006 |
| RFC-0007 item 6; Constraint do pedido original | FR-007 | AC-007 |
| RFC-0007 items 8–9; catálogo de Schemas | FR-008 | AC-008 |
| RFC-0007 item 11; consolidação do CHG-0045 | FR-009 | AC-009 |
| RFC-0007 item 12; Constraint 11 | FR-010 | AC-010 |
| Constraint 12; C-045 | FR-011 | AC-011 |
| RFC-0007 item 13; SR-006 | FR-012 | AC-012 |
| RFC-0007 item 14; SR-007 | FR-013 | AC-013 |

## Compatibility Statement

RFC-0007 (aceito) resolveu a questão normativa central a favor de uma leitura compatível com Protocol 2 (C-045) — nenhuma Change histórica é invalidada, Protocol permanece `2`. Mudanças de Schema em `change-v2`, `policy-review-v2` e `project` são aditivas com default retroativo `strict`; `flow.schema.json`'s narrowing de `const` para enum é a codificação direta da mesma decisão de Contract, sem instâncias históricas análogas a invalidar (FR-008). `protocol/schemas/policy-review.schema.json` (Protocol 1) e todo o Contract de Protocol 1 permanecem intocados. Independência Reviewer/Resolver, evidence, severities, Resolution, Resolution Verification e Convergence Limit são idênticos nos três profiles — nenhuma dessas garantias é reduzida. Uma entrada correspondente SHALL ser adicionada a `protocol/compatibility.md` documentando esta resolução (Documentation Impact).

## Specification Gate

Esta Specification está completa: cada Requirement rastreia a RFC-0007 aceito e/ou à Discovery; os limites arquiteturais (independência, evidence, severities, convergence, Protocol 1 intocado) estão cobertos por FR-007/CON-001/CON-002; a questão normativa que poderia ter bloqueado esta Specification já foi resolvida (RFC-0007); os sete achados da Specification Review adversarial (SR-001–SR-007) foram endereçados: SR-001 (rebatido em RFC-0007's "Alternatives rejected"), SR-002/SR-003 (FR-008/FR-010 revisados, `project-flow.schema.json` incluído — corrigido durante Architecture para o mecanismo já existente e já consumido, não `project.schema.json`), SR-004 (CON-003, risco residual reconhecido), SR-005 (C-059 adicionado a FR-007), SR-006 (FR-012), SR-007 (FR-013). Pronta para Architecture.

## Out of Scope

Qualquer capability concreta; novo lifecycle de Review paralelo; scoring numérico; downgrade automático de Flow por heurística; Review diff-only ou baseada só em testes passando; mudança em `protocol/schemas/policy-review.schema.json` (Protocol 1) ou no Contract de Protocol 1; reescrita de Review histórica; novo identificador de Protocol (resolvido: Protocol 2); RFC-0005 permanece como registro histórico marcado superseded, não apagado.
