# VPS Caddyfile snapshot (2026-11-11)

Source: `/etc/caddy/Caddyfile` on the existing VPS, transcribed from the user's prior read-only inspection.

This is a record of the observed configuration, **not** an automatically installed or tested deployment configuration. Restore only after checking the target VPS and validating the Caddy configuration. No secrets are included in the observed content.

```caddyfile
sarajevo.jp {
    reverse_proxy 127.0.0.1:3000
}

demo.sarajevo.jp {
    root * /var/www/demo
    file_server
}
```

Notes:
- This snapshot preserves the observed Caddyfile content, not necessarily all imported snippets, systemd overrides, or runtime environment.
- `sarajevo.jp` proxies to the XO Node process; `demo.sarajevo.jp` serves `/var/www/demo`.
- The original VPS configuration has not been modified.
