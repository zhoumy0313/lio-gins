"""Copy completed R2 logs into an exclusive lightweight archive; never modify old runs."""
import csv,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for run in sorted((ROOT/'outputs_r2').iterdir()):
    if not run.is_dir() or run==OUT:continue
    m=json.loads((run/'manifest.json').read_text());assert m['status']!='RUNNING'
    for name in ['stdout.log','stderr.log']:
        source=run/name;assert source.stat().st_size<=2**21,'retain a larger log separately rather than truncate'
        dest=OUT/'run_logs'/run.name/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);expected=sha(source);assert sha(dest)==expected
        rows.append({'run_id':run.name,'stage':m['stage'],'exit_code':m['exit_code'],'source':str(source.relative_to(ROOT)),'archive':str(dest.relative_to(OUT)),'bytes':source.stat().st_size,'SHA':expected})
(OUT/'log_archive_index.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'completed_runs':len(rows)//2,'logs':len(rows),'bytes':sum(r['bytes'] for r in rows),'all_copy_SHA_equal':True,'failures_retained':sorted({r['run_id'] for r in rows if r['exit_code']!=0})}))
