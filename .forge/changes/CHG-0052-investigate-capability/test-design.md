---
forge:
  artifact: test_design
  schema: 1
change: CHG-0052
status: complete
---

# CHG-0052 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0052 |
| **Flow** | STANDARD |
| **Status** | Draft |
| **Automated Scenarios** | 6 |
| **Manual Scenarios** | 1 |
| **Primary Layers** | Loader Conformance, Vocabulary Invariants, Manual Acceptance |

## Test Strategy

Nenhum código de produção (`loader.py`, `model.py`) é escrito ou
modificado nesta Change — o único artefato executável novo é o conjunto
de testes que carrega o `CAPABILITY.md` real de `investigate` pelo
loader já existente. A estratégia evita duas armadilhas simétricas:
testar tão pouco que um `CAPABILITY.md` vazio de conteúdo passaria
(Layer A sozinha), e testar tanto texto literal que o teste vira um
freeze de prosa que quebra a cada reformulação editorial legítima
(evitado deliberadamente — Layer B verifica vocabulário/marcadores
estruturais exigidos pelo pedido original, não frases inteiras; Layer C
cobre o julgamento de qualidade que não é mecanicamente verificável).

| Layer | Scope | Method |
|---|---|---|
| Layer A | Loader Conformance — `capabilities/investigate/CAPABILITY.md` via `load_capability` | Automated |
| Layer B | Vocabulary Invariants — marcadores e proibições exigidos pelo pedido original | Automated |
| Layer C | Manual Acceptance — qualidade e fidelidade do conteúdo diagnóstico | Manual |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-003 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004, FR-006 | TD-004 | Automated |
| FR-006 | TD-005 | Automated |
| FR-002 | TD-006 | Automated |
| FR-002, FR-004, FR-005 | TD-007 | Manual Acceptance |

## Layer A · Loader Conformance

### TD-001 · The real investigate definition loads through the unmodified loader
Requirements: FR-001
Type: Integration
Priority: Critical

#### Purpose
Demonstrar o Success Criterion central desta Change: o loader genérico
já existente carrega `capabilities/investigate/CAPABILITY.md` sem
qualquer tratamento especial, produzindo um `Capability` com todas as
seções obrigatórias preenchidas.

#### Preconditions
`capabilities/investigate/CAPABILITY.md` escrito nesta Change.

#### Scenario
Given o caminho real `capabilities/investigate/CAPABILITY.md` no repositório
When `load_capability(path)` é chamado
Then o `Capability` retornado tem `id == "investigate"`, `schema` é um inteiro
And cada uma das sete seções obrigatórias (`identity`, `purpose`, `applicability`, `inputs`, `behavior`, `outputs`, `evidence_expectations`) é uma string não vazia.

#### Evidence
Asserções diretas sobre o `Capability` retornado; nenhum mock do loader.

#### Failure Condition
Falha se `load_capability` levantar `CapabilityDefinitionError` (arquivo
ausente, frontmatter inválido, ou seção ausente/vazia), ou se `id` for
diferente de `"investigate"`.

#### Boundary
Este cenário prova conformidade estrutural com o contrato — não prova
que o conteúdo é semanticamente correto (Layers B e C).

## Layer B · Vocabulary Invariants

### TD-002 · Conclusion markers ROOT CAUSE CONFIRMED / ROOT CAUSE NOT ESTABLISHED are present
Requirements: FR-003
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que o pedido original — "a conclusão deve permitir
explicitamente `ROOT CAUSE CONFIRMED` ou `ROOT CAUSE NOT ESTABLISHED`" —
é satisfeito literalmente, não apenas parafraseado, para que uma
implementação futura possa buscar por esses marcadores de forma
confiável.

#### Scenario
Given o `Capability` carregado de `investigate`
When o texto combinado de `outputs` e `behavior` é inspecionado
Then a substring `ROOT CAUSE CONFIRMED` está presente
And a substring `ROOT CAUSE NOT ESTABLISHED` está presente.

#### Evidence
Asserções `in` sobre a string combinada.

#### Failure Condition
Falha se qualquer um dos dois marcadores literais estiver ausente, ou se
apenas um estiver presente (permitindo confirmação mas não a saída
inconclusiva, ou vice-versa).

