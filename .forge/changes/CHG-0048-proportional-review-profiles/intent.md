---
forge:
  artifact: intent
  schema: 1
change: CHG-0048
status: active
---

# CHG-0048 · Proportional Review Profiles

> **Change Intent**
>
> Introduzir três Review Profiles canônicos ligados a Flow — `focused` (FAST), `standard` (STANDARD), `strict` (FULL) — substituindo o modelo hoje único e Flow-invariante de Strict Review adversarial, sem criar um segundo lifecycle, sem remover independência Reviewer/Resolver, evidence, severities, Resolution ou Convergence Limit, e sob RFC-0007 (aceito para Protocol 2).

## Overview
| | |
|---|---|
| **Change** | CHG-0048 |
| **Flow** | FULL |
| **Status** | Active |

## Problem

Hoje, `protocol/flows/{fast,standard,full}.yml` declaram um bloco `review: {required: true, strict: true, adversarial: true}` idêntico nos três Flows, e o Contract (C-022, C-023) trata "Review" como sinônimo de "Strict Review adversarial" para toda Change, sem exceção por Flow. O classificador semântico de Flow (`fast.yml`'s `disqualifiers`) já distingue explicitamente Changes de baixo impacto (correção localizada, refactor que preserva comportamento) de Changes de alto impacto (arquitetural, segurança, autorização, contrato público) — mas essa distinção nunca chega ao modelo de Review: uma correção de FAST paga o mesmo custo de busca adversarial exaustiva que uma Change arquitetural de FULL. `src/forge_cli/validation/__init__.py` nunca lê `manifest.flow` em nenhuma função de review/convergence, confirmando que o Core hoje é inteiramente Flow-blind nesse ponto.

## Goal

1. Introduzir um campo `profile` (enum `focused | standard | strict`) no bloco `review:` de cada Flow e na política canônica `protocol/versions/2/policies/review.yml`, com `strict` preservando integralmente o comportamento adversarial atual (sem regressão para FULL).
2. Revisar C-022 e C-023 para desacoplar "Review é obrigatória" de "Review é estritamente adversarial", preservando C-031 (FAST não remove TDD/Verification/Review/Documentation Impact) e mantendo C-024–C-027, C-047–C-050, C-067–C-068, independência Reviewer/Resolver, severities e Convergence Limit inalterados e aplicados identicamente aos três profiles.
3. Tornar as mudanças de Schema aditivas (campo `profile` opcional, default `strict` quando omitido), preservando a validade de toda Change histórica (C-045) e sem introduzir novo identificador de Protocol (decisão já registrada em RFC-0007: leitura de clarificação compatível com Protocol 2, não enfraquecimento).
4. Propagar o profile correto para a instrução do Reviewer via Adapter projection (`review_independence.py`, `claude_code/projection.py`, `codex/projection.py`), preservando o bloco de independência Reviewer/Resolver como compartilhado e Flow-invariante.
5. Permitir que a configuração de um projeto exija um profile mais rigoroso que o piso canônico do Flow, mas nunca um profile mais fraco — `forge validate` falha fechado nesse caso.

## Scope

O Contract normativo (C-022, C-023, C-031 e cross-references), as três Flow definitions, os schemas `change-v2`, `flow`, `policy-review-v2` (Protocol 2 apenas), o código de validação relacionado a Flow/profile (sem alterar independência, evidence, severities ou convergence), as projeções de Adapter (Claude Code e Codex) e a documentação/SKILL gerada. RFC-0007 (aceito) é o fundamento normativo desta Change.

## Out of Scope

Qualquer capability concreta ou mecanismo de execução; um novo lifecycle de Review paralelo; remoção ou enfraquecimento de C-024–C-027, C-047–C-050, C-067–C-068 ou de independência Reviewer/Resolver (C-026); scoring numérico de review; downgrade automático de Flow por heurística de linhas/arquivos; Review diff-only ou baseada apenas em testes passando; mudança em `protocol/schemas/policy-review.schema.json` (Protocol 1, permanece intocado); reescrita de Review histórica; nova versão de Protocol (RFC-0007 já resolveu essa questão a favor de Protocol 2); RFC-0005 permanece como registro histórico, marcado superseded, não apagado.

## Success Criteria

Forge aplica Review proporcional ao Flow: FAST usa `focused`, STANDARD usa `standard`, FULL preserva `strict` exatamente como hoje. Toda Change continua exigindo Review real, com autoridade de rejeição, independência Reviewer/Resolver, evidence, severities e Convergence Limit idênticos nos três profiles — apenas a postura de busca por motivos de rejeição varia. Nenhuma Change histórica é invalidada. `forge validate` e os Adapters refletem o novo modelo de forma determinística e auditável.
