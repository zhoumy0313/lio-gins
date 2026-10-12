"""Review all table bindings, compile integrity, fonts, and scientific markers."""
import json,os,re,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);version=Path(sys.argv[1]);bindings=json.loads((version/'table_cell_bindings.json').read_text());memo={}
for cell in bindings:
 source=Path(cell['summary_source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==cell['summary_SHA']
 if str(source) not in memo:memo[str(source)]=json.loads(source.read_text())
 row=next(r for r in memo[str(source)] if r['cache']==cell['cache'] and r['method']==cell['method']);assert row[cell['field']]==cell['raw_value']
 value=cell['raw_value'];field=cell['field'];expected=('yes' if value else 'no') if field=='service_qualified' else (str(value)+'/'+str(row['bias_exposed_rows'])) if field=='bias_accepted_rows' else 'C180' if value is None else f'{value:.3f}'
 assert cell['rendered']==expected
 pdf=version/'main.pdf'
for binding in json.loads((version/'narrative_numeric_bindings.json').read_text()):
 p=Path(binding['source']);assert hashlib.sha256(p.read_bytes()).hexdigest()==binding['SHA'];row=next(r for r in json.loads(p.read_text()) if r['method']==binding['method'] and r['cache']==binding['route']);assert row[binding['field']]==binding['raw_value'];precision=1 if binding['field']=='clean_latency_max_s' else 3
 assert binding['rendered']==('censored' if binding['raw_value'] is None else f"{binding['raw_value']:.{precision}f}")
for binding in json.loads((version/'event_numeric_bindings.json').read_text()):
 p=Path(binding['source']);assert hashlib.sha256(p.read_bytes()).hexdigest()==binding['SHA'];row=next(r for r in json.loads(p.read_text()) if r['method']==binding['method'] and r['case']==binding['case'] and r['cache']==binding['route']);e=row['events'][binding['event']];field=binding['field'];v=e['post_return']['90']['horizontal_RMSE_m'] if field=='post_return.90.horizontal_RMSE_m' else e[field];assert v==binding['raw_value']
 rendered=('missing' if v is None else f'{v:.3f}') if field=='post_return.90.horizontal_RMSE_m' else ('C180' if v is None else f'{v:.0f}') if field=='T_admit_s' else str(v)+'/'+str(e['injected_rows_exposed']);assert rendered==binding['rendered']

text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True);(OUT/'extracted_manuscript.txt').write_text(text);assert 'NOT_SUBMISSION_READY' in text and 'TBD_WITH_EVIDENCE' not in text
info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);pages=int(next(line.split(':')[1] for line in info.splitlines() if line.startswith('Pages:')));assert pages<=6
fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True);(OUT/'pdffonts.txt').write_text(fonts);assert all(line.split()[-5]=='yes' for line in fonts.splitlines()[2:])
log=(version/'main.log').read_text(errors='replace')
for bad in ['Overfull','Undefined control sequence','LaTeX Error','undefined references']:assert bad.lower() not in log.lower(),bad
source=(version/'main.tex').read_text();assert all(k in source for k in ['building01','parking00','street00','playground00','Clock90','NIS30'])
audit={'pages':pages,'table_cells_verified':len(bindings),'new_narrative_cells_verified':len(json.loads((version/'narrative_numeric_bindings.json').read_text())),'all_registered_event_cells_verified':len(json.loads((version/'event_numeric_bindings.json').read_text())),'all_rendered_values_and_source_SHA_match':True,'all_fonts_embedded':True,'overfull_boxes':0,'compile_errors':0,'undefined_references':0,'NOT_SUBMISSION_READY_retained':True,'AI_disclosure':'Acknowledgments section and Methods verification; human approval pending','PDF_SHA':hashlib.sha256(pdf.read_bytes()).hexdigest(),'source_SHA':hashlib.sha256(source.encode()).hexdigest(),'human_author_review_complete':False};(OUT/'manuscript_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
