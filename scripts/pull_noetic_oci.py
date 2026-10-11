#!/usr/bin/env python3
"""Pull digest-locked Noetic into a project OCI layout; never uses a daemon."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

root=Path(__file__).resolve().parents[1]
out=Path(os.environ['LIO_GINS_RUN_DIR'])
layout=out/'oci';blobs=layout/'blobs/sha256';blobs.mkdir(parents=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:7890','http':'http://127.0.0.1:7890'}))
def get(url,headers=None):
    return opener.open(urllib.request.Request(url,headers=headers or {}),timeout=90)
with get('https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/ros:pull') as f:
    token=json.load(f)['token']
headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.docker.distribution.manifest.v2+json'}
lock=json.loads((root/'containers/base_image.lock.json').read_text())
digest=lock['linux_amd64_digest']
with get('https://registry-1.docker.io/v2/library/ros/manifests/'+digest,headers) as f: raw=f.read()
assert 'sha256:'+hashlib.sha256(raw).hexdigest()==digest
(out/'upstream_manifest.json').write_bytes(raw)
manifest=json.loads(raw)
for item in [manifest['config']]+manifest['layers']:
    dst=blobs/item['digest'].split(':')[1];tmp=dst.with_suffix('.partial')
    print('Pulling '+item['digest']+' bytes='+str(item['size']),flush=True)
    for attempt in range(30):
        try:
            offset=tmp.stat().st_size if tmp.exists() else 0
            request_headers=dict(headers)
            if offset:request_headers['Range']='bytes='+str(offset)+'-'
            with get('https://registry-1.docker.io/v2/library/ros/blobs/'+item['digest'],request_headers) as f:
                if offset and (f.status!=206 or not f.headers.get('Content-Range','').startswith('bytes '+str(offset)+'-')):
                    offset=0
                mode='ab' if offset else 'wb'
                with tmp.open(mode) as w:
                    while True:
                        b=f.read(1024*1024)
                        if not b:break
                        w.write(b)
            size=tmp.stat().st_size
            if size!=item['size']:raise ValueError('incomplete blob bytes='+str(size))
            h=hashlib.sha256()
            with tmp.open('rb') as f:
                while True:
                    b=f.read(1024*1024)
                    if not b:break
                    h.update(b)
            if 'sha256:'+h.hexdigest()!=item['digest']:raise ValueError('blob identity mismatch')
            tmp.rename(dst);break
        except Exception as e:
            if attempt==29 or 'identity mismatch' in str(e):raise
            print('Resuming blob after '+type(e).__name__+': '+str(e),flush=True)
# Docker v2 and OCI share config/layer payloads; descriptors are converted explicitly.
manifest['mediaType']='application/vnd.oci.image.manifest.v1+json'
manifest['config']['mediaType']='application/vnd.oci.image.config.v1+json'
for layer in manifest['layers']:layer['mediaType']='application/vnd.oci.image.layer.v1.tar+gzip'
converted=json.dumps(manifest,separators=(',',':')).encode();converted_sha=hashlib.sha256(converted).hexdigest()
(blobs/converted_sha).write_bytes(converted)
(layout/'oci-layout').write_text('{"imageLayoutVersion":"1.0.0"}\n')
(layout/'index.json').write_text(json.dumps({'schemaVersion':2,'manifests':[{'mediaType':manifest['mediaType'],'digest':'sha256:'+converted_sha,'size':len(converted),'annotations':{'org.opencontainers.image.ref.name':'noetic'}}]},indent=2)+'\n')
umoci=root/'cache/local-tools/umoci/usr/bin/umoci'
subprocess.run([str(umoci),'unpack','--rootless','--image',str(layout)+':noetic',str(out/'bundle')],check=True)
(out/'pull_identity.json').write_text(json.dumps({'base_lock':lock,'upstream_manifest_sha256':digest,'converted_oci_manifest_sha256':'sha256:'+converted_sha,'conversion':'descriptor mediaTypes only; original config and compressed layer digests unchanged','umoci_sha256':hashlib.sha256(umoci.read_bytes()).hexdigest(),'rootless_unpack':True},indent=2)+'\n')
print('Verified base unpacked at '+str(out/'bundle/rootfs'),flush=True)
