---
forge:
  artifact: plan
  schema: 1
change: CHG-0042
status: approved
---

# Plan — CHG-0042 Specification Drift Narrative Chronology

1. Em `protocol/artifact-structure.md` §4, reescrever a entrada "Specification Drift" (mantendo `**Structural core (elaborated by `CHG-0042`):**` como abertura, no mesmo padrão retórico de Verification/Review/Test Design/Tasks) para descrever a sequência cronológica completa — `Context`, `Trigger`, `Original Specification`, `Observed Conflict`, `Root Cause`, `Evidence`, `Specification Correction`, `Impact Assessment`, `Affected Artifacts`, `Re-verification`, `## Final decision` (grafia real preservada, minúscula, por último) — deixando explícito: (a) esta é uma exceção deliberada a Result-Before-Evidence (C-068), não sua aplicação; (b) o boundary de materialidade entre Specification Review e Specification Drift, citando `CHG-0013` como precedente real; (c) a distinção entre Resolution, Decision, e Specification Drift, citando `CHG-0012` como precedente real; (d) que a correção deve ser aplicada a `specification.md`, não apenas registrada aqui (evitar Duplicate Authority); (e) que um `Final decision` não deve ser fabricado quando a escolha normativa ainda não foi feita; (f) proporcionalidade — nem toda seção é exigida em toda ocorrência; (g) que este artefato não tem scaffold, stage de Flow, ou schema associado, e esta Change não introduz nenhum.
2. Em `CHANGELOG.md`, adicionar entrada sob `## Unreleased` seguindo o formato das cinco entradas anteriores desta mesma família, com a afirmação explícita de que os quatro `specification-drift.md` reais permanecem inalterados, nenhum código-fonte foi tocado, e nenhuma obrigação normativa nova foi introduzida.
3. Preencher `verification.md` desta própria Change confirmando, por inspeção, que a guidance elaborada cobre as sete Acceptance Criteria da Specification (AC-001–AC-007), que nenhum `specification-drift.md` histórico foi alterado (`git diff` restrito a `protocol/artifact-structure.md` e `CHANGELOG.md`), e que `forge validate` permanece verde — sujeito a Strict Review independente antes de Completion.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.

## Human Plan Authorization

Este Plan é explicitamente autorizado pelo mantenedor humano para avançar à Implementation sob C-077.

<!-- forge:plan-approval-confirmation -->

O usuário aprovou a continuação na sessão ativa em 2026-08-24, escolhendo explicitamente "Aprovar como está" sobre a Specification's 7 Functional Requirements e os 3 itens deste Plan.

<!-- forge:plan-approval-record -->
