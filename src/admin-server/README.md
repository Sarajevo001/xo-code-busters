# Admin Express server

Separate process from the public user API. Defaults to 127.0.0.1:3001; override with ADMIN_HOST and ADMIN_PORT.

Currently only GET /api/health returns 200. All other paths return HTTP 503 until server-side administrator authentication, sessions and authorization are implemented. In particular, src/admin-client is NOT served.

Install dependencies in this directory before starting with npm start. The systemd unit in deploy/systemd is a draft and must not be enabled without an explicit deployment decision.

Planned hostname: admin.sarajevo.jp. Do not make this server publicly accessible in its present state.
