import subprocess
from pathlib import Path
import pytest, yaml
from typer.testing import CliRunner
from forge_cli.app import app
runner = CliRunner()

def init(root: Path, protocol=2):
    subprocess.run(["git","init",str(root)],check=True,capture_output=True); subprocess.run(["git","config","user.email","t@x"],cwd=root,check=True); subprocess.run(["git","config","user.name","T"],cwd=root,check=True)
    f=root/".forge"; f.mkdir(); (f/"forge.yml").write_text(f"schema: forge/project@1\nproject:\n  name: t\nforge:\n  protocol: {protocol}\nflows:\n  default: full\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n")

def commit(root: Path, msg: str):
    subprocess.run(["git","add","."],cwd=root,check=True); subprocess.run(["git","commit","-m",msg],cwd=root,check=True,capture_output=True); return subprocess.run(["git","rev-parse","HEAD"],cwd=root,check=True,capture_output=True,text=True).stdout.strip()

def write(root: Path, s: str, r: str|None, *, status="passed", flow="full", sr="revision-a", rr="revision-a", same_exec=False, same_ctx=False):
    d=root/".forge/changes/CHG-9999-binding"; d.mkdir(parents=True,exist_ok=True)
    it={"id":"review-001","revision":"revision-a","subject_provenance":"resolution-001","status":status};
    if status=="passed": it["reviewer_provenance"]="review-001"
    m={"schema":"forge/change@2","protocol":2,"change":{"id":"CHG-9999","title":"Binding","kind":"bugfix"},"flow":{"initial":flow,"current":flow,"escalations":[]},"state":{"current":"strict_review"},"artifacts":{},"tdd":{"status":"compliant","cycles":1},"verification":{"status":"passed"},"review":{"status":status,"iteration":1,"blockers":0,"majors":0,"minors":0,"observations":0,"iterations":[it]},"documentation":{"impact_evaluated":True,"update_required":False}}
    def rec(i,role,rev,sha,ex,ctx): return {"id":i,"role":role,"execution":{"id":ex,"context_id":ctx},"recorded_at":"2026-08-15T19:00:00Z","revision":{"id":rev,"immutable_ref":{"type":"git_commit","value":sha},"commit":sha},"source":{"assurance":"recorded","observed_by":"self"}}
    records=[rec("resolution-001","resolution",sr,s,"x" if same_exec else "se","c" if same_ctx else "sc")]
    if r: records.append(rec("review-001","review",rr,r,"x" if same_exec else "re","c" if same_ctx else "rc"))
    (d/"manifest.yml").write_text(yaml.safe_dump(m,sort_keys=False)); (d/"provenance.yml").write_text(yaml.safe_dump({"schema":"forge/execution-provenance@1","change":"CHG-9999","records":records},sort_keys=False)); return d

def validate(root, monkeypatch): monkeypatch.chdir(root); return runner.invoke(app,["validate"])

def test_same_id_same_commit_passes(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,a); assert validate(tmp_path,monkeypatch).exit_code==0

def test_same_id_different_commit_fails(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); b=commit(tmp_path,"b"); write(tmp_path,a,b); assert validate(tmp_path,monkeypatch).exit_code==2

def test_missing_all_immutable_refs_fails(tmp_path,monkeypatch):
    init(tmp_path); a=commit(tmp_path,"a"); d=write(tmp_path,a,a); p=yaml.safe_load((d/"provenance.yml").read_text()); p["records"][0]["revision"].pop("immutable_ref"); p["records"][0]["revision"].pop("commit"); (d/"provenance.yml").write_text(yaml.safe_dump(p,sort_keys=False)); assert validate(tmp_path,monkeypatch).exit_code==2

def test_wrong_subject_commit_fails(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,"f"*40,"f"*40); assert validate(tmp_path,monkeypatch).exit_code==2

def test_pending_subject_freeze_passes(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,None,status="pending"); assert validate(tmp_path,monkeypatch).exit_code==0

def test_post_freeze_subject_change_fails(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,None,status="pending"); (tmp_path/"subject.txt").write_text("changed"); commit(tmp_path,"changed"); assert validate(tmp_path,monkeypatch).exit_code==2

def test_review_metadata_after_freeze_passes(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); d=write(tmp_path,a,None,status="pending"); (d/"review.md").write_text("review"); commit(tmp_path,"review metadata"); assert validate(tmp_path,monkeypatch).exit_code==0
@pytest.mark.parametrize("flow",["fast","standard","full"])
def test_all_flows_pass_with_binding(tmp_path,monkeypatch,flow): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,a,flow=flow); assert validate(tmp_path,monkeypatch).exit_code==0

def test_protocol1_compatibility(tmp_path,monkeypatch): init(tmp_path,1); assert validate(tmp_path,monkeypatch).exit_code==0

def test_shared_execution_still_fails(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,a,same_exec=True); assert validate(tmp_path,monkeypatch).exit_code==2

def test_shared_context_still_fails(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,a,same_ctx=True); assert validate(tmp_path,monkeypatch).exit_code==2

def test_wrong_revision_id_still_fails(tmp_path,monkeypatch): init(tmp_path); a=commit(tmp_path,"a"); write(tmp_path,a,a,rr="revision-b"); assert validate(tmp_path,monkeypatch).exit_code==2
