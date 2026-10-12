"""Independent source/cell/figure/PDF check for a complete new S10 manuscript."""
import csv,json,math,os,re,subprocess,sys
from pathlib import Path
from common import ROOT,sha
version=Path(sys.argv[1]).resolve();OUT=Path(os.environ['LIO_GINS_S10_OUT'])
assert version.is_relative_to(ROOT/'paper') and 's10' in version.name
bindings=json.loads((version/'numeric_bindings.json').read_text());numbers=(version/'numbers.tex').read_text()
validated=[]
for key,b in bindings.items():
 source=ROOT/b['source'];assert sha(source)==b['source_SHA']
 op=b['operation']
 if op=='json_number':
  raw=json.loads(source.read_text())
  for step in b['pointer']:raw=raw[step]
 elif op=='text_number':
  assert b['text_number'] in source.read_text();raw=float(b['text_number'])
 else:
  selected=[x for x in csv.DictReader(source.open()) if all(x[k]==str(v) for k,v in b['row'].items())]
  assert len(selected)==(3 if op=='sum_three' else 1)
  raw=sum(int(x[b['field']]) for x in selected) if op=='sum_three' else selected[0][b['field']]
 assert raw==b['raw'],key
 if op=='max_json':
  values=json.loads(raw);assert len(values)==3;value=None if any(x is None for x in values) else max(values)
 elif op=='percent':value=float(raw)*100
 elif op=='bool':assert raw in ['True','False'];value='Y' if raw=='True' else 'N'
 else:value=None if raw=='' else float(raw)
 assert value is None or isinstance(value,str) or math.isfinite(value)
 rendered='C180' if value is None else value if isinstance(value,str) else format(value,b['format'])
 assert rendered==b['display']
 assert r'\csname S'+key+r'\endcsname{'+rendered+'}' in numbers
 validated.append(key)
tex='\n'.join(p.read_text() for p in version.glob('*.tex') if p.name!='numbers.tex');used=set(re.findall(r'\\val\{([^}]+)\}',tex));assert used<=set(bindings),used-set(bindings)
assert (version/'street_table.tex').read_text().count(' & ')==20*5
assert (version/'routes_table.tex').read_text().count(' & ')==7*7
assert (version/'event_table.tex').read_text().count(' & ')==4*7
# Header rows add one: count full table body with line ending and exclude header.
for name,expected in [('street_table.tex',19),('routes_table.tex',6),('event_table.tex',3)]:
 body=[x for x in (version/name).read_text().splitlines() if '\\val{' in x];assert len(body)==expected
fm=json.loads((ROOT/'artifacts/s10/figures/figure_manifest.json').read_text());copied=json.loads((version/'figure_sources.json').read_text())
assert sha(ROOT/copied['manifest_path'])==copied['manifest_SHA']
for name,digest in copied['copied_vector_SHA'].items():assert sha(version/name)==digest and fm['figures'][Path(name).name]==digest
for name,digest in fm['points_files'].items():assert sha(ROOT/'artifacts/s10/figures'/name)==digest
info=subprocess.check_output(['pdfinfo',str(version/'main.pdf')],text=True);pages=int(re.search(r'^Pages:\s*(\d+)',info,re.M)[1]);assert pages<=6
log=(version/'main.log').read_text();assert not any(x in log for x in ['Overfull','undefined','Undefined','multiply defined'])
text=subprocess.check_output(['pdftotext',str(version/'main.pdf'),'-'],text=True)
for marker in ['post-hoc','no-decay','142','C180','building02','independent','3.6013','15-s']:
 assert marker.lower() in text.lower(),marker
assert len(re.findall(r'\[\d+\]',text))>=7
fonts=subprocess.check_output(['pdffonts',str(version/'main.pdf')],text=True);(OUT/'pdffonts.txt').write_text(fonts)
fontrows=fonts.splitlines()[2:];assert fontrows and all(re.search(r'\byes\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$',r) for r in fontrows),'unembedded font'
result={'validated_source_cells':len(validated),'used_macro_count':len(used),'unused_source_keys':sorted(set(bindings)-used),'pages':pages,'all19_street_all6_routes_all3_events':True,'missing_censored_not_filled':True,'PDF_SHA':sha(version/'main.pdf'),'source_SHA':{str(p.relative_to(version)):sha(p) for p in version.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.pdf','.svg','.json']},'negative_evidence_present':True,'embedded_fonts':True,'no_layout_or_reference_errors':True}
(OUT/'numeric_paper_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_SHA'}))
