# Ask Mode Rules

## Non-Obvious Project Context

- The `backend/app/schemas/` and `backend/app/core/domain/` directories are **empty stubs** — Pydantic request/response models currently live directly in `main.py`.
- The `backend/app/api/v1/` directory is also empty — routing is done directly in `main.py` (no router files).
- `WatsonXClient` is wired for IBM Granite (`ibm/granite-13b-instruct-v2`) on `us-south.ml.cloud.ibm.com`, but the entire HTTP layer is bypassed by a mock. The LLM integration is architectural scaffolding only.
- `bob_sessions/` directory contains hackathon session logs (IBM Bob IDE usage evidence), not application code.
- The frontend mirrors the backend's Clean Architecture layer names exactly: `core/domain`, `core/useCases`, `infrastructure/api`, `ui/features`.
- No `.env` file is committed — backend reads `GITHUB_TOKEN` and Watsonx keys from environment, but the mock means neither is required to run locally.
