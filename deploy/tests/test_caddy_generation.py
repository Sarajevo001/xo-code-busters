"""Caddy configuration generation regression tests."""
import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "apply_caddy.py"
spec = importlib.util.spec_from_file_location("apply_caddy", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CaddyGenerationTests(unittest.TestCase):
    def test_main_and_registered_route(self):
        text = module.render([{"host": "demo.sarajevo.jp",
                              "path": "/oop-rpg-workshop/",
                              "directory": "/srv/GitHub/Sarajevo001/oop-rpg-workshop/src/public"}])
        self.assertIn("reverse_proxy 127.0.0.1:3000", text)
        self.assertIn("handle_path /oop-rpg-workshop/*", text)
        self.assertNotIn("/var/www/demo", text)

    def test_reserved_main_host(self):
        with self.assertRaises(module.projects.InvalidConfig):
            module.render([{"host": "sarajevo.jp", "path": "/test/",
                            "directory": "/tmp/test"}])

    def test_empty_registry(self):
        text = module.render([])
        self.assertIn("sarajevo.jp {", text)
        self.assertNotIn("demo.sarajevo.jp", text)


if __name__ == "__main__":
    unittest.main()
