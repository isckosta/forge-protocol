---
forge:
  artifact: test_design
  schema: 1
change: CHG-0039
status: complete
---

# CHG-0039 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0039 |
| **Flow** | STANDARD |
| **Status** | Complete |
| **Automated Scenarios** | 5 |
| **Manual Scenarios** | 1 |
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
| FR-004, FR-005 | TD-004 | Automated |
| FR-001, FR-006 | TD-006 | Manual Acceptance |
| FR-006 | TD-005 | Automated |

## Layer A · Scaffold Rendering

### TD-001 · New tasks.md structural core
Requirements: FR-001
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que o `tasks.md` gerado (Flow FULL) passa a conter as headings `Overview`, `Execution` e `Status` no lugar do template mínimo anterior, e que a heading de identidade segue o padrão `# CHG-XXXX · Tasks`.

#### Preconditions
Flow canônico `full` carregado de `protocol/flows/`; `behavioral=True`.

#### Scenario
Given uma requisição de scaffold FULL comportamental
When `tasks.md` é renderizado
Then o front matter é preservado
And as headings `Overview`, `Execution` e `Status` estão presentes
And a heading `# CHG-0022 · Tasks` (ou equivalente por Change) está presente
And o template mínimo anterior (`- [ ] T-001 <work item>` imediatamente seguido de `## Status`) está ausente.

#### Evidence
Asserções de substring sobre a string Markdown retornada por `render_scaffold(...).files["tasks.md"]`, em `tests/unit/test_change_scaffolding.py`.

#### Failure Condition
O cenário falha se qualquer heading obrigatória estiver ausente, se o template mínimo antigo ainda for emitido, ou se o front matter (`forge:`/`schema: 1`/`change:`/`status:`) mudar de forma.

#### Boundary
Este cenário prova a forma do scaffold gerado; não prova que um autor humano agrupará corretamente as Tasks reais de um Plan concreto.

### TD-002 · Tasks grouped under a stable Plan heading
Requirements: FR-002
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que o exemplo gerado agrupa Tasks sob `### Plan 1 ·`, preservando `T-xxx` como item de checklist (`- [ ] T-xxx`), não como numeração de lista Markdown.

#### Scenario
Given o mesmo scaffold FULL comportamental
When `tasks.md` é renderizado
Then a heading `### Plan 1 ·` está presente dentro de `## Execution`
And pelo menos um item `- [ ] T-001` aparece sob essa heading.

#### Evidence
Asserção de substring sobre `### Plan 1 ·` e `- [ ] T-001` na string gerada.

#### Failure Condition
Falha se a checklist voltar a ser plana (sem heading de agrupamento) ou se `T-xxx` for substituído por numeração de lista Markdown (`1.`, `2.`).

#### Boundary
Não prova que o agrupamento de uma Change real corresponde aos itens verdadeiros do seu próprio Plan — apenas que a forma do scaffold permite e demonstra esse agrupamento.

### TD-003 · Compact optional traceability metadata
Requirements: FR-003
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que o exemplo de Task gerado inclui uma linha de metadata compacta (`` `Plan:` ``/`` `Requirements:` ``) usando `TDD-xxx` (não `TD-xxx`) como convenção de exemplo para Test Design/Test Strategy, e que a guidance declara que nenhuma referência é obrigatória em toda Task.

#### Scenario
Given o scaffold FULL comportamental
When `tasks.md` é renderizado
Then uma linha de metadata contendo `` `Plan:` `` e `` `Requirements:` `` aparece sob pelo menos uma Task
And a string `TD-` (convenção FAST/STANDARD) não aparece como rótulo de exemplo de Test Design no template
And a guidance contém a frase equivalente a "nem toda referência se aplica a toda Task".

#### Evidence
Asserções de substring sobre a linha de metadata e a frase de guidance.

#### Failure Condition
Falha se a metadata usar `TD-xxx` em vez de `TDD-xxx`, se toda Task for forçada a ter todas as referências, ou se a linha de metadata estiver ausente do exemplo.

### TD-004 · Overview and Status stay compact and derivable
Requirements: FR-004, FR-005
Type: Unit
Priority: Major

