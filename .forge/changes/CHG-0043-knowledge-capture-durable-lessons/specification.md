---
forge:
  artifact: specification
  schema: 1
change: CHG-0043
status: draft
---

# CHG-0043 · Specification

> **Change Contract**
>
> Esta Specification define a elaboração do scaffold e da guidance de
> `knowledge-capture.md`: preservar integralmente a estrutura estável
> real (`What Changed` → `Durable Knowledge` → `Consequences for
> Future Changes` → `References`) enquanto torna explícito o que
> conta como conhecimento durável, distinto de Decision, Architecture,
> Specification, Review, Specification Drift, e do Forge Experience
> Report.

## Overview

| | |
|---|---|
| **Change** | CHG-0043 |
| **Flow** | STANDARD |
| **Status** | Draft |

## Summary

O scaffold do `knowledge_capture` (Flow FULL) SHALL emitir identidade
de documento consistente com os demais artefatos redesenhados, guidance
inline em cada seção da estrutura já estável, orientação para itens
`### K-xxx` opcionais em `Durable Knowledge` quando houver múltiplas
lições independentes, e distinção explícita de Decision/Architecture/
Specification/Review/Specification Drift/FER — sem tornar IDs
obrigatórios, sem inventar fluxo de promoção mecânico, e sem alterar
Gate semantics.

## Classification

STANDARD — mesmo Flow de `CHG-0037`–`42` e o default do projeto. O
comportamento é localizado ao renderer do scaffold
(`src/forge_cli/change_scaffolding.py`) e à guidance de documentação
(`protocol/artifact-structure.md`); não há mudança de Protocol
integer, Change Schema, Gate semantics, ou Decision/Architecture/FER
mechanics.

## User Stories

Nenhuma se aplica. Change técnica de tooling/scaffolding sem ator de
domínio distinto.

## Functional Requirements

### FR-001 · Stable structure preserved, identity heading added
Origin: Discovery — guidance anterior explicitamente recomendava "no
material change"; a estrutura de 4 seções é real e estável em 25
exemplos

#### Requirement
O `knowledge-capture.md` gerado SHALL preservar exatamente as quatro
headings estruturais já estáveis (`What Changed`, `Durable Knowledge`,
`Consequences for Future Changes`, `References`), na mesma ordem,
adicionando apenas a heading de identidade `# CHG-XXXX · Knowledge
Capture` (padrão já adotado por `intent`/`specification`/`test_design`/
`tasks`/`verification`/`review`) e guidance inline em cada seção.

#### Boundary
Esta Change NÃO remove, renomeia, ou reordena nenhuma das quatro
seções estáveis.

#### Acceptance
AC-001 — Given um scaffold FULL, When `knowledge-capture.md` é
gerado, Then a heading `# CHG-XXXX · Knowledge Capture` aparece
primeiro, seguida pelas quatro seções estruturais na ordem original,
cada uma com guidance inline não-vazia.

### FR-002 · Optional K-xxx items for multiple independent lessons
Origin: Discovery — `CHG-0016` é o único precedente real de múltiplas
lições independentes; nenhum `K-xxx` já existe no histórico

#### Requirement
O scaffold gerado (`knowledge-capture.md`) SHALL orientar o uso de
itens `### K-xxx · <title>` quando existirem múltiplas lições
genuinamente independentes, e SHALL declarar explicitamente que IDs
não são obrigatórios — prosa curta permanece válida para uma única
lição dominante. A guidance elaborada em
`protocol/artifact-structure.md` (documentação normativa, não o
scaffold em si) SHALL citar pelo menos um precedente real para cada um
dos dois modos (`CHG-0016` para múltiplas lições independentes;
`CHG-0033`/`35`/`36` para prosa curta de lição única).

#### Boundary
Esta Change não formaliza `K-xxx` como namespace normativo — nenhum
consumidor real existe hoje. O scaffold gerado permanece conciso; as
citações de precedente pertencem à documentação normativa elaborada,
não ao texto reutilizável do template.

#### Acceptance
AC-002 — Given o scaffold gerado, When a seção `Durable Knowledge` é
inspecionada, Then ela orienta o uso opcional de `### K-xxx` para
múltiplas lições independentes e declara explicitamente que IDs não
são obrigatórios; Given `protocol/artifact-structure.md`'s seção
"Knowledge Capture", When inspecionada, Then ela cita pelo menos um
precedente real para cada um dos dois modos.

### FR-003 · Distinction from Decision, Architecture, Specification, Review, and Specification Drift
Origin: Discovery — a relação real entre esses artefatos precisa ser
explícita para evitar duplicação de conteúdo

#### Requirement
A guidance elaborada SHALL distinguir Knowledge Capture, em uma frase
cada, de: Decision (qual opção foi escolhida), Architecture (o desenho
da solução), Specification (a obrigação da própria Change), Review (o
problema encontrado no subject revisado), e Specification Drift (como
o contrato mudou) — deixando claro que Knowledge Capture preserva a
lição reutilizável que qualquer um desses pode revelar, sem duplicar
o conteúdo de origem.

#### Acceptance
AC-003 — Given a guidance elaborada, When lida, Then ela distingue
Knowledge Capture de cada um dos cinco artefatos citados, sem sugerir
que um substitui o outro.

