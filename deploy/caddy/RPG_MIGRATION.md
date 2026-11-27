# RPG migration: stage 4 (historical record)

The following preparation and preconditions are historical, not the current deployment procedure. Use `bash deploy/deploy.sh` from the XO checkout; see [common deployment](../COMMON_DEPLOY.md).

## Confirmed inputs
- Current live Caddyfile (provided by operator): `sarajevo.jp` reverse proxy to `127.0.0.1:3000`, `demo.sarajevo.jp` static root `/var/www/demo`.
- RPG repository: `Sarajevo001/oop-rpg-workshop`, static source `src/public`.
- Existing URL: `https://demo.sarajevo.jp/oop-rpg-workshop/`.

## Prepared changes
- RPG repo: `deploy.json` describes `src/public`.
- XO registry: `deploy/projects.json` registers the existing URL.
- `deploy/caddy/demo-rpg.proposed.Caddyfile` is a **review-only** full configuration, not an automatic deployment file.

## Preconditions (before any live change)
1. Verify the VPS clone is updated to the commit containing `deploy.json`, clean, and `src/public/index.html` exists.
2. Verify permissions: the Caddy service user must traverse each parent directory and read published files.
3. Back up `/etc/caddy/Caddyfile`; compare it with the previously observed version. Stop if it differs.
4. Confirm no additional sites/routes exist and no external configuration imports are required.
5. Run the common planner with the registered project; it must succeed.
6. Validate proposed Caddyfile with `caddy validate --config <staged-file> --adapter caddyfile` before any replacement.

## Integration and acceptance
- Apply only after preconditions succeed, with rollback backup and a planned maintenance/reload step.
- Confirm existing XO home and health endpoint, demo root, and RPG entry page over HTTPS.
- Confirm RPG JS/CSS/assets load and gameplay in browser, not just HTTP 200.
- On failure restore the backup, validate, reload, and recheck both sites.

## Status
**Updated status (2026-11-27):** prior operational conversation records report successful deployment and Caddy application on November 19, an unchanged repeat deployment, and successful deployment on November 26 (30ae57a), with operator browser confirmation of the demo entrance and RPG navigation. Raw HTTP status for unregistered paths, current VPS cleanup of `/var/www/demo`, and rollback execution are not established by those records. Current configuration generation points directly to the Git checkout, not the old copy directory.
