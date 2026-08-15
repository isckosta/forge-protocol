# Knowledge Capture — CHG-0008

Protocol compatibility is a semantic boundary. Protocol 1 remains unchanged; Protocol 2 adds independent Execution/Context and concrete revision-bound Strict Review.

The important correction from Iteration 2 is that a logical revision ID is not a concrete review subject. Protocol 2 now normalizes an immutable revision reference and compares it across subject and Reviewer provenance. In Git, commit SHA is the concrete reference.

A provenance record cannot truthfully contain the SHA of the same commit that contains the record. Therefore the reviewable Resolution is frozen first; provenance is review-control metadata committed afterwards and points to the frozen subject. Only manifest/provenance/review metadata may follow without invalidating the subject. Any implementation, test, specification, verification-evidence, or documentation mutation requires a new freeze/provenance record.

`recorded` remains self-recorded repository evidence; `verified` is stronger observer-backed evidence. Core verifies consistency and local revision binding, not cryptographic authorship.
