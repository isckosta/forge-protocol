---
forge:
  artifact: discovery
  schema: 1
change: CHG-0038
status: complete
---

# Discovery — CHG-0038 Test Design Verification Contract

## Executive Summary

`protocol/artifact-structure.md` §4 ("Test Design / Test Strategy") hoje instrui explicitamente a não redesenhar a convenção `## TDD-xxx`, citando dezesseis casos reais em `CHG-0015/test-strategy.md`. Essa mesma guidance, porém, é normativamente não vinculante (Protocol §41, Contract C-067: "Agents SHOULD follow it ... Conformance MUST NOT be a Gate condition") e já foi legitimamente sobrescrita antes: a própria seção "Specification" deste documento foi reescrita pela CHG-0037 quando a prática real evoluiu. O ponto de segurança real não é a proibição textual, mas os dois artefatos que hoje ela agrupa sob uma única forma — Test Design (FAST/STANDARD) e Test Strategy (FULL) são estágios de Flow distintos (`protocol/flows/*.yml`) e, a partir desta Change, deixam de compartilhar a mesma forma. A seção precisa ser dividida em duas entradas, não apenas editada.

## Investigation

### Autoridades do repositório

- Protocol ativo: 2 (`protocol: 2` em `.forge/forge.yml`); nenhuma mudança de Protocol integer é necessária ou proposta aqui.
- Flow default do projeto: `standard` (`.forge/forge.yml` → `flows.default`). A CHG-0038 usa STANDARD, mesma classificação da CHG-0037.
- `test_design` é `required_when: behavioral_change` em `protocol/flows/fast.yml` e `protocol/flows/standard.yml`. `protocol/flows/full.yml` não tem o estágio `test_design`; tem `test_strategy` (`required: true`), estágio separado.
- `src/forge_cli/change_scaffolding.py` é o único código que gera `test-design.md` — dicionário `_STAGE_FILES["test_design"] = ("test-design.md", "test_design")` e o template em `_markdown()`, chave `"test_design"` (linha ~191): `"## Objective\n\n...\n\n## Strategy\n\n## TDD-001 — <behavior>\n\n...\n\n## Completion Criteria\n..."`. `_frontmatter()` não tem caso especial para `test_design`; a heading cai no ramo genérico `f"# {artifact.replace('_', ' ').title()} — {change_id} {title}"`, produzindo `# Test Design — CHG-XXXX Title` — diferente do padrão `# CHG-XXXX · <Tipo>` já adotado por `intent` e `specification`.
- Nenhum validador ou parser em `src/forge_cli/` interpreta o conteúdo Markdown de `test-design.md`. `src/forge_cli/merge_readiness/evaluator.py:225` só verifica a presença da chave `test_design` no `manifest.yml` (`artifacts:` status), não o conteúdo do arquivo. Busca por `test_design`/`test-design` em `src/`, `protocol/`, `docs/` não retorna nenhum outro consumidor estrutural.
- `protocol/artifact-structure.md` é guidance não vinculante (Protocol §41; Contract C-067–C-069): "Conformance to it MUST NOT be treated as a Gate condition, and MUST NOT be validated by `forge validate`". Isso confirma que o redesenho proposto não exige nova validação semântica frágil de Markdown (alinhado à seção 27/28 do pedido original).
- Protocol §19 ("TDD exceptions") já normatiza que TDD pode ser `not_applicable`/`exception` com razão explícita — base normativa correta para a seção "Non-mechanical Validation"/"Manual Acceptance" do novo layout, sem inventar semântica nova.

### A tensão real: guidance existente contra o pedido

`protocol/artifact-structure.md:219-228` (seção atual "Test Design / Test Strategy") diz textualmente: "per-case entries as `## TDD-xxx` headings (this repository's real, stable, already-consistent convention — sixteen such cases in `CHG-0015/test-strategy.md` alone; do not redesign it)" e afirma que Test Design e Test Strategy "both keep this same shape". Comparando `.claude/skills/forge/references/artifact-structure.md` (projeção local desatualizada) com `protocol/artifact-structure.md` (fonte real), confirmei por `diff` que a projeção local está defasada nas seções Intent/Specification (não reflete CHG-0037), mas a seção Test Design/Test Strategy é idêntica nos dois — ou seja, o texto "do not redesign it" não é obsoleto; é o estado real e atual do repositório.

Isso não bloqueia a Change: C-067 é SHOULD, não MUST, e a própria seção Specification deste mesmo documento já foi reescrita quando a prática mudou (CHG-0037). A implicação correta é: (1) a Change deve reconhecer e justificar explicitamente a divergência da guidance anterior, não ignorá-la silenciosamente; (2) a seção deve ser **dividida** em "Test Design" e "Test Strategy" — porque, ao final desta Change, elas deixam de ter a mesma forma; Test Strategy (FULL) permanece com `## TDD-xxx` intocado, e nenhum caso histórico real de `test-strategy.md` é reescrito.

### Achado de compatibilidade

`test-design.md` históricos (ex.: `CHG-0037/test-design.md`, formato `## Objective` / `## Strategy` / `## TDD-001 — ...` / `## Completion Criteria`) não são reescritos — o redesenho é presentation-only e aplica-se a scaffolds novos, exatamente como a CHG-0037 fez para `specification.md`. Nenhum arquivo em `protocol/schemas/` referencia a estrutura Markdown de `test-design.md`; `manifest.yml`/`change-v2.schema.json` só carregam o status agregado do artefato.

### Testes existentes relevantes

`tests/unit/test_change_scaffolding.py` já demonstra o padrão de asserção usado pela CHG-0037 para `specification.md` (`test_render_scaffold_specification_uses_traceable_contract_layout`, `test_render_scaffold_specification_explains_optional_user_stories`) — asserções de substring sobre headings e frases-chave, não snapshot de Markdown inteiro. O mesmo padrão será seguido para `test-design.md`. `test_render_scaffold_uses_only_the_selected_flow_stages` já fixa o conjunto de arquivos por Flow/behavioral; nenhuma mudança de conjunto de arquivos é necessária (apenas o conteúdo de `test-design.md`).

### Classificação de Flow

STANDARD é suficiente e é o default do projeto: o comportamento é localizado ao renderer do scaffold, à guidance de documentação e aos testes focados — sem mudança de Protocol, Schema, Gate ou execução de Adapter. TDD se aplica ao renderer, mesma classificação da CHG-0037.
