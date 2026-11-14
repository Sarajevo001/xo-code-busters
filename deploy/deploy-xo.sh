#!/usr/bin/env bash
# XO-Code Busters: bootstrap and subsequent deployments, one command.
# Run as the owner of the VPS checkout (normally debian), not root.
set -Eeuo pipefail
REPO=/srv/GitHub/Sarajevo001/xo-code-busters
SERVICE=xo-code-busters.service
UNIT=/etc/systemd/system/xo-code-busters.service
HEALTH=http://127.0.0.1:3000/api/health
log() { printf '[deploy] %s\n' "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }
for tool in git npm curl flock sudo systemctl cmp mktemp; do command -v "$tool" >/dev/null || die "$tool unavailable"; done
[[ "$(id -u)" -ne 0 ]] || die "run as checkout owner, not root"
cd "$REPO" || die "repository directory missing"
exec 9>/tmp/xo-code-busters-deploy.lock
flock -n 9 || die "another deployment is running"
[[ "$(git branch --show-current)" == main ]] || die "checkout is not on main"
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] || die "working tree has local changes"
case "$(git remote get-url origin)" in
  https://github.com/Sarajevo001/xo-code-busters|https://github.com/Sarajevo001/xo-code-busters.git|git@github.com:Sarajevo001/xo-code-busters|git@github.com:Sarajevo001/xo-code-busters.git) ;;
  *) die "unexpected origin repository" ;;
esac
old="$(git rev-parse HEAD)"
git fetch --no-tags origin main
target="$(git rev-parse FETCH_HEAD)"
git merge-base --is-ancestor "$old" "$target" || die "main has diverged; no files changed"
if [[ -n "$(git diff --name-only "$old" "$target" -- deploy/caddy/)" ]]; then
  die "Caddy configuration changed; separate infrastructure review required"
fi
# Existing unit may be from an earlier deployment, even if Git is already current.
new_unit="$(git show "$target:deploy/systemd/xo-code-busters.service")"
[[ -n "$new_unit" ]] || die "target systemd unit missing"
tmp_unit="$(mktemp /tmp/xo-code-busters-unit.XXXXXXXX.service)"
printf '%s\n' "$new_unit" > "$tmp_unit"
unit_changed=false
if ! sudo cmp -s "$tmp_unit" "$UNIT"; then unit_changed=true; fi
if [[ "$unit_changed" == true ]]; then
  # Check before touching the live unit. This can fail on an invalid target unit.
  sudo systemd-analyze verify "$tmp_unit" || die "systemd unit verification failed"
fi
npm_needed=false
if [[ -n "$(git diff --name-only "$old" "$target" -- src/server/package.json src/server/package-lock.json)" ]]; then
  npm_needed=true
  git cat-file -e "$target:src/server/package-lock.json" || die "target package-lock missing"
fi
# Allow interactive sudo authentication once, before changing any state.
sudo -v || die "sudo authorization failed"
backup=""
updated=false
unit_installed=false
cleanup() { rm -f "$tmp_unit"; }
rollback() {
  rc=$?
  trap - ERR INT TERM
  log "Deployment failed (exit $rc). Attempting recovery."
  if [[ "$updated" == true ]]; then
    git reset --hard "$old" || log "WARNING: Git restore failed"
    if [[ "$npm_needed" == true ]]; then (cd src/server && npm ci --omit=dev) || log "WARNING: npm restore failed"; fi
  fi
  if [[ "$unit_installed" == true ]]; then
    if [[ -n "$backup" ]]; then
      sudo cp "$backup" "$UNIT" || log "WARNING: unit restore failed"
    else
      sudo rm -f "$UNIT" || log "WARNING: new unit removal failed"
    fi
    sudo systemctl daemon-reload || log "WARNING: daemon-reload failed"
  fi
  if [[ "$updated" == true || "$unit_installed" == true ]]; then
    sudo systemctl restart "$SERVICE" || log "WARNING: restart failed"
  fi
  cleanup
  log "Recovery is not verified. Inspect service health before further changes."
  exit "$rc"
}
trap rollback ERR INT TERM
trap cleanup EXIT
log "Deploying $old -> $target"
if [[ "$old" != "$target" ]]; then
  git merge --ff-only "$target"
  updated=true
fi
if [[ "$npm_needed" == true ]]; then (cd src/server && npm ci --omit=dev); fi
if [[ "$unit_changed" == true ]]; then
  log "Installing validated systemd unit (previous unit backed up)"
  if sudo test -f "$UNIT"; then
    backup="$(sudo mktemp /etc/systemd/system/xo-code-busters.service.backup.XXXXXXXX)"
    sudo cp "$UNIT" "$backup"
  fi
  sudo cp "$tmp_unit" "$UNIT"
  unit_installed=true
  sudo systemctl daemon-reload
fi
# Restart on each successful deployment, including initial reconciliation.
sudo systemctl restart "$SERVICE"
healthy=false
for ((i=1; i<=30; i++)); do
  response="$(curl -fsS --max-time 2 "$HEALTH" 2>/dev/null || true)"
  if [[ "$response" == *'"status":"ok"'* || "$response" == *'"status": "ok"'* ]]; then healthy=true; break; fi
  sleep 1
done
[[ "$healthy" == true ]] || die "local API health check failed"
trap - ERR INT TERM
log "SUCCESS: $(git rev-parse HEAD)"
log "Local API OK; public HTTPS and browser functionality not tested."
