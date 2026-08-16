# Adversarial Specification Review — CHG-0009

Status: pending

## Review subject

Specification subject is the CHG-0009 normative design recorded on branch `feat/chg-0009-protocol-2-semantic-design` after the initial Intent, Discovery, and Specification commits derived from base SHA `70841bd77bd0128c48deda73b24708c3e5e3c461`.

The Reviewer MUST resolve the concrete branch HEAD before beginning the review and record the immutable revision actually reviewed.

## Required adversarial focus

The independent review MUST actively challenge:

- any attempt to reinterpret Protocol 1 under C-045/C-046;
- any silent expansion of the already-published Protocol 2 review-independence boundary;
- compatibility classifications without canonical evidence;
- vague definitions of material mutation or invalidation dependency;
- circular claim/evidence definitions;
- authority precedence that permits prompts, Harnesses, or Adapters to override canonical semantics;
- migration designs that fabricate historical provenance;
- dual canonical Contract sources;
- non-reproducible Protocol version resolution;
- unnecessary mandatory Artifacts;
- provider-specific or hosted-backend dependencies;
- Adapter interval incompatibility;
- incorrect assumption that the next breaking Protocol integer is already reserved.

## Gate rule

Architecture MUST NOT begin until this artifact records an admissible PASS under the current FULL Specification Review gate. Any blocking finding must be resolved through the applicable Reviewer/Resolver process without representing same-execution self-approval as independent review.
