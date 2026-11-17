#!/usr/bin/env python3
"""Unit tests for the read-only publication planner."""
import json
import tempfile
import unittest
from pathlib import Path
from deploy_projects import InvalidConfig, make_plan


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / "Example" / "site"
        (self.checkout / "public").mkdir(parents=True)
        (self.checkout / "deploy.json").write_text(json.dumps({
            "schemaVersion": 1, "publish": {"type": "static", "directory": "public"}
        }), encoding="utf-8")
        self.registry = {"schemaVersion": 1, "projects": [{
            "repository": "Example/site", "host": "demo.example.org", "path": "/site/"
        }]}

    def test_valid(self):
        result = make_plan(self.registry, self.root)
        self.assertEqual(result[0]["directory"], str((self.checkout / "public").resolve()))

    def test_reject_traversal(self):
        (self.checkout / "deploy.json").write_text(json.dumps({
            "schemaVersion": 1, "publish": {"type": "static", "directory": "../private"}
        }), encoding="utf-8")
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_reject_unknown_field(self):
        self.registry["projects"][0]["extra"] = "bad"
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_reject_overlapping_url(self):
        self.registry["projects"].append({
            "repository": "Example/site", "host": "demo.example.org", "path": "/site/sub/"
        })
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_reject_symlink_in_publication(self):
        (self.checkout / "public" / "secret").symlink_to(self.checkout / "deploy.json")
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)

    def test_reject_dynamic_type(self):
        (self.checkout / "deploy.json").write_text(json.dumps({
            "schemaVersion": 1, "publish": {"type": "node", "directory": "public"}
        }), encoding="utf-8")
        with self.assertRaises(InvalidConfig):
            make_plan(self.registry, self.root)


if __name__ == "__main__":
    unittest.main()
