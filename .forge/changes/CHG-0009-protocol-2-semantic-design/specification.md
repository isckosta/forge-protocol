---
forge:
  artifact: specification
  schema: 1
change: CHG-0009
status: complete
---

# Specification — Protocol 2 Semantic Design and Compatibility Boundary

## 1. Normative purpose

This Change is an analysis and design boundary. It MUST NOT implement a new Protocol, broaden Protocol 2 silently, fabricate historical evidence, or convert candidate invalidation rules into executable lifecycle behavior.

The repository state supersedes the original assumption that Protocol 2 does not yet exist. Protocol 2 already has a published review-independence meaning. Therefore conclusions are expressed against Protocol 1, existing Protocol 2, and a non-reserved **Future Protocol** boundary for any additional breaking semantics.

## 2. Compatibility classification vocabulary

- **CLARIFICATION** — makes an already unavoidable obligation more explicit without increasing the minimum state, evidence, lifecycle, or behavior required from any conforming instance.
- **COMPATIBLE_STRENGTHENING** — improves enforcement, diagnostics, precision, or recommended practice while preserving every instance that was valid under the same integer Protocol. It MUST NOT create a new mandatory absence/failure condition for historical conforming instances.
- **OPTIONAL_CAPABILITY** — introduces a new representational or operational facility whose absence preserves existing meaning and conformance.
- **NEW_MANDATORY_OBLIGATION** — requires state, evidence, analysis, artifact content, or behavior that a currently conforming instance may legitimately lack. It cannot be imposed retroactively under the same integer Protocol.
- **BREAKING_SEMANTIC_CHANGE** — changes the meaning or validity of an existing required field, Gate, lifecycle result, Protocol decision, or conforming instance. A new integer Protocol identifier is required.

Classification is semantic, not editorial. A desirable rule is not compatible merely because it improves quality.

## 3. Compatibility Classification Matrix

| Proposal | Classification | Protocol 1 conclusion | Existing Protocol 2 conclusion | Primary reason |
|---|---|---|---|---|
| C-047 Material claims require evidence | NEW_MANDATORY_OBLIGATION | Not compatible as universal MUST | Not already universal | P1/P2 require evidence in bounded areas, not for every material claim |
| C-048 Self-attestation is insufficient | BREAKING_SEMANTIC_CHANGE | Explicitly incompatible | Partially true for P2 Strict Review only | P1 compatibility expressly permits conceptual separation without independent provenance |
| C-049 Evidence must bind to its subject | BREAKING_SEMANTIC_CHANGE | Not generic today | Established for P2 Strict Review, not all evidence | Universal subject binding changes acceptance semantics |
| C-050 Gate results are revision-bound | BREAKING_SEMANTIC_CHANGE | Not generic today | Strict Review is revision-bound; other Gates are not generically bound | Changes meaning and persistence of PASS |
| C-051 Material mutation invalidates affected downstream Gates | BREAKING_SEMANTIC_CHANGE | Not generic today | Not generic today | Previously accepted PASS could become invalid after mutation |
| C-052 Higher normative authority prevails | CLARIFICATION | Compatible | Compatible | Already follows canonical configuration and Adapter/Harness precedence rules |
| C-053 Material scope expansion must be explicit | CLARIFICATION | Compatible if implemented as escalation/drift/scope recording, not a new required field | Compatible | C-005/C-006 and Specification Drift already forbid silent semantic expansion |
| C-054 Unrelated work does not belong to the Change | COMPATIBLE_STRENGTHENING | Compatible as scope discipline/policy, not as retroactive hard Gate | Compatible | Change/Intent semantics support discipline, but no universal hard rejection currently exists |
| C-055 Material assumptions are explicit | NEW_MANDATORY_OBLIGATION | Not compatible as universal MUST | Not already universal | Existing instances need not contain an assumption inventory |
| C-056 Unknowns must not masquerade as facts | CLARIFICATION | Compatible | Compatible | Follows repository truth, explicit trade-offs, and truthful Completion |
| C-057 Irreversible operations require explicit safety analysis | NEW_MANDATORY_OBLIGATION | Not compatible as universal MUST | Not already universal | Introduces mandatory analysis that historical valid Changes may lack |
| C-058 Process completion is not proof of correctness | CLARIFICATION | Compatible | Compatible | C-021 and Verification semantics already reject tests/process as automatic proof |
| C-059 Confidence must follow evidence | COMPATIBLE_STRENGTHENING | Compatible as principle/diagnostic; not as mandatory score/schema | Compatible | C-040 and C-021 support evidence-calibrated confidence without a new required field |

