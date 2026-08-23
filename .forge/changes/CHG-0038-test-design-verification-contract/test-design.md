---
forge:
  artifact: test_design
  schema: 1
change: CHG-0038
status: complete
---

# CHG-0038 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0038 |
| **Flow** | STANDARD |
| **Status** | Complete |
| **Automated Scenarios** | 6 |
| **Manual Scenarios** | 2 |
| **Primary Layers** | Scaffold Rendering, Documentation Consistency, Repository Compatibility |

## Test Strategy

| Layer | Scope | Method |
|---|---|---|
| Layer A | Renderização do scaffold (`change_scaffolding.py`) | Automated |
| Layer B | Consistência da documentação canônica (`protocol/artifact-structure.md`) | Manual |
| Layer C | Compatibilidade com scaffolds, testes e `forge validate` existentes | Automated |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| FR-005 | TD-005 | Automated |
| FR-006 | TD-006 | Automated |
| FR-001, FR-006 | TD-007 | Manual Acceptance |
| FR-001, FR-002, FR-003 | TD-008 | Manual Acceptance |

## Layer A · Scaffold Rendering

### TD-001 · New test-design.md structural core
Requirements: FR-001
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que o `test-design.md` gerado passa a conter o conjunto completo de headings do contrato de verificação (Overview, Test Strategy, Coverage Map, Requirement Coverage, Coverage Gaps, Test Design Gate) no lugar do template mínimo anterior, e que a heading de identidade segue o padrão `# CHG-XXXX · Test Design`.

#### Preconditions
Flow canônico STANDARD ou FAST carregado de `protocol/flows/`; `behavioral=True`.

#### Scenario
Given uma requisição de scaffold STANDARD comportamental
When `test-design.md` é renderizado
Then o front matter é preservado
And as headings `Overview`, `Test Strategy`, `Coverage Map`, `Requirement Coverage`, `Coverage Gaps` e `Test Design Gate` estão presentes
And a heading `# CHG-0022 · Test Design` (ou equivalente por Change) está presente
And o template mínimo anterior (`## Objective`, `## Strategy`, `## TDD-001 — <behavior>`, `## Completion Criteria`) está ausente.

#### Evidence
Asserções de substring sobre a string Markdown retornada por `render_scaffold(...).files["test-design.md"]`, em `tests/unit/test_change_scaffolding.py`.

#### Failure Condition
O cenário falha se qualquer heading obrigatória estiver ausente, se o template mínimo antigo ainda for emitido, ou se o front matter (`forge:`/`schema: 1`/`change:`/`status:`) mudar de forma.

#### Boundary
Este cenário prova a forma do scaffold gerado; não prova que um autor humano preencherá o conteúdo com qualidade.

### TD-002 · Self-contained TD-xxx scenario subsections
Requirements: FR-002
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que o exemplo de cenário gerado usa o identificador estável `### TD-001 ·` com as subseções `Purpose`/`Preconditions`/`Scenario`/`Evidence`/`Failure Condition`/`Boundary`, e que o scaffold não força subseções vazias com `N/A`.

#### Scenario
Given o mesmo scaffold STANDARD comportamental
When `test-design.md` é renderizado
Then a heading `### TD-001 ·` está presente
And as subheadings `#### Purpose` e `#### Scenario` estão presentes
And a string literal `N/A` não é emitida como preenchimento de subseção
And a heading solta `## TDD-001 — <behavior>` do template anterior está ausente.

#### Evidence
Asserções de substring equivalentes às de TD-001, focadas nas subheadings de cenário.

#### Failure Condition
Falha se `### TD-001 ·` ou as subheadings críticas estiverem ausentes, ou se `N/A` for emitido como boilerplate forçado.

#### Boundary
Não prova que todo cenário real terá as seis subseções preenchidas — apenas que a forma existe e não é forçada.

### TD-003 · Requirement Coverage with and without User Stories
Requirements: FR-003
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que a guidance gerada explica a Coverage Map/Requirement Coverage funcionando com Stories e sem Stories, e declara explicitamente que um Requirement sem User Story permanece válido — espelhando o mesmo Requirement que a CHG-0037 já garante para `specification.md`.

#### Scenario
Given o scaffold STANDARD comportamental
When `test-design.md` é renderizado
Then o texto de guidance contém a frase equivalente a "a Requirement without a User Story is valid"
And a guidance não cria um `US-001` fictício por padrão.

#### Evidence
Asserção de substring sobre a frase de guidance; ausência de `### US-001` ou identificador de Story inventado no template.

#### Failure Condition
Falha se a guidance exigir Story para todo Requirement, ou se um identificador de Story fictício for emitido por padrão.

### TD-004 · Manual Acceptance is distinguished from automated scenarios
Requirements: FR-004
Type: Unit
Priority: Major

#### Purpose
Demonstrar que a guidance nomeia explicitamente `Type: Manual Acceptance` como categoria distinta de tipos automatizados, evitando que comportamento interativo (Harness, agente, humano) seja apresentado como garantia mecânica.

#### Scenario
Given o scaffold STANDARD comportamental
When `test-design.md` é renderizado
Then a frase `Manual Acceptance` está presente na guidance
And a guidance associa `Manual Acceptance` a Preconditions, instrução de operador e evidência observável.

#### Evidence
Asserção de substring sobre `Manual Acceptance` e os elementos associados no texto gerado.

#### Failure Condition
Falha se `Manual Acceptance` estiver ausente ou não for distinguível textualmente de um tipo automatizado.

