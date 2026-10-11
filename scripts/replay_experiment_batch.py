"""Serial recorded experiment utility for development-only candidate/ablation runs."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PY=str(ROOT/'.venv/bin/python')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class ExperimentBatch:
    def __init__(self,out,cache,initial,stress,phase='P4'):
        self.out=Path(out);self.cache=Path(cache).resolve();self.initial=Path(initial).resolve();self.stress=Path(stress).resolve();self.phase=phase
        self.events=json.loads((self.stress/'event_manifest.json').read_text())
        if self.events['sequence']!='building00' or self.events['role']!='development':raise ValueError('heldout batch prohibited')
        self.cases={c['id']:c for c in self.events['cases']};self.records={};self.history=[]
        self.config_dir=self.out/'configs';self.config_dir.mkdir()
        self.backend_sources=[ROOT/p for p in ['scripts/run_candidate.py','src/observation_manager/motion_recovery.py','src/observation_manager/availability_recovery.py','src/adapters/geodesy.py','src/adapters/sensor_text.py','src/adapters/causal_lio.py','src/fusion/position_kf.py','src/fusion/fixed_recovery.py']]
        self.eval_sources=[ROOT/p for p in ['scripts/evaluate_outer.py','src/evaluation/reference.py']]
        self.source_identity={str(p):digest(p) for p in self.backend_sources+self.eval_sources}
        (self.out/'source_identity.json').write_text(json.dumps(self.source_identity,indent=2)+'\n')

    def recorded(self,purpose,kind,inputs,argv):
        for name,expected in self.source_identity.items():
            if digest(name)!=expected:raise RuntimeError('source changed during bounded batch: '+name)
        cmd=[PY,str(ROOT/'scripts/record_run.py'),'--phase',self.phase,'--purpose',purpose,'--kind',kind,'--timeout','180']
        for source in inputs:cmd+=['--input',str(source)]
        cmd+=['--']+argv;r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        with (self.out/'driver_commands.jsonl').open('a') as f:f.write(json.dumps({'argv':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n')
        if not r.stdout:raise RuntimeError('missing recorder output '+r.stderr)
        return json.loads(r.stdout.splitlines()[-1])

    def run(self,conf,name,case_id):
        key=name+'__'+case_id
        if key in self.records:return self.records[key]
        path=self.config_dir/(name+'.json')
        if path.exists():
            if json.loads(path.read_text())!=conf:raise ValueError('config name reuse changed parameters')
        else:path.write_text(json.dumps(conf,indent=2)+'\n')
        data=Path(self.cases[case_id]['data_path'])
        b=self.recorded('candidate_'+key,'cached_backend',self.backend_sources+[path,data,data.with_suffix('.identity.json'),self.cache/'lio_cache.npz',self.cache/'cache_identity.json',self.initial/'initial_condition.json'],
            [PY,str(ROOT/'scripts/run_candidate.py'),str(self.cache),str(self.initial),str(path),'--gnss-ned',str(data)])
        run=Path(b['output']);metric=None;evaluation=None
        if (run/'backend_identity.json').exists():
            e=self.recorded('evaluate_candidate_'+key,'engineering',self.eval_sources+[run/'manifest.json',run/'trajectory.csv',run/'per_update.jsonl',run/'backend_identity.json',self.stress/'event_manifest.json',ROOT/'configs/development_experiment_protocol.json',self.initial/'initial_condition.json',ROOT/'data/i2nav-dataset/building00/building00_groundtruth.nav'],
                [PY,str(ROOT/'scripts/evaluate_outer.py'),str(run),str(self.stress/'event_manifest.json'),case_id])
            evaluation=e['output'];mp=Path(evaluation)/'metrics.json'
            if mp.exists():metric=json.loads(mp.read_text())
        result={'name':name,'config':conf,'case':case_id,'backend':b,'evaluation':evaluation,'metrics':metric}
        self.records[key]=result;self.history.append(result)
        with (self.out/'progress.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
        print(json.dumps({'config':name,'case':case_id,'RMSE_m':metric['metrics']['horizontal_rmse_m'] if metric else None,'event_macro_RMSE_m':metric['event_macro_RMSE_m'] if metric else None,'backend_exit':b['exit_code']}),flush=True)
        return result
