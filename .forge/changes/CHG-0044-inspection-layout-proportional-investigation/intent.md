---
forge:
  artifact: intent
  schema: 1
change: CHG-0044
status: active
---

# CHG-0044 · Inspection Layout Proportional Investigation

> **Change Intent**
>
> Elabora a guidance de `inspection.md` (`protocol/artifact-structure.md`,
> §4 "Inspection") e seu scaffold (`change_scaffolding.py`) para melhorar
> identidade visual, consistência mínima e clareza do resultado da
> investigação, preservando integralmente a proporcionalidade que já é a
> propriedade central deste artefato — sem introduzir nenhuma seção,
> heading ou metadata obrigatórios.

## Overview
| | |
|---|---|
| **Change** | CHG-0044 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

`protocol/artifact-structure.md`'s seção "Inspection" (linhas 562-570) é
hoje um único parágrafo: "whatever the fix actually requires explaining —
nothing more", com dois exemplos reais citados (`CHG-0005`, quatro linhas;
`CHG-0012`, 86 linhas). Essa orientação está correta em espírito, mas é a
única, entre os quatorze tipos de Artifact cobertos por este documento, a
não ter recebido a mesma elaboração que Specification (`CHG-0037`), Test
Design (`CHG-0038`), Tasks (`CHG-0039`), Verification (`CHG-0040`), Review
(`CHG-0041`), Specification Drift (`CHG-0042`) e Knowledge Capture
(`CHG-0043`) já receberam.

O scaffold atual (`change_scaffolding.py:135`) emite um corpo mínimo —
`"## Inspection\n\nRecord the relevant inspection findings.\n"` — que
duplica desnecessariamente o heading de identidade (a própria seção já se
chama "Inspection") e não orienta o autor sobre proporcionalidade,
separação sintoma/causa, ou quando declarar um Fix Boundary. O heading de
identidade também usa hoje o formato genérico de fallback
(`# Inspection — CHG-XXXX <Title>`, `change_scaffolding.py:88`), diferente
do formato `# CHG-XXXX · <Type>` já adotado para Specification, Test
Design, Tasks, Verification, Review e Knowledge Capture.

Seis `inspection.md` reais existem no repositório (`CHG-0005`, quatro
linhas de conteúdo; `CHG-0012`, 86 linhas com root cause, precedente e uma
correção pós-Review; `CHG-0024`, `CHG-0026`, `CHG-0028`, `CHG-0029`, entre
44 e 62 linhas). Todos usam headings orgânicos e distintos entre si (Root
Cause, Evidence, Classification, Flow Classification, Decision, Current
state, Recommendation, Documentation Impact, entre outros) — nenhum
vocabulário compartilhado existe hoje, o que torna cada Inspection real
mais difícil de escanear rapidamente por um leitor familiarizado com as
outras.

## Goal

1. Elaborar §4 "Inspection" de `protocol/artifact-structure.md` com um
   vocabulário estrutural recomendado e opcional (`Observation`,
   `Evidence`, `Root Cause`, `Impact`, `Fix Boundary`, `Open Question`,
   `Conclusion`), explicitamente não obrigatório e explicitamente não
   exaustivo — a proporcionalidade continua sendo a primeira regra.
2. Corrigir a caracterização imprecisa do exemplo `CHG-0005` ("a
   four-line file (title only)") para refletir seu conteúdo real (dois
   parágrafos de contexto real, três frases ao todo, sem headings).
3. Atualizar o heading de identidade do scaffold para `# CHG-XXXX ·
   Inspection`, consistente com os demais artefatos já elaborados, e
   tornar o corpo mínimo do scaffold um comentário de orientação em vez
   de um heading vazio duplicado.
4. Documentar explicitamente a distinção entre Inspection e Discovery,
   Specification, Plan, Verification, e Experience Report, e o mecanismo
   real de escalada de Flow quando uma Inspection revela complexidade
   maior do que FAST comporta.
5. Não adicionar nenhuma validação semântica nova sobre headings de
   Inspection, nenhum novo comando, e nenhuma nova obrigação normativa.

## Scope

`protocol/artifact-structure.md` (seção "Inspection"), o scaffold
`inspection` em `change_scaffolding.py`, e os testes de scaffold
correspondentes em `tests/unit/test_change_scaffolding.py`.

## Out of Scope

Não transforma Inspection em Discovery, Specification, Plan, ou
Verification. Não introduz User Stories, IDs de finding próprios, novo
comando de lifecycle, novo schema, ou novo validador semântico. Não
reescreve `inspection.md` históricos. Não altera a classificação de Flow
FAST/STANDARD/FULL, nem outros artefatos além de Inspection.

## Success Criteria

Um agente escrevendo um `inspection.md` real para um fix trivial continua
podendo produzir um arquivo de poucas linhas sem headings, e um agente
investigando um defeito complexo tem um vocabulário consistente e
opcional disponível quando a investigação genuinamente o exige — sem que
`forge validate` ou qualquer scaffold passe a exigir estrutura adicional.
