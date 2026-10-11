"""Validate the exact prepared build inputs before invoking a container builder."""
import hashlib
import json
from pathlib import Path


def verify_context(prepared_run):
    prepared = Path(prepared_run).resolve()
    context = prepared / 'container_context'
    identity = prepared / 'context_sha256.json'
    raw = identity.read_bytes()
    expected = json.loads(raw)
    if not isinstance(expected, dict) or not expected:
        raise ValueError('empty/invalid context manifest')
    for name, digest in expected.items():
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts or not isinstance(digest,str) or len(digest)!=64:
            raise ValueError('invalid context manifest entry')
    paths = list(context.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('symlink in prepared context')
    actual = {str(p.relative_to(context)):p for p in paths if p.is_file()}
    if set(actual) != set(expected):
        raise ValueError('context file set changed')
    for name, path in actual.items():
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):
                h.update(chunk)
        if h.hexdigest() != expected[name]:
            raise ValueError('context SHA mismatch: '+name)
    return {'context':str(context),'files_verified':len(actual),
            'manifest_sha256':hashlib.sha256(raw).hexdigest()}
