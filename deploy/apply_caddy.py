#!/usr/bin/env python3
"""Render and apply the XO-owned Caddy configuration from validated project plans."""
import os
import subprocess
import tempfile
from pathlib import Path

import deploy_projects as projects

HEADER = "# Managed by XO-Code Busters deploy. Do not edit on the server.\n"
LIVE = Path("/etc/caddy/Caddyfile")

def render(plan):
    hosts = {}
    for item in plan:
        prefix = item["path"].rstrip("/")
        if not prefix:
            raise projects.InvalidConfig("root URL mapping is not supported")
        hosts.setdefault(item["host"], []).append((prefix, item))
    if "sarajevo.jp" in hosts:
        raise projects.InvalidConfig("XO main host is reserved")
    lines = [HEADER.rstrip(), "sarajevo.jp {",
             "    reverse_proxy 127.0.0.1:3000", "}", ""]
    for host, items in sorted(hosts.items()):
        lines.append(f"{host} {{")
        for prefix, item in sorted(items):
            lines += [
                f"    redir {prefix} {item['path']} 308",
                f"    handle_path {prefix}/* {{",
                f"        root * {item['directory']}",
                "        file_server",
                "    }",
            ]
        lines += ["}", ""]
    return "\n".join(lines) + "\n"


def run(*args):
    subprocess.run(args, check=True, timeout=60)


def apply(plan, live=LIVE):
    desired = render(plan)
    # No root shell: sudoers must authorize only the required commands.
    # Read through sudo because /etc/caddy may not be readable by deploy user.
    current = subprocess.run(["sudo", "-n", "cat", str(live)], check=True,
                             capture_output=True, text=True, timeout=30).stdout
    if current == desired:
        return "unchanged"
    with tempfile.TemporaryDirectory(prefix="xo-caddy-") as directory:
        staged = Path(directory) / "Caddyfile"
        staged.write_text(desired, encoding="utf-8")
        run("caddy", "validate", "--config", str(staged), "--adapter", "caddyfile")
        # Backup before installing; on failure restore and reload the previous config.
        run("sudo", "-n", "cp", str(live), str(live) + ".xo-backup")
        try:
            run("sudo", "-n", "install", "-m", "0644", str(staged), str(live))
            run("sudo", "-n", "systemctl", "reload", "caddy")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            run("sudo", "-n", "cp", str(live) + ".xo-backup", str(live))
            run("sudo", "-n", "systemctl", "reload", "caddy")
            raise
    return "updated"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--checkout-root", type=Path, default=Path("/srv/GitHub"))
    args = parser.parse_args()
    try:
        plan = projects.make_plan(projects.load_json(args.projects), args.checkout_root)
        print("Caddy:", apply(plan))
    except (projects.InvalidConfig, OSError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Caddy deployment failed: {exc}\n")


if __name__ == "__main__":
    main()
