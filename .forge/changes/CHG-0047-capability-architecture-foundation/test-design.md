---
forge:
  artifact: test_design
  schema: 1
change: CHG-0047
status: complete
---

# CHG-0047 · Test Design

> Verification Design

## Overview

| | |
|---|---|
| **Change** | CHG-0047 |
| **Flow** | STANDARD |
| **Status** | Complete |
| **Automated Scenarios** | 6 |
| **Manual Scenarios** | 1 |
| **Primary Layers** | Model, Loader, Documentation Consistency |

## Test Strategy

| Layer | Scope | Method |
|---|---|---|
| Layer A | `src/forge_cli/capabilities/model.py` | Automated |
| Layer B | `src/forge_cli/capabilities/loader.py` | Automated |
| Layer C | `capabilities/README.md`, `capabilities/capability.md` | Manual |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-003 | TD-001 | Automated |
| FR-004 | TD-002 | Automated |
| FR-004 | TD-003 | Automated |
| FR-004 | TD-004 | Automated |
| FR-004 | TD-005 | Automated |
| FR-005 | TD-006 | Automated |
| FR-001, FR-002 | TD-007 | Manual Acceptance |

## Layer A · Model

### TD-001 · Capability model is a minimal, immutable, Harness-neutral dataclass
Requirements: FR-003
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que `Capability` é exatamente o modelo mínimo descrito na Specification — congelado (não mutável após construção), com os campos exigidos e nenhum campo de lifecycle, autoridade, Gate, execução ou específico de Harness.

#### Scenario
Given uma instância de `Capability` construída com valores válidos para `id`, `schema`, `identity`, `purpose`, `applicability`, `inputs`, `behavior`, `outputs`, `evidence_expectations` e `source_path`
When o código tenta reatribuir um desses campos após a construção
Then a atribuição levanta `dataclasses.FrozenInstanceError`
And o conjunto de campos declarados na dataclass é exatamente o conjunto listado no Requirement, sem campos adicionais.

#### Evidence
Asserção de `pytest.raises(dataclasses.FrozenInstanceError)`; asserção sobre `dataclasses.fields(Capability)` comparando nomes de campo ao conjunto esperado.

#### Failure Condition
Falha se a mutação pós-construção for permitida, se um campo obrigatório estiver ausente, ou se um campo extra (especialmente um nomeado a partir de um Harness concreto) estiver presente.

#### Boundary
Este cenário prova a forma do modelo; não prova que o loader popula esses campos corretamente a partir de um arquivo real (coberto em Layer B).

## Layer B · Loader

### TD-002 · Well-formed CAPABILITY.md loads into a fully populated, normalized model
Requirements: FR-004
Type: Unit
Priority: Critical

#### Purpose
Demonstrar o caminho determinístico completo — localizar, ler, parsear, normalizar, retornar — para uma definição de capability bem formada, incluindo a remoção de espaço em branco de borda nas seções.

#### Preconditions
Um arquivo `CAPABILITY.md` temporário (`tmp_path`) com frontmatter válido (`capability: sample`, `schema: 1`) e as sete seções obrigatórias, algumas com espaço em branco supérfluo nas bordas do conteúdo.

#### Scenario
Given o caminho desse arquivo
When `load_capability(path)` é chamado
Then o `Capability` retornado tem `id == "sample"`, `schema == 1`, `source_path == path`
And cada um dos sete campos de seção contém o texto da seção correspondente sem espaço em branco de borda.

#### Evidence
Asserções de igualdade sobre os campos do `Capability` retornado.

#### Failure Condition
Falha se qualquer campo estiver ausente, incorreto, ou contiver espaço em branco de borda não normalizado.

### TD-003 · Loading the same unchanged file twice is deterministic
Requirements: FR-004
Type: Unit
Priority: Critical

#### Purpose
Demonstrar a propriedade central de "carregamento determinístico": duas chamadas ao loader sobre o mesmo arquivo inalterado produzem modelos iguais.

#### Scenario
Given o mesmo arquivo `CAPABILITY.md` bem formado do TD-002
When `load_capability(path)` é chamado duas vezes
Then os dois `Capability` retornados são iguais (`==`).

#### Evidence
Asserção `first == second` sobre dois `Capability` retornados por duas chamadas independentes.

#### Failure Condition
Falha se as duas chamadas produzirem modelos diferentes (ex.: por dependência de estado global, ordenação não determinística, ou timestamp implícito).

### TD-004 · Missing file raises a specific, explicit error
Requirements: FR-004
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que a etapa "locate" falha de forma explícita e específica do domínio, não com uma exceção genérica do sistema de arquivos.

#### Scenario
Given um `Path` que não existe no sistema de arquivos
When `load_capability(path)` é chamado
Then é levantado um erro específico (`CapabilityDefinitionError` ou subtipo), não uma exceção genérica não tratada
And a mensagem do erro identifica o caminho.

#### Evidence
`pytest.raises(CapabilityDefinitionError, match=...)`.

#### Failure Condition
Falha se uma exceção genérica (`FileNotFoundError` não envolvida, `Exception` bare) propagar sem ser traduzida para o erro específico do domínio, ou se a mensagem não identificar o caminho.

### TD-005 · Missing or invalid frontmatter raises a specific, explicit error
Requirements: FR-004
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que a etapa "parse" valida o frontmatter mínimo (`capability`, `schema`) antes de seguir para as seções, com erro específico e não uma exceção genérica de parsing YAML ou um `KeyError`.

