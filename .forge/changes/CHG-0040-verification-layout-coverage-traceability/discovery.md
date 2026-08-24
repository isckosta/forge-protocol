---
forge:
  artifact: discovery
  schema: 1
change: CHG-0040
status: complete
---

# Discovery — CHG-0040 Verification Layout Coverage Traceability

## Executive Summary

A guidance para o layout elaborado de `verification.md` já existe
normativamente (C-068; `protocol/artifact-structure.md` §4
"Verification", herdada de `CHG-0016`) e já tem um exemplo canônico
parcial (`examples/canonical-artifacts/verification.md`), mas o scaffold
real (`src/forge_cli/change_scaffolding.py:286`) continua emitindo um
esqueleto mínimo de cinco linhas sem tabela de cobertura. Nenhum
`verification.md` real desta família de Changes (`CHG-0037`, `CHG-0038`,
`CHG-0039`) usa `AC-xxx`, `Requirement Coverage` ou `Manual Evidence`
distinta — porque o template nunca ofereceu essa estrutura. Este é o
mesmo padrão de lacuna que `CHG-0037`/`CHG-0038`/`CHG-0039` já
corrigiram para Specification/Test Design/Tasks: elaborar o scaffold
real para materializar guidance não-binding já declarada, sem introduzir
nenhuma nova obrigação de Gate.

## Investigation

### Protocol e Schema ativos

- Protocol: `2` (`.forge/forge.yml: forge.protocol: 2`;
  `protocol/versions/2/specification.md`, aditivo sobre `protocol/specification.md`
  Protocol 1, que permanece autoritativo).
- Change Schema: `forge/change@2` (`manifest.yml: schema:`).
- Flow default do projeto: `standard` (`.forge/forge.yml: flows.default`),
  o mesmo usado por `CHG-0037`/`CHG-0038`/`CHG-0039`.

### Flows e onde `verification.md` é produzido

`verification` é um stage em `protocol/flows/fast.yml`,
`protocol/flows/standard.yml` e `protocol/flows/full.yml` — confirmado em
`_STAGE_FILES` (`change_scaffolding.py:30`) e nos conjuntos de arquivos
esperados por Flow em `tests/unit/test_change_scaffolding.py:54-74`
(FAST não-comportamental, FAST comportamental, STANDARD, FULL
comportamental e não-comportamental — todos incluem `verification.md`).

### Autoridade normativa

- **C-020** — Verification é obrigatória em toda Change.
- **C-068** — "Verification and Review SHOULD present outcome before
  evidence" — a base normativa direta para "Result before evidence".
- **C-067** — `protocol/artifact-structure.md` é guidance não-binding;
  conformidade a ela NÃO PODE ser tratada como condição de Gate nem
  validada por `forge validate` além do que uma revisão futura do
  Contract adicionar explicitamente. Isso delimita o non-goal desta
  Change: nenhum validador semântico novo.
- **C-069** — Planos aprovados não devem absorver silenciosamente
  descobertas de Implementation; tais descobertas pertencem a
  Verification, um Decision record, ou um re-Plan documentado — reforça
  que Verification é o lugar certo para registrar achados pós-Plan.

### Estrutura canônica atual (`protocol/artifact-structure.md` §4 "Verification")

Já declara: `## Result` como primeira seção substantiva, um dos estados
`PASS`/`FAIL`/`SKIPPED`/`NOT APPLICABLE` (`INCONCLUSIVE` explicitamente
não oferecido — sem precedente no Protocol/Contract), renderizado como
texto em negrito (não heading aninhado). Depois do Result: "a Summary (a
short table mapping `AC-xxx` to its individual result reads well here)",
depois Test Evidence e Forge Evidence, depois Compatibility/Limitations,
depois uma Conclusion curta. Essa orientação já existe desde `CHG-0016`
e não foi alterada por `CHG-0037`/`38`/`39` (nenhum deles tocou a seção
"Verification" de `artifact-structure.md`).

### Template atual do scaffold

