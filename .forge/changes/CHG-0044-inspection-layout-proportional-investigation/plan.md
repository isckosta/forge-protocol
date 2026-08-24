---
forge:
  artifact: plan
  schema: 1
change: CHG-0044
status: approved
---

# Plan — CHG-0044 Inspection Layout Proportional Investigation

1. Em `src/forge_cli/change_scaffolding.py`, adicionar um caso especial em
   `_frontmatter()` para `artifact == "inspection"` produzindo
   `# {change_id} · Inspection` (mesmo padrão já usado para
   `specification`/`test_design`/`tasks`/`verification`/`review`/
   `knowledge_capture`), removendo o fallback genérico para este
   artefato. Reescrever a entrada `"inspection"` do dicionário `sections`
   dentro de `_markdown()`, substituindo `"## Inspection\n\nRecord the
   relevant inspection findings.\n"` por um comentário de orientação de
   autoria sem heading `##` (ex.: `<!-- Describe only what the
   investigation materially requires. Optional structural vocabulary
   (Observation, Evidence, Root Cause, Impact, Fix Boundary, Open
   Question, Conclusion) is available in protocol/artifact-structure.md
   when the investigation genuinely needs it. -->`). Não alterar
   nenhuma outra entrada de `sections` nem o `_STAGE_FILES["inspection"]`.
2. Em `tests/unit/test_change_scaffolding.py`, adicionar testes focados
   espelhando o padrão de `CHG-0038`–`43` (TD-001, TD-002, TD-008): (a)
   nenhuma linha do `inspection.md` gerado começa com `## `; (b) o
   `inspection.md` gerado começa com o front matter inalterado seguido
   de `# CHG-XXXX · Inspection`; (c) um teste de proteção de igualdade
   de string completa para `intent.md`/`test-design.md`/
   `tdd-evidence.yml`/`verification.md`/`review.md` permanecerem
   inalterados (gerado a partir de um scaffold FAST).
3. Em `protocol/artifact-structure.md` §4, reescrever a entrada
   "Inspection" (mantendo `**Structural core (elaborated by
   `CHG-0044`):**` como abertura, no mesmo padrão retórico de
   Verification/Review/Test Design/Tasks/Knowledge Capture) preservando
   integralmente a frase central de proportionality já existente, e
   adicionando: (a) o vocabulário estrutural opcional de sete termos
   (`Observation`, `Evidence`, `Root Cause`, `Impact`, `Fix Boundary`,
   `Open Question`, `Conclusion`) com pelo menos um exemplo real citado
   por termo quando existir precedente; (b) a distinção `Observed
   behavior` vs. `Root Cause` confirmada, com "Likely cause" para causa
   não confirmada; (c) o modelo de evidência `Symptom → Reproduction →
   Cause` com um exemplo curto; (d) a distinção de uma frase cada com
   Discovery, Specification, Plan, Verification, e o Forge Experience
   Report, nomeando o mecanismo real de escalada de Flow
   (`fast.yml`/`protocol/specification.md` §11) sem inventar um novo; (e)
   a correção da descrição de `CHG-0005/inspection.md` (não é "title
   only" — duas frases de contexto reais).
4. Em `CHANGELOG.md`, adicionar entrada sob `## Unreleased` seguindo o
   formato das sete entradas anteriores desta mesma família, com a
   afirmação explícita de que os seis `inspection.md` reais permanecem
   inalterados, Discovery/Specification/Plan/Verification/FER mechanics
   inalterados, e nenhuma obrigação normativa nova foi introduzida.
5. Capturar RED em `tdd-evidence.yml` desta própria Change (`TDD-001`,
   agrupando TD-001, TD-002, TD-008) rodando `pytest
   tests/unit/test_change_scaffolding.py -k inspection -q` contra o
   renderer ainda não alterado, confirmando falha pela razão esperada,
   antes de aplicar o item 1.
6. Após GREEN, executar `pytest tests/unit/test_change_scaffolding.py -q`,
   a suíte completa (`pytest -q`), `forge validate`, e `git diff
   --check`; inspecionar o diff final confirmando que nenhum arquivo sob
   `protocol/schemas/`, nenhum Protocol integer, e nenhum
   `inspection.md` histórico foi alterado.
7. Preencher `verification.md` desta própria Change (dogfooding, mesmo
   padrão de `CHG-0038`–`43`) usando o layout já redesenhado por
   `CHG-0040`, com `Result`, `Acceptance Coverage` referenciando
   AC-001–AC-008 (AC-003–AC-007 com Manual Evidence, distinta de Test
   Evidence), `Test Evidence` referenciando o `TDD-xxx` capturado no
   item 5, `Forge Evidence`, `Compatibility and Limitations`, e
   `Conclusion` — sujeito a Strict Review independente antes de
   Completion.
8. Abrir a PR diretamente contra `main` (não empilhar sobre outra branch
   de Change), com merge commit regular (não squash — commits
   referenciados em `provenance.yml` precisam permanecer alcançáveis),
   aguardar checks, endereçar qualquer finding de review automatizado
   antes de mergear, e obter uma iteração de Strict Review independente
   antes de fechar a Change.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar
à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou a continuação na sessão ativa em 2026-08-24, escolhendo
explicitamente "Aprovar como está" sobre a Specification's 8 Functional
Requirements e os 8 itens deste Plan.

<!-- forge:plan-approval-record -->
