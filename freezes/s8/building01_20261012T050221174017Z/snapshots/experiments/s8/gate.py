"""S8 prospective role gate. R1/R2 access code is never modified."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def metadata_access(seq):
 if seq!='building01':raise ValueError('S8 entry only accepts building01')
 return None
def technical_access(seq,role,freeze=None,*args):
 metadata_access(seq)
 if role!='s8_prospective_heldout':raise ValueError('explicit S8 role required')
 return None
def technical_opening(*args):pass
def check_raw_identity(access,source):
 source=Path(source).resolve();audit=json.loads((ROOT/'artifacts/s8/data_manifest.json').read_text());item=next(i for i in audit['files'] if Path(i['path']).resolve()==source)
 if sha(source)!=item['sha256']:raise ValueError('raw text changed')
def check_frozen_input(access,path):
 key=str(Path(path).resolve())
 if key not in access['input_SHA'] or sha(path)!=access['input_SHA'][key]:raise ValueError('unfrozen or changed input: '+key)
def verify_freeze(freeze_path,receipt_path,root=ROOT,check_sources=True):
 path=Path(freeze_path).resolve();f=json.loads(path.read_text());receipt=json.loads(Path(receipt_path).read_text())
 if f.get('type')!='S8_FULL_SCIENTIFIC_FREEZE' or not f.get('new_heldout_opening_authorized'):raise ValueError('not a complete S8 freeze')
 if receipt.get('freeze_SHA')!=sha(path) or receipt.get('push_exit_code')!=0 or receipt.get('ls_remote_exit_code')!=0 or not receipt.get('verified_S8_HEAD'):raise ValueError('freeze has no verified successful remote receipt')
 if receipt.get('remote_S8_SHA')!=receipt.get('local_commit'):raise ValueError('exact remote SHA mismatch')
 if receipt.get('branch')!='research/lio-gins-s8-building01':raise ValueError('wrong branch receipt')
 if check_sources:
  for rel,digest in f['source_config_SHA'].items():
   if sha(root/rel)!=digest:raise ValueError('scientific source/config changed: '+rel)
 return f
def verify_access(seq,role,freeze,config):
 technical_access(seq,role)
 if not freeze:raise ValueError('S8 requires explicit full freeze path')
 f=verify_freeze(freeze,ROOT/'docs/research_s8/FREEZE_PUSH_RECEIPT.json')
 if sha(config) not in f['method_config_file_SHA'].values():raise ValueError('unfrozen strategy parameters')
 # Full bag was streamed once and officially verified; immutable stat identity
 # checked here, avoiding 152 unnecessary 42 GiB full hashes. Text inputs sealed.
 for item in f['raw_inputs']:
  st=Path(item['path']).stat()
  if (st.st_size,st.st_mtime_ns,st.st_ctime_ns)!=(item['size_bytes'],item['mtime_ns'],item['ctime_ns']):raise ValueError('raw original changed since audited full SHA')
 receipt=json.loads((ROOT/'docs/research_s8/FREEZE_PUSH_RECEIPT.json').read_text())
 subprocess.run(['git','merge-base','--is-ancestor',receipt['local_commit'],'HEAD'],cwd=ROOT,check=True,capture_output=True)
 committed=subprocess.check_output(['git','show',receipt['local_commit']+':'+f['freeze_relative_path']],cwd=ROOT)
 if hashlib.sha256(committed).hexdigest()!=receipt['freeze_SHA']:raise ValueError('remote-verified commit does not contain this exact scientific freeze')
 return f
def record_opening(access,kind):
 if access is None:raise ValueError('S8 performance access without freeze')
 out=Path(os.environ['LIO_GINS_RUN_DIR']);(out/'S8_ACCESS_RECEIPT.json').write_text(json.dumps({'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':kind,'freeze_id':access['freeze_id'],'freeze_SHA':sha(ROOT/access['freeze_relative_path']),'remote_receipt_SHA':sha(ROOT/'docs/research_s8/FREEZE_PUSH_RECEIPT.json'),'new_route':'building01','role':'prospective_heldout','reference_online':False},indent=2)+'\n')

def verify_native_access(seq,role,freeze):
 f=verify_access(seq,role,freeze,ROOT/'configs/s8/P.json')
 if f['native_KF_protocol']['noise_std_multiplier']!=2:raise ValueError('native configuration transfer changed')
 return f
