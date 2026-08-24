---
forge:
  artifact: discovery
  schema: 1
change: CHG-0039
status: complete
---

# Discovery — CHG-0039 Tasks Layout Plan Grouping Traceability

## Executive Summary

`protocol/artifact-structure.md` §4 ("Tasks") hoje descreve, corretamente, o estado real e estável do artefato: "a checklist (`- [ ] T-xxx <work>`) referencing the Plan items it executes, and a closing `## Status` section". Essa guidance é não vinculante (Protocol §41, Contract C-067) e já foi legitimamente superada duas vezes na mesma direção — Specification (CHG-0037) e Test Design (CHG-0038) — quando a prática real precisou evoluir. O mesmo padrão se aplica aqui: a forma plana atual não está errada, mas não escala para um Plan com múltiplos itens, e o redesenho deve evoluir a estrutura existente (agrupamento por Plan, referências compactas), não substituí-la por um modelo incompatível.

## Investigation

### Autoridades do repositório

- Protocol ativo: 2 (`protocol: 2` em `.forge/forge.yml`); nenhuma mudança de Protocol integer é necessária ou proposta.
- Flow default do projeto: `standard` (`.forge/forge.yml` → `flows.default`). Mesma classificação usada por CHG-0037 e CHG-0038.
- `tasks` só existe como estágio no Flow FULL (`protocol/flows/full.yml`); FAST e STANDARD não têm o estágio `tasks`. Confirmado por `tests/unit/test_change_scaffolding.py::test_render_scaffold_uses_only_the_selected_flow_stages`: o conjunto de arquivos esperado para `full`/behavioral e `full`/não-behavioral inclui `tasks.md`; `standard` e `fast` não o incluem. Confirmado também pelo fato real de que `CHG-0037` e `CHG-0038` (ambos STANDARD) não têm `tasks.md` em seus diretórios.
- `src/forge_cli/change_scaffolding.py` é o único código que gera `tasks.md`: `_STAGE_FILES["tasks"] = ("tasks.md", "tasks")` e, em `_markdown()`, a chave `"tasks"`: `"- [ ] T-001 <work item>\n\n## Status\n\nNo task has started.\n"`. `_frontmatter()` não tem caso especial para `tasks`; a heading cai no ramo genérico `f"# {artifact.replace('_', ' ').title()} — {change_id} {title}"`, produzindo `# Tasks — CHG-XXXX Title` — diferente do padrão `# CHG-XXXX · <Tipo>` já adotado por `intent`, `specification` e `test_design`.
- Nenhum validador ou parser em `src/forge_cli/` interpreta o conteúdo Markdown de `tasks.md`. Busca por `tasks.md`/`tasks_ready`/referência ao artefato `tasks` em `src/forge_cli/` só encontra: (1) `change_scaffolding.py` (geração do arquivo); (2) `validation/__init__.py:396`, `_DEC_OWNING_BY_CLASS` — classificação de qual Decision `class` (`technical`) uma Decision pertencente a `plan`/`tasks` usa, não relacionado ao conteúdo de `tasks.md`. Nenhum outro consumidor programático depende de headings, IDs ou formato atual de `tasks.md`.
- `protocol/artifact-structure.md` é guidance não vinculante (Protocol §41; Contract C-067–C-069): "Conformance to it MUST NOT be treated as a Gate condition, and MUST NOT be validated by `forge validate`". Confirma que o redesenho não exige, e não deve introduzir, validação semântica frágil de referências (`Plan:`/`Requirements:`/`Stories:`/`Test Design:`) — alinhado à seção 25 do pedido original.
- `examples/canonical-artifacts/` cobre apenas Intent, Verification e Review (`README.md`); nenhum `tasks.md` ilustrativo foi adicionado por CHG-0037 ou CHG-0038 para os artefatos que redesenharam (Specification, Test Design). Precedente direto para não fabricar aqui um exemplo de domínio completo (ex.: ERP) como artefato real do repositório — a Change CHG-0038 removeu explicitamente esse item do próprio escopo na aprovação humana do seu Plan (`CHG-0038/plan.md`, item 4: "com a ressalva explícita de remover o item do exemplo de domínio ERP ... do escopo desta Change"). Um exemplo de domínio permanece válido apenas como ilustração dentro da prosa de `protocol/artifact-structure.md`, não como scaffold ou diretório novo.

### Relação com CHG-0037 (User Stories) e CHG-0038 (Test Design)

- CHG-0037 introduziu `US-xxx` (User Stories) como seção condicional da Specification. CHG-0038 introduziu `TD-xxx` como convenção real de cenário de Test Design (Flow FAST/STANDARD) — distinta de `TDD-xxx`, que continua sendo a convenção real e intocada do Test Strategy (Flow FULL, `## TDD-xxx`, dezesseis casos reais em `CHG-0015/test-strategy.md`). Como Tasks só existe em Flow FULL, e Flow FULL usa Test Strategy (não Test Design), a referência opcional de rastreabilidade correta em `tasks.md` é a `Test Design:` mencionada no pedido original — mas a convenção de ID real que uma Task de Flow FULL encontraria no seu próprio Change é `TDD-xxx` (Test Strategy), não `TD-xxx` (que só existe em Changes FAST/STANDARD). O template deve, portanto, usar `TDD-xxx` no rótulo de exemplo de rastreabilidade a Test Design/Test Strategy, refletindo a convenção real que uma Change FULL de fato produz, evitando inventar uma nova convenção sem autoridade normativa (seção 17 do pedido original).
- Nenhuma das duas Changes anteriores tocou `tasks.md`; não há dependência de código entre esta Change e elas além do arquivo comum (`change_scaffolding.py`, chaves de dicionário distintas).

### Achado de compatibilidade

`tasks.md` históricos (`CHG-0015`, `CHG-0016`, e qualquer outro Flow FULL já completo) não são reescritos — o redesenho é presentation-only e aplica-se a scaffolds novos, exatamente como CHG-0037 e CHG-0038 fizeram. Nenhum arquivo em `protocol/schemas/` referencia a estrutura Markdown de `tasks.md`; `manifest.yml`/`change-v2.schema.json` só carregam o status agregado do artefato (`artifacts.tasks`).

### Testes existentes relevantes

`tests/unit/test_change_scaffolding.py` já demonstra o padrão de asserção usado por CHG-0037 (`test_render_scaffold_specification_uses_traceable_contract_layout`, `test_render_scaffold_specification_explains_optional_user_stories`) e por CHG-0038 (asserções análogas para `test_design`) — asserções de substring sobre headings e frases-chave, não snapshot de Markdown inteiro. O mesmo padrão será seguido para `tasks`. `test_render_scaffold_uses_only_the_selected_flow_stages` já fixa o conjunto de arquivos por Flow/behavioral; nenhuma mudança de conjunto de arquivos é necessária (apenas o conteúdo de `tasks.md`, gerado apenas quando `flow_id == "full"`).

### Classificação de Flow

STANDARD é suficiente e é o default do projeto: o comportamento é localizado ao renderer do scaffold, à guidance de documentação e aos testes focados — sem mudança de Protocol, Schema, Gate ou execução de Adapter. TDD se aplica ao renderer, mesma classificação de CHG-0037 e CHG-0038.
