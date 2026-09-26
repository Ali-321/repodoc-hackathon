# Agent Mode Rules

## Must-Know Before Coding

- **WatsonX mock block** is in `backend/app/infrastructure/llm/watsonx_client.py` inside `_generate()`. The real HTTP call is commented out directly above it. Do NOT delete the commented-out code — it is the reference implementation.
- **`fetch_repo_summary()` returns `file_tree` key**, but `analyze_repo.py` accesses `repo_data.get('tree', [])` — note the key mismatch; `tree` comes from GitHub's raw API, `file_tree` is the cleaned version. The use-case reads the raw `tree` list from the metadata dict separately if you look closely — verify actual key access before modifying the data flow.
- Async clients must be used via `async with` — both `GithubClient` and `WatsonXClient` close their `httpx.AsyncClient` on `__aexit__`. Calling methods without context manager leaks connections.
- **No test runner is configured.** To add tests, use `pytest` + `pytest-asyncio` and run from `backend/` with the venv active: `pytest tests/`.
- Frontend has **no state management library** — all state is local `useState` in `AuditPage.jsx`. Keep it that way unless explicitly asked to add one.
- Backend venv is at `backend/.venv` — always activate before running uvicorn or pip commands.
