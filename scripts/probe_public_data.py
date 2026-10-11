#!/usr/bin/env python3
"""Bounded anonymous probes; never store a sharing webpage as sensor data."""
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

out = Path(os.environ['LIO_GINS_RUN_DIR'])
onedrive = 'https://1drv.ms/f/c/7da41598f6f07e02/EgJ-8PaYFaQggH3CBQAAAAABlmP45s_NHaBuLd3xXk04AA?e=sMNBhd'
baidu = 'https://pan.baidu.com/s/1UGZI-LvoTKxH6GN6JbzMZw?pwd=hs6p'
results = []
for name, url in [('onedrive_attempt1', onedrive), ('onedrive_attempt2', onedrive), ('baidu_alternate', baidu)]:
    item = {'attempt': name, 'url': url}
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=35) as r:
            body = r.read(2 * 1024 * 1024)
            item.update(status=r.status, content_type=r.headers.get('Content-Type'), bytes_read=len(body), final_url=r.url)
            (out / (name + '.response')).write_bytes(body)
            # Public shares require explicit enumeration and actual object size before download.
            item['data_downloaded'] = False
            item['response_is_dataset'] = False
    except (urllib.error.URLError, TimeoutError) as e:
        item.update(error=str(e), data_downloaded=False)
    results.append(item)
    print(json.dumps(item), flush=True)
(out / 'access_attempts.json').write_text(json.dumps(results, indent=2)+'\n')
