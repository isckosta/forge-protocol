---
forge:
  artifact: discovery
  schema: 1
change: CHG-0041
status: complete
---

# Discovery — CHG-0041 Review Layout Verdict First Findings

## Executive Summary

A guidance para "aggregate Verdict antes do histórico" já existe
normativamente (C-068; `protocol/artifact-structure.md` §4 "Review",
herdada de `CHG-0016`) e `CHG-0016/review.md`'s próprio Review já
demonstra quase toda a estrutura elaborada que este prompt pede — mas
o scaffold real (`change_scaffolding.py:311`) continua emitindo um
esqueleto de duas linhas. Mesmo padrão de lacuna que `CHG-0037`
(Specification), `CHG-0038` (Test Design), `CHG-0039` (Tasks) e
`CHG-0040` (Verification) já corrigiram: materializar guidance
não-binding já declarada no template real, sem nova obrigação de Gate.

Uma decisão de design importante: o prompt original ilustra uma seção
`## Iteration History` envolvendo `### Iteration N · <verdict>`
(heading nível 3, separador "·"). O histórico real e 100% consistente
em todo `review.md` já existente usa `## Iteration N — <verdict>`
(heading nível 2, travessão) sem wrapper. `protocol/artifact-structure.md`
já compromete-se explicitamente a preservar essa convenção "unchanged".
Esta Discovery recomenda preservar a convenção real exatamente como
está (sem wrapper, sem mudança de heading level/separador) e apenas
inserir as novas seções (Review Summary, Current Subject, Open
Findings, Reviewer Independence) entre `## Verdict` e a primeira
`## Iteration N`. Isso atinge o objetivo real do prompt (estado atual
visível antes do histórico) sem inventar uma convenção que nenhuma
Review real já usa.

## Investigation

### Protocol, Schema e Flows

Inalterados desde `CHG-0040`: Protocol `2`; Change Schema
`forge/change@2`; Flow default `standard`. `strict_review` é stage
obrigatório em `fast.yml`, `standard.yml`, `full.yml`
(`_STAGE_FILES["strict_review"] = ("review.md", "review")`).

### Distinção Specification Review vs Strict Review

Dois artefatos e namespaces de finding completamente distintos,
confirmados:

- **Specification Review** (`specification_review`, arquivo
  `specification-review.md`) — template atual: `## Verdict\n\n**PENDING**\n\n## Findings\n\nRecord findings.\n\n## Checked and found sound\n\nRecord sound claims.\n\n## Conclusion\n\n`.
  Guidance em `artifact-structure.md`: "Verdict at the top..., Findings
  (`SR-xxx`...), Checked and found sound, Conclusion." Fora de escopo
  desta Change (§45 do prompt original; nenhum `SR-xxx` é tocado).
- **Strict Review** (`strict_review`, arquivo `review.md`) — o
  artefato desta Change. Findings usam `Rxxx` (confirmado por grep:
  nenhum `review.md` desde `CHG-0016` usa `SR-xxx`; `specification-review.md`
  nunca usa `Rxxx`).

### Autoridade normativa (Contract)

- **C-022** — Review obrigatória. **C-023** — adversarial. **C-025** —
  Findings BLOCKER/MAJOR MUST incluir evidência suficiente (MINOR/OBSERVATION
  não exigidos, mas não proibidos). **C-026** — Reviewer/Resolver
  separation; Protocol 2 exige Execution/Execution Context distintos,
  não apenas separação conceitual de Role. **C-027** — BLOCKER não
  resolvido impede Completion; threads bloqueantes em review surface
  externo também. **C-047** — Resolution Verification é escopada aos
  Findings-alvo, Resolution Delta, e Out-of-Scope Mutation — não é
  re-audit irrestrito. **C-048** — mutação material fora do escopo
  declarado exige Full Review Escalation (nova Initial Review). **C-049**
  — convergência tem terminação determinística (Convergence Limit).
  **C-050** — finding latente não-relacionado descoberto durante
  Resolution Verification é registrado, não descartado nem usado para
  virar re-audit irrestrito. **C-059** — Reviewer que descobre Decision
  Unresolved material registra Finding, não resolve dentro da mesma
  Review. **C-068** — Verification e Review SHOULD apresentar outcome
  antes de evidência (base normativa direta deste redesign).

### Severity model e policy real

`protocol/policies/review.yml` (`forge/policy/review@1`) e
`protocol/schemas/policy-review-v2.schema.json` (Protocol 2, `@2`)
confirmam: `severities: [blocker, major, minor, observation]`;
`blocking: [blocker, major]` — **MAJOR também bloqueia**, não só
BLOCKER; `evidence.required_for: [blocker, major]`;
`reviewer_resolver_separation` exige `same_execution_forbidden`,
`same_context_forbidden`, `review_subject_freeze_required`,
`post_freeze_subject_mutation_invalidates_binding`; `re_review.required_after_blocking_resolution: true`.
Nenhuma severity nova deve ser introduzida.

### Estrutura de dados já autoritativa (`manifest.yml`, `provenance.yml`)

