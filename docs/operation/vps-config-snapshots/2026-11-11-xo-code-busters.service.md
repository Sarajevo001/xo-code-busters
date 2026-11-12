# VPS systemd unit snapshot (2026-11-11)

Source: output of `sudo systemctl cat xo-code-busters.service` provided by the VPS operator on 2026-11-11.

Original path: `/etc/systemd/system/xo-code-busters.service`.

This is an exact record of the unit content shown in the command output, not a new deployment configuration. The original VPS file has not been changed.

```ini
[Unit]
Description=XO-Code Busters Express Server
After=network.target

[Service]
Type=simple
User=xo-code-busters
Group=xo-code-busters
WorkingDirectory=/srv/xo-code-busters/src/server
ExecStart=/usr/bin/node /srv/xo-code-busters/src/server/server.js
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Restoration notes:
- This preserves the unit file contents but does not automatically recreate its directory, service account, Node installation, executable files, or systemd enablement.
- For rollback, keep the existing `/srv/xo-code-busters` worktree and restore the unit path references, then perform `systemctl daemon-reload` and an explicitly approved service restart.
- Do not apply the old paths to a new deployment without checking the actual target layout.
