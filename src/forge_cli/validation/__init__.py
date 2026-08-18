"""Forge validation boundary."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
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
    """CHG-0011: committed diff between two already-frozen historical commits.

    Unlike _reviewable_workspace_delta (a frozen commit vs. the *current*
    workspace), both endpoints here are immutable history, so only the
    committed-diff half of that machinery applies.
    """
    root=_git_root(r)
    if root is None:return None
    diff=_diff_paths(root,f"{from_commit}..{to_commit}")
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
        if _record_fields(candidate) is None:return _HISTORY_ERROR
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
        if p is None or p.get("schema")!="forge/execution-provenance@1":out.append(_finding(r,ppath if ppath.exists()else mpath,"Protocol 2 bound Review Iterations require supported repository-native provenance."));continue
        records=p.get("records")
        if not isinstance(records,list):out.append(_finding(r,ppath,"Protocol 2 provenance records are missing."));continue
        idx={};bad=False
        for rec in records:
            f=_record_fields(rec)
            if f is None or f[0] in idx:bad=True;break
            idx[f[0]]=rec
        if bad:out.append(_finding(r,ppath,"Protocol 2 provenance contains a partial, duplicate, inconsistent, or incomplete immutable revision record."));continue
        for it in bound:
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
                elif status in{"pending","passed"} and _changed(r,mpath,sim[1]):out.append(_finding(r,mpath,"C-026 review subject changed after its immutable revision freeze; create new subject provenance."))
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
def validate_project(project_root:Path,protocol_root:Path)->ValidationResult:
    f=project_root/".forge"
    if not f.is_dir():return ValidationResult((ValidationFinding("E_FORGE_NOT_INITIALIZED",".forge/","Forge is not initialized. Run `forge init` from this Git repository.",f),))
    try:cfg=load_project_configuration(f/"forge.yml")
    except(UnsupportedProtocolVersionError,InvalidProjectConfigurationError)as e:return ValidationResult((ValidationFinding(e.code,".forge/forge.yml",str(e),f/"forge.yml"),))
    pid=cfg["forge"]["protocol"];out=[];fd=f/"flows"
    if fd.is_dir():
        for p in sorted(fd.glob("*.yml")):
            try:resolve_effective_flow(protocol_root,project_root,p.stem,pid)
            except UnknownCanonicalFlowError as e:out.append(ValidationFinding("E_FORGE_UNKNOWN_CANONICAL_FLOW",str(p.relative_to(project_root)),str(e),p))
            except InvalidProjectFlowConfigurationError as e:out.append(ValidationFinding("E_FORGE_INVALID_PROJECT_FLOW",str(p.relative_to(project_root)),str(e),p))
    try:resolve_effective_contract(protocol_root,project_root,pid)
    except CanonicalContractUnavailableError as e:out.append(ValidationFinding("E_FORGE_CANONICAL_CONTRACT_UNAVAILABLE",f"protocol/{pid}/contract/engineering.md",str(e),protocol_root))
    if pid==2:out.extend(_validate_protocol2_review_provenance(project_root))
    return ValidationResult(tuple(out))