### FR-004 · Relationship with the Forge Experience Report is documented
Origin: Discovery — FER é um mecanismo real, ativo, e distinto
(`docs/experience-reporting.md`); a relação nunca foi documentada

#### Requirement
A guidance elaborada SHALL declarar a distinção real entre Forge
Experience Report (FER — opt-in, local, registra o que aconteceu
durante uma execução real, armazenado fora do diretório da Change) e
Knowledge Capture (sempre presente quando o Flow exige, registra
conhecimento durável já distilado, com escopo da própria Change).

#### Acceptance
AC-004 — Given a guidance elaborada, When lida, Then ela declara a
distinção FER vs. Knowledge Capture citando `docs/experience-reporting.md`.

### FR-005 · Reference to permanent documentation reflects real F-008 practice, not an invented promotion workflow
Origin: Discovery — nenhum "Promoted to:" existe no histórico real;
F-008 já exige ADR/RFC diretamente para trabalho material

#### Requirement
A guidance de `References` SHALL orientar que, quando o trabalho for
arquiteturalmente ou normativamente material (F-008: ADR para
Architecture material, RFC para Protocol material), o `docs/adr/`/
`docs/rfcs/` correspondente — já produzido como parte do próprio
trabalho, não uma promoção posterior — seja referenciado a partir de
`References`.

#### Boundary
Esta Change não inventa um mecanismo de "promoção" de conteúdo de
Knowledge Capture para documentação permanente; documenta a relação
real já existente via F-008.

#### Acceptance
AC-005 — Given a guidance elaborada, When a seção `References` é
inspecionada, Then ela orienta referenciar `docs/adr/`/`docs/rfcs/`
quando F-008 se aplica, sem descrever um fluxo de promoção que não
existe no repositório real.

### FR-006 · An empty Knowledge Capture is a valid, honest outcome
Origin: Discovery — nenhum Requirement ou Gate exige conteúdo
fabricado; `required_knowledge_capture_complete` verifica status, não
riqueza de conteúdo

#### Requirement
A guidance elaborada SHALL declarar explicitamente que, quando nenhuma
lição durável além da própria Change existir, uma declaração curta e
honesta é uma resposta completa e válida — não uma falha a disfarçar
com conteúdo fabricado.

#### Acceptance
AC-006 — Given a guidance elaborada, When lida, Then ela declara
explicitamente que a ausência de conhecimento adicional é um resultado
válido, com um exemplo de frase curta e honesta.

### FR-007 · Compatibility and scope boundary
Origin: Discovery — mesmo padrão de fechamento usado por
`CHG-0037`–`42`

#### Requirement
Esta Change SHALL preservar os 25 `knowledge-capture.md` reais
inalterados, SHALL NOT alterar Decision/Architecture/Specification/
Review/Specification-Drift/FER mechanics, Protocol integer, Change
Schema, ou Harness Adapter behavior, e SHALL NOT introduzir validação
semântica de Markdown ou namespace `K-xxx` obrigatório.

#### Acceptance
AC-007 — Given a suíte completa de testes e `forge validate` antes e
depois da Change, When executados, Then ambos permanecem verdes e
nenhum `knowledge-capture.md` histórico é reescrito.

## Non-functional Requirements

### NFR-001 · Plain-text readability
A guidance elaborada SHALL permanecer legível como texto plano, sem
HTML, emoji, ou elementos decorativos.

## Constraints

### CON-001 · Scope boundary
Esta Change está limitada a `src/forge_cli/change_scaffolding.py`
(template `knowledge_capture`), `protocol/artifact-structure.md`
(seção "Knowledge Capture"), e os testes de scaffold correspondentes.

## Traceability Matrix

| Discovery | Requirement | Acceptance |
| --- | --- | --- |
| Estrutura de 4 seções é real, estável, "no material change" prévio | FR-001 | AC-001 |
| CHG-0016 é o único precedente de múltiplas lições; sem K-xxx real | FR-002 | AC-002 |
| Relação com Decision/Architecture/Specification/Review/Drift | FR-003 | AC-003 |
| FER é mecanismo real distinto, nunca documentado como tal | FR-004 | AC-004 |
| F-008 já exige ADR/RFC direto; sem "Promoted to" real | FR-005 | AC-005 |
| Nenhum exemplo real está vazio, mas Gate não exige riqueza | FR-006 | AC-006 |
| Compatibilidade retroativa e escopo | FR-007 | AC-007 |

## Compatibility Statement

Nenhum impacto retroativo: os 25 `knowledge-capture.md` reais
permanecem válidos; nenhum Protocol integer, Change Schema, ou schema
JSON alterado; `forge validate` não passa a interpretar conteúdo deste
artefato (C-067). Decision, Architecture, Specification, Review,
Specification Drift, e FER mechanics inalterados.

## Specification Gate

Requirements são independentes e verificáveis; nenhum Requirement
introduz obrigação de Gate nova; Compatibility Statement confirma
ausência de impacto retroativo. Pronta para Plan.

## Out of Scope

Namespace `K-xxx` obrigatório; novo validador; fluxo mecânico de
"promoção" para documentação permanente; mudanças em Decision,
Architecture, Specification, Review, Specification Drift, ou FER;
qualquer Harness Adapter; nova versão de Protocol; reescrita de
`knowledge-capture.md` histórico.
