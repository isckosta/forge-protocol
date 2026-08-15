"""Deterministic, in-memory Codex projection resources."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
import yaml
@dataclass(frozen=True)
class CodexProjectionInput: flow_id:str; flow_content:str; contract_content:str; protocol_id:int=1
@dataclass(frozen=True)
class CodexProjectionResource: name:str; content:str; digest:str
@dataclass(frozen=True)
class CodexProjectionBundle: adapter_id:str; flow_id:str; resources:tuple[CodexProjectionResource,...]
def load_workflow_skill_template()->str:return files("forge_cli.adapters.codex").joinpath("resources","skills","workflow.md").read_text(encoding="utf-8").rstrip()
def _resource(name,content):
 n=content.rstrip()+"\n";return CodexProjectionResource(name,n,sha256(n.encode()).hexdigest())
def _label(s):return {"specification_review":"Specification Review","tdd_implementation":"TDD Implementation","verification":"Verification","strict_review":"Strict Review","completion":"Completion"}.get(s,s.replace("_"," ").title())
def _instructions(protocol_id,flow_id,flow_content):
 data=yaml.safe_load(flow_content)or{};stages=data.get("stages")or[];gates=data.get("gates")or{};ids=[x.get("id")for x in stages if isinstance(x,dict)and x.get("id")];lines=[load_workflow_skill_template(),""]
 if ids:lines+=["### Required stage order",""]+[f"{i}. {_label(s)}"for i,s in enumerate(ids,1)]+[""]
 checks=set((gates.get("before_behavioral_implementation")or{}).get("checks")or[])
 if "red_executed"in checks:lines.append("- RED must be executed.")
 if "red_failed_for_expected_reason"in checks:lines.append("- RED must fail for the expected reason.")
 if checks:lines.append("")
 req=set((gates.get("before_completion")or{}).get("require")or[])
 if "verification_passed"in req:lines.append("- Completion requires Verification to pass.")
 if "review_passed"in req:lines.append("- Completion requires Strict Review to pass.")
 if "blocking_review_threads_resolved"in req:lines.append("- Completion requires all blocking review threads on any active external review surface to be resolved.")
 if protocol_id>=2 and flow_id in{"fast","standard","full"}:
  lines += ["","### Reviewer/Resolver independence","","- Finish the Implementation/Resolution and all reviewable evidence before freezing the review subject.","- Identify the concrete immutable subject revision. In Git, use the subject commit SHA; `revision.id` alone is not sufficient.","- Record subject provenance for that frozen revision. Do not continue changing implementation, tests, specification, verification evidence, or documentation after the freeze; if they change, create a new subject revision and provenance.","- Review-control metadata (`manifest.yml`, `provenance.yml`, `review.md` for the Change) may be committed after the freeze because the provenance record cannot self-reference the commit that contains itself.","- Start Strict Review against the frozen subject, not an ambiguous later HEAD.","- Reviewer provenance must bind to the exact same logical revision and immutable reference as subject provenance.","- Reviewer Execution and Context must both differ from the subject Execution and Context. Role switching is self-review.","- `claimed` is insufficient; `recorded` is repository-native self-recorded evidence, while `verified` requires stronger observer-backed evidence.","- After blocking findings are resolved, freeze the new Resolution revision and re-review that concrete revision with a new independent Reviewer execution."]
 return "\n".join(lines).rstrip()
def generate_codex_projection_bundle(canonical):
 flow=_resource("forge-flow.md","\n".join(("# Forge Flow Projection","",f"Flow: {canonical.flow_id}","","This resource is a derived Forge projection for Codex.","Repository-native Forge state remains authoritative.","",_instructions(canonical.protocol_id,canonical.flow_id,canonical.flow_content),"","## Canonical Flow","",canonical.flow_content)))
 contract=_resource("forge-contract.md","\n".join(("# Forge Contract Projection","",f"Flow context: {canonical.flow_id}","","This resource is a derived Forge projection for Codex.","","## Canonical Engineering Contract","",canonical.contract_content)))
 return CodexProjectionBundle("codex",canonical.flow_id,tuple(sorted((flow,contract),key=lambda x:x.name)))