#### Scenario
Given um arquivo sem bloco de frontmatter, e separadamente um arquivo com frontmatter presente mas sem a chave `capability` ou sem `schema` inteiro
When `load_capability(path)` é chamado para cada caso
Then é levantado `CapabilityDefinitionError` em todos os casos
And a mensagem identifica o problema (frontmatter ausente ou campo de identidade inválido).

#### Evidence
`pytest.raises(CapabilityDefinitionError, match=...)` para cada caso parametrizado.

#### Failure Condition
Falha se qualquer um dos casos propagar `KeyError`, `yaml.YAMLError` não traduzido, ou `AttributeError`, ou se um frontmatter inválido for silenciosamente aceito.

### TD-006 · Missing or empty required section raises a specific, explicit error
Requirements: FR-004
Type: Unit
Priority: Critical

#### Purpose
Demonstrar que a etapa "normalize" valida a presença e não-vacuidade de cada uma das sete seções obrigatórias antes de retornar o modelo, cobrindo o Requirement de erro explícito de FR-004 e a garantia de FR-005 de que nenhuma capability incompleta é silenciosamente aceita.

#### Scenario
Given um arquivo com frontmatter válido mas com uma das sete seções obrigatórias ausente, e separadamente um arquivo com uma seção presente mas vazia (só espaço em branco)
When `load_capability(path)` é chamado para cada caso
Then é levantado `CapabilityDefinitionError` identificando a seção ausente/vazia, para cada uma das sete seções testada isoladamente.

#### Evidence
`pytest.raises(CapabilityDefinitionError, match=...)`, parametrizado pelas sete seções obrigatórias.

#### Failure Condition
Falha se qualquer seção ausente ou vazia for aceita silenciosamente, produzindo um `Capability` com um campo vazio.

## Layer C · Documentation Consistency

### TD-007 · README and capability contract are complete, consistent, and boundary-honest
Requirements: FR-001, FR-002
Type: Manual Acceptance
Priority: Major

#### Purpose
Demonstrar que `capabilities/README.md` e `capabilities/capability.md` cobrem, em prosa, tudo que FR-001/FR-002 exigem — algo que não é mecanicamente verificável por não haver (e não dever haver) um parser de Markdown para esses documentos.

#### Preconditions
`capabilities/README.md` e `capabilities/capability.md` escritos nesta Change.

#### Operator instructions
Um mantenedor lê os dois documentos e confirma: (1) o README responde às seis perguntas do FR-001, incluindo a desambiguação com `adapters/capabilities.py`; (2) `capability.md` lista as sete seções mínimas, descreve cada uma, mostra o frontmatter mínimo, e declara a distinção com `SKILL.md`; (3) nenhum dos dois documentos introduz lifecycle, autoridade, Gate, ou acoplamento a um Harness específico.

#### Milestones
Diff dos dois documentos revisado antes da Strict Review independente.

#### Evidence
Observação humana/reviewer registrada na Review; diff dos arquivos.

#### Failure Condition
Falha se qualquer um dos seis pontos do FR-001 estiver ausente, se `capability.md` introduzir JSON Schema ou formato rígido não solicitado, ou se a distinção com `SKILL.md` não estiver explícita.

#### Boundary
Este cenário não é mecanicamente verificável — é revisão humana/reviewer de prosa, consistente com C-067 (guidance não vinculante, sem parser de Markdown obrigatório).

## Valid RED

RED é válido apenas quando o teste falha pela razão comportamental esperada — nesta Change, por `forge_cli.capabilities` (o pacote e seus símbolos: `Capability`, `load_capability`, `CapabilityDefinitionError`) ainda não existir, produzindo `ModuleNotFoundError`/`ImportError` no momento em que o teste é escrito antes da Implementation, ou por uma asserção de comportamento falhar contra um `loader.py` ainda incompleto. Um RED causado por erro de sintaxe no próprio teste, fixture quebrada, ou infraestrutura de teste indisponível não é evidência válida e deve ser corrigido antes de contar.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | — | TD-007 | Covered |
| FR-002 | — | TD-007 | Covered |
| FR-003 | TD-001 | — | Covered |
| FR-004 | TD-002, TD-003, TD-004, TD-005, TD-006 | — | Covered |
| FR-005 | TD-006 (indireto: nenhuma seção incompleta aceita) | Review (busca por classes prematuras no diff) | Covered |
| NFR-001 | TD-002–TD-006 (loader opera sobre `Path` arbitrário via `tmp_path`, sem caminho fixo do repositório) | — | Covered |

## Coverage Gaps

Nenhum Requirement obrigatório permanece sem estratégia de verificação.

## Test Design Gate

- Todos os Requirements obrigatórios (FR-001 a FR-005, NFR-001) possuem estratégia de verificação declarada.
- Cenários críticos (TD-001 a TD-006) possuem Purpose claro e Failure Condition explícita.
- Automated e Manual Acceptance estão separados (Layer A/B vs. Layer C, TD-007).
- Nenhuma propriedade manual (TD-007) é apresentada como garantia automática.
- Nenhum Requirement crítico permanece sem cobertura conhecida.
- Valid RED está definido e aponta para a razão comportamental correta (pacote/símbolos ainda inexistentes).

**Ready for Plan.**