`protocol/schemas/change-v2.schema.json`'s propriedade `review` já
estrutura tudo que `Review Summary`/`Open Findings`/`Current Subject`
precisam apresentar: `status` (`pending|active|passed|failed`),
`iteration` (int), `blockers`/`majors`/`minors`/`observations` (int,
contagem **outstanding**, não cumulativa — confirmado por
`CHG-0016/review.md`'s própria distinção explícita entre "Raised" e
"Outstanding"), e `iterations[]` com `id`, `revision`,
`subject_provenance`, `reviewer_provenance`, `status`, `kind`
(`initial_review|resolution_verification`), `full_review_required`,
`new_material_findings`, `finding_classes[]`, `convergence_decision`.
Uma iteração `status: passed` exige `subject_provenance` e
`reviewer_provenance` (schema `allOf`/`if`). `execution-provenance-v2.schema.json`
confirma `role: [implementation, resolution, review, delegated_task]`
— "Resolution" é um role de provenance, não um artefato/stage
separado; referenciado em `review.md` como `Subject provenance:
resolution-001` (padrão real já usado em `CHG-0016/review.md`), nunca
copiado por extenso.

Isso confirma o modelo do prompt (§41 "Structured Authority"): `review.md`
deve **apresentar** esses campos já estruturados, nunca duplicá-los
como segunda fonte manualmente contável.

### Template atual do scaffold

`change_scaffolding.py:311`:
```
"review": "## Verdict\n\n**PENDING**\n\n## Iteration 1 — PENDING\n\nRecord Strict Review findings.\n",
```
`PENDING` é placeholder de scaffold (ainda não executado), mesmo
padrão de `specification_review`; não é um dos estados finais
reconhecidos (`PASS`/`REQUEST CHANGES`).

### Convenção real de heading de iteração

Levantamento (`grep -rh "^## Iteration" .forge/changes/*/review.md`):
`## Iteration N — <verdict>` (travessão) é a forma dominante e
100% presente onde a estrutura já segue `CHG-0016`; formas mais
antigas incluem `FAIL`/`FAILED`/texto livre ("Adversarial Re-review",
"GitHub Review Reconciliation") — ruído histórico pré-estabilização,
não autoridade atual. Alguns `review.md` reais anotam o `kind` inline:
`## Iteration 4 — REQUEST CHANGES (\`kind: initial_review\`)`,
`## Iteration 2 — PASS (\`kind: resolution_verification\`)` — convenção
útil e já real, vale preservar como guidance opcional.

### Convenção real de finding ID

Confirmado por grep: `CHG-0008` até aproximadamente `CHG-0014` usavam
`CHG-XXXX-Rxxx` (prefixo com Change id). A partir de `CHG-0016`
(inclusive), a convenção real e a guidance textual de
`artifact-structure.md` ("Findings use `Rxxx`") usam `Rxxx` puro, sem
prefixo de Change — confirmado em `CHG-0016`, `CHG-0017`, `CHG-0018`,
`CHG-0019`, `CHG-0020`, `CHG-0021`, `CHG-0027`, `CHG-0038`. Esta é a
convenção atual a preservar; `CHG-XXXX-Rxxx` é histórico legado, não
reescrito.

### Estrutura real de finding (`CHG-0016/review.md`)

Já demonstra o padrão-alvo: `### R012 — BLOCKER — <title>` seguido de
**Problem:**, evidência (bloco de código/diff quando aplicável),
consequência. Não usa subtítulos `####` obrigatórios
(`Finding`/`Evidence`/`Impact`/`Required Resolution`) — usa prosa
compacta com labels em negrito inline. Esta é uma estrutura mais leve
que a do prompt original, mas preserva os quatro elementos exigidos
(identidade, severidade, evidência, consequência) sem forçar
subheadings redundantes numa Review pequena. Recomendo seguir esse
padrão real (label em negrito, não `####`), com `####` como opção
quando a Review for grande o suficiente para precisar de navegação
adicional (proporcionalidade, §2.5).

### `Checked and Found Sound` — precedente real

Confirmado como convenção real e estável, em dois níveis conforme
proporcionalidade: `## Checked and found sound` (top-level, Review de
iteração única) em `CHG-0017`, `CHG-0018`, `CHG-0020`; `### Checked
and found sound` (aninhado dentro de uma Iteration, Review
multi-iteração) em `CHG-0038`, e nos próprios `review.md` de
`CHG-0039`/`CHG-0040` desta sessão.

### Harness Adapters

Nenhuma referência a `Iteration`/`Verdict`/`Rxxx`/estrutura de
`review.md` em `src/forge_cli/adapters/*.py` (grep vazio). Confirma
nenhum impacto de Adapter, mesmo padrão de `CHG-0037`/`38`/`39`/`40`.

### Testes existentes

Nenhum teste hoje verifica o conteúdo estrutural de `review.md`
(apenas presença no conjunto de arquivos por Flow, e o teste de
proteção `test_render_scaffold_review_plan_test_strategy_tasks_templates_are_unchanged`
que **esta própria Change vai quebrar deliberadamente** e precisa
atualizar, já que `review` deixa de ser um dos templates "unchanged").

### Validators

Nenhum parser de conteúdo Markdown de `review.md` existe em
`src/forge_cli/validation/__init__.py`; os checks relacionados a
Review (`_validate_resolution_verification`, C-026/C-047/C-049) operam
inteiramente sobre `manifest.yml`/`provenance.yml` estruturados, nunca
sobre o texto de `review.md`. Confirma C-067 (nenhuma validação nova
de Markdown deve ser introduzida) e que `review.md` é puramente
apresentação da autoridade estruturada já existente.

## Compatibility Finding

Nenhum impacto retroativo: `review.md` históricos não são reescritos;
nenhuma mudança de Protocol integer, Change Schema, severity model,
reviewer/resolver independence semantics, ou `forge validate`
semantics. `specification-review.md`/`SR-xxx` inalterados.
