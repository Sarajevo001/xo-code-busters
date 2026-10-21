# Shared server library

This directory holds server-side modules used by both the public user API and the administration API. Each service installs or bundles its own copy for independent deployment; no runtime dependency on the other service is allowed.

Planned modules:
- `db/`: connection management and transaction/SQL infrastructure (separate credentials per service)
- `logging/`: logging infrastructure
- `errors/`: shared error types and error handling helpers
- `config/`: configuration loading
- `utils/`: generic helpers

No database access, logging, authentication, or other backend features are implemented by this initial scaffold. Do not import this package in browser code. Preserve separate authorization checks in each service.
