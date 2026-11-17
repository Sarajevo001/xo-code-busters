#!/usr/bin/env python3
"""Validate static project manifests and print a read-only publication plan."""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
HOST_RE = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")
URL_RE = re.compile(r"^/(?:[A-Za-z0-9_.~-]+/)*$")
DIR_RE = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")


class InvalidConfig(ValueError):
    pass


def object_fields(value, required, where):
    if not isinstance(value, dict) or set(value) != set(required):
        raise InvalidConfig(f"{where}: expected fields {sorted(required)}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidConfig(f"{path}: {exc}") from exc


def safe_directory(value):
    return (isinstance(value, str) and bool(DIR_RE.fullmatch(value))
            and all(part not in (".", "..") for part in value.split("/")))


def make_plan(registry, checkout_root):
    object_fields(registry, {"schemaVersion", "projects"}, "projects.json")
    if type(registry["schemaVersion"]) is not int or registry["schemaVersion"] != 1:
        raise InvalidConfig("projects.json: unsupported schemaVersion")
    entries = registry["projects"]
    if not isinstance(entries, list):
        raise InvalidConfig("projects.json: projects must be an array")
    plan = []
    used = set()
    for number, item in enumerate(entries):
        where = f"projects[{number}]"
        object_fields(item, {"repository", "host", "path"}, where)
        repository, host, url_path = (item[k] for k in ("repository", "host", "path"))
        if not isinstance(repository, str) or not REPO_RE.fullmatch(repository):
            raise InvalidConfig(f"{where}: invalid repository")
        if not isinstance(host, str) or not HOST_RE.fullmatch(host):
            raise InvalidConfig(f"{where}: invalid host")
        if not isinstance(url_path, str) or not URL_RE.fullmatch(url_path):
            raise InvalidConfig(f"{where}: invalid URL path")
        key = (host, url_path)
        if key in used:
            raise InvalidConfig(f"{where}: duplicate URL")
        used.add(key)
        # Do not resolve a project by running shell commands or following a checkout symlink.
        checkout = checkout_root.joinpath(*repository.split("/"))
        if checkout.is_symlink() or not checkout.is_dir():
            raise InvalidConfig(f"{where}: checkout missing or symlink: {checkout}")
        root = checkout.resolve(strict=True)
        if not root.is_relative_to(checkout_root.resolve(strict=True)):
            raise InvalidConfig(f"{where}: checkout escapes root")
        manifest = load_json(checkout / "deploy.json")
        object_fields(manifest, {"schemaVersion", "publish"}, f"{where}.deploy.json")
        if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
            raise InvalidConfig(f"{where}: unsupported deploy schemaVersion")
        publish = manifest["publish"]
        object_fields(publish, {"type", "directory"}, f"{where}.publish")
        if publish["type"] != "static":
            raise InvalidConfig(f"{where}: only static publication is supported")
        directory = publish["directory"]
        if not safe_directory(directory):
            raise InvalidConfig(f"{where}: invalid publication directory")
        published = checkout / directory
        resolved = published.resolve(strict=False)
        if not resolved.is_relative_to(root) or not published.is_dir():
            raise InvalidConfig(f"{where}: publication directory missing or escapes checkout")
        # Reject symlinks anywhere within the publication tree, including files.
        for path in published.rglob("*"):
            if path.is_symlink():
                raise InvalidConfig(f"{where}: symlink inside publication directory: {path}")
        plan.append({"repository": repository, "host": host, "path": url_path,
                     "directory": str(resolved)})
    for i, left in enumerate(plan):
        for right in plan[i + 1:]:
            if left["host"] == right["host"]:
                a, b = left["path"], right["path"]
                if a.startswith(b) or b.startswith(a):
                    raise InvalidConfig(f"overlapping URL paths: {a} and {b} on {left['host']}")
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", type=Path, default=Path(__file__).with_name("projects.json"))
    parser.add_argument("--checkout-root", type=Path, default=Path("/srv/GitHub"))
    args = parser.parse_args()
    try:
        plan = make_plan(load_json(args.projects), args.checkout_root)
    except (InvalidConfig, OSError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"schemaVersion": 1, "publications": plan}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
