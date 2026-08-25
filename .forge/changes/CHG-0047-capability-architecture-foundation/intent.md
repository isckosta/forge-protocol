---
forge:
  artifact: intent
  schema: 1
change: CHG-0047
status: active
---

# CHG-0047 · Capability Architecture Foundation

> **Change Intent**
>
> Introduzir uma abstração explícita de Forge Capability — uma competência agentic especializada e reutilizável, canonicamente definida por um `CAPABILITY.md` legível por humanos e carregável deterministicamente pelo CLI — sem implementar nenhuma capability concreta, registry, executor ou novo lifecycle.

## Overview
| | |
|---|---|
| **Change** | CHG-0047 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

O Forge hoje não possui uma camada explícita para representar competências agentic especializadas (ex.: investigar um incidente, revisar uma Mudança, checar provenance, desafiar uma alegação). Na ausência dessa camada, uma nova competência tende a ser absorvida por uma das camadas existentes — a Skill principal do Harness Adapter, o próprio Flow, ou código ad hoc — porque não há um terceiro lugar canônico para ela viver. Isso aumenta acoplamento (a competência vira parte da Skill de um Harness específico), duplicação (cada novo Harness Adapter reimplementaria a mesma competência do zero) e custo de contexto (a Skill principal cresce com conhecimento que só é relevante quando aquela competência específica é exercida). O Protocol e o Engineering Contract corretamente não conhecem "capabilities" hoje — mas isso também significa que registrar uma nova competência não tem endereço arquitetural próprio.

## Goal

1. Introduzir o conceito explícito de Forge Capability, com responsabilidades e limites documentados, na separação: Protocol/Engineering Contract definem obrigações e invariantes; Forge Core/Flow decidem lifecycle e quando uma competência é necessária; Capabilities fornecem a competência especializada; Harness Adapters traduzem essa capability para um ambiente concreto (ex.: uma Claude Skill); o repositório permanece a evidência durável.
2. Definir um contrato mínimo, humano e legível (`capability.md`) que qualquer definição concreta futura de capability (`CAPABILITY.md`) deve satisfazer, cobrindo no mínimo: Identity, Purpose, Applicability, Inputs, Behavior, Outputs, Evidence Expectations.
3. Implementar um modelo mínimo (`src/forge_cli/capabilities/model.py`) e um carregamento determinístico (`src/forge_cli/capabilities/loader.py`) — locate → read → parse → normalize → return capability model — sem execução agentic, composição, registry remoto ou lifecycle.
4. Preservar a possibilidade de uma Change futura introduzir `capabilities/investigate/CAPABILITY.md` como a primeira capability real, e de um Harness Adapter futuro derivar dela uma representação específica (ex.: `.claude/skills/forge-investigate/SKILL.md`) sem redesenhar esta fundação.

## Scope

A abstração conceitual de Capability (documentação em `capabilities/README.md` e `capabilities/capability.md`), o modelo mínimo e o loader determinístico correspondentes em `src/forge_cli/capabilities/`, e os testes focados desses dois módulos.

## Out of Scope

Qualquer capability concreta (`investigate`, `review`, `provenance`, `challenge` ou outra); marketplace; package manager; plugin system; remote registry; capability registry extensível; capability composition runtime; dependency graph; confidence scoring; capability executor; orchestration paralela; adapters para múltiplos Harnesses; novo artifact obrigatório de Change; novo Gate; nova versão de Protocol; storage próprio para capabilities ou estado paralelo ao repositório; árvores vazias para Codex, Cursor, plugin registries ou outras integrações futuras.

## Success Criteria

Forge passa a possuir um conceito explícito e documentado de Capability, com um contrato mínimo e legível para futuras capabilities, e o CLI consegue carregar deterministicamente uma definição compatível com esse contrato. Capability não controla Flow, lifecycle, Gates ou autoridade humana, e o conceito não está acoplado ao Claude. `CAPABILITY.md` funciona como definição canônica futura (distinta de um `SKILL.md` de Harness Adapter). Nenhuma infraestrutura especulativa é adicionada, e a próxima Change pode implementar `investigate` sobre esta fundação sem redesenhar a arquitetura.