### TD-003 · Evidence classification CONFIRMED / INFERRED / UNKNOWN is declared
Requirements: FR-003
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que a distinção evidence-vs-inferência exigida pelo pedido
original ("Preserve claramente a distinção: CONFIRMED / INFERRED /
UNKNOWN") é declarada, não apenas implícita — o requisito central que
impede `investigate` de fabricar certeza.

#### Scenario
Given o `Capability` carregado de `investigate`
When `evidence_expectations` é inspecionado
Then as substrings `CONFIRMED`, `INFERRED` e `UNKNOWN` estão todas presentes.

#### Evidence
Asserções `in` sobre `capability.evidence_expectations`.

#### Failure Condition
Falha se qualquer uma das três classes estiver ausente da seção Evidence
Expectations.

### TD-004 · No Harness-specific vocabulary and no forbidden mechanism vocabulary
Requirements: FR-004, FR-006
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que `investigate` permanece Harness-neutro e não introduz,
nem sequer em prosa, os mecanismos explicitamente fora de escopo
(pedido original — seção "Architecture").

#### Scenario
Given o texto completo bruto de `capabilities/investigate/CAPABILITY.md`
When o texto é buscado (case-insensitive) por `claude`, `codex`, `cursor`, `capabilityregistry`, `capabilityexecutor`, `/investigate`, `skill.md`
Then nenhuma dessas ocorrências é encontrada.

#### Evidence
Asserções `not in` sobre o texto lido em minúsculas.

#### Failure Condition
Falha se qualquer um dos termos proibidos aparecer, inclusive dentro de
um exemplo ilustrativo — um exemplo mencionando "um Harness Adapter
pode gerar um SKILL.md" ainda violaria a Constraint e deve ser reescrito
sem nomear o artefato proibido.

#### Boundary
Este cenário não substitui uma busca no diff completo da Change
(coberta por Review/AC-006) — cobre apenas o próprio `CAPABILITY.md`.

### TD-005 · Boundary denials are present for every prohibited authority
Requirements: FR-006
Type: Unit
Priority: Major

#### Purpose
Demonstrar que cada item da lista de Boundaries do pedido original é
negado explicitamente no texto, não apenas coberto por uma frase geral
de "isto é diagnóstico".

#### Scenario
Given o texto completo de `capabilities/investigate/CAPABILITY.md`
When o texto é inspecionado por menção a cada autoridade proibida (corrigir automaticamente, aprovar Changes, selecionar/redefinir Flow, criar Gates, controlar lifecycle, substituir decisão humana)
Then cada uma dessas frases-chave (ou uma negação equivalente) está presente na seção de boundaries.

#### Evidence
Asserções `in` sobre um conjunto de fragmentos-chave definidos a partir
do pedido original (não frases completas coladas do pedido, para não
congelar prosa — apenas os substantivos/verbos que identificam cada
autoridade negada: "aprova", "Flow", "Gate", "lifecycle", "decisões
humanas"/"decisão humana").

#### Failure Condition
Falha se qualquer uma das autoridades proibidas não tiver nenhuma menção
correspondente no texto — o que deixaria a Capability Architecture
sem defesa textual contra esse uso indevido específico.

### TD-006 · The eight-step evidence-driven sequence and its antagonist are named
Requirements: FR-002
Type: Unit
Priority: Major

#### Purpose
Demonstrar que o fluxo central do pedido original — a sequência de oito
passos e o padrão a evitar — está declarado por seus termos-chave, não
apenas espiritualmente sugerido.

#### Scenario
Given o texto de `behavior`
When o texto é inspecionado por termos-chave (`hypothes` — cobrindo hypothesis/hypotheses, `reproduc`, `evidence`, `root cause`) e pela substring `plausible guess`
Then todos os termos-chave estão presentes
And a substring `plausible guess` está presente, nomeando explicitamente o padrão a evitar.

#### Evidence
Asserções `in`/regex sobre `capability.behavior`.

#### Failure Condition
Falha se `behavior` descrever apenas um processo genérico de
"investigar o problema" sem nomear hipóteses concorrentes, reprodução,
evidence, root cause, ou o antipadrão `symptom -> plausible guess ->
code change`.

## Layer C · Manual Acceptance

### TD-007 · investigate genuinely embodies evidence-driven investigation, not buzzword coverage
Requirements: FR-002, FR-004, FR-005
Type: Manual Acceptance
Priority: Major

#### Purpose
Os TD-002 a TD-006 provam presença de vocabulário; nenhum teste
mecânico prova que a prosa ao redor desse vocabulário descreve, de fato,
um processo disciplinado e coerente, que a lista de Applicability é
completa, ou que Outputs recomenda a próxima ação sem assumir
implementação. Essa é uma propriedade de leitura humana, consistente com
C-067 (guidance não vinculante, sem parser de Markdown obrigatório para
prosa) e com o mesmo padrão já usado por `CHG-0047`/TD-007.

#### Preconditions
`capabilities/investigate/CAPABILITY.md` escrito nesta Change; TD-001 a
TD-006 passando.

#### Operator instructions
Um revisor independente lê o arquivo completo e confirma: (1) `##
Behavior` descreve um processo real e sequencial, não uma lista solta de
palavras-chave; (2) `## Applicability` cobre as categorias do pedido
original e a exclusão explícita para causa já estabelecida; (3) `##
Outputs` recomenda a próxima ação sem presumir que implementação é
sempre necessária, e não inventa um novo artifact obrigatório; (4) `##
Behavior`/`## Applicability`/`## Outputs` juntos negam, de forma que um
leitor razoável reconheceria como clara, cada Boundary do pedido
original — não apenas as frases-chave isoladas que TD-005 verifica.

#### Milestones
Diff do arquivo revisado antes da Strict Review independente desta
Change.

#### Evidence
Observação humana/reviewer registrada na Review; diff do arquivo.

#### Failure Condition
Falha se o texto satisfizer TD-001–TD-006 mecanicamente (vocabulário
presente) mas um leitor razoável concluir que o processo descrito ainda
tende a `symptom -> plausible guess -> code change` na prática, ou que
alguma Boundary está coberta apenas nominalmente.

#### Boundary
Este cenário não é mecanicamente verificável — é revisão humana/reviewer
de prosa.

## Valid RED

RED é válido quando os testes desta Change falham pela razão
comportamental esperada: `capabilities/investigate/CAPABILITY.md` ainda
não existe, então TD-001 falha com `CapabilityDefinitionError` (arquivo
ausente) e TD-002–TD-006 falham por não haver `Capability` carregável
para inspecionar (erro na fixture/setup do próprio teste, que carrega o
arquivo real uma vez por módulo). Um RED causado por erro de sintaxe no
teste, um import quebrado de `forge_cli.capabilities`, ou infraestrutura
de teste indisponível não é evidência válida e deve ser corrigido antes
de contar.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | — | Covered |
| FR-002 | TD-006 | TD-007 | Covered |
| FR-003 | TD-002, TD-003 | — | Covered |
| FR-004 | TD-004 | TD-007 | Covered |
| FR-005 | — | TD-007 | Covered |
| FR-006 | TD-004, TD-005 | — | Covered |
| NFR-001 | TD-001 (loader opera sobre `Path` arbitrário, sem lógica específica de repositório) | — | Covered |

## Coverage Gaps

Nenhum Requirement obrigatório permanece sem estratégia de verificação.
FR-005 (Applicability scope) depende primariamente de TD-007 (Manual
Acceptance) porque completude de uma lista de categorias de aplicação é
uma propriedade de julgamento de conteúdo, não uma propriedade
estrutural mecanicamente verificável sem também arriscar congelar a
prosa que a expressa.

## Test Design Gate

- Todos os Requirements obrigatórios (FR-001 a FR-006, NFR-001) possuem estratégia de verificação declarada.
- Cenários críticos (TD-001 a TD-004) possuem Purpose claro e Failure Condition explícita.
- Automated (Layers A/B) e Manual Acceptance (Layer C) estão separados.
- TD-007 não é apresentado como garantia automática.
- Nenhum cenário automatizado testa prosa palavra-por-palavra além dos marcadores literais exigidos pelo próprio pedido original (`ROOT CAUSE CONFIRMED`, `ROOT CAUSE NOT ESTABLISHED`, `CONFIRMED`/`INFERRED`/`UNKNOWN`) — os demais usam termos-chave, não frases completas.
- Valid RED está definido e aponta para a razão comportamental correta (arquivo ainda inexistente).

**Ready for Plan.**
