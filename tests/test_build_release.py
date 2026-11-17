import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_release import OWNER, ReleaseError, build

SHA = 'a' * 40
ENV = {
    'GITHUB_REPOSITORY': OWNER,
    'GITHUB_REF': 'refs/heads/main',
    'GITHUB_EVENT_NAME': 'push',
    'GITHUB_SHA': SHA,
}
HTML = b'<!doctype html><html><head><title>Matthias Bridge Squad - ShadowOps</title></head><body></body></html>'


class BuildReleaseTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.dir = Path(self.t.name)
        self.source = self.dir / 'index.html'
        self.source.write_bytes(HTML)
        self.dest = self.dir / '_site'

    def test_release_is_byte_identical_and_cryptographically_pinned(self):
        manifest = build(self.source, self.dest, ENV)
        self.assertEqual((self.dest/'index.html').read_bytes(), HTML)
        self.assertEqual(json.loads((self.dest/'release.json').read_text()), manifest)
        self.assertEqual(manifest['source_sha'], SHA)
        self.assertEqual(manifest['files']['index.html']['sha256'], hashlib.sha256(HTML).hexdigest())
        self.assertEqual(manifest['files']['index.html']['bytes'], len(HTML))
        self.assertEqual(manifest['authentication'], {
            'provider': 'shadowops-id', 'audience': 'bridgesquad', 'required': True,
        })
        self.assertEqual({p.name for p in self.dest.iterdir()}, {'index.html','release.json'})

    def test_untrusted_source_branch_event_and_sha_are_rejected(self):
        for changed in [
            {'GITHUB_REPOSITORY': 'outsider/matthias-bridge-squad'},
            {'GITHUB_REF': 'refs/heads/feature'},
            {'GITHUB_EVENT_NAME': 'pull_request'},
            {'GITHUB_SHA': 'untrusted'},
            {'GITHUB_SHA': 'A' * 40},
        ]:
            with self.subTest(changed=changed), self.assertRaises(ReleaseError):
                build(self.source, self.dest, {**ENV, **changed})
            self.assertFalse(self.dest.exists())

    def test_missing_malformed_and_linked_source_are_rejected(self):
        self.source.write_bytes(b'not a game')
        with self.assertRaises(ReleaseError):
            build(self.source, self.dest, ENV)
        self.source.unlink()
        with self.assertRaises(ReleaseError):
            build(self.source, self.dest, ENV)
        other = self.dir / 'outside.html'
        other.write_bytes(HTML)
        self.source.symlink_to(other)
        with self.assertRaises(ReleaseError):
            build(self.source, self.dest, ENV)

    def test_nonempty_or_linked_destination_is_rejected(self):
        self.dest.mkdir()
        (self.dest/'foreign.txt').write_text('do not remove')
        with self.assertRaises(ReleaseError):
            build(self.source, self.dest, ENV)
        self.assertEqual((self.dest/'foreign.txt').read_text(), 'do not remove')
        self.dest.joinpath('foreign.txt').unlink()
        self.dest.rmdir()
        self.dest.symlink_to(self.dir, target_is_directory=True)
        with self.assertRaises(ReleaseError):
            build(self.source, self.dest, ENV)


if __name__ == '__main__':
    unittest.main()
