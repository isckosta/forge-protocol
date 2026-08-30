"""Forge validation boundary."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Any
import yaml
from forge_cli.configuration import InvalidProjectConfigurationError, UnsupportedProtocolVersionError, load_project_configuration
from forge_cli.protocol_resolution import CanonicalContractUnavailableError, InvalidProjectFlowConfigurationError, UnknownCanonicalFlowError, resolve_effective_contract, resolve_effective_flow
@dataclass(frozen=True)
class ValidationFinding:
    code:str; artifact:str; message:str; path:Path|None=None
@dataclass(frozen=True)
class ValidationResult:
    findings:tuple[ValidationFinding,...]
    @property
    def passed(self)->bool:return not self.findings
def _finding(r:Path,p:Path,m:str)->ValidationFinding:return ValidationFinding("C-026",str(p.relative_to(r)),m,p)
def _load_mapping(p:Path)->dict[str,Any]|None:
    try:d=yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except (OSError,yaml.YAMLError):return None
    return d if isinstance(d,dict) else None
def _record_fields(x:object):
    if not isinstance(x,dict):return None
    e,v,s=x.get("execution"),x.get("revision"),x.get("source"); i,role=x.get("id"),x.get("role")
    if not(isinstance(i,str)and i and role in{"implementation","resolution","review"}and isinstance(e,dict)and isinstance(v,dict)and isinstance(s,dict)):return None
    ex,ctx,rid=e.get("id"),e.get("context_id"),v.get("id")
    if not(isinstance(ex,str)and ex and isinstance(ctx,str)and ctx and isinstance(rid,str)and rid and s.get("assurance") in{"claimed","recorded","verified"}):return None
    im,com=v.get("immutable_ref"),v.get("commit")
    if im is None and isinstance(com,str):im={"type":"git_commit","value":com}
    if not isinstance(im,dict):return None
    typ,val=im.get("type"),im.get("value")
    if typ not in{"git_commit","content_digest","vcs_revision"}or not isinstance(val,str)or not val:return None
    if typ=="git_commit":
        if len(val)!=40 or any(c not in"0123456789abcdefABCDEF" for c in val):return None
        val=val.lower()
    if com is not None and(typ!="git_commit"or not isinstance(com,str)or com.lower()!=val):return None
    return i,role,ex,ctx,rid,(typ,val)
def _git_exists(r:Path,c:str)->bool:return subprocess.run(["git","cat-file","-e",f"{c}^{{commit}}"],cwd=r,capture_output=True,check=False).returncode==0
def _git_root(r:Path)->Path|None:
    q=subprocess.run(["git","rev-parse","--show-toplevel"],cwd=r,capture_output=True,text=True,check=False)
    if q.returncode:return None
    try:return Path(q.stdout.strip()).resolve()
    except OSError:return None
def _decode_git_path(value:bytes)->str:return value.decode("utf-8","surrogateescape")
def _name_status_paths(data:bytes)->set[str]|None:
    parts=data.split(b"\0"); paths:set[str]=set();i=0
    if parts and parts[-1]==b"":parts.pop()
    while i<len(parts):
        status=parts[i];i+=1
        if not status:return None
        count=2 if status[:1] in{b"R",b"C"}else 1
        if i+count>len(parts):return None
        for _ in range(count):paths.add(_decode_git_path(parts[i]));i+=1
    return paths
def _diff_paths(root:Path,*args:str)->set[str]|None:
    q=subprocess.run(["git","diff","--name-status","-z","--find-renames",*args,"--"],cwd=root,capture_output=True,check=False)
    return None if q.returncode else _name_status_paths(q.stdout)
def _untracked_paths(root:Path)->set[str]|None:
    q=subprocess.run(["git","ls-files","--others","--exclude-standard","-z","--"],cwd=root,capture_output=True,check=False)
    if q.returncode:return None
    return {_decode_git_path(p) for p in q.stdout.split(b"\0") if p}
def _review_control_metadata_paths(root:Path,m:Path)->set[str]|None:
    try:d=m.parent.resolve().relative_to(root).as_posix()
    except ValueError:return None
    return {f"{d}/manifest.yml",f"{d}/provenance.yml",f"{d}/review.md"}
def _reviewable_workspace_delta(r:Path,m:Path,c:str)->set[str]|None:
    root=_git_root(r)
    if root is None:return None
    committed=_diff_paths(root,f"{c}..HEAD");staged=_diff_paths(root,"--cached");unstaged=_diff_paths(root);untracked=_untracked_paths(root)
    if any(x is None for x in(committed,staged,unstaged,untracked)):return None
    changed=set().union(committed or set(),staged or set(),unstaged or set(),untracked or set())
    allowed=_review_control_metadata_paths(root,m)
    if allowed is None:return changed
    reviewable=set()
    for path in changed:
        if path not in allowed:
            reviewable.add(path);continue
        target=root/Path(path)
        if not target.exists()or target.is_symlink()or not target.is_file():reviewable.add(path)
    return reviewable
def _changed(r:Path,m:Path,c:str)->bool:
    delta=_reviewable_workspace_delta(r,m,c)
    return delta is None or bool(delta)
def _resolution_delta(r:Path,m:Path,from_commit:str,to_commit:str)->set[str]|None:
    """CHG-0011: committed diff introduced by the frozen resolution commit.

    Unlike _reviewable_workspace_delta (a frozen commit vs. the *current*
    workspace), this uses the resolution commit's first-parent delta. Using
    the full range from the prior subject would incorrectly include unrelated
    Changes merged into the branch between the two frozen subjects.
    """
    root=_git_root(r)
    if root is None:return None
    if from_commit==to_commit:return set()
    parent=subprocess.run(["git","rev-parse",f"{to_commit}^"],cwd=root,capture_output=True,text=True,check=False)
    if parent.returncode:return None
    diff=_diff_paths(root,f"{parent.stdout.strip()}..{to_commit}")
    if diff is None:return None
    allowed=_review_control_metadata_paths(root,m)
    return diff if allowed is None else diff-allowed
def _uncovered_paths(paths:set[str],scope:object)->set[str]|None:
    """CHG-0011-R003: exact repository-relative path match only.

    Glob/wildcard containment was found trivially defeatable (scope: ["*"]
    covers every path); Resolution Scope declares the exact paths it
    touches, not a pattern that can be widened to swallow the whole delta.
    """
    if not isinstance(scope,list)or not scope:return None
    patterns=[p for p in scope if isinstance(p,str)and p]
    if len(patterns)!=len(scope):return None
    return {p for p in paths if p not in patterns}
def _residual_risk_permitted(r:Path)->bool:
    cfg=_load_mapping(r/".forge/forge.yml")
    if cfg is None:return False
    review=cfg.get("review")
    conv=review.get("convergence")if isinstance(review,dict)else None
    return isinstance(conv,dict)and conv.get("allow_residual_risk_acceptance")is True
def _validate_resolution_verification(r:Path,mpath:Path,m:dict,its:list,idx:dict)->list[ValidationFinding]:
    out:list[ValidationFinding]=[]
    if not any(isinstance(it,dict)and it.get("kind")in{"initial_review","resolution_verification"}for it in its):
        return out
    for pos,it in enumerate(its):
        if not isinstance(it,dict)or it.get("kind")!="resolution_verification":continue
        if pos==0:
            out.append(_finding(r,mpath,"A resolution_verification Iteration MUST NOT be the first Review Iteration; there is no prior reviewed subject to compute a Resolution Delta against."));continue
        sref=it.get("subject_provenance")
        sub=idx.get(sref)if isinstance(sref,str)else None
        if sub is None:
            out.append(_finding(r,mpath,"A resolution_verification Iteration requires subject_provenance identifying the Resolution it verifies."));continue
        sf=_record_fields(sub)
        if sf is None:continue
        _,srole,_,_,_,sim=sf
        if srole!="resolution":
            out.append(_finding(r,mpath,"A resolution_verification Iteration must reference resolution-role subject provenance; an implementation-role subject is definitionally an initial_review."));continue
        scope,targets=sub.get("scope"),sub.get("targets")
        if not(isinstance(scope,list)and scope)or not(isinstance(targets,list)and targets):
            out.append(_finding(r,mpath,"The Resolution referenced by a resolution_verification Iteration must declare non-empty scope and targets before it can be mechanically verified as scoped."));continue
        prior=its[pos-1]
        pref=prior.get("subject_provenance")if isinstance(prior,dict)else None
        psub=idx.get(pref)if isinstance(pref,str)else None
        pf=_record_fields(psub)if psub is not None else None
        if pf is None:
            out.append(_finding(r,mpath,"resolution_verification cannot resolve the prior Iteration's subject provenance required to compute the Resolution Delta."));continue
        pim=pf[5]
        if sim[0]!="git_commit"or pim[0]!="git_commit":
            out.append(_finding(r,mpath,"Resolution Delta computation requires git_commit immutable references on both the prior and current subject."));continue
        delta=_resolution_delta(r,mpath,pim[1],sim[1])
        if delta is None:
            out.append(_finding(r,mpath,"Resolution Delta could not be determined from local Git history; validation fails closed."));continue
        uncovered=_uncovered_paths(delta,scope)
        if uncovered is None:
            out.append(_finding(r,mpath,"Declared Resolution scope is malformed."));continue
        status,full_review=it.get("status"),it.get("full_review_required")is True
        if uncovered:
            if status!="failed"or not full_review:
                paths=", ".join(sorted(uncovered))
                out.append(_finding(r,mpath,f"Resolution Delta contains Out-of-Scope Mutation not covered by declared scope ({paths}); a resolution_verification Iteration that detects this MUST be status: failed with full_review_required: true, never passed."))
            continue
        nmf=it.get("new_material_findings")
        if status=="passed"and nmf not in(None,0):
            out.append(_finding(r,mpath,"A passed resolution_verification Iteration MUST NOT declare new_material_findings greater than 0."))
        elif status=="failed"and nmf is not None and(not isinstance(nmf,int)or isinstance(nmf,bool)or nmf<0):
            out.append(_finding(r,mpath,"new_material_findings must be a non-negative integer."))
    # FR-010: Full Review Escalation applies from the very first occurrence,
    # independently of the (separate) Convergence Limit below — a single
    # full_review_required Iteration already forbids the next Iteration from
    # being another scoped resolution_verification.
    for pos,it in enumerate(its):
        if not(isinstance(it,dict)and it.get("full_review_required")is True):continue
        if pos+1>=len(its):continue
        nxt=its[pos+1]
        if isinstance(nxt,dict)and nxt.get("kind")=="resolution_verification":
            out.append(_finding(r,mpath,"A further resolution_verification Iteration is not valid immediately after full_review_required: true; only a new initial_review Iteration may continue the review lifecycle."))
    streaks:list[int]=[];s=0
    for it in its:
        nmf=it.get("new_material_findings")if isinstance(it,dict)else None
        qualifies=isinstance(it,dict)and it.get("kind")=="resolution_verification"and it.get("status")=="failed"and isinstance(nmf,int)and not isinstance(nmf,bool)and nmf>0
        s=s+1 if qualifies else 0
        streaks.append(s)
    run=streaks[-1]if streaks else 0
    review=m.get("review")if isinstance(m.get("review"),dict)else{}
    conv=review.get("convergence")if isinstance(review,dict)else None
    declared_count=conv.get("consecutive_unconverged_verifications")if isinstance(conv,dict)else None
    if declared_count is not None and declared_count!=run:
        out.append(_finding(r,mpath,f"Declared review.convergence.consecutive_unconverged_verifications ({declared_count!r}) disagrees with the Core-derived value ({run}); the convergence counter is derived, not self-declared."))
    if run>=2:
        declared_state=conv.get("state")if isinstance(conv,dict)else None
        if declared_state!="review_convergence_failed":
            out.append(_finding(r,mpath,"The Convergence Limit was reached (2 consecutive Resolution Verifications with new material findings); review.convergence.state MUST be review_convergence_failed."))
        if review.get("status")=="passed":
            out.append(_finding(r,mpath,"review.status MUST NOT be passed while the Change is in review_convergence_failed."))
    # Historical scan (not just the current trailing run): every index where the
    # limit was reached is checked, so appending a fresh initial_review later
    # cannot silently erase an earlier, never-decided non-convergence episode.
    # CHG-0011-R001: the decision is read from the *specific* Iteration that
    # follows each episode (`convergence_decision`), never from one shared
    # manifest-wide field — a decision recorded for one episode cannot be
    # reused to silently authorize a later, independent episode, because each
    # episode necessarily produces its own distinct following Iteration and
    # historical Iterations are already immutable once committed (CHG-0008).
    for i,streak_i in enumerate(streaks):
        if streak_i<2 or i+1>=len(its):continue
        nxt=its[i+1]
        decision=nxt.get("convergence_decision")if isinstance(nxt,dict)else None
        valid_decision=isinstance(decision,dict)and decision.get("option")in{"new_full_review","return_to_earlier_phase","accept_residual_risk","abort_or_supersede"}and isinstance(decision.get("reason"),str)and decision.get("reason")
        if not valid_decision:
            out.append(_finding(r,mpath,"The Iteration immediately after the Convergence Limit was reached requires its own valid convergence_decision (option and reason); a decision recorded for a different episode does not authorize this one."))
        elif decision.get("option")=="accept_residual_risk"and not _residual_risk_permitted(r):
            out.append(_finding(r,mpath,"convergence_decision.option accept_residual_risk requires the project configuration to explicitly permit it (review.convergence.allow_residual_risk_acceptance: true)."))
        if isinstance(nxt,dict)and nxt.get("kind")=="resolution_verification":
            out.append(_finding(r,mpath,"A further resolution_verification Iteration is not valid once the Convergence Limit was reached; only a new initial_review Iteration may continue the review lifecycle."))
    return out
_HISTORY_ERROR=object()
def _committed_history_mappings(r:Path,path:Path)->list[object]|None:
    root=_git_root(r)
    if root is None:return None
    head=subprocess.run(["git","rev-parse","--verify","HEAD"],cwd=root,capture_output=True,text=True,check=False)
    if head.returncode:return []
    shallow=subprocess.run(["git","rev-parse","--is-shallow-repository"],cwd=root,capture_output=True,text=True,check=False)
    if shallow.returncode or shallow.stdout.strip() not in{"true","false"}:return None
    if shallow.stdout.strip()=="true":return None
    try:rel=path.resolve().relative_to(root).as_posix()
    except(OSError,ValueError):return None
    history=subprocess.run(["git","log","--format=%H","--reverse","--diff-filter=AM","--",rel],cwd=root,capture_output=True,text=True,check=False)
    if history.returncode:return None
    documents:list[object]=[]
    for commit in(line.strip() for line in history.stdout.splitlines()):
        if not commit:continue
        snapshot=subprocess.run(["git","show",f"{commit}:{rel}"],cwd=root,capture_output=True,check=False)
        if snapshot.returncode:
            documents.append(_HISTORY_ERROR);continue
        try:loaded=yaml.safe_load(snapshot.stdout.decode("utf-8")) or {}
        except(UnicodeDecodeError,yaml.YAMLError):
            documents.append(_HISTORY_ERROR);continue
        if not isinstance(loaded,dict):
            documents.append(_HISTORY_ERROR);continue
        documents.append(loaded)
    return documents
def _first_committed_provenance_record(r:Path,path:Path,record_id:str):
    documents=_committed_history_mappings(r,path)
    if documents is None:return _HISTORY_ERROR
    legacy_prefixes:list[str]=[]
    for document in documents:
        if document is _HISTORY_ERROR:return _HISTORY_ERROR
        assert isinstance(document,dict)
        records=document.get("records")
        if not isinstance(records,list):continue
        matches=[record for record in records if isinstance(record,dict)and record.get("id")==record_id]
        if len(matches)>1:return _HISTORY_ERROR
        if not matches:continue
        candidate=matches[0]
        revision=candidate.get("revision") if isinstance(candidate,dict) else None
        if not isinstance(revision,dict) or revision.get("immutable_ref") is None:continue
        if _record_fields(candidate) is None:
            immutable=revision.get("immutable_ref")
            value=immutable.get("value") if isinstance(immutable,dict) else None
            if (
                isinstance(immutable,dict)
                and immutable.get("type")=="git_commit"
                and isinstance(value,str)
                and 7<=len(value)<40
                and all(c in"0123456789abcdefABCDEF"for c in value)
            ):
                # Historical Forge versions recorded abbreviated Git SHAs.
                # They are not valid immutable subjects by themselves, but a
                # later complete record may migrate the same subject safely if
                # its full SHA preserves every legacy prefix exactly.
                legacy_prefixes.append(value.lower())
                continue
            return _HISTORY_ERROR
        if legacy_prefixes:
            immutable=candidate["revision"].get("immutable_ref")
            value=immutable.get("value") if isinstance(immutable,dict) else None
            if not isinstance(value,str) or any(not value.lower().startswith(prefix) for prefix in legacy_prefixes):
                return _HISTORY_ERROR
        return candidate
    return None
def _first_committed_review_iteration(r:Path,path:Path,iteration_id:str):
    documents=_committed_history_mappings(r,path)
    if documents is None:return _HISTORY_ERROR
    unresolved_history_error=False
    for document in documents:
        if document is _HISTORY_ERROR:
            unresolved_history_error=True
            continue
        assert isinstance(document,dict)
        review=document.get("review");iterations=review.get("iterations")if isinstance(review,dict)else None
        if not isinstance(iterations,list):continue
        matches=[iteration for iteration in iterations if isinstance(iteration,dict)and iteration.get("id")==iteration_id]
        if len(matches)>1:return _HISTORY_ERROR
        if not matches:continue
        candidate=matches[0]
        if not(isinstance(candidate.get("revision"),str)and candidate.get("revision") and isinstance(candidate.get("subject_provenance"),str)and candidate.get("subject_provenance")):continue
        return candidate
    return _HISTORY_ERROR if unresolved_history_error else None
def _committed_review_iteration_ids(r:Path,path:Path):
    documents=_committed_history_mappings(r,path)
    if documents is None:return _HISTORY_ERROR
    authorities:set[str]=set()
    for document in documents:
        if document is _HISTORY_ERROR:continue
        assert isinstance(document,dict)
        review=document.get("review");iterations=review.get("iterations")if isinstance(review,dict)else None
        if not isinstance(iterations,list):continue
        seen:set[str]=set()
        for iteration in iterations:
            if not isinstance(iteration,dict):continue
            iid,rid,sref=iteration.get("id"),iteration.get("revision"),iteration.get("subject_provenance")
            if not(isinstance(iid,str)and iid and isinstance(rid,str)and rid and isinstance(sref,str)and sref):continue
            if iid in seen:return _HISTORY_ERROR
            seen.add(iid);authorities.add(iid)
    return authorities
def _validate_protocol2_review_provenance(r:Path)->list[ValidationFinding]:
    out=[]; changes=r/".forge/changes"
    if not changes.is_dir():return out
    for mpath in sorted(changes.glob("*/manifest.yml")):
        m=_load_mapping(mpath)
        if m is None:continue
        st=m.get("state")or{}
        if m.get("schema")=="forge/change@1":
            if not isinstance(st,dict)or st.get("current")!="complete":out.append(_finding(r,mpath,"Protocol 2 active Changes must use forge/change@2; forge/change@1 cannot bypass C-026."))
            continue
        if m.get("schema")!="forge/change@2":continue
        if m.get("protocol")!=2:out.append(_finding(r,mpath,"forge/change@2 must declare protocol: 2."));continue
        rev=m.get("review")or{}
        if not isinstance(rev,dict):continue
        its=rev.get("iterations")
        if not isinstance(its,list)or not its:
            if rev.get("status")=="passed":out.append(_finding(r,mpath,"Protocol 2 review_passed requires a Review Iteration linked to provenance."))
            continue
        bound=[i for i in its if isinstance(i,dict)and i.get("subject_provenance")]
        if not bound and rev.get("status")!="passed":continue
        historical_ids=_committed_review_iteration_ids(r,mpath)
        if historical_ids is _HISTORY_ERROR:
            out.append(_finding(r,mpath,"C-026 could not determine committed Review Iteration identity authority; validation fails closed."));continue
        current_ids=[i.get("id") for i in bound if isinstance(i.get("id"),str)and i.get("id")]
        if len(current_ids)!=len(set(current_ids)):
            out.append(_finding(r,mpath,"C-026 Review Iteration identities are ambiguous or duplicated."));continue
        missing_ids=set(historical_ids)-set(current_ids)
        if missing_ids:
            missing=", ".join(sorted(missing_ids))
            out.append(_finding(r,mpath,f"C-026 immutable Review Iteration identity was removed or replaced: {missing}."));continue
        ppath=mpath.parent/"provenance.yml"; p=_load_mapping(ppath)
        if p is None or p.get("schema")not in{"forge/execution-provenance@1","forge/execution-provenance@2"}:out.append(_finding(r,ppath if ppath.exists()else mpath,"Protocol 2 bound Review Iterations require supported repository-native provenance."));continue
        records=p.get("records")
        if not isinstance(records,list):out.append(_finding(r,ppath,"Protocol 2 provenance records are missing."));continue
        idx={};bad=False
        for rec in records:
            f=_record_fields(rec)
            if f is None or f[0] in idx:bad=True;break
            idx[f[0]]=rec
        if bad:out.append(_finding(r,ppath,"Protocol 2 provenance contains a partial, duplicate, inconsistent, or incomplete immutable revision record."));continue
        for position,it in enumerate(bound):
            rid,sref,rref,status=it.get("revision"),it.get("subject_provenance"),it.get("reviewer_provenance"),it.get("status")
            if not(isinstance(rid,str)and rid and isinstance(sref,str)and sref):out.append(_finding(r,mpath,"A bound Review Iteration requires revision and subject_provenance."));continue
            iid=it.get("id")
            if isinstance(iid,str)and iid:
                ia=_first_committed_review_iteration(r,mpath,iid)
                if ia is _HISTORY_ERROR:out.append(_finding(r,mpath,f"C-026 could not determine committed Review Iteration authority for {iid}; validation fails closed."));continue
                if ia is not None and(ia.get("revision")!=rid or ia.get("subject_provenance")!=sref):out.append(_finding(r,mpath,"C-026 immutable Review Iteration subject binding differs from its first committed authority."));continue
            sub=idx.get(sref)
            if sub is None:out.append(_finding(r,mpath,"Subject provenance was not found; invented IDs are not evidence."));continue
            sa=_first_committed_provenance_record(r,ppath,sref)
            if sa is _HISTORY_ERROR:out.append(_finding(r,ppath,"C-026 could not determine committed immutable subject provenance authority; validation fails closed."));continue
            if sa is not None and sa!=sub:out.append(_finding(r,ppath,"C-026 immutable subject provenance differs from its first committed record; frozen subject authority cannot be rewritten."));continue
            sf=_record_fields(sub);assert sf is not None
            _,srole,sex,sctx,srid,sim=sf
            if srole not in{"implementation","resolution"}or sub["source"].get("assurance")not in{"recorded","verified"}:out.append(_finding(r,mpath,"Review subject must be recorded/verified implementation or resolution provenance."));continue
            if srid!=rid:out.append(_finding(r,mpath,"Review subject provenance does not bind to the logical revision under review."))
            explicit=isinstance(sub.get("revision"),dict)and sub["revision"].get("immutable_ref") is not None
            if explicit and sim[0]=="git_commit":
                if not _git_exists(r,sim[1]):out.append(_finding(r,mpath,"C-026 review subject immutable git commit does not exist in the local repository."))
                elif position==len(bound)-1 and status in{"pending","passed"}and st.get("current")!="complete"and _changed(r,mpath,sim[1]):out.append(_finding(r,mpath,"C-026 review subject changed after its immutable revision freeze; create new subject provenance."))
            if status!="passed":continue
            if not isinstance(rref,str)or not rref:out.append(_finding(r,mpath,"A passed Protocol 2 Review Iteration requires reviewer_provenance."));continue
            reviewer=idx.get(rref)
            if reviewer is None:out.append(_finding(r,mpath,"Reviewer provenance was not found; invented IDs are not proof of independence."));continue
            rf=_record_fields(reviewer);assert rf is not None
            _,rrole,rex,rctx,rrid,rim=rf
            if rrole!="review"or reviewer["source"].get("assurance")not in{"recorded","verified"}:out.append(_finding(r,mpath,"Reviewer provenance must be recorded/verified review provenance."));continue
            if rrid!=rid:out.append(_finding(r,mpath,"Reviewer provenance does not bind to the logical revision under review."))
            if rim!=sim:out.append(_finding(r,mpath,"C-026 concrete revision binding failed: subject and Reviewer provenance reference different immutable revisions."))
            if sex==rex:out.append(_finding(r,mpath,"Strict Review is not independent: Reviewer and subject share the same Execution."))
            if sctx==rctx:out.append(_finding(r,mpath,"Strict Review is context-contaminated: Reviewer and subject share the same Execution Context."))
        if rev.get("status")=="passed"and not any(isinstance(i,dict)and i.get("status")=="passed"for i in its):out.append(_finding(r,mpath,"review.status is passed but no Review Iteration is passed."))
        out.extend(_validate_resolution_verification(r,mpath,m,its,idx))
    return out
_DEC_CLASSES={"product","contract","architectural","technical"}
_DEC_MATERIALITY={"material","non_material"}
_DEC_STATUSES={"open","analyzing","awaiting_decision","resolved","superseded"}
_DEC_OPEN_BLOCKING={"open","analyzing","awaiting_decision"}
_DEC_AUTHORITIES={"human","agent","agent_with_review"}
_DEC_RESOLVED_VIA={"evidence","autonomous_decision","human_decision"}
_DEC_OWNING_BY_CLASS={"product":{"specification"},"contract":{"specification","compatibility"},"architectural":{"architecture"},"technical":{"plan","tasks"}}
_DEC_AUTHORITY_FLOOR={"product":"human","contract":"human"}
_DEC_ID_RE=re.compile(r"^DEC-[0-9]{3,}$")
def render_decision_rules_reference()->str:
    """CHG-0021: render the Decision structural rules `forge validate`
    actually enforces, directly from the constants above -- never a
    hand-duplicated second copy (NFR-001). If this ever disagrees with a
    real `forge validate` rejection, this function is stale; the
    constants above are authoritative."""
    lines=[
        "# Forge Decision Structural Rules",
        "",
        "Generated directly from the constants `forge validate` enforces "
        "(`src/forge_cli/validation/__init__.py`), not hand-maintained "
        "prose. If this disagrees with an actual `forge validate` "
        "rejection, the code is authoritative and this file is stale.",
        "",
        "## Enums",
        "",
        f"- `class`: {', '.join(sorted(_DEC_CLASSES))}",
        f"- `materiality`: {', '.join(sorted(_DEC_MATERIALITY))}",
        f"- `status`: {', '.join(sorted(_DEC_STATUSES))}",
        f"- `authority`: {', '.join(sorted(_DEC_AUTHORITIES))}",
        f"- `resolved_via`: {', '.join(sorted(_DEC_RESOLVED_VIA))} "
        "(or omit while unresolved)",
        "",
        "## `owning_artifact` valid per `class`",
        "",
        *(
            f"- `{cls}` -> {', '.join(sorted(owning))}"
            for cls,owning in sorted(_DEC_OWNING_BY_CLASS.items())
        ),
        "",
        "## Non-negotiable `authority` floor per `class`",
        "",
        *(
            f"- `{cls}` -> `{floor}`"
            for cls,floor in sorted(_DEC_AUTHORITY_FLOOR.items())
        ),
    ]
    return "\n".join(lines)+"\n"
def _dec_finding(r:Path,p:Path,m:str)->ValidationFinding:return ValidationFinding("C-051",str(p.relative_to(r)),m,p)
def _c077_applies(m:dict)->bool:
    change=m.get("change") if isinstance(m.get("change"),dict) else {}
    change_id=change.get("id")
    match=re.fullmatch(r"CHG-(\d+)",change_id) if isinstance(change_id,str) else None
    if match is None:return False
    suffix=match.group(1).lstrip("0") or "0"
    return len(suffix)>2 or len(suffix)==2 and suffix>="25"
def _decision_gates(m:dict)->list[tuple[str,set[str]|None]]:
    """CHG-0013: which already-passed Gates a manifest currently asserts.

    `None` scope means the Gate depends on every owning Artifact
    (before_completion/review_passed); a concrete set means the Gate only
    depends on Decisions owned by those specific Artifacts.
    """
    artifacts=m.get("artifacts")if isinstance(m.get("artifacts"),dict)else{}
    review=m.get("review")if isinstance(m.get("review"),dict)else{}
    state=m.get("state")if isinstance(m.get("state"),dict)else{}
    gates:list[tuple[str,set[str]|None]]=[]
    if artifacts.get("specification_review")in{"complete","passed"}:gates.append(("specification_review_passed",{"specification","compatibility"}))
    if artifacts.get("plan")=="approved" and _c077_applies(m):gates.append(("before_implementation",{"plan"}))
    if artifacts.get("architecture")=="complete":gates.append(("before_implementation",{"architecture"}))
    if review.get("status")=="passed":gates.append(("review_passed",None))
    if state.get("current")=="complete":gates.append(("before_completion",None))
    return gates
def _validate_unresolved_decisions(r:Path,mpath:Path,m:dict)->list[ValidationFinding]:
    """CHG-0013: C-051-C-059 / FR-009/FR-013/FR-014 mechanical slice.

    Protocol-version-independent (unlike Protocol-2-only review provenance):
    absence of `decisions` is the compatibility guard and returns no
    findings, exactly like CHG-0011's `kind`-absence guard.
    """
    out:list[ValidationFinding]=[]
    decisions=m.get("decisions")
    if not decisions:return out
    if not isinstance(decisions,list):return[_dec_finding(r,mpath,"decisions must be a list.")]
    seen_ids:set[str]=set();valid:list[dict]=[]
    for entry in decisions:
        if not isinstance(entry,dict):out.append(_dec_finding(r,mpath,"Each decisions[] entry must be a mapping."));continue
        did,cls,materiality,status,authority,owning,discovered,resolved_via,invalidates=(
            entry.get("id"),entry.get("class"),entry.get("materiality"),entry.get("status"),
            entry.get("authority"),entry.get("owning_artifact"),entry.get("discovered_in"),
            entry.get("resolved_via"),entry.get("invalidates"))
        bad=False
        if not(isinstance(did,str)and _DEC_ID_RE.match(did)):out.append(_dec_finding(r,mpath,f"Decision id {did!r} must match ^DEC-[0-9]{{3,}}$."));bad=True
        elif did in seen_ids:out.append(_dec_finding(r,mpath,f"Duplicate Decision id {did!r}."));bad=True
        else:seen_ids.add(did)
        if cls not in _DEC_CLASSES:out.append(_dec_finding(r,mpath,f"Decision {did!r} has an invalid class {cls!r}."));bad=True
        if materiality not in _DEC_MATERIALITY:out.append(_dec_finding(r,mpath,f"Decision {did!r} has an invalid materiality {materiality!r}."));bad=True
        if status not in _DEC_STATUSES:out.append(_dec_finding(r,mpath,f"Decision {did!r} has an invalid status {status!r}."));bad=True
        if authority not in _DEC_AUTHORITIES:out.append(_dec_finding(r,mpath,f"Decision {did!r} has an invalid authority {authority!r}."));bad=True
        if not(isinstance(owning,str)and owning):out.append(_dec_finding(r,mpath,f"Decision {did!r} is missing owning_artifact."));bad=True
        if not(isinstance(discovered,str)and discovered):out.append(_dec_finding(r,mpath,f"Decision {did!r} is missing discovered_in."));bad=True
        if resolved_via is not None and resolved_via not in _DEC_RESOLVED_VIA:out.append(_dec_finding(r,mpath,f"Decision {did!r} has an invalid resolved_via {resolved_via!r} (expected one of {sorted(_DEC_RESOLVED_VIA)}, or omit while unresolved)."));bad=True
        if invalidates is not None and not(isinstance(invalidates,list)and all(isinstance(x,str)for x in invalidates)):out.append(_dec_finding(r,mpath,f"Decision {did!r} invalidates must be a list of artifact keys."));bad=True
        if bad:continue
        # FR-009/C-054/C-055: resolved_via <-> status consistency. A `superseded`
        # Decision was `resolved` before being superseded and legitimately
        # retains its historical resolved_via; only an Open-blocking status
        # (never yet resolved) must carry none.
        if status in{"resolved","superseded"}and resolved_via is None:out.append(_dec_finding(r,mpath,f"Decision {did!r} is {status!r} but declares no resolved_via."))
        if status in _DEC_OPEN_BLOCKING and resolved_via is not None:out.append(_dec_finding(r,mpath,f"Decision {did!r} declares resolved_via {resolved_via!r} while status is {status!r} (not yet resolved)."))
        if authority=="human"and resolved_via=="autonomous_decision":out.append(_dec_finding(r,mpath,f"Decision {did!r}: human-authority Decisions MUST NOT be resolved via autonomous_decision (C-055)."))
        # CHG-0013-R002: the product/contract authority floor (C-055, FR-017,
        # protocol/policies/decision.yml authority_floor) is a property of the
        # Class itself, not only of the (authority, resolved_via) pair above —
        # a manifest that sets authority away from `human` on a product/contract
        # Decision bypassed the floor entirely under the narrower check alone.
        floor=_DEC_AUTHORITY_FLOOR.get(cls)
        if floor is not None and authority!=floor:
            out.append(_dec_finding(r,mpath,f"Decision {did!r}: class {cls!r} has a non-negotiable authority floor of {floor!r}; authority {authority!r} MUST NOT be declared (C-055)."))
        # INV-003: owning_artifact must be a valid Owning Artifact for the Class.
        allowed_owning=_DEC_OWNING_BY_CLASS.get(cls)
        if allowed_owning is not None and owning not in allowed_owning:
            out.append(_dec_finding(r,mpath,f"Decision {did!r}: owning_artifact {owning!r} is not a valid owning Artifact for class {cls!r} (expected one of {sorted(allowed_owning)})."))
        valid.append(entry)
    # C-051/INV-001: a material, Open-blocking Decision conflicts with any
    # Gate already asserted passed and depending on its owning Artifact.
    gates=_decision_gates(m)
    for entry in valid:
        if entry.get("materiality")!="material"or entry.get("status")not in _DEC_OPEN_BLOCKING:continue
        did,owning=entry.get("id"),entry.get("owning_artifact")
        for gate_name,scope in gates:
            if scope is None or owning in scope:
                out.append(_dec_finding(r,mpath,f"Gate {gate_name!r} MUST NOT be asserted passed while material Decision {did!r} (owned by {owning!r}) remains {entry.get('status')!r} (C-051)."))
    # C-057: a declared invalidation target must actually reflect invalidated
    # status, not silently remain complete/approved.
    artifacts=m.get("artifacts")if isinstance(m.get("artifacts"),dict)else{}
    for entry in valid:
        for key in entry.get("invalidates")or[]:
            if key not in artifacts:
                # CHG-0013-R003: artifacts.get(key) is None for a missing key,
                # which is not in {"complete","approved"} — the check below
                # would silently pass a typo'd or never-tracked artifact key,
                # dropping the invalidation obligation entirely. A declared
                # invalidation target must name a real, tracked Artifact.
                out.append(_dec_finding(r,mpath,f"Decision {entry.get('id')!r} declares invalidates: {key!r}, but {key!r} is not tracked in artifacts at all (C-057)."))
                continue
            current=artifacts.get(key)
            if current in{"complete","approved"}:
                out.append(_dec_finding(r,mpath,f"Decision {entry.get('id')!r} declares invalidates: {key!r}, but artifacts.{key} is still {current!r}; it must become invalidated until revisited (C-057)."))
    return out
def _validate_plan_authorization(r:Path,mpath:Path,m:dict)->list[ValidationFinding]:
    """CHG-0025: C-077 human authority at the Plan/Implementation boundary."""
    change=m.get("change")if isinstance(m.get("change"),dict)else{}
    change_id=change.get("id")
    if not _c077_applies(m):return[]
    state=m.get("state")if isinstance(m.get("state"),dict)else{}
    artifacts=m.get("artifacts")if isinstance(m.get("artifacts"),dict)else{}
    if state.get("current")=="complete"or artifacts.get("plan")!="approved":return[]
    decisions=m.get("decisions")
    if not isinstance(decisions,list):decisions=[]
    try:
        plan_text=(mpath.parent/"plan.md").read_text(encoding="utf-8") if (mpath.parent/"plan.md").is_file() else ""
    except (OSError,UnicodeError):
        plan_text=""
    provenance=_load_mapping(mpath.parent/"provenance.yml")
    provenance_matches=(isinstance(provenance,dict)
                        and provenance.get("schema") in {"forge/execution-provenance@1","forge/execution-provenance@2"}
                        and provenance.get("change")==change_id)
    records=provenance.get("records") if provenance_matches else None
    provenance_confirmation=False
    if isinstance(records,list):
        for record in records:
            fields=_record_fields(record)
            source=record.get("source") if isinstance(record,dict) else None
            if fields is None or not isinstance(source,dict):continue
            _,role,_,_,_,_=fields
            if (
                role=="implementation"
                and source.get("assurance") in {"recorded","verified"}
                and source.get("observed_by")=="operator"
                and source.get("reference")=="plan.md#approval-record"
                and isinstance(source.get("statement"),str)
                and bool(source["statement"].strip())
            ):
                provenance_confirmation=True
                break
    recorded_confirmation=("<!-- forge:plan-approval-confirmation -->" in plan_text
                           and "<!-- forge:plan-approval-record -->" in plan_text
                           and provenance_confirmation)
    matching=[]
    superseded_plan=False
    for entry in decisions:
        if isinstance(entry,dict) and entry.get("owning_artifact")=="plan" and entry.get("status")=="superseded":
            superseded_plan=True
        if not(
            isinstance(entry,dict)
            and entry.get("class")=="technical"
            and entry.get("materiality")=="material"
            and entry.get("owning_artifact")=="plan"
            and entry.get("authority")=="human"
            and entry.get("status")=="resolved"
            and entry.get("resolved_via")=="human_decision"
        ):continue
        matching.append(entry)
    if len(matching)>1:
        return[_deleg_finding(r,mpath,"C-077","Plan authorization is ambiguous: more than one active resolved human Plan Decision exists; supersede all but one before crossing the Plan/Implementation boundary (C-077).")]
    authorized=bool(matching) and recorded_confirmation
    if authorized:return[]
    if superseded_plan:
        return[_deleg_finding(r,mpath,"C-077","Plan authorization is missing: the recorded Plan Decision is superseded and cannot authorize crossing the Plan/Implementation boundary (C-077).")]
    return[_deleg_finding(r,mpath,"C-077",("Plan authorization is missing: an active Change with artifacts.plan: approved MUST record a material "
        "technical Decision owned by plan with authority: human, status: resolved, resolved_via: human_decision, and explicit confirmation in plan.md and provenance.yml before crossing the Plan/Implementation boundary "
        "(C-077)."))]
def _validate_all_unresolved_decisions(r:Path)->list[ValidationFinding]:
    out:list[ValidationFinding]=[];changes=r/".forge/changes"
    if not changes.is_dir():return out
    for mpath in sorted(changes.glob("*/manifest.yml")):
        m=_load_mapping(mpath)
        if m is None:continue
        out.extend(_validate_plan_authorization(r,mpath,m))
        out.extend(_validate_unresolved_decisions(r,mpath,m))
    return out
# --- CHG-0015: Delegated Execution Authority (C-060-C-066) ---------------
_DELEG_ROLE="delegated_task"
def _content_fingerprint(root:Path,rel:str)->str|None:
    target=root/rel
    if not target.exists()or target.is_symlink()or not target.is_file():return None
    q=subprocess.run(["git","hash-object",rel],cwd=root,capture_output=True,text=True,check=False)
    return None if q.returncode else q.stdout.strip()
def _tracked_in_head(root:Path,rel:str)->bool:
    q=subprocess.run(["git","cat-file","-e",f"HEAD:{rel}"],cwd=root,capture_output=True,check=False)
    return q.returncode==0
def _current_dirty_fingerprint(root:Path)->dict[str,str]|None:
    staged=_diff_paths(root,"--cached");unstaged=_diff_paths(root);untracked=_untracked_paths(root)
    if any(x is None for x in(staged,unstaged,untracked)):return None
    paths=set().union(staged or set(),unstaged or set(),untracked or set())
    out:dict[str,str]={}
    for p in paths:
        fp=_content_fingerprint(root,p)
        if fp is not None:
            out[p]=fp
        elif _tracked_in_head(root,p):
            # Preserve tracked deletions as an observable content state. A
            # missing fingerprint must not collapse "deleted" into "not a
            # file" and silently erase the path from the delegate's effect.
            out[p]="<deleted>"
    return out
def _valid_baseline_shape(b:object)->bool:
    if not isinstance(b,dict):return False
    head,dirty=b.get("head"),b.get("dirty")
    if not(isinstance(head,str)and len(head)==40 and all(c in"0123456789abcdefABCDEF"for c in head)):return False
    if not isinstance(dirty,list):return False
    for entry in dirty:
        if not isinstance(entry,dict):return False
        p,h=entry.get("path"),entry.get("hash")
        if not(isinstance(p,str)and p and isinstance(h,str)and h):return False
    return True
def _delegated_execution_effect(root:Path,mpath:Path,baseline:dict,close_revision:str)->set[str]|None:
    """CHG-0015: baseline-vs-now Observed Effect for a delegated_task Execution.

    Generalizes _reviewable_workspace_delta's frozen-commit-vs-current-
    workspace comparison to an arbitrary delegation-open baseline, with a
    content-identity `dirty` map so a delegating Execution's own pre-
    existing uncommitted work is not misattributed to its delegate. The
    review-control-metadata exclusion is reused for the same reason it
    exists elsewhere in this file: the primary Execution's own bookkeeping
    write of this delegate's provenance record is unavoidable noise, not
    part of the delegate's effect. Self-authorization (C-062) is checked
    separately, by history comparison, not by this path-diff.
    """
    if not _git_exists(root,baseline["head"]):return None
    committed=_diff_paths(root,f"{baseline['head']}..{close_revision}")
    if committed is None:return None
    current=_current_dirty_fingerprint(root)
    if current is None:return None
    base_dirty={e["path"]:e["hash"]for e in baseline["dirty"]}
    effect=set(committed)
    for p,fp in current.items():
        if base_dirty.get(p)!=fp:effect.add(p)
    allowed=_review_control_metadata_paths(root,mpath)
    if allowed:effect-=allowed
    return effect
def _deleg_uncovered(paths,scope:list[str])->set[str]:
    """Exact-path coverage check where an empty `scope` legitimately means
    'nothing authorized' (CHG-0015's `minItems: 0` relaxation), unlike
    _uncovered_paths (CHG-0011), which treats an empty scope as malformed
    input because Resolution Scope is never legitimately empty."""
    return {p for p in paths if p not in scope}
def _deleg_close_commit(rec:dict)->str|None:
    rev=rec.get("revision")
    if not isinstance(rev,dict):return None
    im=rev.get("immutable_ref")
    if isinstance(im,dict)and im.get("type")=="git_commit"and isinstance(im.get("value"),str):return im["value"]
    com=rev.get("commit")
    return com if isinstance(com,str)else None
def _deleg_finding(r:Path,p:Path,code:str,m:str)->ValidationFinding:return ValidationFinding(code,str(p.relative_to(r)),m,p)
def _deleg_first_committed_scope(r:Path,path:Path,record_id:str):
    """Like _first_committed_provenance_record, but for delegated_task
    records specifically: _record_fields hardcodes the Protocol-2 Reviewer/
    Resolver role set (implementation/resolution/review) and would reject
    every delegated_task candidate, which is correct for that machinery but
    wrong here. Same 'first committed representation is authority' rule
    (C-026 precedent), narrower acceptance check."""
    documents=_committed_history_mappings(r,path)
    if documents is None:return _HISTORY_ERROR
    for document in documents:
        if document is _HISTORY_ERROR:return _HISTORY_ERROR
        assert isinstance(document,dict)
        records=document.get("records")
        if not isinstance(records,list):continue
        matches=[rec for rec in records if isinstance(rec,dict)and rec.get("id")==record_id and rec.get("role")==_DELEG_ROLE]
        if len(matches)>1:return _HISTORY_ERROR
        if not matches:continue
        scope=matches[0].get("scope")
        return scope if isinstance(scope,list)else _HISTORY_ERROR
    return None
def _validate_delegated_authority(r:Path,mpath:Path)->list[ValidationFinding]:
    out:list[ValidationFinding]=[]
    ppath=mpath.parent/"provenance.yml"
    p=_load_mapping(ppath)
    if p is None or p.get("schema")not in{"forge/execution-provenance@1","forge/execution-provenance@2"}:return out
    records=p.get("records")
    if not isinstance(records,list):return out
    idx:dict[str,dict]={}
    for rec in records:
        if isinstance(rec,dict)and isinstance(rec.get("id"),str)and rec.get("id"):idx[rec["id"]]=rec
    delegated=[rec for rec in records if isinstance(rec,dict)and rec.get("role")==_DELEG_ROLE]
    if not delegated:return out
    prefix=f".forge/changes/{mpath.parent.name}/"
    for deleg in delegated:
        did=deleg.get("id")
        if not(isinstance(did,str)and did):
            out.append(_deleg_finding(r,ppath,"C-060","A delegated_task record is missing a valid id."));continue
        execution,scope,baseline=deleg.get("execution"),deleg.get("scope"),deleg.get("baseline")
        delegated_by=execution.get("delegated_by")if isinstance(execution,dict)else None
        shape_ok=(isinstance(execution,dict)
                  and isinstance(execution.get("id"),str)and execution.get("id")
                  and isinstance(execution.get("context_id"),str)and execution.get("context_id")
                  and isinstance(delegated_by,str)and delegated_by
                  and isinstance(scope,list)and all(isinstance(x,str)and x for x in scope)
                  and _valid_baseline_shape(baseline))
        if not shape_ok:
            out.append(_deleg_finding(r,ppath,"C-060",f"delegated_task record {did!r} has an invalid shape: execution.delegated_by, baseline, and scope (possibly empty) are all required (C-060/FR-001)."));continue
        close_commit=_deleg_close_commit(deleg)
        if close_commit is None:
            out.append(_deleg_finding(r,ppath,"C-060",f"delegated_task record {did!r} has no resolvable immutable revision."));continue
        delegator=idx.get(delegated_by)
        if delegator is None:
            out.append(_deleg_finding(r,ppath,"C-065",f"delegated_task record {did!r}: delegated_by {delegated_by!r} does not reference any record in this ledger; the Delegation Ceiling cannot be established, and validation fails closed."));continue
        # C-063 Delegation Ceiling.
        if delegator.get("role")==_DELEG_ROLE:
            d_scope=delegator.get("scope")
            if not isinstance(d_scope,list):
                out.append(_deleg_finding(r,ppath,"C-065",f"delegated_task record {did!r}: delegator {delegated_by!r} has no valid scope; the Delegation Ceiling cannot be established, and validation fails closed."))
            else:
                excess=_deleg_uncovered(scope,d_scope)
                if excess:out.append(_deleg_finding(r,ppath,"C-063",f"delegated_task record {did!r} was granted scope exceeding its delegator {delegated_by!r}'s own scope: {', '.join(sorted(excess))}."))
        else:
            d_scope=delegator.get("scope")
            if isinstance(d_scope,list):
                excess=_deleg_uncovered(scope,d_scope)
            else:
                excess={x for x in scope if not x.startswith(prefix)}
            if excess:out.append(_deleg_finding(r,ppath,"C-063",f"delegated_task record {did!r} was granted scope exceeding its delegator's Authorized Scope (or the conservative default {prefix!r} when none is declared): {', '.join(sorted(excess))}."))
        # C-061 Out-of-Scope Mutation.
        effect=_delegated_execution_effect(r,mpath,baseline,close_commit)
        if effect is None:
            out.append(_deleg_finding(r,ppath,"C-065",f"delegated_task record {did!r}: Observed Effect could not be determined from local Git history; validation fails closed."))
        else:
            oos=_deleg_uncovered(effect,scope)
            if oos:out.append(_deleg_finding(r,mpath,"C-061",f"delegated_task record {did!r} produced Out-of-Scope Mutation not covered by its declared scope: {', '.join(sorted(oos))}."))
        # C-062 self-authorization: compare against first committed representation.
        first_scope=_deleg_first_committed_scope(r,ppath,did)
        if first_scope is _HISTORY_ERROR:
            out.append(_deleg_finding(r,ppath,"C-065",f"delegated_task record {did!r}: committed provenance history could not be determined; validation fails closed."))
        elif isinstance(first_scope,list)and set(first_scope)!=set(scope):
            out.append(_deleg_finding(r,ppath,"C-062",f"delegated_task record {did!r} declares scope {scope!r} differing from its first committed representation {first_scope!r}; an Execution MUST NOT rewrite the declaration of its own Authority (C-062)."))
    return out
def _validate_all_delegated_authority(r:Path)->list[ValidationFinding]:
    out:list[ValidationFinding]=[];changes=r/".forge/changes"
    if not changes.is_dir():return out
    for mpath in sorted(changes.glob("*/manifest.yml")):
        out.extend(_validate_delegated_authority(r,mpath))
    return out

# --- CHG-0050: semantic User Story obligation -----------------------------
_BEHAVIOR_RE = re.compile(r"^[ ]{0,3}Behavior:\s*(behavioral|technical)\s*$", re.MULTILINE)
_USER_STORY_HEADING_RE = re.compile(r"^[ ]{0,3}###\s+(US-[0-9]{3,})(?:\s|·|$)", re.MULTILINE)

def _markdown_without_fenced_code(markdown: str) -> str:
    lines: list[str] = []
    fence: tuple[str, int] | None = None
    for line in markdown.splitlines():
        match = re.match(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$", line)
        if match and fence is not None:
            delimiter = match.group(1)
            if (delimiter[0] == fence[0] and len(delimiter) >= fence[1]
                    and not match.group(2).strip()):
                fence = None
            continue
        if match:
            delimiter = match.group(1)
            fence = (delimiter[0], len(delimiter))
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)

def _validate_user_story_contract(r: Path, mpath: Path, manifest: dict) -> list[ValidationFinding]:
    change = manifest.get("change")
    if not isinstance(change, dict) or "observable_behavior" not in change:
        return []
    observable = change.get("observable_behavior")
    if not isinstance(observable, bool):
        return [_finding(r, mpath, "change.observable_behavior must be a boolean when present; User Story applicability cannot be determined reliably.")]
    specification_path = mpath.parent / "specification.md"
    flow = manifest.get("flow")
    flow_id = flow.get("current") if isinstance(flow, dict) else None
    if not specification_path.is_file() and flow_id == "fast":
        return []
    try:
        specification = _markdown_without_fenced_code(specification_path.read_text(encoding="utf-8"))
    except OSError:
        return [_finding(r, mpath, "A semantically classified Change must have a readable specification.md; validation fails closed.")]
    declaration = _BEHAVIOR_RE.search(specification)
    expected = "behavioral" if observable else "technical"
    if declaration is None:
        return [_finding(r, specification_path, "Specification Classification must declare Behavior: behavioral or Behavior: technical.")]
    findings: list[ValidationFinding] = []
    if declaration.group(1) != expected:
        findings.append(_finding(r, specification_path, f"Specification Behavior: {declaration.group(1)} does not match manifest change.observable_behavior={observable!r}."))
    ids = _USER_STORY_HEADING_RE.findall(specification)
    duplicates = sorted({story_id for story_id in ids if ids.count(story_id) > 1})
    if duplicates:
        findings.append(_finding(r, specification_path, f"Specification contains duplicate User Story identifier(s): {', '.join(duplicates)}."))
    if observable and not ids:
        findings.append(_finding(r, specification_path, "A behavioral Change Specification must contain at least one stable US-xxx User Story."))
    return findings

def _validate_all_user_story_contracts(r: Path) -> list[ValidationFinding]:
    changes = r / ".forge" / "changes"
    if not changes.is_dir():
        return []
    findings: list[ValidationFinding] = []
    for mpath in sorted(changes.glob("*/manifest.yml")):
        manifest = _load_mapping(mpath)
        if manifest is not None:
            findings.extend(_validate_user_story_contract(r, mpath, manifest))
    return findings

_STORY_TRACEABILITY_STATES = {"implementation", "verification", "review", "complete"}

def _validate_user_story_traceability(r: Path, mpath: Path, manifest: dict) -> list[ValidationFinding]:
    change = manifest.get("change")
    if not isinstance(change, dict) or change.get("observable_behavior") is not True:
        return []
    flow = manifest.get("flow")
    flow_id = flow.get("current") if isinstance(flow, dict) else None
    state = manifest.get("state")
    current = state.get("current") if isinstance(state, dict) else None
    if current not in _STORY_TRACEABILITY_STATES:
        return []
    specification_path = mpath.parent / "specification.md"
    if flow_id == "fast" and not specification_path.is_file():
        return []
    try:
        specification = _markdown_without_fenced_code(specification_path.read_text(encoding="utf-8"))
    except OSError:
        return [_finding(r, specification_path, "User Story traceability cannot be determined without a readable specification.md; validation fails closed.")]
    story_ids = set(_USER_STORY_HEADING_RE.findall(specification))
    traceability_path = mpath.parent / "traceability.yml"
    tasks_path = mpath.parent / "tasks.md"
    try:
        task_text = _markdown_without_fenced_code(tasks_path.read_text(encoding="utf-8"))
    except OSError:
        task_text = ""
    completed_tasks = set(re.findall(r"^[ ]{0,3}-\s*\[[xX]\]\s+(T-[0-9]{3,})\b", task_text, re.MULTILINE))
    acceptance_ids = set(re.findall(r"^[ ]{0,3}#{4,5}\s+(AC-[0-9]{3,})\b", specification, re.MULTILINE))
    try:
        verification_text = _markdown_without_fenced_code((mpath.parent / "verification.md").read_text(encoding="utf-8"))
    except OSError:
        verification_text = ""
    traceability = _load_mapping(traceability_path)
    if traceability is None:
        return [_finding(r, traceability_path, "A behavioral Change in Implementation or beyond must provide traceability.yml with Task and Verification links for every User Story.")]
    stories = traceability.get("stories")
    if not isinstance(stories, dict):
        return [_finding(r, traceability_path, "traceability.yml must contain a stories mapping for every User Story before Implementation can be completed.")]
    findings: list[ValidationFinding] = []
    for story_id in sorted(story_ids):
        entry = stories.get(story_id)
        if not isinstance(entry, dict):
            findings.append(_finding(r, traceability_path, f"User Story {story_id} has no traceability entry."))
            continue
        tasks = entry.get("tasks")
        verification = entry.get("verification")
        if not isinstance(tasks, list) or not tasks or not all(isinstance(item, str) and item for item in tasks):
            findings.append(_finding(r, traceability_path, f"User Story {story_id} must reference at least one executable Task."))
        elif any(item not in completed_tasks for item in tasks):
            missing = ", ".join(item for item in tasks if item not in completed_tasks)
            findings.append(_finding(r, traceability_path, f"User Story {story_id} references Task(s) without completed repository-native evidence: {missing}."))
        if not isinstance(verification, list) or not verification or not all(isinstance(item, str) and item for item in verification):
            findings.append(_finding(r, traceability_path, f"User Story {story_id} must reference at least one Verification evidence item."))
        else:
            passing = {
                match.group(1)
                for match in re.finditer(
                    r"^[ ]{0,3}\|\s*(AC-[0-9]{3,})\s*\|[^\n|]*\|\s*PASS\s*\|",
                    verification_text,
                    re.MULTILINE,
                )
            }
            missing = [item for item in verification if item not in acceptance_ids or item not in passing]
            if missing:
                findings.append(_finding(r, traceability_path, f"User Story {story_id} references Verification item(s) without passing repository-native evidence: {', '.join(missing)}."))
    for story_id in sorted(stories):
        if story_id not in story_ids:
            findings.append(_finding(r, traceability_path, f"Traceability story {story_id} is not present in specification.md."))
    return findings

def _validate_all_user_story_traceability(r: Path) -> list[ValidationFinding]:
    changes = r / ".forge" / "changes"
    if not changes.is_dir():
        return []
    findings: list[ValidationFinding] = []
    for mpath in sorted(changes.glob("*/manifest.yml")):
        manifest = _load_mapping(mpath)
        if manifest is not None:
            findings.extend(_validate_user_story_traceability(r, mpath, manifest))
    return findings
_PROFILE_RANK={"focused":0,"standard":1,"strict":2}
def _validate_review_profile_floor(root:Path,path:Path,effective:dict)->list[ValidationFinding]:
    canonical=effective.get("canonical")if isinstance(effective,dict)else None
    canonical_flow=canonical.get("flow")if isinstance(canonical,dict)else None
    canonical_review=canonical_flow.get("review")if isinstance(canonical_flow,dict)else None
    canonical_profile=canonical_review.get("profile","strict")if isinstance(canonical_review,dict)else"strict"
    project=effective.get("project")if isinstance(effective,dict)else None
    project_review=project.get("review")if isinstance(project,dict)else None
    if not isinstance(project_review,dict)or"profile"not in project_review:return[]
    project_profile=project_review["profile"]
    if _PROFILE_RANK.get(project_profile,-1)<_PROFILE_RANK.get(canonical_profile,0):
        return[ValidationFinding("E_FORGE_REVIEW_PROFILE_BELOW_FLOOR",str(path.relative_to(root)),
            f"Project Flow declares review.profile={project_profile!r}, weaker than the canonical floor {canonical_profile!r} for this Flow.",path)]
    return[]
def validate_project(project_root:Path,protocol_root:Path)->ValidationResult:
    f=project_root/".forge"
    if not f.is_dir():return ValidationResult((ValidationFinding("E_FORGE_NOT_INITIALIZED",".forge/","Forge is not initialized. Run `forge init` from this Git repository.",f),))
    try:cfg=load_project_configuration(f/"forge.yml")
    except(UnsupportedProtocolVersionError,InvalidProjectConfigurationError)as e:return ValidationResult((ValidationFinding(e.code,".forge/forge.yml",str(e),f/"forge.yml"),))
    pid=cfg["forge"]["protocol"];out=[];fd=f/"flows"
    if fd.is_dir():
        for p in sorted(fd.glob("*.yml")):
            try:effective=resolve_effective_flow(protocol_root,project_root,p.stem,pid)
            except UnknownCanonicalFlowError as e:out.append(ValidationFinding("E_FORGE_UNKNOWN_CANONICAL_FLOW",str(p.relative_to(project_root)),str(e),p));continue
            except InvalidProjectFlowConfigurationError as e:out.append(ValidationFinding("E_FORGE_INVALID_PROJECT_FLOW",str(p.relative_to(project_root)),str(e),p));continue
            out.extend(_validate_review_profile_floor(project_root,p,effective))
    try:resolve_effective_contract(protocol_root,project_root,pid)
    except CanonicalContractUnavailableError as e:out.append(ValidationFinding("E_FORGE_CANONICAL_CONTRACT_UNAVAILABLE",f"protocol/{pid}/contract/engineering.md",str(e),protocol_root))
    if pid==2:out.extend(_validate_protocol2_review_provenance(project_root))
    out.extend(_validate_all_unresolved_decisions(project_root))
    out.extend(_validate_all_delegated_authority(project_root))
    out.extend(_validate_all_user_story_contracts(project_root))
    out.extend(_validate_all_user_story_traceability(project_root))
    return ValidationResult(tuple(out))
