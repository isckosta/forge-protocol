---
forge:
  artifact: review
  schema: 1
change: CHG-0025
status: pending
---

# Review — Plan Approval Semantics

## Verdict

**PENDING.** A resolução dos bloqueadores externos está preparada em
`9b71fdd815eaba8f91959d3e9521201c5e91ee5` e aguarda Strict Review
independente e fria.

A revisão anterior foi executada por subagente independente, em execução fria
e sem acesso à conversa de implementação ou a dicas sobre os defeitos. O
sujeito anterior foi `145b9743be6f29b10a332107bb421d855fa7382a`.

## Resolution scope

A resolução aceita as formas de revision previstas pelos schemas
(`revision.commit` e `revision.immutable_ref`), aceita assurance `recorded` e
`verified` mantendo `observed_by: operator`, limita o Gate de Plan ao CHG-0025
em diante e evita conversão inteira ilimitada para IDs de Change. A suíte
focada passa 37 testes; a suíte completa na cópia de resolução passa 582, com
três falhas ambientais/históricas documentadas em `verification.md`.
