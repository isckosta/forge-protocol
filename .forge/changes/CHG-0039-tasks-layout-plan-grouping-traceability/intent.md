---
forge:
  artifact: intent
  schema: 1
change: CHG-0039
status: active
---

# CHG-0039 · Tasks Layout Plan Grouping Traceability

> **Change Intent**
>
> Redesenhar o artefato `tasks.md` (Flow FULL) para que a checklist plana de execução passe a agrupar Tasks pelo item de Plan correspondente e a expor referências compactas a Requirements, User Stories e Test Design, sem deixar de ser uma checklist operacional.

## Overview
| | |
|---|---|
| **Change** | CHG-0039 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

O scaffold atual de `tasks.md` (`src/forge_cli/change_scaffolding.py`) gera apenas uma checklist plana (`- [ ] T-001 <work item>`) seguida de `## Status`, sem qualquer agrupamento ou referência estrutural. Isso corresponde à guidance real e estável documentada em `protocol/artifact-structure.md` §4 ("Tasks"), confirmada por precedente real (`CHG-0015/tasks.md`, `CHG-0016/tasks.md`). Para uma Change FULL com um Plan de vários itens, essa forma plana obriga o leitor a reconstruir mentalmente de qual item do Plan cada Task se origina, e não expõe rastreabilidade a Requirements, User Stories (introduzidas pela CHG-0037) ou Test Design (redesenhado pela CHG-0038) quando essas relações existem e são relevantes.

## Goal

1. Agrupar as Tasks geradas pelo item do Plan correspondente (`### Plan N · <título>`), preservando a checklist (`- [ ] T-xxx`) como fonte de estado de execução.
2. Permitir referência compacta e opcional a `Plan`, `Requirements`, `Stories` e `Test Design` por Task, sem forçar todo tipo de referência em toda Task.
3. Adicionar uma seção `Overview` compacta no topo do artefato, com campos derivados de forma segura (Change, Flow, Status), sem inventar garantias que o Forge não sustenta.
4. Preservar `## Status` como leitura rápida do estado operacional, sem transformá-la em diário de desenvolvimento.

## Scope

O template gerado de `tasks.md` (Flow FULL, quando comportamental), a guidance não vinculante correspondente em `protocol/artifact-structure.md`, documentação afetada, e os testes focados do scaffold renderer.

## Out of Scope

Novo artefato, substituição do Plan/Specification/Test Design/Verification, Story Points, estimativas, assignees obrigatórios, Sprint, Epic, backlog, prioridade obrigatória por Task, dependency graph entre Tasks, novo comando de lifecycle, nova versão de Protocol, novo Schema, parser de Markdown ou validação semântica frágil de referências (`Plan:`/`Requirements:`/`Stories:`/`Test Design:`), sintaxe nova para blocked Tasks, e qualquer artefato de exemplo fabricado de domínio (ex.: ERP) fora da guidance ilustrativa em `protocol/artifact-structure.md`.

## Success Criteria

Novos `tasks.md` gerados (Flow FULL) expõem Overview, Tasks agrupadas por item de Plan, IDs `T-xxx` estáveis, referências compactas opcionais a Requirements/Stories/Test Design, e `## Status`. `tasks.md` históricos continuam válidos e `forge validate` continua correto.
