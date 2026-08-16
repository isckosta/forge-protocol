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
def _reviewable_workspace_delta(r:Path,m:Path,c:str)->set[str]|None:
    root=_git_root(r)
    if root is None:return None
    committed=_diff_paths(root,f"{c}..HEAD");staged=_diff_paths(root,"--cached");unstaged=_diff_paths(root);untracked=_untracked_paths(root)
    if any(x is None for x in(committed,staged,unstaged,untracked)):return None
    changed=set().union(committed or set(),staged or set(),unstaged or set(),untracked or set())
    try:d=m.parent.resolve().relative_to(root).as_posix()
    except ValueError:return changed
    allowed={f"{d}/manifest.yml",f"{d}/provenance.yml",f"{d}/review.md"};reviewable=set()
    for path in changed:
        if path not in allowed:
            reviewable.add(path);continue
        target=root/Path(path)
        if not target.exists()or target.is_symlink()or not target.is_file():reviewable.add(path)
    return reviewable
def _changed(r:Path,m:Path,c:str)->bool:
    delta=_reviewable_workspace_delta(r,m,c)
    return delta is None or bool(delta)
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