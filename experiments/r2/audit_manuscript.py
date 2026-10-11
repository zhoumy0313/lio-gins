"""Verify all rendered table cells, missing placeholders, page count, and warnings."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);version=Path(sys.argv[1]);source=ROOT/'artifacts/r2/S3/summary_table.json';rows=json.loads(source.read_text());bindings=json.loads((version/'table_cell_bindings.json').read_text());sha=hashlib.sha256(source.read_bytes()).hexdigest();checks=0
for cell in bindings:
    row=next(r for r in rows if r['cache']==cell['cache'] and r['method']==cell['method']);assert row[cell['field']]==cell['raw_value'];assert cell['summary_SHA']==sha;checks+=1
pdf=version/'main.pdf';text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True);(OUT/'extracted_manuscript.txt').write_text(text);assert 'TBD_WITH_EVIDENCE' not in text;assert 'NOT_SUBMISSION_READY' in text
info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);pages=int(next(x.split(':')[1] for x in info.splitlines() if x.startswith('Pages:')));assert pages<=6
fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True);(OUT/'pdffonts.txt').write_text(fonts);fontrows=fonts.splitlines()[2:];assert all(line.split()[-5]=='yes' for line in fontrows)
log=(version/'main.log').read_text(errors='replace');assert 'Overfull' not in log;assert 'Undefined control sequence' not in log;assert 'LaTeX Error' not in log;assert 'undefined references' not in log.lower()
abstract=(version/'main.tex').read_text().split('\\begin{abstract}')[1].split('\\end{abstract}')[0]
terms={word:[abstract[max(0,m.start()-80):m.end()+80] for m in re.finditer(word,abstract,re.I)] for word in ['improv','reduc','faster','robust','novel','superior']}
audit={'pages':pages,'table_cells_verified':checks,'all_table_raw_values_and_summary_SHA_match':True,'all_font_rows_embedded':True,'overfull_boxes':0,'compile_errors':0,'undefined_references':0,'final_placeholders':False,'NOT_SUBMISSION_READY_marker_present':True,'abstract_comparison_contexts':terms,'PDF_SHA':hashlib.sha256(pdf.read_bytes()).hexdigest(),'manuscript_SHA':hashlib.sha256((version/'main.tex').read_bytes()).hexdigest(),'rendered_page_visual_audit':'separately recorded by Codex; human author review pending','scientific_approval':'not asserted'}
(OUT/'manuscript_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
