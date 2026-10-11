"""Inspect official public app assets without executing scripts or opening accounts."""
import datetime,hashlib,json,os,re,urllib.request,urllib.parse
from pathlib import Path
OUT=Path(os.environ['LIO_GINS_RUN_DIR']);base='https://upinlbs2026.com/'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:7890'}))
queue=['assets/index-DYUnbZvC.js'];seen=set();rows=[]
for i in range(8):
    if not queue:break
    path=queue.pop(0)
    if path in seen:continue
    seen.add(path);url=urllib.parse.urljoin(base,path);item={'URL':url,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as r:blob=r.read(3*2**20+1);item.update(status=r.status,bytes=len(blob))
        assert len(blob)<=3*2**20,'bounded asset limit';item['SHA']=hashlib.sha256(blob).hexdigest();(OUT/f'official_asset_{i}.js').write_bytes(blob);source=blob.decode(errors='replace')
        item['contexts']=[source[max(0,m.start()-120):m.end()+240] for m in re.finditer(r'(?i)October|2026-10|six pages|6 pages|anonymous|template|cmt3|submission deadline|AI.generated|time zone|timezone',source)][:50]
        item['external_literal_links']=sorted(set(re.findall(r'https?://[^\s\"\x27<>\\]+',source)))
        for child in re.findall(r'[\"\x27]([^\"\x27]*\.js)[\"\x27]',source):
            child=urllib.parse.urljoin(path,child)
            if not child.startswith('http') and child not in seen and child not in queue:queue.append(child)
    except Exception as e:item['error']=repr(e)
    rows.append(item)
(OUT/'venue_bundle_access_audit.json').write_text(json.dumps({'assets':rows,'account_login':False,'script_execution':False,'formal_submission':False,'verification_rule':'literal official content; contextual interpretation recorded separately; absence does not establish requirements'},indent=2)+'\n');print(json.dumps(rows))
