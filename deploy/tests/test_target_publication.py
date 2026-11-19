"""Offline regression checks for the fetched-publication preflight.

Run: python3 -m unittest discover -s deploy/tests -v
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "deploy_projects.py"
spec = importlib.util.spec_from_file_location("deploy_projects", SOURCE)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class TargetPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_git("init", "-q", "-b", "main")
        self.run_git("config", "user.name", "Deployment Test")
        self.run_git("config", "user.email", "test@example.invalid")

    def run_git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def revision(self, *, manifest=True, publication=True, symlink=False):
        published = self.root / "src/public"
        published.mkdir(parents=True, exist_ok=True)
        index = published / "index.html"
        if index.exists() or index.is_symlink():
            index.unlink()
        if publication:
            if symlink:
                index.symlink_to("/etc/passwd")
            else:
                index.write_text("ok", encoding="utf-8")
        descriptor = self.root / "deploy.json"
        if descriptor.exists():
            descriptor.unlink()
        if manifest:
            descriptor.write_text(json.dumps({
                "schemaVersion": 1,
                "publish": {"type": "static", "directory": "src/public"},
            }), encoding="utf-8")
        self.run_git("add", "-A")
        self.run_git("commit", "-q", "--allow-empty", "-m", "fixture")
        return self.run_git("rev-parse", "HEAD")

    def test_valid_revision(self):
        deploy.validate_target_publication(self.root, "test/repo", self.revision())

    def test_missing_manifest(self):
        rev = self.revision(manifest=False)
        with self.assertRaises(deploy.InvalidConfig):
            deploy.validate_target_publication(self.root, "test/repo", rev)

    def test_missing_publication(self):
        rev = self.revision(publication=False)
        with self.assertRaises(deploy.InvalidConfig):
            deploy.validate_target_publication(self.root, "test/repo", rev)

    def test_symlink_in_publication(self):
        rev = self.revision(symlink=True)
        with self.assertRaises(deploy.InvalidConfig):
            deploy.validate_target_publication(self.root, "test/repo", rev)


if __name__ == "__main__":
    unittest.main()
