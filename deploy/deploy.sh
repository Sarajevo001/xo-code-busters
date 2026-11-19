#!/usr/bin/env bash
# One-command deployment of XO checkout and registered static projects.
# Updates registered projects and applies XO-owned Caddy configuration.
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
XO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
PROJECTS="$SCRIPT_DIR/projects.json"
DEPLOYER="$SCRIPT_DIR/deploy_projects.py"

if [[ "${EUID}" -eq 0 ]]; then
  printf 'ERROR: run as the normal deployment user, not root.\n' >&2
  exit 1
fi
for command in python3 git flock caddy sudo; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' "$command" >&2
    exit 1
  fi
done

# Hold the lock across self-update and re-execution.
if [[ "${XO_DEPLOY_LOCK_HELD:-}" != "1" ]]; then
  exec 9>"${TMPDIR:-/tmp}/xo-code-busters-project-deploy-$(id -u).lock"
  if ! flock -n 9; then
    printf 'ERROR: another project deployment is running.\n' >&2
    exit 1
  fi
  export XO_DEPLOY_LOCK_HELD=1
fi

if [[ "${XO_DEPLOY_SELF_UPDATED:-}" != "1" ]]; then
  if [[ "$(git -C "$XO_ROOT" rev-parse --show-toplevel)" != "$XO_ROOT" ||
        "$(git -C "$XO_ROOT" branch --show-current)" != "main" ]]; then
    printf 'ERROR: XO checkout must be the main branch at repository root.\n' >&2
    exit 1
  fi
  origin="$(git -C "$XO_ROOT" remote get-url origin)"
  case "$origin" in
    https://github.com/Sarajevo001/xo-code-busters|https://github.com/Sarajevo001/xo-code-busters.git|git@github.com:Sarajevo001/xo-code-busters|git@github.com:Sarajevo001/xo-code-busters.git) ;;
    *) printf 'ERROR: unexpected XO origin: %s\n' "$origin" >&2; exit 1 ;;
  esac
  if [[ -n "$(git -C "$XO_ROOT" status --porcelain --untracked-files=normal)" ]]; then
    printf 'ERROR: XO checkout has local changes.\n' >&2
    exit 1
  fi
  git -C "$XO_ROOT" fetch --no-tags origin main
  git -C "$XO_ROOT" merge --ff-only FETCH_HEAD
  # Restart from the updated file; avoid running a mix of old/new scripts.
  export XO_DEPLOY_SELF_UPDATED=1
  exec bash "$XO_ROOT/deploy/deploy.sh"
fi

if [[ ! -f "$PROJECTS" || ! -f "$DEPLOYER" ]]; then
  printf 'ERROR: missing deployment configuration or implementation.\n' >&2
  exit 1
fi
python3 "$DEPLOYER" --projects "$PROJECTS" --update
python3 "$SCRIPT_DIR/apply_caddy.py" --projects "$PROJECTS"
