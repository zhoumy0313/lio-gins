"""Compile a retained version with a project-local compiler and bundle cache."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ['LIO_GINS_RUN_DIR']);version=Path(sys.argv[1]).resolve()
env=os.environ.copy();env['TECTONIC_CACHE_DIR']=str(ROOT/'cache/r2/tectonic_bundle')
env['HTTPS_PROXY']=env['HTTP_PROXY']='http://127.0.0.1:7890'
binary=ROOT/'cache/r2/tools/tectonic'
argv=[str(binary),'-X','compile','main.tex','--outdir',str(OUT),'--keep-logs','--keep-intermediates','--untrusted']
print(json.dumps({'argv':argv,'source':str(version)}),flush=True)
rc=subprocess.call(argv,cwd=version,env=env)
if rc:raise SystemExit(rc)
pdf=OUT/'main.pdf';info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
(OUT/'pdfinfo.txt').write_text(info)
pages=int(next(line.split(':')[1] for line in info.splitlines() if line.startswith('Pages:')))
source_files=[f for f in version.rglob('*') if f.is_file() and (f.suffix in {'.tex','.bib','.tikz'} or (f.parent.name=='figures' and f.suffix in {'.pdf','.svg'}) or f.name in {'table_cell_bindings.json','figure_sources.json','narrative_numeric_bindings.json'})]
result={'pages':pages,'within_six_pages':pages<=6,'PDF_SHA256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'compiler_SHA256':hashlib.sha256(binary.read_bytes()).hexdigest(),'source_selection':'TeX/BibTeX/TikZ, vector figure sources and numeric/figure bindings; excludes prior compiled outputs','sources':{str(f.relative_to(version)):hashlib.sha256(f.read_bytes()).hexdigest() for f in source_files}}
(OUT/'build_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));raise SystemExit(0 if pages<=6 else 2)
