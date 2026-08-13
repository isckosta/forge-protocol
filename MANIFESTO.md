# The Forge Manifesto

Software engineering is entering an era in which producing code is becoming dramatically cheaper than validating the decisions behind it. Forge exists because faster code generation does not reduce the need for engineering discipline. It increases it.

## Intent before implementation

Software should begin with a clear understanding of what reality is expected to change. Every meaningful Change begins with explicit Intent.

## Specification before behavior

Agents must not invent requirements while implementing them. Expected behavior should be established before production behavior is written.

## Tests before behavioral implementation

Forge is TDD-first. When behavior is reasonably testable, executable evidence must be designed before the production implementation intended to satisfy it. The default cycle is `RED -> GREEN -> REFACTOR`.

## RED must be real

A test must be executed and fail for the expected behavioral reason. A broken environment, syntax error, unrelated failure, or invalid fixture is not RED.

## GREEN should be small

Once RED is established, Implementation should introduce the minimum behavior necessary to satisfy the test.

## Refactor after GREEN

Design improvement belongs after behavior is protected. Refactoring must preserve GREEN. New behavior requires a new TDD cycle.

## Coverage is not TDD

Post-hoc tests may improve confidence and prevent regressions, but they are not evidence that Implementation was developed through TDD.

## Small diffs may have large semantic impact

Line count is a poor measure of engineering risk. Forge classifies Changes by semantic impact.

## Process must be proportional

Forge rejects both under-engineering and process theater. Rigor is mandatory. Ceremony is proportional.

## FAST does not mean careless

FAST removes unnecessary artifacts. It does not remove applicable TDD, Verification, Strict Review, or Documentation Impact evaluation.

## Passing tests are evidence, not proof

Verification asks whether the evidence is sufficient. Review asks what the evidence failed to prove.

## Review should attempt falsification

Forge Review is adversarial. The reviewer asks what plausible reason exists for rejecting the Implementation.

## Findings require evidence

Material Findings identify the problem, impact, evidence, location, violated requirement or invariant when applicable, and confidence.

## Reviewer and Resolver are different roles

The role judging an Implementation should not silently become the role rewriting it.

## Documentation describes reality

Every Change evaluates Documentation Impact. Not every Change requires documentation changes; every Change must decide whether it does.

## The repository is durable memory

Chats, models, Harnesses, and developers change. Durable engineering knowledge belongs with the software it describes.

## The chat is the runtime

Coding Harnesses execute. Forge governs.

## Agents may reason, but they may not redefine the process silently

Contracts define invariants. Policies define project rules. Flows define required stages. Gates define acceptance conditions.

## Completion is a repository state

A Change is complete when Specification, tests, Implementation, Verification, Review, and Documentation Impact agree with repository reality.

## Forge is strict about correctness and quiet about ceremony

Forge should never demand ceremony that adds no engineering value, and should never trade engineering confidence for convenience without making that trade explicit.
