---
forge:
  artifact: discovery
  schema: 1
change: CHG-0052
status: complete
---

# Discovery — CHG-0052 Investigate Capability

## Executive Summary

O achado mais forte é negativo, e é o achado correto para esta Change:
não existe nenhuma incompatibilidade entre o que `investigate` precisa
dizer e o que `capabilities/capability.md` já permite dizer. `ADR-0019`
(a própria decisão que fechou `CHG-0047`) já antecipa textualmente este
Change — "A future Change can introduce `investigate` as
`capabilities/investigate/CAPABILITY.md` and load it with the existing,
unmodified loader — no redesign of this foundation is required." O
loader (`src/forge_cli/capabilities/loader.py`) e o modelo
(`src/forge_cli/capabilities/model.py`) são genéricos por desenho: nada
neles nomeia ou trata `investigate` de forma especial, e nenhuma mudança
de código é necessária para carregá-lo. A implicação é que esta Change é
puramente de conteúdo (uma definição de competência) mais teste — não há
decisão arquitetural em aberto para levar ao Plan.

## Investigation

### O contrato existente já cobre o formato de `investigate`

`capabilities/capability.md` exige frontmatter mínimo (`capability`,
`schema`) e sete seções `##` não vazias (Identity, Purpose,
Applicability, Inputs, Behavior, Outputs, Evidence Expectations), em
qualquer ordem, sem schema JSON. Nenhuma seção nova é necessária para
expressar "problem → establish facts → reproduce → evidence → competing
hypotheses → test → isolate root cause → conclusion": esse fluxo cabe
inteiramente em `## Behavior`, os artefatos observáveis (`Problem`,
`Observations`, `Reproduction Status`, `Evidence`, `Hypotheses
Evaluated`, `Root Cause`, `Uncertainty`, `Recommended Next Action`) cabem
em `## Outputs`, e a distinção `CONFIRMED` / `INFERRED` / `UNKNOWN` cabe
em `## Evidence Expectations`. Nenhum campo de frontmatter além de
`capability`/`schema` é parseado pelo loader (`_FRONTMATTER_PATTERN` +
leitura direta de `frontmatter.get("capability")` /
`frontmatter.get("schema")`), então não há tentação de inventar um campo
extra (ex.: um campo de "status" de investigação) — isso pertenceria a
evidência repository-native (Change Artifacts), não à definição da
Capability.

### O loader é genérico e não precisa de tratamento especial

Lido integralmente (`loader.py:37-116`): `load_capability` localiza o
arquivo, extrai frontmatter via regex, valida `capability`
(string não vazia) e `schema` (int), e então corre `_parse_sections`,
que percorre o corpo linha a linha rastreando estado de fence (tipo de
delimitador `` ` `` vs `~` e comprimento) para não confundir uma
heading-shaped line dentro de um bloco de código com uma seção real —
esse rastreamento existe justamente para que texto de exemplo dentro de
`## Behavior` (por exemplo, um bloco ilustrando
`ROOT CAUSE CONFIRMED` / `ROOT CAUSE NOT ESTABLISHED`) não seja
mal-interpretado como uma nova seção. Nenhuma branch do loader depende
do valor de `capability:` — `investigate` percorre exatamente o mesmo
caminho que qualquer outro id.

### Teste real já existe para o loader genérico; falta o teste do arquivo real

`tests/capabilities/test_loader.py` e `test_model.py` já testam o
loader/model de forma completamente genérica, usando arquivos sintéticos
em `tmp_path` — nenhum deles carrega um `CAPABILITY.md` real do
repositório. Não existe hoje nenhum teste que exercite
`capabilities/capability.md` em si nem (obviamente)
`capabilities/investigate/CAPABILITY.md`, porque este último ainda não
existe. Isso confirma o gap de TDD real desta Change: um teste que
chama `load_capability(Path("capabilities/investigate/CAPABILITY.md"))`
falha hoje (`CapabilityDefinitionError`, arquivo inexistente) e deve
passar depois que o arquivo for escrito — sem qualquer mudança em
`loader.py`/`model.py`.

### Nenhum registry, executor ou discovery automático existe para colidir

Busca por `CapabilityRegistry`, `CapabilityExecutor` e `investigate` em
`src/`, `capabilities/` e `.claude/skills/forge/` não retorna nenhuma
ocorrência de código — apenas menções em prosa (`README.md`,
`docs/adr/0019-...md`) antecipando este Change exatamente como
especificado. Não há `/investigate`, `SKILL.md` de `investigate`, nem
qualquer adapter wiring hoje; nada precisa ser removido ou desfeito para
manter os Architectural boundaries do Goal.

### Classificação de Flow

STANDARD é suficiente e é o Flow adotado pelo scaffold. O trabalho é
localizado a um novo diretório de documentação
(`capabilities/investigate/`) e a testes focados
(`tests/capabilities/test_investigate_capability.py`); não há mudança de
Protocol integer, Schema, Gate, `capabilities/README.md`, ou
`capabilities/capability.md`. TDD se aplica de forma limitada: o
comportamento testável é "o loader existente carrega este arquivo real
e produz um `Capability` cujo conteúdo satisfaz invariantes estruturais
verificáveis" — não há justificativa para testar prosa palavra-por-
palavra (isso congelaria texto, não comportamento), então os casos de
teste focam em invariantes estruturais e arquiteturais (frontmatter,
presença/consistência das seções, ausência de vocabulário de Harness ou
de artifact/Gate/Flow novo, presença dos marcadores de conclusão
`ROOT CAUSE CONFIRMED` / `ROOT CAUSE NOT ESTABLISHED` e de
`CONFIRMED`/`INFERRED`/`UNKNOWN`).