#### Purpose
Demonstrar que `## Overview` expõe apenas campos seguros (`Change`, `Flow`) numa tabela de duas colunas, e que `## Status` permanece uma frase curta de leitura rápida (`No task has started.`), sem introduzir um campo mantido manualmente que possa divergir do estado real da checklist.

#### Scenario
Given o scaffold FULL comportamental
When `tasks.md` é renderizado
Then `## Overview` contém uma tabela com `**Change**` e `**Flow**`
And `## Status` é a última seção do arquivo
And o texto `No task has started.` está presente sob `## Status`.

#### Evidence
Asserções de substring sobre a tabela de Overview e o texto de Status.

#### Failure Condition
Falha se Overview introduzir um campo de contagem manual não derivado, ou se Status deixar de ser a seção final.

## Layer B · Documentation Consistency

### TD-006 · Tasks guidance describes Plan grouping and traceability without new obligations
Requirements: FR-001, FR-006
Type: Manual Acceptance
Priority: Major

#### Purpose
Demonstrar que `protocol/artifact-structure.md` §4 ("Tasks") passa a descrever o agrupamento por Plan e a metadata compacta de rastreabilidade como layout recomendado, sem transformá-los em nova obrigação normativa e sem exigir retroativamente esse formato de `tasks.md` históricos.

#### Preconditions
`protocol/artifact-structure.md` atualizado nesta Change.

#### Operator instructions
Um mantenedor lê a seção 4 do documento e confirma que a entrada "Tasks" descreve o agrupamento por Plan e as referências compactas como guidance, cita que Task concluída não implica Requirement verificado, e não introduz uma nova obrigação de Gate.

#### Milestones
Diff do documento revisado antes do merge.

#### Evidence
Observação humana registrada nesta revisão; diff do arquivo.

#### Failure Condition
Falha se a entrada passar a exigir agrupamento por Plan como obrigação de Gate, ou se `tasks.md` históricos forem descritos como não conformes.

#### Boundary
Este cenário não é mecanicamente verificável — é revisão humana da guidance, consistente com C-067 (guidance não vinculante, sem parser de Markdown).

## Layer C · Repository Compatibility

### TD-005 · Historical scaffolds, full suite, and forge validate remain unaffected
Requirements: FR-006
Type: Integration
Priority: Critical

#### Purpose
Demonstrar que o redesenho não altera o conjunto de arquivos por Flow, não altera `plan.md` nem `test-strategy.md`, e não quebra a suíte de testes existente nem `forge validate`.

#### Preconditions
Suíte `tests/unit/test_change_scaffolding.py` e suíte completa passando na baseline antes da Implementation.

#### Scenario
Given o renderer modificado
When a suíte de testes unitários e golden-path e `forge validate` são executados
Then todos passam
And os templates de `plan` e `test_strategy` em `_markdown()` permanecem byte-idênticos aos anteriores
And o conjunto de arquivos por Flow (`test_render_scaffold_uses_only_the_selected_flow_stages`) permanece inalterado.

#### Evidence
Saída de `pytest`, saída/exit code de `forge validate`, diff dos templates `plan`/`test_strategy`.

#### Failure Condition
Qualquer teste previamente verde regride, ou o conteúdo de `plan`/`test_strategy` muda.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001 | TD-006 | Covered |
| FR-002 | TD-002 | — | Covered |
| FR-003 | TD-003 | — | Covered |
| FR-004 | TD-004 | — | Covered |
| FR-005 | TD-004 | — | Covered |
| FR-006 | TD-005 | TD-006 | Covered |
| NFR-001 | — | Review | Covered |

## Coverage Gaps

Nenhum Requirement obrigatório permanece sem estratégia de verificação.

## Test Design Gate

- Todos os Requirements obrigatórios (FR-001 a FR-006) possuem estratégia de verificação declarada.
- Cenários críticos (TD-001, TD-002, TD-003, TD-005) possuem Purpose claro e Failure Condition explícita.
- Automated e Manual Acceptance estão separados (Layer A/C vs. Layer B, TD-006).
- Nenhuma propriedade manual (TD-006) é apresentada como garantia automática.
- Nenhum Requirement crítico permanece sem cobertura conhecida.

**Ready for Plan.**