`change_scaffolding.py:286`:
```
"verification": "## Result\n\n**PENDING**\n\n## Summary\n\nRecord verification results.\n\n## Test Evidence\n\n## Forge Evidence\n\n## Conclusion\n\n",
```
`PENDING` aqui é um placeholder de scaffold (artefato ainda não
executado), análogo ao mesmo padrão usado em `specification_review`
("Verdict\n\n**PENDING**") e `review` ("Verdict\n\n**PENDING**") — não é
um dos quatro estados finais reconhecidos e não deve ser confundido com
eles; o Result final é preenchido manualmente após a Verificação real.
Nenhuma tabela de cobertura, nenhuma seção Manual Evidence, nenhuma
seção Compatibility/Limitations combinada existe no template atual.

### Exemplo canônico atual

`examples/canonical-artifacts/verification.md` já demonstra parcialmente
a estrutura-alvo: `Result` (bold, primeira seção), `Summary` (tabela
`AC-xxx → Result`), `Test Evidence`, `Forge Evidence`, `Compatibility`,
`Conclusion`. Não demonstra: `Requirement Coverage`, `User Story
Coverage`, `Manual Evidence` distinta, `Limitations`, FAIL/SKIPPED/NOT
APPLICABLE, ou referência estruturada a `TDD-xxx` RED→GREEN.

### Código responsável pela criação do artefato

`src/forge_cli/change_scaffolding.py`: `_STAGE_FILES` mapeia o stage
`verification` para `verification.md`; `_markdown()` monta o front
matter (`_frontmatter`, inalterado) mais o corpo por artefato (dict
`sections`, linha 286); `render_scaffold()` itera os stages do Flow
canônico e escreve cada arquivo. Este é exatamente o ponto que
`CHG-0037`/`38`/`39` editaram para seus artefatos.

### Validators e schemas relacionados

Nenhum validador em `src/forge_cli/validation/__init__.py` faz parsing
de conteúdo Markdown de `verification.md`; as únicas referências a
"verification" ali são sobre `resolution_verification`, um tipo de
Review Iteration (`kind: resolution_verification`) — um conceito de
Review completamente distinto, não relacionado à estrutura do artefato
Verification. Não há schema JSON para `verification.md` (nenhum
`verification.schema.json` em `protocol/schemas/`). O único campo
estruturado é `manifest.yml: verification.status`, que usa vocabulário
minúsculo (`pending`/`passed`) — 100% dos 27 manifests reais examinados
usam `passed` no estado final; nenhum usa `failed`/`skipped`/
`not_applicable` nesse campo até hoje. Este é um vocabulário distinto do
`## Result` do Markdown (maiúsculo, `PASS`/`FAIL`/`SKIPPED`/`NOT
APPLICABLE`) — os dois não devem ser conflados nem esta Change deve
alterar o schema do manifest (fora de escopo).

