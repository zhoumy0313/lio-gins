"""Build a new review version from complete S9 evidence; preserve all old drafts."""
import json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text());route=state['included_routes'][0]
def record(purpose,script,args=(),timeout=300,inputs=()):
    argv=[sys.executable,str(ROOT/'experiments/s9'/route/'record_run.py'),'--stage','D','--purpose',purpose,'--input',str(ROOT/'experiments/s9'/script),'--timeout',str(timeout)]
    for p in inputs:argv+=['--input',str(p)]
    argv+=['--',sys.executable,str(ROOT/'experiments/s9'/script),*map(str,args)]
    p=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True);print(p.stdout,flush=True)
    receipt=json.loads(p.stdout.splitlines()[-1]);out=Path(receipt['output'])
    return p.returncode,out
version=ROOT/'paper/versions/s9_r03'
assert version.exists()
rc,build=record('full_multiscenario_six_page_PDF_build','build_paper.py',[version],timeout=300,inputs=[version/'main.tex',version/'generated_tables.tex',version/'references.bib'])
for name in ['main.pdf','main.log','main.bbl','pdfinfo.txt','build_audit.json']:
    if (build/name).exists():shutil.copy2(build/name,version/name)
if rc:
    print('Compile/page failure retained with its complete version. Create a separate typography revision, retaining this source/PDF and actual failure.',flush=True);raise SystemExit(rc)
rc,audit=record('all_table_narrative_event_bindings_fonts_and_pages','audit_manuscript.py',[version]);assert rc==0
shutil.copy2(audit/'manuscript_audit.json',ROOT/'artifacts/s9/manuscript_audit.json')
candidate=ROOT/'paper/submission_candidate/s9';shutil.copytree(version,candidate)
rc,report=record('complete_route_signs_failures_provenance_and_author_brief','report.py');assert rc==0
for name in ['EXPERIMENT_REPORT.md','AUTHOR_BRIEF_ZH.md','CLAIM_EVIDENCE_MAP.json']:shutil.copy2(report/name,ROOT/'docs/research_s9'/name)
for p in report.glob('*_fallback_events.json'):shutil.copy2(p,ROOT/'artifacts/s9'/p.name)
state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text());state.update(paper_version='s9_r03',review_PDF='paper/submission_candidate/s9/main.pdf',manuscript_audit_run=str(audit),paper_report_run=str(report));state['flags']['full_review_pdf_ready']=False
(ROOT/'docs/research_s9/STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print('Complete PDF/numeric audit ready; every PDF page visual review and final E audit remain.',flush=True)
