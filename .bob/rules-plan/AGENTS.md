# Plan Mode Rules

## Architectural Constraints

- **Strict Clean Architecture** — domain logic must never import from `infrastructure.*`; use cases orchestrate, infrastructure implements. Violating this layering breaks the intended testability.
- **WatsonX integration is forward-only placeholder** — the mock in `_generate()` must be replaced (not wrapped) when real credentials are available. The real call signature is already commented in the same method.
- **GitHub rate limiting** is handled by `GithubClientError` (403) — any plan involving heavy GitHub API use must account for optional token injection via `GithubClient(token=...)`.
- **CORS is single-origin** (`localhost:5173`) — multi-environment deployment requires parameterising `allow_origins` in `main.py`.
- **No database** — all results are ephemeral, returned per-request. Any persistence plan requires adding a DB layer from scratch.
- **No auth layer** — the `/api/v1/repos/analyze` endpoint is fully public. Security must be added before any production deployment plan.
- **Frontend is zero-dependency UI** — plans to add component libraries must account for the current all-inline-style approach across `AuditPage.jsx`.