## 4. Per-proposal semantic analysis

### C-047 — Material claims require evidence

Current Protocol already requires evidence for valid RED and material Review Findings and rejects passing tests as automatic proof. It does not define `claim`, `material claim`, or a universal evidence obligation. Making evidence mandatory for all material lifecycle assertions could require new provenance or artifacts and could reject historically conforming Changes. It therefore requires a new Protocol boundary if normative and universal. An optional claim/evidence model MAY be introduced under existing Protocols if its absence has no conformance effect.

### C-048 — Self-attestation is insufficient

For Protocol 1 this is directly breaking: compatibility explicitly states that P1 does not retroactively require independent Execution/Context IDs or revision-bound provenance. Existing Protocol 2 already applies a form of this guarantee to Strict Review. Extending it to Verification, TDD, Specification Review, Completion, or all lifecycle claims would add new mandatory obligations and must not be silently attached to Protocol 2.

### C-049 — Evidence must bind to its subject

Protocol 1 evidence is not uniformly modeled as subject-bound. Protocol 2 Strict Review provenance is subject/revision-bound. A universal subject-binding rule would require a subject model, identity rules, and likely schema changes. If used only as an optional capability it is compatible; if required for acceptance it belongs to a Future Protocol unless already covered by an existing P2 Review rule.

### C-050 — Gate results are revision-bound

Protocol 1 Gate PASS is not generically specified as an immutable revision assertion. Protocol 2 binds Strict Review to a concrete revision. Generalizing revision binding to Specification Review, Verification, Architecture gates, or Completion changes PASS semantics and may invalidate historical PASS results; that is breaking.

### C-051 — Material mutation invalidates affected downstream Gates

Specification Drift already forces a return to an appropriate specification stage when implementation evidence invalidates the Specification. That is narrower than a general invalidation graph. A generic rule that automatically revokes prior PASS after later material mutation is new Gate semantics and breaking under C-046.

### C-052 — Higher normative authority prevails

Canonical Protocol definitions already override project configuration, Harness representations, and Adapter behavior. Formalizing the hierarchy is a clarification if it preserves those rules. Same-level conflict resolution may be added as deterministic interpretation rules provided they do not redefine existing obligations.

### C-053 — Material scope expansion must be explicit

Silent expansion that changes Requirements or impact already triggers escalation or Specification Drift. This concept is compatible when expressed through existing mechanisms. Requiring a new mandatory `scope_expansions` field would instead be a new obligation and would need a new Protocol/schema boundary.

### C-054 — Unrelated work does not belong to the Change

This is sound scope discipline but is not currently a universal completion Gate. It may be a Policy/Review strengthening under existing Protocols so long as it does not retroactively invalidate conforming Changes merely because unrelated edits were bundled. A future hard invariant could be considered separately.

### C-055 — Material assumptions are explicit

Protocol 1 requires explicit Intent and trade-offs but not an assumptions ledger. Templates may recommend assumptions now. Making explicit assumptions mandatory for every material assumption is a new obligation and must not be retrofitted to P1/P2 without a new Protocol boundary.

### C-056 — Unknowns must not masquerade as facts

This is a clarification of truthful repository state, explicit confidence reduction, and no false Completion. It can be stated canonically without adding mandatory fields. Fabricated or knowingly false repository claims were never compatible with C-029/C-035.

### C-057 — Irreversible operations require explicit safety analysis

