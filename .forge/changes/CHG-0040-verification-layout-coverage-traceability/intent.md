---
forge:
  artifact: intent
  schema: 1
change: CHG-0040
status: active
---

# CHG-0040 · Verification Layout Coverage Traceability

> **Change Intent**
>
> Redesenha o `verification.md` gerado pelo scaffold para elaborar a
> estrutura "Result-before-evidence" já normatizada (C-068,
> `protocol/artifact-structure.md` §4 "Verification") com cobertura
> rastreável por Acceptance Criterion e Requirement, evidência manual
> distinta da automatizada, e representação explícita de FAIL/SKIPPED/NOT
> APPLICABLE — sem alterar a semântica normativa de PASS/FAIL.

## Overview
| | |
|---|---|
| **Change** | CHG-0040 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

O `verification.md` gerado pelo scaffold hoje (`change_scaffolding.py`) é um
esqueleto mínimo: `Result`/`Summary`/`Test Evidence`/`Forge Evidence`/
`Conclusion`, sem tabela de cobertura por critério. O exemplo canônico
(`examples/canonical-artifacts/verification.md`) e a guidance normativa
(`protocol/artifact-structure.md` §4 "Verification", C-068) já apontam
para "Result first" seguido de uma tabela `AC-xxx → Result`, mas essa
elaboração nunca foi materializada no template real nem detalhada o
suficiente para cobrir Requirement Coverage agregada, User Story
Coverage opcional, Manual Evidence distinta de Test/Forge Evidence,
sequenciamento RED→GREEN referenciado (não renarrado), representação de
FAIL sem mascarar o resultado agregado, e rationale exigido para
SKIPPED/NOT APPLICABLE. `verification.md` reais desta mesma família
(`CHG-0037`, `CHG-0038`, `CHG-0039`) já seguem Result-first na prática,
mas nenhum usa tabela `AC-xxx`, porque o scaffold nunca ofereceu essa
estrutura.

Esta é a mesma lacuna que `CHG-0037` (Specification), `CHG-0038` (Test
Design) e `CHG-0039` (Tasks) já corrigiram para seus respectivos
artefatos: guidance não-binding definida em `protocol/artifact-structure.md`
existia em forma genérica, mas o scaffold real nunca a materializou.

## Goal

1. O `verification.md` gerado SHALL apresentar `Result` como primeira
   seção substantiva, com um dos estados reconhecidos
   (`PASS`/`FAIL`/`SKIPPED`/`NOT APPLICABLE`).
2. O scaffold SHALL oferecer estrutura para Summary agregado, Acceptance
   Coverage (`AC-xxx`), Requirement Coverage, Test Evidence, Forge
   Evidence, Manual Evidence, Compatibility and Limitations, e
   Conclusion — presentes apenas quando materialmente aplicável
   (proporcionalidade, §2.5).
3. A guidance canônica (`protocol/artifact-structure.md` §4
   "Verification") SHALL documentar essa estrutura elaborada, sem
   substituir C-068 nem introduzir novo estado de resultado.
4. Nenhuma mudança de Protocol integer, Change Schema, Gate semantics,
   `forge validate` enforcement ou Harness Adapter é introduzida.

## Scope

O layout de apresentação do artefato Verification: o template do
scaffold (`verification` em `change_scaffolding.py`), a guidance
correspondente em `protocol/artifact-structure.md`, o exemplo canônico
em `examples/canonical-artifacts/verification.md` quando necessário para
demonstrar a estrutura elaborada, e os testes de scaffold cobrindo o
novo layout.

## Out of Scope

Não introduz novo validador Markdown, novo campo de schema, novo estado
de resultado além de `PASS`/`FAIL`/`SKIPPED`/`NOT APPLICABLE`, nova
versão de Protocol, nem reescreve `verification.md` de Changes
históricas. Não duplica `traceability.yml` (schema `forge/traceability@1`),
que permanece um artefato legado opcional não vinculado ao scaffold —
mesma decisão já tomada por `CHG-0037`/`CHG-0038`/`CHG-0039`. Não
redesenha `review.md`, `test-strategy.md`, `plan.md` ou qualquer outro
artefato.

## Success Criteria

Um leitor de qualquer `verification.md` recém-gerado consegue responder
"a Change passou?" lendo apenas a primeira seção, e consegue rastrear
qualquer afirmação de conformidade até a evidência correspondente sem
precisar reconstruir manualmente a relação entre Acceptance Criteria,
Requirements e evidência. A guidance permanece proporcional: uma Change
pequena continua podendo produzir um `verification.md` curto sem seções
vazias.
