---
forge:
  artifact: plan
  schema: 1
change: CHG-0043
status: approved
---

# Plan — CHG-0043 Knowledge Capture Durable Lessons

1. Em `src/forge_cli/change_scaffolding.py`, reescrever a entrada `"knowledge_capture"` do dicionário `sections` dentro de `_markdown()`, preservando exatamente as quatro headings estáveis na mesma ordem, com um callout `> **Durable Knowledge**` de abertura e guidance inline: `## What Changed` (curto, apenas contexto, não um relato arquivo-por-arquivo); `## Durable Knowledge` (a regra "isso continuará útil depois que ninguém mais estiver trabalhando nesta Change"; não duplicar Decision/Architecture/Specification/Review/Specification Drift; orientar `### K-xxx · <title>` opcional para múltiplas lições independentes citando o precedente real de `CHG-0016`, prosa curta para uma lição dominante citando `CHG-0033`/`35`/`36`; declaração explícita de que "nenhum conhecimento adicional" é uma resposta válida); `## Consequences for Future Changes` (apenas quando existirem implicações concretas); `## References` (referenciar por id, não duplicar; orientar `docs/adr/`/`docs/rfcs/` quando F-008 se aplicar; distinguir explicitamente do Forge Experience Report — `docs/experience-reporting.md` — como mecanismo separado, opt-in, que registra o que aconteceu, não o que deve ser lembrado). Adicionar caso especial em `_frontmatter()` para `artifact == "knowledge_capture"` produzindo `# {change_id} · Knowledge Capture`. Não alterar as entradas `"review"`, `"specification_review"`, `"plan"`, `"test_strategy"`, `"tasks"`.
2. Em `tests/unit/test_change_scaffolding.py`, adicionar testes focados espelhando o padrão de `CHG-0038`–`41` (TD-001 a TD-007): heading/frontmatter novo (`# CHG-XXXX · Knowledge Capture`) e ordem das quatro headings estruturais com guidance não-vazia em cada uma; guidance de `Durable Knowledge` mencionando `### K-xxx` e declarando explicitamente que ids não são obrigatórios; guidance distinguindo Decision/Architecture/Specification/Review/Specification Drift; guidance mencionando o Forge Experience Report como mecanismo distinto; guidance de `References` mencionando `docs/adr/`; guidance declarando que "nenhum conhecimento adicional" é uma resposta válida; e um teste de proteção de igualdade de string completa para `review.md`/`specification-review.md`/`plan.md`/`test-strategy.md`/`tasks.md` permanecerem inalterados (gerado a partir de um scaffold FULL).
3. Em `protocol/artifact-structure.md` §4, reescrever a entrada "Knowledge Capture" (mantendo `**Structural core (elaborated by `CHG-0043`):**` como abertura, no mesmo padrão retórico de Verification/Review/Test Design/Tasks/Specification Drift) para descrever a estrutura elaborada, deixando explícito: (a) as quatro seções permanecem exatamente as mesmas, na mesma ordem — isto elabora, não substitui, a guidance anterior; (b) a distinção de Decision/Architecture/Specification/Review/Specification Drift; (c) a relação real com F-008 (ADR/RFC já produzidos como parte do próprio trabalho, referenciados aqui — não uma "promoção" mecânica inventada); (d) a distinção com o Forge Experience Report; (e) que um Knowledge Capture vazio/honesto é válido; (f) que `### K-xxx` é opcional, sem consumidor real hoje, citando `CHG-0016` como precedente do padrão multi-lição sem IDs formais.
4. Em `CHANGELOG.md`, adicionar entrada sob `## Unreleased` seguindo o formato das seis entradas anteriores desta mesma família, com a afirmação explícita de que os 25 `knowledge-capture.md` reais permanecem inalterados, Decision/Architecture/Specification/Review/Specification-Drift/FER mechanics inalterados, e nenhuma obrigação normativa nova foi introduzida.
5. Capturar RED em `tdd-evidence.yml` desta própria Change (`TDD-001`, agrupando TD-001–TD-007) rodando `pytest tests/unit/test_change_scaffolding.py -k knowledge -q` contra o renderer ainda não alterado, confirmando falha pela razão esperada, antes de aplicar o item 1.
6. Após GREEN, executar `pytest tests/unit/test_change_scaffolding.py -q`, a suíte completa (`pytest -q`), `forge validate`, e `git diff --check`; inspecionar o diff final confirmando que nenhum arquivo sob `protocol/schemas/`, nenhum Protocol integer, e nenhum `knowledge-capture.md` histórico foi alterado.
7. Preencher `verification.md` desta própria Change (dogfooding, mesmo padrão de `CHG-0038`–`42`) usando o layout já redesenhado por `CHG-0040`, com `Result`, `Acceptance Coverage` referenciando AC-001–AC-007, `Test Evidence` referenciando o `TDD-xxx` capturado no item 5, `Forge Evidence`, `Compatibility and Limitations`, e `Conclusion` — sujeito a Strict Review independente antes de Completion.
8. Abrir a PR diretamente contra `main` (não empilhar sobre outra branch de Change), com merge commit regular (não squash — commits referenciados em `provenance.yml` precisam permanecer alcançáveis), aguardar checks, endereçar qualquer finding de review automatizado antes de mergear, e obter uma iteração de Strict Review independente antes de fechar a Change.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou a continuação na sessão ativa em 2026-08-24, escolhendo explicitamente "Aprovar como está" sobre a Specification's 7 Functional Requirements e os 8 itens deste Plan.

<!-- forge:plan-approval-record -->
