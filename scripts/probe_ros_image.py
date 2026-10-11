#!/usr/bin/env python3
"""Verify Noetic tag via authenticated anonymous registry manifest, not a guessed digest."""
import datetime
import hashlib
import json
import urllib.request
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--proxy', default=None)
args = parser.parse_args()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({'https': args.proxy, 'http': args.proxy})) if args.proxy else urllib.request.build_opener()

def get(url, headers=None):
    with opener.open(urllib.request.Request(url, headers=headers or {}), timeout=35) as r:
        return r.read(), r.headers

token_raw, _ = get('https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/ros:pull')
token = json.loads(token_raw)['token']
body, headers = get('https://registry-1.docker.io/v2/library/ros/manifests/noetic-ros-base-focal',
                    {'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.index.v1+json'})
digest = 'sha256:'+hashlib.sha256(body).hexdigest()
if digest != headers['Docker-Content-Digest']:
    raise RuntimeError('manifest digest mismatch')
manifest = json.loads(body)
amd64 = [m for m in manifest.get('manifests', []) if m.get('platform', {}).get('architecture') == 'amd64' and m.get('platform', {}).get('os') == 'linux']
if len(amd64) != 1:
    raise RuntimeError('linux/amd64 manifest missing/ambiguous')
record = {'image': 'docker.io/library/ros:noetic-ros-base-focal', 'index_digest': digest,
          'linux_amd64_digest': amd64[0]['digest'], 'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'registry_manifest_verified': True, 'image_layers_pulled': False, 'container_build_verified': False}
root = Path(__file__).resolve().parents[1]
(root/'containers/base_image.lock.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
