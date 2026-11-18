#!/usr/bin/env bash
# Update registered static project checkouts; never modify the live Caddyfile.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECTS="$SCRIPT_DIR/projects.json"
DEPLOYER="$SCRIPT_DIR/deploy_projects.py"

if [[ "${EUID}" -eq 0 ]]; then
  printf 'ERROR: run as the normal deployment user, not root.\n' >&2
  exit 1
fi
for command in python3 git flock; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' "$command" >&2
    exit 1
  fi
done
if [[ ! -f "$PROJECTS" || ! -f "$DEPLOYER" ]]; then
  printf 'ERROR: missing deployment configuration or implementation.\n' >&2
  exit 1
fi

# Prevent concurrent executions without altering tracked files.
exec 9>"${TMPDIR:-/tmp}/xo-code-busters-project-deploy-$(id -u).lock"
if ! flock -n 9; then
  printf 'ERROR: another project deployment is running.\n' >&2
  exit 1
fi

# Preflight validates the current registry, manifests and publication paths.
python3 "$DEPLOYER" --projects "$PROJECTS" >/dev/null

# Updates clean main checkouts using fetch + fast-forward, then validates output.
# No Caddy changes, file copies, service restarts or destructive Git resets.
python3 "$DEPLOYER" --projects "$PROJECTS" --update
