---
forge:
  artifact: architecture
  schema: 1
change: CHG-0048
status: complete
---

# Architecture — CHG-0048 Proportional Review Profiles

## Solution Summary

Nenhum subsistema novo é introduzido (C-032/C-033, F-010): o `profile`
é um campo de dados novo em estruturas já existentes (manifest,
policy, Flow, project-flow override), lido pelos pontos de código já
existentes que já consomem essas estruturas (`validate_project`,
`resolve_effective_flow`, as projeções de Adapter). A checagem de piso
de profile (FR-010) se integra em `validate_project`
(`src/forge_cli/validation/__init__.py:773-789`) exatamente no ponto
onde `resolve_effective_flow` já é chamado hoje para cada
`.forge/flows/*.yml` de projeto — hoje esse resultado é descartado
(só exceções são checadas); esta Change passa a inspecioná-lo.

Durante a inspeção obrigatória de Architecture existente (C-032), foi
descoberto que a Specification (pós-Specification-Review) apontava
para o schema errado para o mecanismo de "configuração efetiva de
projeto" do FR-010/FR-008 — ver DEC-001 abaixo. Corrigido nesta
Architecture antes de Plan/Implementation, evitando que o erro se
propagasse para código real.

## Architectural Goals

1. Um único mecanismo de leitura de Flow (`resolve_effective_flow`,
   já existente) serve tanto à geração de scaffold/Adapter quanto à
   nova checagem de piso — sem segundo caminho de leitura (F-011).
2. Nenhuma nova classe, engine ou serviço — `profile` é um campo de
   dados, não um subsistema.
3. O raio de mudança em `validation/__init__.py` é mínimo: uma nova
   função pura (`_validate_review_profile_floor` ou equivalente) e uma
   chamada a mais em `validate_project`, sem tocar
   `_validate_resolution_verification` nem
   `_validate_protocol2_review_provenance` (FR-007).
4. Toda mudança de Schema é localizada e revisável linha a linha; nenhum
   Schema ganha `additionalProperties: true` genérico como atalho.

## DEC-001 · Mecanismo de "configuração efetiva de projeto" para o piso de profile

**Classe**: architectural (owning_artifact: architecture, per `protocol/decision-rules.md`) · **Materialidade**: material · **Autoridade**: agent (architectural não está no piso de autoridade humana obrigatória — `_DEC_AUTHORITY_FLOOR` só exige `human` para `product`/`contract`) · **Status**: resolved · **Resolved via**: evidence

