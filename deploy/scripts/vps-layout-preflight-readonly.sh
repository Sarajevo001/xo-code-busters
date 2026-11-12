#!/usr/bin/env bash
# VPS migration preflight: read-only inventory, run locally on the VPS.
# Do not run with sudo. Output may contain user names, internal paths and Git remotes.
set -u
export LC_ALL=C
umask 077
echo "XO/RPG VPS preflight (read-only)"; date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
echo "host=$(hostname) user=$(id -un)"
echo "=== services (state only) ==="
for svc in caddy xo-code-busters; do
  printf '%s active=' "$svc"; systemctl is-active "$svc" 2>&1 || :
  printf '%s enabled=' "$svc"; systemctl is-enabled "$svc" 2>&1 || :
done
echo "=== service unit references (no environment variables) ==="
systemctl show xo-code-busters -p FragmentPath -p DropInPaths -p User -p Group -p WorkingDirectory -p ExecStart --no-pager 2>&1 || :
systemctl show caddy -p FragmentPath -p DropInPaths -p User -p Group --no-pager 2>&1 || :
echo "=== configured paths (metadata only) ==="
for p in /srv/xo-code-busters /home/debian/oop-rpg-workshop /var/www/demo/oop-rpg-workshop /srv/GitHub/Sarajevo001/xo-code-busters /srv/GitHub/Sarajevo001/oop-rpg-workshop /var/lib/projects/Sarajevo001/xo-code-busters /var/lib/projects/Sarajevo001/oop-rpg-workshop /etc/caddy/Caddyfile /etc/systemd/system/xo-code-busters.service; do
  if test -e "$p" || test -L "$p"; then stat -c '%A %U:%G %F %n' "$p" 2>&1 || :; else echo "MISSING $p"; fi
done
echo "=== Git checkouts (no remote URL, credentials or file contents) ==="
for p in /srv/xo-code-busters /home/debian/oop-rpg-workshop /srv/GitHub/Sarajevo001/xo-code-busters /srv/GitHub/Sarajevo001/oop-rpg-workshop; do
  echo "PATH $p"
  if test -d "$p/.git" || test -f "$p/.git"; then
    git -C "$p" rev-parse --show-toplevel HEAD 2>&1 || :
    git -C "$p" branch --show-current 2>&1 || :
    git -C "$p" status --porcelain=v1 -uno 2>&1 | sed -n '1,30p'
    printf 'tracked files='; git -C "$p" ls-files | wc -l
    printf 'untracked files='; git -C "$p" ls-files --others --exclude-standard | wc -l
  else echo 'NO GIT WORKTREE'; fi
done
echo "=== Caddy configuration references (path and status only) ==="
if test -r /etc/caddy/Caddyfile; then
  echo 'Caddyfile readable (contents intentionally not printed)'
  sha256sum /etc/caddy/Caddyfile
  grep -nE '^[[:space:]]*(import|root|file_server|reverse_proxy|handle|handle_path|route)[[:space:]]' /etc/caddy/Caddyfile | sed -E 's/(password|token|secret|key)[^[:space:]]*/[REDACTED]/Ig' | head -60
else echo 'Caddyfile unreadable'; fi
echo "=== public URL baseline (headers only) ==="
for url in https://sarajevo.jp/ https://sarajevo.jp/game/ https://sarajevo.jp/api/health https://demo.sarajevo.jp/oop-rpg-workshop/; do
  curl --silent --show-error --location --max-redirs 3 --connect-timeout 5 --max-time 15 --output /dev/null --write-out '%{url_effective} HTTP %{http_code} redirects %{num_redirects}\n' "$url" || echo "REQUEST_FAILED $url"
done
echo "=== done: NO changes made ==="
