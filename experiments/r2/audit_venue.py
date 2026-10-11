"""Read-only bounded official-page probes; no account, submission, or contact."""
import datetime,hashlib,json,os,re,urllib.request,urllib.error
from html.parser import HTMLParser
from pathlib import Path
OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
class Parse(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links += [v for k,v in attrs if k=='href']
    def handle_data(self,data):
        if data.strip():self.text.append(data.strip())
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:7890'}));results=[]
for i,url in enumerate(['https://upinlbs2026.com/','https://upinlbs2026.com/submission','https://upinlbs2026.com/submission/']):
    item={'URL':url,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as r:blob=r.read(2**20);item.update(status=r.status,final_URL=r.url,bytes=len(blob),SHA=hashlib.sha256(blob).hexdigest())
        (OUT/('official_page_'+str(i)+'.html')).write_bytes(blob);parser=Parse();parser.feed(blob.decode(errors='replace'));item['links']=parser.links;item['matched_text']=[t for t in parser.text if any(w in t.lower() for w in ['page','deadline','template','anonymous','cmt','submission','time zone','timezone','ai-generated'])][:45]
    except (urllib.error.URLError,TimeoutError) as e:item['error']=str(e)
    results.append(item)
(OUT/'venue_access_audit.json').write_text(json.dumps({'official_page_probes':results,'indexed_homepage_verified':{'full_paper_deadline':'2026-10-15','maximum_full_paper_pages':6},'template':'UNVERIFIED','anonymity':'UNVERIFIED','exact_timezone':'UNVERIFIED','specific_CMT_URL':'UNVERIFIED_unless_official_links_establish','IEEE_AI_policy':'If IEEE policy applies: identify AI tool, sections and extent in acknowledgments; actual venue applicability not established','no_account_login':True,'no_submission':True},indent=2)+'\n');print(json.dumps(results))
