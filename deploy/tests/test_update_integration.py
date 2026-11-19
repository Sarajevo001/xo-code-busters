"""Integration tests using local Git repositories only.

Run: python3 -m unittest discover -s deploy/tests -v
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "deploy_projects.py"
spec = importlib.util.spec_from_file_location("deploy_projects_integration", SOURCE)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def git(path, *args):
    return subprocess.run(["git", *args], cwd=path, check=True,
                          capture_output=True, text=True).stdout.strip()


class UpdateIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote"
        self.remote.mkdir()
        git(self.remote, "init", "-q", "-b", "main")
        git(self.remote, "config", "user.name", "Deployment Test")
        git(self.remote, "config", "user.email", "test@example.invalid")
        self.public = self.remote / "src/public"
        self.public.mkdir(parents=True)
        (self.public / "index.html").write_text("old", encoding="utf-8")
        (self.remote / "deploy.json").write_text(json.dumps({
            "schemaVersion": 1,
            "publish": {"type": "static", "directory": "src/public"}
        }), encoding="utf-8")
        git(self.remote, "add", "-A")
        git(self.remote, "commit", "-qm", "old")
        self.checkout_root = self.root / "checkouts"
        (self.checkout_root / "Test").mkdir(parents=True)
        self.checkout = self.checkout_root / "Test/repo"
        git(self.root, "clone", "-q", str(self.remote), str(self.checkout))
        self.repository = "Test/repo"
        self.entries = [{"repository": self.repository}]
        self.old = git(self.checkout, "rev-parse", "HEAD")
        self.original_expected_origin = deploy.expected_origin
        deploy.expected_origin = lambda repository: {str(self.remote)}
        self.addCleanup(self.restore_origin)

    def restore_origin(self):
        deploy.expected_origin = self.original_expected_origin

    def commit_remote(self):
        git(self.remote, "add", "-A")
        git(self.remote, "commit", "-qm", "update")
        return git(self.remote, "rev-parse", "HEAD")

    def test_valid_fast_forward(self):
        (self.public / "index.html").write_text("new", encoding="utf-8")
        target = self.commit_remote()
        deploy.update_checkouts(self.entries, self.checkout_root)
        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), target)
        self.assertEqual((self.checkout / "src/public/index.html").read_text(), "new")

    def test_invalid_publication_does_not_advance_head(self):
        (self.public / "index.html").unlink()
        self.commit_remote()
        with self.assertRaises(deploy.InvalidConfig):
            deploy.update_checkouts(self.entries, self.checkout_root)
        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), self.old)

    def test_dirty_checkout_does_not_advance_head(self):
        (self.public / "index.html").write_text("new", encoding="utf-8")
        self.commit_remote()
        (self.checkout / "src/public/index.html").write_text("local change")
        with self.assertRaises(deploy.InvalidConfig):
            deploy.update_checkouts(self.entries, self.checkout_root)
        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), self.old)


if __name__ == "__main__":
    unittest.main()