This should not become an unconditional Contract invariant for every Change. It belongs primarily in risk-sensitive Policy and project requirements, with a Future Protocol considering a mandatory high-risk safety-analysis trigger if desired. A universal required rollback/safety artifact would invalidate historical conforming instances.

### C-058 — Process completion is not proof of correctness

Already implied by C-021 and Verification/Strict Review. Lifecycle compliance demonstrates process conformance, not mathematical or empirical correctness. This can be clarified under existing Protocols.

### C-059 — Confidence must follow evidence

Evidence-calibrated confidence is consistent with C-040 and C-021. No canonical numeric score, enum, or mandatory dimensions should be introduced without independent justification. As a principle and Review/Verification guidance it is compatible; as a required machine-readable Completion field it becomes a new obligation.

## 5. C-045/C-046 Decision Framework

A same-integer Protocol revision is compatible only if **every previously valid conforming instance remains valid and retains the same interpretation of its required fields, stages, Gates, and lifecycle results**.

Apply these rules:

1. Editorial explanation with no obligation change: CLARIFICATION; same Protocol.
2. Making an already inevitable obligation explicit: CLARIFICATION; same Protocol, but the inevitability MUST be demonstrated from canonical text.
3. Adding a `SHOULD`: normally compatible if failure to satisfy it does not newly invalidate an instance.
4. Adding a `MUST`: breaking unless every conforming instance already necessarily satisfied it.
5. New mandatory field: new integer Protocol if absence becomes non-conforming.
6. New optional field/artifact: MAY be same Protocol through an independently versioned schema if absence preserves meaning.
7. New mandatory Artifact: new integer Protocol.
8. Historical evidence requirement that old instances may lack: new integer Protocol; evidence MUST NOT be fabricated.
9. Changing meaning of PASS: new integer Protocol.
10. Binding a previously unbound PASS to a SHA/immutable subject: new integer Protocol for that Gate.
11. Invalidating PASS after mutation where it previously survived: new integer Protocol.
12. Additional mandatory identity/provenance: new integer Protocol unless already mandatory for that exact Protocol/Gate.
13. New Gate or required lifecycle stage: new integer Protocol.
14. Stronger validation that merely detects states already forbidden: compatible enforcement fix.
15. Stronger validation that rejects a formerly valid state: new integer Protocol.
16. Stronger Review technique without changing acceptance obligations: compatible Policy strengthening.
17. Stronger Review evidence required for PASS: new integer Protocol unless already semantically required.
18. Altering Completion semantics so a formerly complete Change becomes incomplete: new integer Protocol.

Schema versioning is necessary for shape changes but never substitutes for the integer Protocol boundary when Core meaning changes.

## 6. Evidence and Subject Concept Analysis

### Claim
A proposition asserted about lifecycle, implementation, review, verification, repository state, or engineering behavior. Protocol 1 uses claims implicitly but has no universal claim schema.

### Evidence
Information offered to support a claim. Protocol 1 has bounded evidence semantics for TDD and Findings; Protocol 2 adds repository-native Review provenance. A universal evidence model is new.

### Subject
The entity or immutable state to which a claim/evidence item applies. Protocol 2 Strict Review has a concrete revision subject. Protocol 1 does not define one universal subject model.

### Subject binding
A deterministic relation between evidence and its subject. Existing Protocol 2 Review uses this concept. General lifecycle subject binding is future work.

### Execution provenance
Repository-native evidence of an execution identity/context and revision relationship. It is canonical in Protocol 2 Review infrastructure, not required by Protocol 1.

### Review provenance
Established in Protocol 2 and used to prove the stronger independent Strict Review boundary at recorded assurance.

### Resolution provenance
Established by Protocol 2 review-resolution lifecycle so later independent re-review can distinguish Resolver from Reviewer.

### Gate provenance
Not yet a universal canonical abstraction. Creating one is optional capability until a Protocol makes it mandatory.

**Decision on self-attestation proposition:** “Material lifecycle claims should not be accepted solely because an agent wrote that they occurred” is not a general consequence of Protocol 1. It is a breaking strengthening if made a universal acceptance rule. Protocol 2 already embodies the narrower proposition for Strict Review provenance.

