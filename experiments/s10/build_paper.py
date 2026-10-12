"""Compile a preserved new S10 version; reject excess pages or broken layout."""
import json,os,subprocess,sys
from pathlib import Path
from common import ROOT,sha
OUT=Path(os.environ['LIO_GINS_S10_OUT']);version=Path(sys.argv[1]).resolve()
assert version.is_relative_to(ROOT/'paper/versions') and version.name.startswith('s10_')
env=os.environ.copy();env['TECTONIC_CACHE_DIR']=str(ROOT/'cache/r2/tectonic_bundle');env['HTTPS_PROXY']=env['HTTP_PROXY']='http://127.0.0.1:7890'
binary=ROOT/'cache/r2/tools/tectonic';argv=[str(binary),'-X','compile','main.tex','--outdir',str(OUT),'--keep-logs','--keep-intermediates','--untrusted']
print(json.dumps({'argv':argv,'source':str(version)}),flush=True)
rc=subprocess.call(argv,cwd=version,env=env)
if rc:raise SystemExit(rc)
info=subprocess.check_output(['pdfinfo',str(OUT/'main.pdf')],text=True);(OUT/'pdfinfo.txt').write_text(info)
pages=int(next(x.split(':')[1] for x in info.splitlines() if x.startswith('Pages:')))
log=(OUT/'main.log').read_text();issues=[x for x in log.splitlines() if any(t in x for t in ['Overfull','undefined','Undefined','multiply defined'])]
files=[p for p in version.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.pdf','.svg','.json'} and p.name!='main.pdf']
audit={'pages':pages,'within_six_pages':pages<=6,'layout_or_reference_errors':issues,'PDF_SHA256':sha(OUT/'main.pdf'),'compiler_SHA256':sha(binary),'sources':{str(p.relative_to(version)):sha(p) for p in files},'new_scientific_run':False}
(OUT/'build_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
raise SystemExit(0 if pages<=6 and not issues else 2)