### TD-005 · Valid RED guidance excludes non-behavioral failure causes
Requirements: FR-005
Type: Unit
Priority: Major

#### Purpose
Demonstrar que a guidance gerada explicita o que torna um RED válido (falha pela razão comportamental esperada) e lista causas que invalidam um RED como evidência de TDD.

#### Scenario
Given o scaffold STANDARD comportamental
When `test-design.md` é renderizado
Then a guidance menciona que RED deve falhar pela razão comportamental esperada
And a guidance lista pelo menos erro de sintaxe, import quebrado, fixture inválida e infraestrutura indisponível como causas de RED inválido.

#### Evidence
Asserção de substring sobre a guidance de RED válido/inválido no template gerado.

#### Failure Condition
Falha se a distinção entre RED válido e inválido estiver ausente do template.

#### Boundary
Este cenário verifica que a guidance textual existe no scaffold; não executa um ciclo TDD real.

## Layer B · Documentation Consistency

### TD-007 · Test Design and Test Strategy are described as distinct shapes
Requirements: FR-001, FR-006
Type: Manual Acceptance
Priority: Major

#### Purpose
Demonstrar que `protocol/artifact-structure.md` deixa de descrever Test Design e Test Strategy como uma única forma compartilhada — já que, a partir desta Change, elas divergem estruturalmente — sem tornar a seção incorreta em relação à prática real do repositório (obrigação do próprio documento, §1).

#### Preconditions
`protocol/artifact-structure.md` atualizado nesta Change.

#### Operator instructions
Um mantenedor lê a seção 4 do documento e confirma que existem duas entradas distintas: "Test Design" (nova forma, TD-xxx/Layers/Coverage Map) e "Test Strategy" (forma antiga, `TDD-xxx`, inalterada).

#### Milestones
Diff do documento revisado antes do merge.

#### Evidence
Observação humana registrada nesta revisão; diff do arquivo.

#### Failure Condition
Falha se as duas entradas continuarem descritas como uma forma única, ou se a entrada de Test Strategy divergir do template real de `test_strategy` em `change_scaffolding.py`.

#### Boundary
Este cenário não é mecanicamente verificável — é revisão humana da guidance, consistente com C-067 (guidance não vinculante, sem parser de Markdown).

## Layer C · Repository Compatibility

### TD-006 · Historical scaffolds, full suite, and forge validate remain unaffected
Requirements: FR-006
Type: Integration
Priority: Critical

#### Purpose
Demonstrar que o redesenho não altera o conjunto de arquivos por Flow, não altera `test-strategy.md`, e não quebra a suíte de testes existente nem `forge validate`.

#### Preconditions
Suíte `tests/unit/test_change_scaffolding.py` e suíte completa passando na baseline antes da Implementation.

#### Scenario
Given o renderer modificado
When a suíte de testes unitários e golden-path e `forge validate` são executados
Then todos passam
And o template de `test_strategy` em `_markdown()` permanece byte-idêntico ao anterior
And o conjunto de arquivos por Flow (`test_render_scaffold_uses_only_the_selected_flow_stages`) permanece inalterado.

#### Evidence
Saída de `pytest`, saída/exit code de `forge validate`, diff do template `test_strategy`.

#### Failure Condition
Qualquer teste previamente verde regride, ou o conteúdo de `test_strategy` muda.

### TD-008 · ERP domain example demonstrates the layout outside Forge itself
Requirements: FR-001, FR-002, FR-003
Type: Manual Acceptance
Priority: Minor

#### Purpose
Demonstrar que o novo layout de Test Design é utilizável para uma feature de domínio comum (Customer Price Lists), não apenas para Changes de tooling do próprio Forge — mitigando o risco de a estrutura estar sobreajustada a Changes de scaffolding.

#### Preconditions
`examples/canonical-artifacts/test-design.md` adicionado nesta Change.

#### Operator instructions
Um revisor lê o exemplo e confirma que os cenários `TD-xxx` referenciam Requirements/Stories plausíveis, têm Evidence e Failure Condition concretos, e não inventam uma Story fictícia onde nenhuma se justifica.

#### Evidence
O próprio arquivo de exemplo; observação humana registrada nesta revisão.

#### Failure Condition
Falha se o exemplo for internamente inconsistente, inventar uma Story sem justificativa, ou omitir Evidence/Failure Condition em um cenário crítico.

#### Boundary
Este cenário não prova que o ERP fictício existe ou é implementado — apenas que a forma do artefato é aplicável ao domínio.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | TD-007, TD-008 | Covered |
| FR-002 | TD-002 | TD-008 | Covered |
| FR-003 | TD-003 | TD-008 | Covered |
| FR-004 | TD-004 | — | Covered |
| FR-005 | TD-005 | — | Covered |
| FR-006 | TD-006 | TD-007 | Covered |
| NFR-001 | — | Review | Covered |

## Coverage Gaps

Nenhum Requirement obrigatório permanece sem estratégia de verificação.

## Test Design Gate

- Todos os Requirements obrigatórios (FR-001 a FR-006) possuem estratégia de verificação declarada.
- Cenários críticos (TD-001, TD-002, TD-003, TD-006) possuem Purpose claro e Failure Condition explícita.
- Automated e Manual Acceptance estão separados (Layer A/C vs. Layer B, TD-007/TD-008).
- RED válido está definido (TD-005) para o ciclo TDD desta Change.
- Nenhuma propriedade manual (TD-007, TD-008) é apresentada como garantia automática.
- Nenhum Requirement crítico permanece sem cobertura conhecida.

**Ready for Plan.**
