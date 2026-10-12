"""Explicit heldout access requires sealed development proof and unchanged freeze.

This guard checks experiment identity, not estimator accuracy. Development never
requires a freeze. No environment-variable override opens a heldout sequence.
"""
import hashlib,json,os,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def verify_access(sequence,role,freeze=None,config=None):
    if sequence=='building00' and role=='development':return None
    if sequence!='parking00' or role!='heldout' or freeze is None:
        raise ValueError('heldout performance is closed: verified scientific freeze required')
    folder=Path(freeze).resolve();path=folder/'scientific_freeze.json'
    if not folder.is_relative_to(ROOT/'freezes'):raise ValueError('freeze must be a project archive')
    record=json.loads(path.read_text())
    if sha(path)!=(folder/'scientific_freeze.sha256').read_text().strip():raise ValueError('freeze identity changed')
    if not record['development_conditions_passed'] or record['heldout_sequence']!=sequence:
        raise ValueError('development conditions not met')
    proof=Path(record['development_proof']);manifest=json.loads((proof.parent/'manifest.json').read_text())
    if manifest['status']!='PASSED' or sha(proof)!=record['development_proof_SHA'] or not json.loads(proof.read_text())['quantitative_development_gate']:
        raise ValueError('development proof failed or changed')
    for name,expected in record['source_SHA'].items():
        if sha(ROOT/name)!=expected:raise ValueError('scientific source changed after freeze: '+name)
    for name,expected in record['config_SHA'].items():
        if sha(ROOT/name)!=expected:raise ValueError('scientific configuration changed after freeze: '+name)
    if config is not None:
        conf=json.loads(Path(config).read_text())
        if conf not in record['allowed_method_configs']:
            raise ValueError('heldout parameters were not frozen')
    return record

def record_opening(freeze_record,operation):
    if freeze_record is None:return
    path=ROOT/'docs/TEST_OPENED.json'
    identity={'freeze_id':freeze_record['freeze_id'],'sequence':'parking00','opened_at_UTC':datetime.now(timezone.utc).isoformat(),
        'operation':operation,'argv':sys.argv,'run_directory':os.environ.get('LIO_GINS_RUN_DIR'),
        'note':'first authorized heldout performance-stage access; no retuning after this point'}
    try:
        with path.open('x') as f:json.dump(identity,f,indent=2);f.write('\n')
    except FileExistsError:
        if json.loads(path.read_text())['freeze_id']!=identity['freeze_id']:
            raise ValueError('heldout has already been opened under another scientific freeze')

def check_raw_identity(record,path):
    if record is None:return
    path=Path(path).resolve();expected=record['raw_inputs'][str(path)]
    if path.stat().st_size!=expected['size_bytes'] or sha(path)!=expected['sha256']:
        raise ValueError('heldout original input changed')
