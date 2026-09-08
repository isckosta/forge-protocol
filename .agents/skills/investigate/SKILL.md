---
name: investigate
description: "The default failure mode for diagnosing a problem is `symptom -> plausible guess -> code change`: the first explanation that fits the symptom gets acted on, evidence that would have contradicted it is never collected, and the resulting change may correct a coincidence rather than a cause. Investigate exists to replace that shortcut with: ``` problem -> establish facts -> reproduce when possible -> gather evidence -> competing hypotheses -> test hypotheses -> isolate root cause -> conclusion ``` Its value is a conclusion whose confidence is proportionate to the evidence actually gathered — including, when the evidence does not support one, the explicit conclusion that root cause is not yet established, rather than a fabricated certainty that only exists to end the investigation."
---

# Forge capability: investigate

This is a Harness projection of a canonical Forge Capability.
Read `references/CAPABILITY.md` before acting and follow that definition as the sole source of competency behavior.

The projection does not add lifecycle, gate, approval, or enforcement semantics. Record the capability's outputs and evidence in the repository-native form required by the surrounding work.