## 7. Gate Revision Binding Analysis

### Specification Review
Current subject: the Specification content under review, but Protocol 1 does not define a generic immutable subject identifier. PASS is a lifecycle result and is not generically specified to survive or fail after arbitrary later mutations. Explicit SHA binding would change semantics and therefore belongs to a Future Protocol if mandatory.

### Verification
Current subject: the Change implementation/repository reality being verified. Protocol 1 requires Verification but does not generically bind PASS to an immutable revision. Mandatory immutable revision binding is breaking.

### Strict Review
Protocol 1: conceptual review with no mandatory immutable provenance. Protocol 2: revision-bound independent Review provenance already exists. No CHG-0009 rule may weaken or silently broaden that published boundary.

### Completion readiness
Current subject: aggregate Change state and required gates. It is repository-reality sensitive but not represented as a revision-bound Gate result. Making Completion readiness a reusable immutable assertion would be new semantics.

## 8. Candidate Material Mutation / Invalidation Model

This section is **candidate design only** for a later Change.

Mutation classes:

- `non_reviewable_provenance_mutation` — append/update lifecycle-control evidence that does not alter reviewed subject semantics.
- `reviewable_non_behavioral_mutation` — formatting or non-behavioral durable content that is reviewable but does not alter intended runtime behavior.
- `material_specification_mutation` — changes requirements, acceptance criteria, scope, invariants, or externally observable intent.
- `material_architecture_mutation` — changes component boundaries, data flows, persistence/transaction/security architecture, or selected architectural decisions.
- `material_implementation_mutation` — changes production behavior or executable structure material to a Gate.
- `material_test_mutation` — changes tests/evidence relied upon by Verification or Review.
- `documentation_only_mutation` — changes durable documentation with no Specification/Architecture/Implementation/Test semantic effect.

Candidate dependency matrix:

| Mutation | Candidate invalidation |
|---|---|
| non-reviewable provenance | none if subject authority and historical binding remain unchanged |
| reviewable non-behavioral | affected Review only when the Gate claims whole-revision review |
| material Specification | Specification Review and all downstream Architecture/Test Strategy/Plan/Tasks/Implementation/Verification/Strict Review/Completion decisions that depend on changed semantics |
| material Architecture | Architecture Gate and downstream Test Strategy/Plan/Tasks/Implementation/Verification/Strict Review/Completion |
| material Implementation | Verification/Strict Review/Completion; may also trigger Specification Drift if behavior diverges |
| material Test | Verification/Strict Review/Completion when the changed test/evidence was relied upon |
| documentation-only | Documentation/Knowledge/Completion when required documentation obligations are affected; not automatically behavioral Gates |

No automatic invalidation engine is authorized by this Change.

## 9. Authority Model

Candidate precedence from highest to lowest, subject to explicit extension rules:

1. Integer Protocol Specification and Engineering Contract for the selected Protocol.
2. Protocol compatibility rules and canonical schemas/Flows/Policies applicable to that Protocol.
3. Project Contract extensions and project configuration, which may strengthen only where permitted.
4. Change Specification and accepted Architecture decisions for the active Change.
5. Test Strategy, Plan, and Tasks as derived execution guidance.
6. Harness/Adapter projections as derived representations.
7. Execution prompts and chat context as transient instructions.

A lower level MUST NOT silently redefine a higher level. Conflicts within the same level MUST fail closed when they alter normative meaning unless the level defines an explicit deterministic precedence rule. Prompts and chat context may request work but cannot supersede repository-native canonical semantics.

Formalizing this precedence is compatible to the extent it restates existing authority constraints. Any new rule that changes existing same-level meaning requires separate compatibility analysis.

## 10. Scope, assumptions, unknowns, and reversibility placement

