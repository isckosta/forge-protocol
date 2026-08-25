---
forge:
  artifact: discovery
  schema: 1
change: CHG-0047
status: complete
---

# Discovery — CHG-0047 Capability Architecture Foundation

## Executive Summary

Nenhuma abstração de "Forge Capability" existe hoje no repositório — nem no Protocol, nem no Engineering Contract, nem no CLI. O achado mais importante desta Discovery é um risco de nome, não um risco técnico: `src/forge_cli/adapters/capabilities.py` já existe e define `CapabilityRequirement`/`CapabilityLimitation` — um conceito completamente diferente ("o Harness declara que suporta a feature X, e o Forge relata a limitação quando não suporta"). Não há colisão de import (`forge_cli.capabilities` é um pacote novo em `src/forge_cli/capabilities/`, distinto de `forge_cli.adapters.capabilities`), mas há colisão semântica de vocabulário que a documentação desta Change precisa desambiguar explicitamente, para que um leitor futuro não confunda "Harness capability" (feature flag de ambiente) com "Forge Capability" (competência agentic especializada). A segunda constatação relevante é que o padrão determinístico de carregamento já existe no repositório (`resolve_protocol_root` em `protocol_resources.py`: localizar → ler, com fallback empacotado/source-tree) e deve informar, sem ser copiado literalmente, o design do novo `loader.py` — com uma diferença material: `protocol/` é conteúdo do próprio produto Forge e é empacotado no wheel (`pyproject.toml` → `force-include`), enquanto `capabilities/<nome>/CAPABILITY.md` é conteúdo repository-native de um Forge-enabled repository concreto (o próprio `forge-protocol` neste caso, ou qualquer outro), lido diretamente do working tree — não precisa, e não deve, ser empacotado.

## Investigation

### Ausência do conceito no Protocol e no Contract

Busca por `capability`/`Capability` em `protocol/` e nos 77 Contract rules (`C-001`–`C-077`) não retorna nenhuma ocorrência normativa relacionada a competências agentic. O Protocol e o Contract definem Flow, Gates, TDD, Review, Provenance e Decisions — nenhum desses conceitos hoje conhece "capability". Isso confirma que esta Change pode introduzir o conceito sem tocar `protocol/` nem `.claude/skills/forge/references/engineering-contract.md`: a camada de Capability é aditiva, não uma reinterpretação de uma obrigação existente.

### Colisão de vocabulário com `src/forge_cli/adapters/capabilities.py`

`src/forge_cli/adapters/capabilities.py` define `RequirementSource`, `CapabilityRequirement`, `CapabilityLimitation` e `evaluate_capability_requirements(...)` — usado por `adapters/assessment.py`, `adapters/validation.py`, `adapters/planner.py`, `adapters/codex/driver.py`. Esse módulo responde a uma pergunta diferente: "este Harness concreto declara suportar a feature X (ex.: subagents, hooks)? Se não, registre uma limitação." Não há sobreposição de responsabilidade com a Forge Capability desta Change (uma competência agentic reutilizável como `investigate`), mas o nome `capabilities` já está em uso no namespace `forge_cli.adapters`. `capabilities/README.md` (a documentação canônica) precisa declarar essa distinção explicitamente na seção "o que não é", e o novo pacote vive em `src/forge_cli/capabilities/` (irmão de `adapters/`, não dentro dele), evitando qualquer colisão de import real.

### Padrão de carregamento determinístico já existente

`src/forge_cli/protocol_resources.py::resolve_protocol_root` demonstra o único precedente real de "localizar conteúdo canônico com fallback determinístico" no repositório: prefere `package_root/resources/protocol` (empacotado), cai para `source_protocol` (árvore de desenvolvimento), e lança `ProtocolResourcesUnavailableError` se nenhum existir. Esse padrão resolve um problema que a Capability *não* tem: `protocol/` é conteúdo do próprio produto Forge, precisa existir tanto instalado via pip quanto em desenvolvimento. Uma definição de capability (`capabilities/<nome>/CAPABILITY.md`) é conteúdo repository-native do repositório Forge-governed onde ela é usada — não precisa de fallback empacotado. O `loader.py` desta Change, portanto, recebe um `Path` explícito (o caminho do `CAPABILITY.md`, ou futuramente o diretório de capabilities de um projeto) e não introduz lógica de resolução de pacote — mais simples que `resolve_protocol_root`, por não ter o mesmo problema a resolver.

`pyproject.toml` confirma: `[tool.hatch.build.targets.wheel.force-include]` só empacota `protocol` → `forge_cli/resources/protocol`. Nenhuma mudança em `pyproject.toml` é necessária para esta Change — `capabilities/` (a documentação canônica em `forge-protocol`) não precisa ser distribuída dentro do wheel do CLI, pelo mesmo motivo que `.forge/changes/` do próprio `forge-protocol` não é.

### Precedente de modelo mínimo com dataclass congelado

`CapabilityRequirement`/`CapabilityLimitation` (`adapters/capabilities.py`) e `CapabilityEvidence` (`adapters/claude_code/evidence.py`) já demonstram o padrão real e estável deste repositório para "modelo mínimo carregado de um arquivo": `@dataclass(frozen=True)` simples, sem hierarquia de classes, sem builder, sem registry. `parse_claude_code_capability_evidence` (`adapters/claude_code/evidence.py`) é o precedente mais próximo de "parse determinístico de um formato de arquivo simples para uma lista de dataclasses imutáveis", incluindo suas próprias mensagens de erro explícitas por campo ausente/inválido — o mesmo padrão de honestidade de erro (falhar com mensagem específica, não silenciosamente) deve informar `loader.py`.

### Convenção de frontmatter já estabelecida

Todo artefato Markdown de Change usa um bloco `forge:` YAML no topo (`artifact`, `schema`, `change`, `status` — `protocol/artifact-structure.md` §1). Não existe, porém, nenhum precedente de frontmatter para um arquivo que não é um artefato de Change — `CAPABILITY.md` é um novo tipo de documento repository-native, não um artefato de Change (não tem `change:` nem `status:` de lifecycle). Um frontmatter mínimo e disjunto (`capability:` identidade, `schema:` inteiro) mantém o parsing determinístico sem herdar campos de Change que não se aplicam a uma Capability (que não tem `status: active/complete` de lifecycle — Capability não possui lifecycle próprio, por desenho explícito do pedido original).

### Ausência de qualquer registry, executor ou catálogo hoje

Busca por `registry`, `plugin`, `marketplace` em `src/forge_cli/` retorna apenas `adapters/registry.py` (um registry de Harness Adapters empacotados — `codex`, `claude-code` — não relacionado a capabilities de domínio) e nada relacionado a execução de competências agentic. Não há hoje nenhum mecanismo que esta Change precise integrar, estender ou romper — confirma que a fundação pode ser puramente aditiva.

### Classificação de Flow

STANDARD é suficiente (já é o Flow do scaffold gerado para CHG-0047) e é o default do projeto: o comportamento é localizado a dois novos artefatos de documentação, um pacote Python novo e pequeno (`model.py`, `loader.py`), e os testes focados correspondentes — sem mudança de Protocol integer, Schema, Gate, ou execução de Harness Adapter. TDD se aplica ao `loader.py` (comportamento determinístico e testável) e, de forma mais limitada, ao `model.py` (estrutura de dados, mas com invariantes verificáveis — imutabilidade, presença de campos).
