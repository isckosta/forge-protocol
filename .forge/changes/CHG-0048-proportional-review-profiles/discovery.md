---
forge:
  artifact: discovery
  schema: 1
change: CHG-0048
status: complete
---

# Discovery — CHG-0048 Proportional Review Profiles

## Executive Summary

O Forge hoje trata "Review" e "Strict Review adversarial" como sinônimos incondicionais para toda Change, em todo Flow — as três definições de Flow (`protocol/flows/{fast,standard,full}.yml`) declaram um bloco `review: {required: true, strict: true, adversarial: true}` byte-idêntico, e o Contract (C-022, C-023) não menciona Flow. `src/forge_cli/validation/__init__.py` nunca lê `manifest.flow` em nenhuma função de review/convergence — o Core é inteiramente Flow-blind nesse ponto, apesar do classificador semântico de Flow já existir e já distinguir explicitamente baixo de alto impacto (`fast.yml`'s próprio `disqualifiers`: `architectural_change`, `security_model_change`, `major_public_contract_change`, etc.). O achado mais importante, e que redesenha o escopo desta Change antes mesmo de a Specification começar: já existe um RFC anterior sobre este tema exato — RFC-0005 ("Review Cost Proportionality", produzido por CHG-0027) — que permaneceu `Proposed` (nunca aceito) e cujos próprios Non-goals proibiam explicitamente "removal of adversarial Review" e "changes to current Flows, Review policy, Contract, schemas, or CLI". RFC-0007 (proposto e aceito nesta sessão, ver `docs/rfcs/0007-proportional-review-profiles.md`) supera essa proibição de forma explícita e estreita, e resolve a questão normativa central (enfraquecimento de invariante vs. clarificação compatível) a favor da leitura compatível com Protocol 2, sem novo identificador de Protocol.

## Investigation

### Contract atual — C-022, C-023 e vizinhança

`protocol/contract/engineering.md` (canônico Protocol 1) e `protocol/versions/2/contract/engineering.md` (canônico Protocol 2, que herda C-001–C-025 e C-027–C-046 de Protocol 1 sem enfraquecê-los, e introduz C-026 mais forte) carregam o mesmo texto para C-022/C-023:

- **C-022** — "Every Change MUST undergo Strict Review."
- **C-023** — "Strict Review MUST actively search for reasons to reject the Implementation."
- **C-031** — "FAST MUST NOT remove applicable TDD, Verification, Review, or Documentation Impact evaluation." (já reconhece que FAST reduz cerimônia, mas nunca fala de postura/voz de Review — não há hoje contradição textual a resolver, apenas uma lacuna a preencher.)
- C-024 (TDD reviewable), C-025 (evidence para BLOCKER/MAJOR), C-026 (independência Reviewer/Resolver, Protocol 2 — "for FAST, STANDARD, and FULL"), C-027 (BLOCKER bloqueia Completion), C-047–C-050 (Resolution Verification scoping, Out-of-Scope Mutation, Convergence Limit, unrelated-latent-finding), C-067–C-068 (estrutura de Artifact, outcome-before-evidence) — nenhuma dessas menciona Flow; todas tratam "Review"/"Strict Review" como um conceito único e plano.

`.forge/contract/engineering.md` é a extensão de projeto (F-001–F-011), não uma cópia do Contract canônico — F-008 ("Material Protocol Changes require RFC"), F-009 (compatibility awareness para Schema/Protocol/Adapter), F-010 (foundation simplicity — preferir estruturas explícitas a plugin systems), F-011 (deterministic validation) são diretamente aplicáveis a esta Change.

### As três Flows — `review:` idêntico, mas vocabulário Flow-scoped já existe em outro lugar

`fast.yml`, `standard.yml`, `full.yml` declaram o mesmo bloco `review: {required: true, strict: true, adversarial: true}` (linhas 68–71, 62–65, 77–80 respectivamente). O stage `strict_review` em si também é idêntico e sem `mode:` nos três — em contraste direto com o stage `specification_review` de FULL, que já carrega `mode: adversarial` (`full.yml`, linha 19). Isso confirma que o vocabulário "mode por stage" já existe no schema/Flow, só nunca foi aplicado a `strict_review`.

`protocol/versions/2/policies/review.yml` (a política canônica de Protocol 2) também declara `strict: true`/`adversarial: true` no topo, mas seu campo `reviewer_resolver_separation.independence` já é Flow-keyed (`{fast: execution_context, standard: execution_context, full: execution_context}`, linha 15) — hoje com os três valores idênticos, mas a forma já antecipa variação por Flow que nunca foi usada para o próprio modelo de Review.

Não existe um segundo conjunto canônico de Flow files sob `protocol/versions/2/` — Protocol 2 varia a semântica de review via `protocol/versions/2/policies/review.yml`, não via cópias de `.yml` de Flow.

### Schemas — mudança aditiva é viável, mas em quatro arquivos distintos

- `protocol/schemas/change-v2.schema.json`: o objeto `review` do manifest (`additionalProperties: false`) tem `status`, `iteration`, `blockers/majors/minors/observations`, `iterations[]` (`kind: initial_review|resolution_verification`, `finding_classes`, `convergence_decision`), `convergence`. Nenhum campo `profile` existe hoje; adicioná-lo é aditivo.
- `protocol/schemas/flow.schema.json`: o sub-schema `review` de cada Flow tem `required`, `strict`, `adversarial` todos como `const: true` fixo, com `additionalProperties: false` — este é o schema que precisa mudar estruturalmente para permitir que os três `.yml` de Flow declarem valores diferentes (ou um enum `profile`). O mesmo arquivo já usa `if/then` por `flow.id` para outras propriedades (ex.: `stages` — ver precedente abaixo), então o padrão de variação por Flow já existe no próprio schema.
- `protocol/schemas/policy-review-v2.schema.json`: mesmos três `const: true`, mas o objeto é `additionalProperties: true` — uma chave `profile` adicional já é legal sem editar o schema; só os `const` de `strict`/`adversarial` precisariam relaxar se este RFC quiser que sejam também Flow-dependentes aqui (não apenas nos três `.yml` de Flow).
- `protocol/schemas/policy-review.schema.json` (Protocol 1): `additionalProperties: false` e `const: true` fixos — Discovery recomienda deixar este arquivo **intocado**: profiles são um conceito de Protocol 2 apenas nesta Change (RFC-0007, item 9), evitando reabrir semântica de Protocol 1.

### Código de validação — hoje inteiramente Flow-blind no review/convergence

`src/forge_cli/validation/__init__.py` (789 linhas): busca por `"flow"` retorna apenas 2 ocorrências, ambas fora de qualquer função de review/convergence (resolução de arquivo de Flow, não semântica). `_validate_resolution_verification` (linha 120) e `_validate_protocol2_review_provenance` (linha 315) operam inteiramente sobre `manifest.review`, `iterations[]` e `provenance.yml`, sem nunca inspecionar `manifest.flow`. O Convergence Limit é um `2` hardcoded (linha 188), lido de `protocol/versions/2/policies/review.yml`'s `convergence_limit: 2` — não parametrizado por Flow em lugar nenhum.

`src/forge_cli/merge_readiness/evaluator.py`: mesma constatação — a label `"STRICT REVIEW NOT READY"` é fixa (linha 90), a checagem de blockers/majors (linhas 285–288) e a verificação de independência Reviewer/Resolver (execution/context/revision binding) são aplicadas identicamente sem nenhum branch de Flow.

**Implicação de design**: um `profile` pode ser adicionado ao Schema e à instrução do Reviewer sem que `validation/__init__.py` precise diferenciar comportamento de independência/evidence/severities/convergence por profile — essas continuam sendo checadas do mesmo jeito para os três profiles (RFC-0007, item 10). Isso mantém o raio de mudança do código de validação mínimo, alinhado a F-010/F-011.

### Adapter projections — hoje deliberadamente de voz única, não Flow-aware

`src/forge_cli/adapters/review_independence.py` é a fonte compartilhada consolidada pelo CHG-0045 (o próprio docstring do arquivo registra que essa consolidação *removeu* repetição por Flow: antes, o bloco de independência era reemitido uma vez por Flow efetivo). O ponteiro atual (`REVIEWER_RESOLVER_INDEPENDENCE_POINTER`) diz textualmente: "Strict Review for this Flow is subject to the single ... section below; it is not restated per Flow."

`claude_code/projection.py`'s `_gate_instructions()` (linhas 81–135) gera uma seção `### Flow \`{flow_id}\` gate obligations` por Flow, mas a linha de review dentro de cada uma é idêntica: `"- Completion requires Strict Review to pass."` (linha 114). `codex/projection.py` espelha exatamente o mesmo padrão. O `SKILL.md` gerado (`.claude/skills/forge/SKILL.md`, linhas 130/142/155) confirma: a mesma frase aparece nas três seções de Flow.

**Implicação de design**: esta Change precisa desfazer parcialmente essa consolidação — não o bloco de independência em si (que continua compartilhado, por ser Flow-invariante per RFC-0007 item 6), mas a frase de instrução de review dentro de cada seção `### Flow` passa a ser profile-specific. Isso é uma mudança localizada em `_gate_instructions()` e equivalente no Codex Adapter, não uma reversão arquitetural do CHG-0045.

### Precedentes de comportamento Flow-condicional já existentes

1. `tasks` e `specification_review` existem apenas em FULL (`full.yml` linhas 17–19, 26). `flow.schema.json` já força arrays de `stages` diferentes por Flow via `if/then` em `flow.id` — precedente direto de "o Schema já sabe variar por Flow.id".
2. `reviewer_resolver_separation.independence` já é um mapa por Flow em `protocol/versions/2/policies/review.yml`, mesmo com os três valores hoje idênticos.
3. `escalation.target` difere estruturalmente por Flow (`standard.yml` tem `target: full`; `fast.yml` não tem essa chave) — confirma que os arquivos de Flow já podem divergir em forma, não só em valor.

### RFC-0005 — por que não é suficiente e por que precisa ser superado, não estendido

RFC-0005 ("Review Cost Proportionality", `docs/rfcs/0005-review-cost-proportionality.md`, produzido por CHG-0027) propôs algo materialmente mais estreito: um "Review Calibration Profile" *descritivo*, camada sobre um modelo adversarial único e inalterado — dimensões de ênfase/evidência, não uma voz de Review diferente. Seus próprios Non-goals (linha 65–66) proíbem "removal of adversarial Review or independent reviewer/resolver roles" e "changes to current Flows, Review policy, Contract, schemas, or CLI". RFC-0005 nunca foi aceito (permaneceu `Proposed` desde CHG-0027) e nenhuma Change o implementou. RFC-0007 (aceito nesta sessão) supera essa proibição de forma explícita e estreita — apenas para o conceito de review profile aqui definido — e RFC-0005 foi marcado `Status: Superseded by RFC-0007`.

### Questão normativa central — já resolvida via RFC-0007

C-022/C-023 aplicam-se hoje a toda Change sem exceção por Flow. Desacoplar FAST/STANDARD da postura `strict`/adversarial pode ser lido como enfraquecimento de invariante (C-046, exigindo novo Protocol 3) ou como clarificação compatível (C-045 — nenhuma Change histórica invalidada, independência e autoridade de rejeição idênticas nos três profiles, só a postura de busca muda). Esta foi tratada como Material Unresolved Decision (classe Contract, autoridade humana, C-054/C-055) e escalada — o usuário resolveu explicitamente a favor da leitura compatível com Protocol 2 (ver `docs/rfcs/0007-proportional-review-profiles.md`'s seção "Open normative question — resolved at acceptance" e `provenance.yml`'s `rfc-acceptance-001`). Protocol permanece `2`.

### Classificação de Flow

FULL. Esta Change modifica: texto normativo do Contract (C-022, C-023, e a nota de C-031); as três definições de Flow; múltiplos Schemas de Protocol 2; código de validação (mesmo que de forma aditiva/mínima); e projeções de Harness Adapter — corresponde diretamente aos disqualifiers de FAST (`architectural_change`, `major_public_contract_change`) e exige RFC (F-008), Architecture, Specification Review adversarial e Test Strategy. Escalada de STANDARD (default do scaffold) para FULL antes de qualquer trabalho de Specification, registrada em `manifest.yml`'s `flow.escalations` (C-005).
