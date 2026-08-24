---
forge:
  artifact: specification
  schema: 1
change: CHG-0044
status: draft
---

# CHG-0044 · Specification

> **Change Contract**
>
> Esta Specification define a elaboração da guidance de `inspection.md`
> (`protocol/artifact-structure.md`, §4 "Inspection") e de seu scaffold
> (`change_scaffolding.py`): adicionar um vocabulário estrutural opcional
> e uma identidade de documento consistente com os demais artefatos já
> elaborados, preservando integralmente a proporcionalidade que já é a
> propriedade central e correta deste artefato.

## Overview

| | |
|---|---|
| **Change** | CHG-0044 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O scaffold do `inspection` (Flow FAST) SHALL emitir identidade de
documento consistente com os demais artefatos redesenhados
(`# CHG-XXXX · Inspection`) e um corpo mínimo que orienta sem impor
estrutura. A guidance normativa em `protocol/artifact-structure.md` SHALL
documentar um vocabulário estrutural opcional (`Observation`, `Evidence`,
`Root Cause`, `Impact`, `Fix Boundary`, `Open Question`, `Conclusion`),
uma distinção explícita de confiança entre causa confirmada e causa
provável, um modelo Symptom → Reproduction → Cause para evidência, e a
relação real com Discovery, Specification, Plan, Verification, e o Forge
Experience Report — sem tornar nenhuma seção obrigatória, sem introduzir
validação semântica nova, e sem alterar a classificação FAST/STANDARD/FULL.

## Classification

STANDARD — mesmo Flow de `CHG-0037`–`43` e o default do projeto. O
comportamento é localizado ao renderer do scaffold
(`src/forge_cli/change_scaffolding.py`) e à guidance de documentação
(`protocol/artifact-structure.md`); não há mudança de Protocol integer,
Change Schema, Gate semantics, ou classificação de Flow.

## User Stories

Nenhuma se aplica. Change técnica de tooling/scaffolding e documentação
normativa, sem ator de domínio distinto.

## Functional Requirements

### FR-001 · Proportionality remains the first, undiluted rule
Origin: Discovery — a orientação atual já está correta em espírito; esta
Change elabora, não relaxa, essa propriedade

#### Requirement
A guidance elaborada SHALL declarar proportionality como a primeira regra
de Inspection, antes de qualquer vocabulário estrutural, e SHALL declarar
explicitamente que nenhuma seção do vocabulário opcional é obrigatória. O
scaffold gerado SHALL NOT emitir nenhum heading de seção fixo além da
identidade do documento.

#### Boundary
Esta Change NÃO introduz um conjunto obrigatório de seções, NÃO exige
Overview, NÃO exige Summary, e NÃO valida semanticamente a presença de
qualquer heading.

#### Acceptance
AC-001 — Given o scaffold gerado, When inspecionado, Then ele não contém
nenhum heading `##` além da identidade do documento; Given a guidance
elaborada, When lida, Then ela declara proportionality como a primeira
regra e declara explicitamente que o vocabulário estrutural é opcional.

### FR-002 · Identity heading and minimal scaffold body
Origin: Discovery — `_frontmatter()` hoje usa o fallback genérico
`# Inspection — CHG-XXXX <Title>`; o corpo do scaffold duplica esse
heading com `## Inspection`

#### Requirement
O `inspection.md` gerado SHALL usar a heading de identidade
`# CHG-XXXX · Inspection` (mesmo padrão de `specification`/`test_design`/
`tasks`/`verification`/`review`/`knowledge_capture`), preservando o front
matter `forge:` existente sem alteração. O corpo emitido após a heading
SHALL ser uma orientação de autoria (comentário ou prosa curta),
não um heading de seção vazio ou redundante.

#### Boundary
Esta Change NÃO altera o front matter (`artifact`, `schema`, `change`,
`status`) de nenhum artefato.

#### Acceptance
AC-002 — Given um scaffold FAST, When `inspection.md` é gerado, Then a
primeira linha de conteúdo é `# CHG-0044 · Inspection` (com o
`change_id` real substituindo `CHG-0044`), seguida por uma orientação de
autoria sem heading `##` duplicado.

