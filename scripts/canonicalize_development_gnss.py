#!/usr/bin/env python3
"""Sort a new development-only observed-data copy; never amend sealed inputs.

The frozen estimators intentionally reject unordered input. This optional
adapter establishes chronological order before replay and preserves row IDs.
Byte identity changes are recorded, never treated as the same cached input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def canonicalize(source, destination):
    source, destination = Path(source), Path(destination)
    identity = json.loads(source.with_suffix('.identity.json').read_text())
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if identity.get('role') != 'development' or identity.get('sequence') != 'building00' or identity.get('fault_labels_included') is not False:
        raise ValueError('only unlabeled building00 development copies are supported')
    if identity.get('derived_sha256') != digest:
        raise ValueError('input bytes changed')
    rows = np.loadtxt(source, delimiter=',', skiprows=1, ndmin=2)
    if rows.size == 0:
        rows = np.empty((0, 8))
    if rows.shape[1] != 8 or not np.isfinite(rows[:, :2]).all():
        raise ValueError('observed-data schema or identity invalid')
    if np.any(rows[:, 0] != np.floor(rows[:, 0])) or len(set(rows[:, 0])) != len(rows) or len(set(rows[:, 1])) != len(rows):
        raise ValueError('ambiguous IDs or timestamps; no automatic deduplication')
    rows = rows[np.argsort(rows[:, 1], kind='stable')]
    with destination.open('x') as stream:
        np.savetxt(stream, rows, delimiter=',', header='id,sow,N,E,D,stdN,stdE,stdD', comments='')
    identity.update(derived_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(), canonicalization={'source':str(source.resolve()),'source_sha256':digest,'policy':'stable SOW sort, original unique IDs retained; no value correction'})
    with destination.with_suffix('.identity.json').open('x') as stream:
        json.dump(identity, stream, indent=2); stream.write('\n')
    return destination

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('source'); parser.add_argument('new_destination'); args=parser.parse_args()
    canonicalize(args.source,args.new_destination)
