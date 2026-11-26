"""Caddy configuration generation regression tests."""
import importlib.util
import sys
import unittest
from unittest.mock import patch, call
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "apply_caddy.py"
sys.path.insert(0, str(SOURCE.parent))
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

    def test_demo_entrance_exact_path_and_existing_route(self):
        plan = [{"host": "demo.sarajevo.jp",
                 "path": "/oop-rpg-workshop/",
                 "directory": "/srv/GitHub/Sarajevo001/oop-rpg-workshop/src/public"},
                {"host": "other.example.org", "path": "/test/", "directory": "/tmp/test"}]
        text = module.render(plan)
        self.assertEqual(text.count("    handle / {"), 1)
        self.assertIn(f'        root * "{module.PORTAL}"', text)
        self.assertIn("    redir /oop-rpg-workshop /oop-rpg-workshop/ 308", text)
        self.assertIn("    handle_path /oop-rpg-workshop/* {", text)
        self.assertNotIn("    handle {", text)
        self.assertNotIn("    handle /*", text)
        self.assertIn("sarajevo.jp {\n    reverse_proxy 127.0.0.1:3000\n}", text)
        html = (module.PORTAL / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/oop-rpg-workshop/"', html)
        self.assertIn("RPGで学ぶ！", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("<script", html)
        self.assertNotIn("file://", html)

    def test_no_entrance_without_registered_rpg(self):
        text = module.render([{"host": "demo.sarajevo.jp", "path": "/other/",
                               "directory": "/tmp/other"}])
        self.assertNotIn("    handle / {", text)

    def test_missing_entrance_stops_generation(self):
        plan = [{"host": "demo.sarajevo.jp", "path": "/oop-rpg-workshop/",
                 "directory": "/tmp/rpg"}]
        with patch.object(module, "PORTAL", Path("/nonexistent-demo-entrance")):
            with self.assertRaises(module.projects.InvalidConfig):
                module.render(plan)

    def test_replaces_unmanaged_live_configuration(self):
        plan = [{"host": "demo.sarajevo.jp",
                 "path": "/oop-rpg-workshop/",
                 "directory": "/srv/GitHub/Sarajevo001/oop-rpg-workshop/src/public"}]
        old = "demo.sarajevo.jp {\\n    root * /var/www/demo\\n}\\n"
        with patch.object(module.subprocess, "run") as read, patch.object(module, "run") as execute:
            read.return_value.stdout = old
            self.assertEqual(module.apply(plan, Path("/etc/caddy/Caddyfile")), "updated")
            self.assertEqual(execute.call_count, 4)
            self.assertEqual(execute.call_args_list[0].args[0], "caddy")
            self.assertEqual(execute.call_args_list[1].args[:3],
                             ("sudo", "-n", "cp"))
            self.assertEqual(execute.call_args_list[2].args[:3],
                             ("sudo", "-n", "install"))

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