### FR-003 · Optional recommended structural vocabulary
Origin: Discovery — seis exemplos reais usam headings orgânicos e
inconsistentes para os mesmos conceitos (Root Cause/Root cause/Finding;
Classification/Flow Classification)

#### Requirement
A guidance elaborada SHALL documentar um vocabulário estrutural
recomendado e explicitamente opcional: `Observation`, `Evidence`, `Root
Cause`, `Impact`, `Fix Boundary`, `Open Question`, `Conclusion` — em
inglês quando usado, com a prosa livre para seguir a língua de interação.
A guidance SHALL declarar que este vocabulário não é exaustivo nem
obrigatório, e que um Inspection real pode continuar usando zero, uma, ou
várias dessas seções, conforme a investigação realmente exigir.

#### Boundary
Esta Change NÃO exige que nenhum `inspection.md` futuro use qualquer
subconjunto específico deste vocabulário.

#### Acceptance
AC-003 — Given a guidance elaborada, When lida, Then ela lista o
vocabulário de sete termos, declara explicitamente que é opcional e não
exaustivo, e cita pelo menos um exemplo real (`CHG-0012`, `CHG-0024`,
`CHG-0026`, `CHG-0028`, ou `CHG-0029`) por termo quando um precedente
real existir.

### FR-004 · Root cause confidence is distinguished from certainty
Origin: Discovery — nenhum exemplo real usa uma escala de confiança;
`CHG-0012` mostra causa confirmada, outros mostram julgamento ainda em
aberto

#### Requirement
A guidance elaborada SHALL distinguir explicitamente `Observed behavior`
(sintoma observado, sem conclusão de causa) de `Root Cause` (causa
confirmada), e SHALL orientar o uso de uma frase explícita como "Likely
cause" quando a causa ainda não estiver confirmada — sem introduzir uma
escala de confiança numérica ou complexa.

#### Boundary
Esta Change NÃO exige que Root Cause esteja presente quando a
investigação não a confirmou.

#### Acceptance
AC-004 — Given a guidance elaborada, When lida, Then ela distingue
`Observed behavior` de `Root Cause` confirmada e orienta o uso de
"Likely cause" (ou equivalente) para causa não confirmada, sem propor
uma escala numérica.

### FR-005 · Evidence quality model (Symptom → Reproduction → Cause)
Origin: Discovery — `CHG-0012` já demonstra evidência específica
(commit, linha, comando); a guidance atual não nomeia esse padrão

#### Requirement
A guidance elaborada SHALL descrever um modelo de evidência de três
passos (`Symptom` → `Reproduction` → `Cause`) como preferível a uma
narrativa vaga, e SHALL orientar que claims relevantes sejam sustentados
por referência concreta (código, teste, comando, log, comportamento em
runtime, ou documentação normativa) — evitando grandes dumps de output.

#### Boundary
Esta Change NÃO exige que toda Inspection inclua os três passos quando a
investigação não os tiver produzido.

#### Acceptance
AC-005 — Given a guidance elaborada, When lida, Then ela descreve o
modelo Symptom → Reproduction → Cause com um exemplo curto, e orienta
evidência concreta em vez de conjectura não marcada.

### FR-006 · Distinction from Discovery, Specification, Plan, Verification, and the Forge Experience Report
Origin: Discovery — Inspection e Discovery nunca coexistem no mesmo
Flow; nenhum `/investigate` ou artefato paralelo existe hoje

#### Requirement
A guidance elaborada SHALL distinguir, em uma frase cada, Inspection de:
Discovery (entendimento amplo pré-Specification, STANDARD/FULL),
Specification (obrigação `FR-xxx` formal), Plan (trabalho aprovado),
Verification (o que foi comprovado após o fix, com convenção
Result-first), e o Forge Experience Report (execução real registrada,
opt-in, fora do diretório da Change). A guidance SHALL nomear o
mecanismo real de escalada de Flow (`fast.yml`: `escalation.enabled`,
`automatic_downgrade: false`; `protocol/specification.md` §11) para o
caso em que uma Inspection revela complexidade incompatível com FAST,
sem inventar um novo mecanismo.

