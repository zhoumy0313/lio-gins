import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from scripts.context_integrity import verify_context


class ContextIntegrity(unittest.TestCase):
    def setup_context(self, path):
        context=path/'container_context';context.mkdir()
        (context/'Dockerfile').write_text('FROM verified-base\n')
        (context/'source.cpp').write_text('int main() { return 0; }\n')
        manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in context.iterdir()}
        (path/'context_sha256.json').write_text(json.dumps(manifest))
        return context

    def test_exact_context_and_mutated_source(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d);context=self.setup_context(path)
            self.assertEqual(verify_context(path)['files_verified'],2)
            (context/'source.cpp').write_text('int main() { return 1; }\n')
            with self.assertRaisesRegex(ValueError,'SHA mismatch'):verify_context(path)

    def test_missing_extra_and_symlink_rejected(self):
        for mutation in ['missing','extra','symlink']:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as d:
                path=Path(d);context=self.setup_context(path)
                if mutation=='missing':(context/'source.cpp').unlink()
                elif mutation=='extra':(context/'unexpected.txt').write_text('extra')
                else:
                    (context/'source.cpp').unlink()
                    (path/'external.cpp').write_text('outside context')
                    (context/'source.cpp').symlink_to(path/'external.cpp')
                with self.assertRaises(ValueError):verify_context(path)

    def test_manifest_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d);self.setup_context(path)
            (path/'context_sha256.json').write_text(json.dumps({'../outside':'0'*64}))
            with self.assertRaisesRegex(ValueError,'invalid context'):verify_context(path)
