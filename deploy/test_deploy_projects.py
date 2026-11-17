#!/usr/bin/env python3
"""Offline unit tests for common static publication preparation."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from deploy_projects import InvalidConfig, make_plan, caddy_snippet, validate_registry, update_checkouts, write_preview


class DeployTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / "Example" / "site"
        (self.checkout / "public").mkdir(parents=True)
        self.manifest = self.checkout / "deploy.json"
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "publish": {
            "type": "static", "directory": "public"}}), encoding="utf-8")
        self.registry = {"schemaVersion": 1, "projects": [{
            "repository": "Example/site", "host": "demo.example.org", "path": "/site/"}]}

    def test_valid_and_caddy(self):
        plan = make_plan(self.registry, self.root)
        self.assertEqual(plan[0]["directory"], str((self.checkout / "public").resolve()))
        self.assertIn("handle_path /site/*", caddy_snippet(plan))

    def test_traversal(self):
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "publish": {
            "type": "static", "directory": "../private"}}))
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_unknown_field(self):
        self.registry["projects"][0]["extra"] = "bad"
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_overlap(self):
        self.registry["projects"].append({"repository": "Example/site",
            "host": "demo.example.org", "path": "/site/sub/"})
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_symlink(self):
        (self.checkout / "public" / "secret").symlink_to(self.manifest)
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_directory_symlink(self):
        (self.checkout / "link").symlink_to(self.checkout / "public")
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "publish": {
            "type": "static", "directory": "link"}}))
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_dynamic(self):
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "publish": {
            "type": "node", "directory": "public"}}))
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_schema_version_bool(self):
        self.registry["schemaVersion"] = True
        with self.assertRaises(InvalidConfig):
            validate_registry(self.registry)

    def test_git_update(self):
        with patch("deploy_projects.verify_git_checkout", side_effect=InvalidConfig("bad origin")):
            with self.assertRaises(InvalidConfig):
                update_checkouts(self.registry["projects"], self.root)

    def test_same_host_grouping(self):
        (self.root / "Example" / "other" / "public").mkdir(parents=True)
        (self.root / "Example" / "other" / "deploy.json").write_text(self.manifest.read_text())
        self.registry["projects"].append({"repository": "Example/other",
            "host": "demo.example.org", "path": "/other/"})
        self.assertEqual(caddy_snippet(make_plan(self.registry, self.root)).count("demo.example.org {"), 1)

    def test_empty_registry(self):
        self.assertEqual(make_plan({"schemaVersion": 1, "projects": []}, self.root), [])

    def test_repository_dot_segment(self):
        self.registry["projects"][0]["repository"] = "../site"
        with self.assertRaises(InvalidConfig):
            validate_registry(self.registry)

    def test_preview_write(self):
        target = self.root / "preview.caddy"
        write_preview(target, "preview")
        self.assertEqual(target.read_text(), "preview")


if __name__ == "__main__":
    unittest.main()
