import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / '.github/scripts/sync_namespace.py'
spec = importlib.util.spec_from_file_location('sync_namespace', SCRIPT)
syncer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(syncer)


class PublicationSyncTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source'
        self.target = Path(self.temp.name) / 'target'
        self.target.mkdir()
        for directory in syncer.DIRECTORIES:
            (self.source / directory).mkdir(parents=True)
            (self.source / directory / 'example.txt').write_text(directory)
        for name in syncer.ROOT_FILES:
            (self.target / name).write_text('publication-owned ' + name)
        (self.source / 'README.md').write_text('bundle README must not replace publication README')
        syncer.write_integrity(self.source, {'canonicalNamespace': 'https://w3id.org/tib/datacite/'})

    def test_sync_keeps_shapes_and_root_files_and_removes_stale_generated_files(self):
        (self.target / 'shapes').mkdir()
        (self.target / 'shapes/stale.ttl').write_text('old')
        roots = {name: (self.target / name).read_bytes() for name in syncer.ROOT_FILES}
        syncer.sync(self.source, self.target)
        self.assertEqual((self.target / 'shapes/example.txt').read_text(), 'shapes')
        self.assertEqual((self.target / 'schema-profiles/example.txt').read_text(), 'schema-profiles')
        self.assertFalse((self.target / 'shapes/stale.ttl').exists())
        self.assertEqual(roots, {name: (self.target / name).read_bytes() for name in roots})
        self.assertNotIn(syncer.INTEGRITY, (self.target / 'CHECKSUMS.sha256').read_text())
        syncer.compare_source(self.source, self.target)
        syncer.verify_integrity(self.target)

    def test_missing_shape_fails_source_completeness_even_after_rechecksumming(self):
        syncer.sync(self.source, self.target)
        shutil.rmtree(self.target / 'shapes')
        syncer.write_integrity(self.target, {})
        syncer.verify_integrity(self.target)
        with self.assertRaisesRegex(ValueError, 'file list'):
            syncer.compare_source(self.source, self.target)

    def test_stale_summary_is_rejected(self):
        syncer.sync(self.source, self.target)
        metadata = json.loads((self.target / syncer.INTEGRITY).read_text())
        for field, value in [('artifactFileCount', 0), ('bundleChecksum', 'stale')]:
            broken = dict(metadata, **{field: value})
            (self.target / syncer.INTEGRITY).write_text(json.dumps(broken))
            with self.assertRaises(ValueError):
                syncer.verify_integrity(self.target)

    def test_unlisted_extra_file_is_rejected(self):
        syncer.sync(self.source, self.target)
        (self.target / 'dist/extra.ttl').write_text('unlisted')
        with self.assertRaisesRegex(ValueError, 'cover exactly'):
            syncer.verify_integrity(self.target)

    def test_corrupt_source_is_rejected_before_target_changes(self):
        (self.source / 'dist/example.txt').write_text('corrupt')
        with self.assertRaises(subprocess.CalledProcessError):
            syncer.sync(self.source, self.target)
        self.assertFalse((self.target / 'dist').exists())

    def test_older_bundle_without_shapes_can_still_sync(self):
        shutil.rmtree(self.source / 'shapes')
        shutil.rmtree(self.source / 'schema-profiles')
        syncer.write_integrity(self.source, {})
        syncer.sync(self.source, self.target)
        self.assertFalse((self.target / 'shapes').exists())
        syncer.verify_integrity(self.target)

    def test_new_source_directory_requires_an_explicit_sync_update(self):
        (self.source / 'new-section').mkdir()
        with self.assertRaisesRegex(ValueError, 'Unrecognized'):
            syncer.sync(self.source, self.target)


if __name__ == '__main__':
    unittest.main()
