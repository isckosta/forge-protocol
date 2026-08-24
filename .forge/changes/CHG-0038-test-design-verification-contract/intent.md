---
forge:
  artifact: intent
  schema: 1
change: CHG-0038
status: active
---

# CHG-0038 · Test Design Verification Contract

> **Change Intent**
>
> Redesenhar o artefato `test-design.md` para que deixe de ser uma lista solta de casos de teste e passe a funcionar como um contrato explícito de verificação, rastreável até Requirements e User Stories, antes da Implementation.

## Overview
| | |
|---|---|
| **Change** | CHG-0038 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

O scaffold atual de `test-design.md` (`src/forge_cli/change_scaffolding.py`) gera apenas `## Objective`, `## Strategy`, um exemplo solto `## TDD-001 — <behavior>` e `## Completion Criteria`. Isso não obriga nem orienta o autor a declarar qual Requirement cada cenário cobre, qual evidência sustenta o resultado, o que invalida uma evidência aparentemente positiva, ou se um cenário é automatizado ou depende de observação humana. Para Changes STANDARD/FAST com Requirements formais (evolução trazida por CHG-0037), essa lacuna dificulta responder, antes da Implementation, se todo Requirement crítico tem uma estratégia de verificação plausível.

## Goal

1. Fazer o `test-design.md` gerado expressar explicitamente: o que precisa ser provado, por que o cenário existe, qual Requirement (e, quando aplicável, qual User Story) ele cobre, que tipo de evidência será produzida, o que invalida o cenário, e quais gaps de cobertura permanecem.
2. Separar claramente verificação automatizada de aceitação manual, sem tratar interação humana como mecanicamente verificável.
3. Preservar a distinção entre Test Design (pré-Implementation) e Verification (pós-Implementation): Test Design não deve registrar resultados como se já tivessem sido executados.

## Scope

O template gerado de `test-design.md` (STANDARD/FAST, quando comportamental), a guidance não vinculante correspondente em `protocol/artifact-structure.md`, documentação afetada, e os testes focados do scaffold renderer.

## Out of Scope

`test-strategy.md` (Flow FULL) permanece com sua convenção `## TDD-xxx` real e estável, sem redesenho. Nenhum parser de Markdown, framework BDD, geração automática de testes, nova versão de Protocol, novo Schema, novo comando de lifecycle, ou exigência de User Story para todo Requirement.

## Success Criteria

Novos `test-design.md` gerados expõem estrutura de Overview, Test Strategy, Coverage Map, cenários `TD-xxx` autocontidos, Requirement Coverage, Coverage Gaps e um Test Design Gate. `test-design.md` históricos continuam válidos e `forge validate` continua correto.
