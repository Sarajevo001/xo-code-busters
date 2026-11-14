#!/usr/bin/env bash
# Run as the Git checkout owner (debian), not root:
# bash /srv/GitHub/Sarajevo001/xo-code-busters/deploy/deploy-xo.sh
set -Eeuo pipefail
REPO=/srv/GitHub/Sarajevo001/xo-code-busters
SERVICE=xo-code-busters.service
HEALTH=http://127.0.0.1:3000/api/health
log() { printf '[deploy] %s\n' "$*"; }
fail() { log "ERROR: $*" >&2; exit 1; }
for cmd in git npm curl flock sudo; do command -v "$cmd" >/dev/null || fail "$cmd unavailable"; done
[[ "$(id -u)" -ne 0 ]] || fail "run as checkout owner, not root"
cd "$REPO" || fail "repository missing"
exec 9>/tmp/xo-code-busters-deploy.lock
flock -n 9 || fail "deployment already running"
[[ "$(git branch --show-current)" == main ]] || fail "checkout must be on main"
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] || fail "working tree is dirty"
remote="$(git remote get-url origin)"
case "$remote" in
  https://github.com/Sarajevo001/xo-code-busters|https://github.com/Sarajevo001/xo-code-busters.git|git@github.com:Sarajevo001/xo-code-busters|git@github.com:Sarajevo001/xo-code-busters.git) ;;
  *) fail "unexpected origin: $remote" ;;
esac
old="$(git rev-parse HEAD)"
git fetch --no-tags origin main
target="$(git rev-parse FETCH_HEAD)"
git merge-base --is-ancestor "$old" "$target" || fail "not a fast-forward; no update"
if [[ "$old" == "$target" ]]; then log "Already current: $old"; exit 0; fi
if [[ -n "$(git diff --name-only "$old" "$target" -- deploy/caddy/ deploy/systemd/)" ]]; then
  fail "infrastructure config changed; manual review required before deploying"
fi
npm_needed=false
restart_needed=false
if [[ -n "$(git diff --name-only "$old" "$target" -- src/server/package.json src/server/package-lock.json)" ]]; then npm_needed=true; fi
if [[ -n "$(git diff --name-only "$old" "$target" -- src/server/ src/shared/)" ]]; then restart_needed=true; fi
if [[ "$npm_needed" == true ]]; then
  git cat-file -e "$target:src/server/package-lock.json" || fail "target lockfile missing"
fi
# This must succeed before the checkout is modified.
sudo -n systemctl show "$SERVICE" --property=LoadState --value >/dev/null || fail "cannot query service"
updated=false
rollback() {
  rc=$?
  trap - ERR INT TERM
  if [[ "$updated" == true ]]; then
    log "Failure ($rc). Attempting rollback to $old"
    if git reset --hard "$old"; then
      if [[ "$npm_needed" == true ]]; then (cd src/server && npm ci --omit=dev) || log "WARNING: npm rollback failed"; fi
      sudo -n systemctl restart "$SERVICE" || log "WARNING: restart during rollback failed"
    else
      log "WARNING: git rollback failed"
    fi
    log "Rollback health is NOT verified; inspect the VPS manually."
  fi
  exit "$rc"
}
trap rollback ERR INT TERM
log "Updating $old -> $target"
git merge --ff-only "$target"
updated=true
if [[ "$npm_needed" == true ]]; then (cd src/server && npm ci --omit=dev); fi
if [[ "$restart_needed" == true ]]; then sudo -n systemctl restart "$SERVICE"; fi
ok=false
for ((i=1; i<=30; i++)); do
  response="$(curl -fsS --max-time 2 "$HEALTH" 2>/dev/null || true)"
  if [[ "$response" == *'"status":"ok"'* || "$response" == *'"status": "ok"'* ]]; then ok=true; break; fi
  sleep 1
done
[[ "$ok" == true ]] || fail "health check failed"
trap - ERR INT TERM
log "SUCCESS: $(git rev-parse HEAD)"
log "Local health OK. HTTPS, UI and P2P are not verified."
