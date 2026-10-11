"""Download official self-contained Tectonic into this project, with fixed digest."""
import hashlib,json,os,tarfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
DEST=ROOT/'cache/r2/tools';DEST.mkdir(parents=True,exist_ok=True)
url='https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-unknown-linux-musl.tar.gz'
expected='8533d07f9ccbd7a65824b9e0459041bca34af1eb33daba48f59215593753a3b7'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:7890','http':'http://127.0.0.1:7890'}))
with opener.open(url,timeout=90) as response:blob=response.read(15000000)
actual=hashlib.sha256(blob).hexdigest()
assert actual==expected,(actual,expected)
archive=DEST/'tectonic-0.17.0-musl.tar.gz';archive.write_bytes(blob)
with tarfile.open(archive) as tar:
    member=next(m for m in tar.getmembers() if Path(m.name).name=='tectonic' and m.isfile())
    binary=DEST/'tectonic';binary.write_bytes(tar.extractfile(member).read());binary.chmod(0o755)
(OUT/'toolchain.json').write_text(json.dumps({'official_asset_URL':url,'archive_SHA256':actual,'binary_SHA256':hashlib.sha256(binary.read_bytes()).hexdigest(),'version':'0.17.0','path':str(binary),'global_install':False},indent=2)+'\n')
print(json.dumps({'downloaded_bytes':len(blob),'SHA256':actual}))