`protocol/schemas/tdd-evidence.schema.json` já estrutura `red`,
`intermediate_green` (opcional) e `green` por ciclo `TDD-xxx` — este é o
mecanismo real que já registra a sequência RED→GREEN; Verification deve
referenciar `TDD-xxx` por id (como `CHG-0039/verification.md` já faz na
prática: "`TDD-001` (RED, ...) failed before... for the expected
reason... passes after") em vez de renarrar manualmente a sequência.

`protocol/schemas/traceability.schema.json` (`forge/traceability@1`)
tem `requirements` (→ `tasks`) e `acceptance` (→ ids), mas
`traceability.yml` não é produzido pelo scaffold (`_STAGE_FILES` não o
inclui) e está ausente em `CHG-0037`/`38`/`39`. Não é uma fonte viva a
integrar nesta Change — mesma decisão de escopo já tomada pelos três
precedentes.

### Documentação que descreve Verification

- `protocol/specification.md` §41 "Canonical Artifact Structure" —
  aponta para `artifact-structure.md` como a guidance completa; foi
  estendido por `CHG-0037` apenas porque introduziu um conceito novo
  (User Stories opcionais) que merecia menção no nível de Protocol.
  `CHG-0038`/`CHG-0039` não tocaram este arquivo — apenas elaboraram
  `artifact-structure.md`. Mesmo padrão se aplica aqui: elaborar
  Acceptance/Requirement Coverage dentro de Verification não introduz
  conceito novo de Protocol (já é "Result-Before-Evidence" e
  "Scanability", §2.3/§2.4), então `protocol/specification.md` não
  precisa de edição.
- `protocol/compatibility.md` — recebe uma entrada nova por Change desta
  família (`CHG-0037` seção "CHG-0037 — Specification layout...")
  confirmando ausência de impacto de compatibilidade retroativa.
  `CHG-0038`/`39` não adicionaram entrada equivalente (confirmado via
  `git show --stat`); tratarei como opcional, decidindo na Specification
  se há algo de compatibilidade genuinamente novo a registrar (não há —
  mesmo padrão "guidance evolutiva, sem novo Schema/Gate/Protocol").

### Harness Adapters

`src/forge_cli/adapters/{diagnostics,formatting,service,validation}.py`
usam `PASS`/`FAIL`/`WARN` apenas para status de Adapter doctor/validation
(`AdapterDoctorResult`, `AdapterValidationResult`) — não relacionado ao
conteúdo de `verification.md`. Um Harness Adapter projeta Flow/Contract
por referência (Protocol §34), não o conteúdo de
`artifact-structure.md`. Nenhum dos três precedentes (`CHG-0037/38/39`)
tocou código de Adapter. Nenhuma mudança de Adapter esperada aqui.

### Testes existentes

`tests/unit/test_change_scaffolding.py` cobre o conjunto de arquivos por
Flow (linhas 54-74) e tem testes focados por artefato redesenhado
(`test_render_scaffold_test_design_uses_verification_design_contract_layout`,
padrão a seguir). Nenhum teste hoje verifica o conteúdo estrutural de
`verification.md` além de sua presença no conjunto de arquivos.

### Exemplos históricos relevantes

- `CHG-0001/verification.md` — citado pela própria guidance como bom
  precedente parcial (Result mencionado cedo, embora em prosa, não bold
  isolado).
  `CHG-0015/verification.md` — citado como o caso que perdeu a
  convenção (Result ausente).
- `CHG-0039/verification.md` (mais recente) — já Result-first
  (`## Result\n\n**PASS**`), `Summary` prosa curta, `Test Evidence` com
  referência a `TDD-001` por id (não renarrado), `Forge Evidence`,
  `Compatibility/Limitations` combinado, `Conclusion` que **não**
  reivindica Completion (Strict Review pendente é declarado
  explicitamente) — bom precedente real para a seção de Limitations e
  para o non-goal "Verification PASS não implica Review PASS" (§30 do
  prompt original, já C-020/C-068 consistente).
- Nenhum `verification.md` real usa `AC-xxx` hoje — a tabela de
  Acceptance Coverage é guidance ainda não materializada em precedente
  real, mesma situação em que `CHG-0037` estava para User Stories antes
  de sua própria Implementation.

### Convenções atuais para evidência

`CHG-0039/verification.md` demonstra o padrão real já adotado:
comando + contagem resumida (`pytest ... -q: 36 passed`), não despejo de
log; referência a `forge validate`/`git diff --check` como Forge
Evidence; uma seção `Compatibility/Limitations` combinada (não duas
seções separadas) quando o conteúdo é pequeno — evidência de que a
proporcionalidade (§2.5) já é praticada e deve continuar sendo permitida
(Compatibility e Limitations podem ser uma única seção combinada quando
proporcional, não duas seções obrigatórias).

### Relação Verification ↔ Test Design/Test Strategy ↔ Requirements ↔ Acceptance ↔ Review

Já documentada por Contract/guidance existente: Test Design/Test Strategy
definem a estratégia de verificação *antes* da Implementation
(`TD-xxx`/`TDD-xxx`); Verification registra o resultado real *depois*.
`Tasks` (`CHG-0039`) já declara explicitamente "marking a Task complete
records that the work was executed; it does not mean the Requirement it
references is verified — Verification remains the Artifact responsible
for demonstrating that" — o mesmo princípio que esta Change deve
preservar e tornar operacional na estrutura do artefato (Acceptance
Coverage/Requirement Coverage exigem referência a evidência, não a um
Task concluído). Review é um artefato distinto (`## Verdict`,
`Rxxx`) que responde conformidade/qualidade/independência — Verification
não deve ser confundida com ele; `CHG-0039/verification.md` já modela
essa distinção corretamente na Conclusion.

## Compatibility Finding

Nenhum impacto de compatibilidade retroativa: `verification.md`
históricos não são reescritos (mesma decisão de `CHG-0037`/`38`/`39`);
nenhuma mudança de Protocol integer, Change Schema, ou `forge validate`
semantics. `manifest.yml: verification.status` (vocabulário
`pending`/`passed`) não é alterado.