**Contexto**: A Specification, revisada após a Specification Review adversarial, apontava `protocol/schemas/project.schema.json` (`.forge/forge.yml`'s bloco `review.strict`, global, hoje um `const: true` inflexível) como o mecanismo de override de projeto para FR-010.

**Achado durante inspeção de Architecture**: `grep -rn "review" src/forge_cli/configuration/__init__.py` não retorna nenhuma ocorrência — `.forge/forge.yml`'s `review.strict` não é lido por nenhum código de CLI hoje; é um campo validado mas não consumido. Em contraste, `protocol/schemas/project-flow.schema.json` (`.forge/flows/<flow_id>.yml`, `schema: forge/project-flow@1`) já tem um objeto `review` (hoje só com `blocking`), já é por-Flow (exatamente a granularidade que FR-010 precisa — "mais rigoroso que o piso daquele Flow"), e já é ativamente mesclado com o Flow canônico por `resolve_effective_flow` (`protocol_resolution/__init__.py:66-112`), que por sua vez já é chamado por `validate_project` (`validation/__init__.py:781`) para cada arquivo de projeto encontrado.

**Decisão**: FR-008/FR-010 e RFC-0007 (Decision point 8) revisados para apontar `project-flow.schema.json` como o mecanismo real. `project.schema.json` permanece fora de escopo — nenhuma mudança nele.

**Por que autoridade agent, não human**: esta é uma decisão de qual arquivo de código/schema já existente implementa um Requirement já aprovado pelo humano (FR-010's intenção — piso não-negociável por Flow, override só para cima — não muda); é uma correção de binding técnico, não uma nova obrigação normativa. Evidência (o grep acima) precede e sustenta a decisão, consistente com C-053.

## Component Design

### 1. Contract (`protocol/versions/2/contract/engineering.md`)

C-022 e C-023 substituídos pelo texto definido em Specification FR-005 (verbatim). C-031 ganha a frase de clarificação de FR-006. Nenhuma outra rule é tocada (FR-007). `protocol/contract/engineering.md` (Protocol 1) intocado.

### 2. Flows canônicos (`protocol/flows/{fast,standard,full}.yml`)

Cada `review:` block ganha `profile: <focused|standard|strict>` como nova chave, ao lado de `required`/`strict`/`adversarial` já existentes (que passam a ser, para `fast`/`standard`, `strict: false, adversarial: false` — refletindo o profile — e para `full`, permanecem `strict: true, adversarial: true`, byte-idênticos a hoje). Isso preserva os campos existentes (nenhum consumidor que já lê `strict`/`adversarial` quebra) enquanto adiciona o campo novo que os Adapters/validação passam a preferir.

### 3. Política canônica (`protocol/versions/2/policies/review.yml`)

Ganha `profile: <...>` ao lado dos `strict`/`adversarial` de topo, espelhando o Flow correspondente — esta política já é por-projeto/Protocol, não por-Flow individual, então carrega o profile do Flow `full` como piso mais alto documentado, com nota de que o valor efetivo por Change vem do Flow file, não desta política (esta política é o piso de Protocol, não o piso de Flow).

### 4. Schemas

- `protocol/schemas/change-v2.schema.json`: `review.iterations[]`'s item schema ganha `"profile": {"enum": ["focused", "standard", "strict"]}` opcional — registrado **por Iteration**, não como um campo `review.profile` de topo. Isto é deliberado, não um esquecimento: um campo de topo seria exatamente o tipo de valor cacheado/potencialmente obsoleto que FR-012 proíbe (o profile efetivo deriva sempre de `manifest.flow.current`, nunca de um valor persistido); registrar por Iteration preserva evidência histórica precisa de qual profile se aplicava quando aquele Iteration específico ocorreu, coerente com FR-012's regra de não-invalidação retroativa.
- `protocol/schemas/policy-review-v2.schema.json`: idem (já `additionalProperties: true`, mas o campo é declarado explicitamente por clareza e para F-011).
- `protocol/schemas/project-flow.schema.json`: `review` object ganha `"profile": {"enum": [...]}` opcional, ao lado do `blocking` já existente.
- `protocol/schemas/flow.schema.json`: `review` sub-schema — `required`/`strict`/`adversarial` continuam presentes (compatibilidade com consumidores existentes), mas `strict`/`adversarial` deixam de ser `const: true` fixo e passam a `{"type": "boolean"}`; adiciona-se `"profile": {"enum": [...]}`. **Correção (Independent Strict Review Iteration 1, OBSERVATION 3)**: `strict`/`adversarial` permanecem em `required` no schema efetivamente implementado (`"required": ["required", "profile", "strict", "adversarial"]`) — mais estrito, não mais fraco, do que esta seção originalmente descrevia (que dizia que se tornariam deriváveis/não-obrigatórios); a Specification (FR-008) nunca prometeu removê-los de `required`, só relaxar seus `const`, então o texto original desta seção estava desalinhado com sua própria Specification, não com o código.
- `protocol/schemas/policy-review.schema.json` (Protocol 1): intocado.

### 5. `src/forge_cli/validation/__init__.py`

Nova função pura:

```python
_PROFILE_RANK = {"focused": 0, "standard": 1, "strict": 2}

def _validate_review_profile_floor(root: Path, path: Path, effective: dict) -> list[ValidationFinding]:
    canonical_profile = effective["canonical"]["flow"].get("review", {}).get("profile", "strict")
    project_review = effective["project"].get("review")
    if not isinstance(project_review, dict) or "profile" not in project_review:
        return []
    project_profile = project_review["profile"]
    if _PROFILE_RANK.get(project_profile, -1) < _PROFILE_RANK.get(canonical_profile, 0):
        return [_finding(root, path, f"Project Flow declares review.profile={project_profile!r}, "
                          f"weaker than the canonical floor {canonical_profile!r} for this Flow.")]
    return []
```

Chamada em `validate_project`, linha 781, capturando o retorno de `resolve_effective_flow` (hoje descartado) e passando-o à nova função. Nenhuma mudança em `_validate_resolution_verification` nem `_validate_protocol2_review_provenance` (FR-007).

FR-012 (profile por Flow efetivo) não exige nova validação — é uma propriedade de correção de implementação: qualquer código que precise do profile de uma Change (Adapter projection) SHALL sempre derivá-lo de `manifest.flow.current` no momento da leitura, nunca cachear/fixar. Não há estado a validar; é uma restrição de implementação, verificada por teste (AC-012), não por um novo Finding.

### 6. Adapters (`claude_code/projection.py`, `codex/projection.py`)

`_gate_instructions()` ganha um pequeno mapa `_REVIEW_PROFILE_INSTRUCTION = {"focused": "...", "standard": "...", "strict": "Completion requires Strict Review to pass."}` (texto exato definido em Test Strategy/Implementation, coerente com FR-002–FR-004), indexado pelo profile do Flow sendo renderizado (lido do Flow canônico efetivo, já disponível no ponto de chamada). `review_independence.py` não é tocado.

### 7. Merge Readiness (`src/forge_cli/merge_readiness/evaluator.py`)

Linha 90: string do diagnóstico `MR-004` trocada de `"STRICT REVIEW NOT READY"` para `"REVIEW NOT READY"`. Nenhuma outra linha da função muda.

### 8. Documentação

`protocol/compatibility.md` ganha uma entrada `### CHG-0048 — Proportional Review Profiles` (padrão das entradas existentes). `CHANGELOG.md` ganha entrada em `## Unreleased`. `docs/adr/00NN-proportional-review-profiles.md` — **não** é necessário como ADR separado: RFC-0007 já cumpre o papel normativo de F-008 para esta Change; um ADR adicional duplicaria, não complementaria.

## Architecture Gate

Toda Component Design acima rastreia a um FR da Specification. DEC-001 resolve a única ambiguidade de binding técnico descoberta durante a inspeção obrigatória (C-032). Nenhuma nova classe/engine/serviço foi introduzida (Architectural Goal 2). Pronta para Test Strategy.