- Scope expansion: Specification/Drift and Review guidance; no new mandatory schema field in P1/P2.
- Unrelated work: Policy/Review scope-discipline rule; hard Gate deferred.
- Assumptions: template and Specification guidance now; mandatory structured assumptions require Future Protocol analysis.
- Unknowns: Contract/Specification clarification of truthful assertions is compatible.
- Irreversible operations: security/risk Policy is the preferred location. Project policies MAY require stronger analysis. A universal mandatory safety artifact is deferred to a Future Protocol.

## 11. Engineering Confidence

Forge must distinguish:

- **lifecycle compliance** — required stages/Gates were conducted according to the selected Protocol;
- **verification result** — executed checks support or fail the expected state;
- **review result** — adversarial Review accepted or rejected the reviewed subject;
- **engineering confidence** — calibrated judgment about residual uncertainty;
- **correctness** — the system actually satisfies its intended properties.

Lifecycle compliance, Verification PASS, and Review PASS are evidence about correctness; none is proof of correctness. Engineering confidence should remain informative and evidence-calibrated. No score, enum, schema field, or Completion requirement is authorized by CHG-0009.

## 12. Protocol Evolution Decision

**Decision: MIXED_EVOLUTION.**

The reason differs from the original framing because repository reality has moved forward:

- Protocol 1 can receive clarifications and non-invalidating strengthening for C-052, C-053, C-056, C-058, and principle-level C-059; C-054 can be strengthened as Policy without a new hard conformance Gate.
- Existing Protocol 2 already contains part of C-048/C-049/C-050 for Strict Review provenance and revision binding.
- Universal C-047, broader C-048/C-049/C-050, C-051, mandatory C-055, and mandatory C-057 would add obligations or Gate semantics not guaranteed by valid Protocol 1 or existing Protocol 2 instances.
- Those broader mandatory semantics require a **Future Protocol integer boundary** if adopted. CHG-0009 does not assign or reserve that integer identifier.

Protocol 2 is therefore necessary for the review-independence semantics already implemented by CHG-0008, but this Change does **not** implement Protocol 2 and does not expand its published meaning.

## 13. Candidate version architecture

Existing structure already demonstrates the safe direction: version-specific canonical resources may live under `protocol/versions/<integer>/`, while shared compatibility and schema catalog resources remain addressable independently.

Candidate rule for future evolution:

- Every integer Protocol MUST have an unambiguous, reproducible Specification and Contract address.
- A Change using `forge/change@2` declares Protocol 2 explicitly; future schema selection MUST remain tied to the selected Protocol contract, not inferred only from filename suffix.
- Historical Protocol resources MUST remain readable after later Protocols are introduced.
- Shared resources MAY remain outside version directories only when their applicability is explicitly version-independent.
- No mass relocation of Protocol 1 is required merely for aesthetic symmetry; reproducibility matters more than directory uniformity.

### Machine-readable Engineering Contract

`protocol/contract/engineering.yml` is a reasonable future derived representation, but Markdown should remain canonical until a dedicated Change proves deterministic generation/validation and eliminates semantic drift risk. Making YAML canonical now would create a second authority or require a migration of all normative references. A future Change may reverse the authority only through an explicit Protocol/compatibility decision.

## 14. Migration Principles

1. Evidence that was not captured historically MUST remain absent.
2. Migration MUST NOT manufacture TDD, Verification, Review, or execution provenance.
3. Completed Protocol 1 Changes remain interpretable as Protocol 1.
4. Existing Protocol 2 Changes remain interpretable under the published Protocol 2 review-independence contract.
5. Project migration to a newer Protocol is explicit and separate from installing software support for that Protocol.
6. Forge self-migration is a distinct governed Change and MUST NOT be implied by adding support.
7. Adapters declare the Protocol interval they support; adapter installation MUST NOT silently migrate a project.
8. Migration tooling must be local-capable and provider-independent.
9. Missing evidence may produce `unknown`, `not_available`, or migration warnings only if the future schema defines such states honestly; it must never be upgraded to proof.

Distinguish:

- **Protocol support** — tooling can resolve/validate the Protocol.
- **Project migration** — repository opts into new semantic obligations.
- **Forge self-migration** — forge-protocol itself adopts that Protocol for new active Changes.