#### Acceptance
AC-006 — Given a guidance elaborada, When lida, Then ela distingue
Inspection de cada um dos cinco artefatos/mecanismos citados e nomeia o
mecanismo de escalada de Flow já existente.

### FR-007 · Correction of the CHG-0005 characterization
Origin: Discovery — o texto atual descreve `CHG-0005/inspection.md` como
"a four-line file (title only)"; o conteúdo real tem dois parágrafos
substantivos, três frases ao todo

#### Requirement
A guidance elaborada SHALL corrigir a descrição de
`CHG-0005/inspection.md` para refletir seu conteúdo real (um título
seguido de dois parágrafos de contexto, três frases ao todo, sem
headings), preservando o ponto original da citação (o exemplo mínimo
real de Inspection).

#### Acceptance
AC-007 — Given a guidance elaborada, When a citação a `CHG-0005` é
inspecionada, Then ela não afirma que o arquivo é "title only" ou
equivalente, e descreve corretamente seu conteúdo real.

### FR-008 · Compatibility and scope boundary
Origin: Discovery — mesmo padrão de fechamento usado por `CHG-0037`–`43`

#### Requirement
Esta Change SHALL preservar os seis `inspection.md` reais inalterados,
SHALL NOT alterar Discovery/Specification/Plan/Verification/FER
mechanics, Protocol integer, Change Schema, classificação de Flow, ou
Harness Adapter behavior, e SHALL NOT introduzir validação semântica de
Markdown sobre headings de Inspection.

#### Acceptance
AC-008 — Given a suíte completa de testes e `forge validate` antes e
depois da Change, When executados, Then ambos permanecem verdes e
nenhum `inspection.md` histórico é reescrito.

## Non-functional Requirements

### NFR-001 · Plain-text readability
A guidance elaborada SHALL permanecer legível como texto plano, sem
HTML, emoji, badges, ou elementos decorativos.

## Constraints

### CON-001 · Scope boundary
Esta Change está limitada a `src/forge_cli/change_scaffolding.py`
(template e frontmatter do artefato `inspection`),
`protocol/artifact-structure.md` (seção "Inspection"), e os testes de
scaffold correspondentes.

## Traceability Matrix

| Discovery | Requirement | Acceptance |
| --- | --- | --- |
| Guidance atual já correta em espírito; não deve ser relaxada | FR-001 | AC-001 |
| Heading fallback genérico + `## Inspection` redundante no scaffold | FR-002 | AC-002 |
| Seis exemplos reais, vocabulário inconsistente para os mesmos conceitos | FR-003 | AC-003 |
| Nenhuma escala de confiança real existe; causa nem sempre confirmada | FR-004 | AC-004 |
| `CHG-0012` demonstra evidência concreta sem nomear o padrão | FR-005 | AC-005 |
| Inspection e Discovery nunca coexistem; escalada de Flow já existe | FR-006 | AC-006 |
| Descrição "title only" de `CHG-0005` não corresponde ao conteúdo real | FR-007 | AC-007 |
| Compatibilidade retroativa e escopo | FR-008 | AC-008 |

## Compatibility Statement

Nenhum impacto retroativo: os seis `inspection.md` reais permanecem
válidos; nenhum Protocol integer, Change Schema, ou schema JSON alterado;
`forge validate` não passa a interpretar conteúdo deste artefato
(C-067). Discovery, Specification, Plan, Verification, e FER mechanics
inalterados. Classificação de Flow FAST/STANDARD/FULL inalterada.

## Specification Gate

Requirements são independentes e verificáveis; nenhum Requirement
introduz obrigação de Gate nova; Compatibility Statement confirma
ausência de impacto retroativo. Pronta para Test Design e Plan.

## Out of Scope

Conjunto obrigatório de headings; Overview ou Summary obrigatórios;
escala de confiança complexa; novo validador semântico; novo comando de
lifecycle; mudanças em Discovery, Specification, Plan, Verification, ou
FER; qualquer Harness Adapter; nova versão de Protocol; reescrita de
`inspection.md` histórico; mudança de classificação de Flow.
