#!/usr/bin/env python3
"""Prepare static publication plans and Caddy previews without modifying live Caddy."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
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


def validate_registry(registry):
    object_fields(registry, {"schemaVersion", "projects"}, "projects.json")
    if type(registry["schemaVersion"]) is not int or registry["schemaVersion"] != 1:
        raise InvalidConfig("projects.json: unsupported schemaVersion")
    entries = registry["projects"]
    if not isinstance(entries, list):
        raise InvalidConfig("projects.json: projects must be an array")
    used = set()
    for number, item in enumerate(entries):
        where = f"projects[{number}]"
        object_fields(item, {"repository", "host", "path"}, where)
        repository, host, url_path = (item[k] for k in ("repository", "host", "path"))
        if (not isinstance(repository, str) or not REPO_RE.fullmatch(repository)
                or any(part in (".", "..") for part in repository.split("/"))):
            raise InvalidConfig(f"{where}: invalid repository")
        if not isinstance(host, str) or not HOST_RE.fullmatch(host):
            raise InvalidConfig(f"{where}: invalid host")
        if not isinstance(url_path, str) or not URL_RE.fullmatch(url_path):
            raise InvalidConfig(f"{where}: invalid URL path")
        if (host, url_path) in used:
            raise InvalidConfig(f"{where}: duplicate URL")
        used.add((host, url_path))
    for i, left in enumerate(entries):
        for right in entries[i + 1:]:
            if left["host"] == right["host"]:
                a, b = left["path"], right["path"]
                if a.startswith(b) or b.startswith(a):
                    raise InvalidConfig(f"overlapping URL paths: {a} and {b} on {left['host']}")
    return entries


def git(*args, cwd=None):
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                                text=True, check=True, timeout=120)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        raise InvalidConfig(f"git operation failed: {args[0]}") from exc


def expected_origin(repository):
    return {f"https://github.com/{repository}", f"https://github.com/{repository}.git",
            f"git@github.com:{repository}", f"git@github.com:{repository}.git"}


def checkout_path(root, repository):
    root = root.resolve(strict=True)
    checkout = root.joinpath(*repository.split("/"))
    if any(p.is_symlink() for p in (checkout.parent, checkout)):
        raise InvalidConfig(f"checkout symlink not allowed: {checkout}")
    if not checkout.is_dir() or not checkout.resolve(strict=True).is_relative_to(root):
        raise InvalidConfig(f"checkout missing or outside checkout root: {checkout}")
    return checkout


def verify_git_checkout(checkout, repository):
    if git("rev-parse", "--show-toplevel", cwd=checkout) != str(checkout.resolve()):
        raise InvalidConfig(f"not a Git repository root: {checkout}")
    if git("remote", "get-url", "origin", cwd=checkout) not in expected_origin(repository):
        raise InvalidConfig(f"unexpected origin: {checkout}")
    if git("branch", "--show-current", cwd=checkout) != "main":
        raise InvalidConfig(f"not on main: {checkout}")
    if git("status", "--porcelain", "--untracked-files=normal", cwd=checkout):
        raise InvalidConfig(f"dirty checkout: {checkout}")


def validate_target_publication(checkout, repository, target):
    """Validate the fetched revision before changing the checked-out commit."""
    try:
        manifest = json.loads(git("show", f"{target}:deploy.json", cwd=checkout))
    except (json.JSONDecodeError, InvalidConfig) as exc:
        raise InvalidConfig(f"invalid target deploy.json: {repository}") from exc
    object_fields(manifest, {"schemaVersion", "publish"}, "target.deploy.json")
    if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
        raise InvalidConfig(f"unsupported target schema: {repository}")
    publish = manifest["publish"]
    object_fields(publish, {"type", "directory"}, "target.publish")
    directory = publish["directory"]
    if publish["type"] != "static" or not safe_directory(directory):
        raise InvalidConfig(f"invalid target publication: {repository}")
    # Git tree entries include modes, allowing symlinks to be rejected before merge.
    entries = git("ls-tree", "-r", target, "--", directory, cwd=checkout).splitlines()
    if not entries:
        raise InvalidConfig(f"missing target publication directory: {repository}")
    for entry in entries:
        mode = entry.split(" ", 1)[0]
        if mode == "120000":
            raise InvalidConfig(f"symlink in target publication: {repository}")
    # Also reject symlink components of the publication directory itself.
    parts = directory.split("/")
    for i in range(1, len(parts) + 1):
        component = "/".join(parts[:i])
        item = git("ls-tree", target, "--", component, cwd=checkout)
        if item and item.split(" ", 1)[0] == "120000":
            raise InvalidConfig(f"symlink target directory: {repository}")


def update_checkouts(entries, root):
    """Opt-in fast-forward update of existing clean main checkouts only."""
    unique = {}
    for entry in entries:
        repository = entry["repository"]
        if repository not in unique:
            checkout = checkout_path(root, repository)
            verify_git_checkout(checkout, repository)
            unique[repository] = checkout
    targets = {}
    for repository, checkout in unique.items():
        old = git("rev-parse", "HEAD", cwd=checkout)
        git("fetch", "--no-tags", "origin", "main", cwd=checkout)
        target = git("rev-parse", "FETCH_HEAD", cwd=checkout)
        try:
            git("merge-base", "--is-ancestor", old, target, cwd=checkout)
        except InvalidConfig as exc:
            raise InvalidConfig(f"non-fast-forward update: {repository}") from exc
        validate_target_publication(checkout, repository, target)
        targets[repository] = (old, target)
    for repository, checkout in unique.items():
        old, target = targets[repository]
        if old != target:
            git("merge", "--ff-only", target, cwd=checkout)
    return targets


def make_plan(registry, checkout_root):
    entries = validate_registry(registry)
    plan = []
    for number, item in enumerate(entries):
        where = f"projects[{number}]"
        repository, host, url_path = (item[k] for k in ("repository", "host", "path"))
        checkout = checkout_path(checkout_root, repository)
        manifest_path = checkout / "deploy.json"
        if manifest_path.is_symlink():
            raise InvalidConfig(f"{where}: manifest symlink not allowed")
        manifest = load_json(manifest_path)
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
        parts = directory.split("/")
        if any(checkout.joinpath(*parts[:i]).is_symlink() for i in range(1, len(parts) + 1)):
            raise InvalidConfig(f"{where}: publication directory path contains symlink")
        if not resolved.is_relative_to(checkout.resolve()) or not published.is_dir():
            raise InvalidConfig(f"{where}: publication directory missing or escapes checkout")
        for path in published.rglob("*"):
            if path.is_symlink():
                raise InvalidConfig(f"{where}: symlink inside publication directory: {path}")
        plan.append({"repository": repository, "host": host, "path": url_path,
                     "directory": str(resolved)})
    return plan


def caddy_snippet(plan):
    """Preview only; not a replacement for a live Caddyfile."""
    hosts = {}
    for item in plan:
        prefix = item["path"].rstrip("/")
        if not prefix:
            raise InvalidConfig("root URL mapping requires separate integration review")
        hosts.setdefault(item["host"], []).append((item, prefix))
    lines = ["# Generated preview only. DO NOT overwrite /etc/caddy/Caddyfile."]
    for host, items in hosts.items():
        lines.append(f"{host} {{")
        for item, prefix in items:
            lines.extend([
                f"    # {item['repository']}",
                f"    redir {prefix} {item['path']} 308",
                f"    handle_path {prefix}/* {{",
                f"        root * {item['directory']}",
                "        file_server",
                "    }",
            ])
        lines.append("}")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_preview(path, content):
    if path.resolve() == Path("/etc/caddy/Caddyfile") or path.is_symlink():
        raise InvalidConfig("refusing to write live Caddyfile or symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".preview-", delete=False) as tmp:
        tmp.write(content)
        temp_path = Path(tmp.name)
    try:
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", type=Path, default=Path(__file__).with_name("projects.json"))
    parser.add_argument("--checkout-root", type=Path, default=Path("/srv/GitHub"))
    parser.add_argument("--update", action="store_true", help="fast-forward existing clean main checkouts")
    parser.add_argument("--caddy-preview", type=Path, help="write a Caddy preview without applying it")
    args = parser.parse_args()
    try:
        registry = load_json(args.projects)
        entries = validate_registry(registry)
        if args.update:
            update_checkouts(entries, args.checkout_root)
        plan = make_plan(registry, args.checkout_root)
        if args.caddy_preview:
            write_preview(args.caddy_preview, caddy_snippet(plan))
    except (InvalidConfig, OSError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"schemaVersion": 1, "publications": plan}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