## 15. Follow-up Change Roadmap

Identifiers are placeholders only and MUST NOT be reserved by this document.

1. **Future Protocol semantic foundation** — define the exact new mandatory contract boundary and choose the next integer only when created. Depends on CHG-0009. Excludes schemas/engine implementation. Done when semantics and compatibility are frozen.
2. **Evidence and Subject Model** — define claim/evidence/subject/binding/provenance abstractions. Depends on semantic foundation. Excludes Gate invalidation. Done when provider-independent model and trust boundaries are normative.
3. **Revision-bound Gates and Invalidation** — define Gate subjects, mutation taxonomy, dependency graph, invalidation rules. Depends on evidence/subject model. Excludes broad schema rollout until semantics stabilize.
4. **Future Protocol Schemas** — implement manifest/evidence/Gate schema shapes required by the selected Protocol. Depends on semantic model. Excludes migration behavior.
5. **Flow and Review Policy Evolution** — version Flow/Policy semantics for new Gate/evidence obligations. Depends on schemas and invalidation semantics.
6. **Machine-readable Engineering Contract** — introduce structured representation plus deterministic drift validation. Depends on frozen semantic authority decision. Excludes changing canonical source unless explicitly approved.
7. **Protocol Migration Framework** — implement explicit project migration and diagnostics without fabricating evidence. Depends on schemas and compatibility rules.
8. **Future Protocol Conformance Suite** — fixtures and deterministic validation for Protocol selection, versioned resources, evidence, Gates, migration, Adapters, and historical preservation.
9. **Forge Self-migration** — only after tooling, conformance, and Adapter support are proven; migrates active Forge development explicitly and preserves historical P1/P2 Changes.

## 16. Requirements

- **FR-001** Preserve Protocol 1 historical validity.
- **FR-002** Preserve existing Protocol 2 published review-independence semantics.
- **FR-003** Classify C-047 through C-059 using the defined categories.
- **FR-004** Demonstrate classifications from canonical compatibility rules.
- **FR-005** Define operational C-045/C-046 criteria.
- **FR-006** Define evidence/subject/provenance conceptual boundaries without implementation.
- **FR-007** Analyze Gate revision binding separately for Specification Review, Verification, Strict Review, and Completion readiness.
- **FR-008** Provide a candidate mutation taxonomy and invalidation matrix without making it executable.
- **FR-009** Provide an authority model that keeps prompts/Harnesses below canonical repository semantics.
- **FR-010** Avoid new mandatory P1/P2 fields for assumptions, confidence, or reversibility.
- **FR-011** Define migration principles that forbid fabricated history.
- **FR-012** Separate Protocol support, project migration, and Forge self-migration.
- **FR-013** Preserve provider independence and local Core operation.
- **FR-014** Preserve Adapter compatibility as an explicit Protocol interval concern.
- **FR-015** Keep machine-readable Contract representation single-authority or derived, never parallel canonical truth.
- **FR-016** Use placeholder future Change identifiers only.
- **FR-017** Do not implement Future Protocol semantics in CHG-0009.
- **FR-018** Do not advance past Specification Review without satisfying the current FULL gate.

## 17. Acceptance criteria

- AC-001: all thirteen proposals have one explicit classification and rationale.
- AC-002: the analysis recognizes that Protocol 2 already exists at the base SHA.
- AC-003: no proposed breaking rule is labeled compatible solely for desirability.
- AC-004: no historical evidence is invented.
- AC-005: no future integer Protocol identifier or Change ID is reserved.
- AC-006: existing P1 and P2 meanings remain reproducible.
- AC-007: candidate invalidation rules are visibly non-executable design.
- AC-008: authority precedence cannot be overridden by agent prompts or Harness projections.
- AC-009: machine-readable Contract design avoids dual canonical sources.
- AC-010: migration remains explicit, local-capable, and provider-independent.
- AC-011: Architecture does not begin before an admissible Adversarial Specification Review PASS.
