import json
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_WATSONX_API_BASE = "https://us-south.ml.cloud.ibm.com"
_GENERATE_PATH = "/ml/v1/text/generation?version=2023-05-29"

_DEFAULT_MODEL_ID = "ibm/granite-13b-instruct-v2"
_DEFAULT_MAX_TOKENS = 1024
_DEFAULT_TIMEOUT = 30.0

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """\
You are a senior software architect performing a codebase audit.

Repository: {repo_name}

Root-level file structure:
{file_list}

Tasks:
1. Write a concise architecture_summary (2–4 sentences) describing the likely \
architecture, tech stack, and separation of concerns.
2. Identify up to 5 potential state_leaks: places where sensitive data \
(credentials, tokens, PII) may be exposed or persisted insecurely. \
For each leak provide: file, line (null if unknown), severity \
(critical|high|medium|low), and description.

Respond ONLY with a valid JSON object matching this schema:
{{
  "architecture_summary": "<string>",
  "state_leaks": [
    {{
      "file": "<path>",
      "line": <int|null>,
      "severity": "<critical|high|medium|low>",
      "description": "<string>"
    }}
  ]
}}
"""

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class WatsonXClientError(Exception):
    """Raised on authentication failures, HTTP errors, or malformed responses."""


class WatsonXTimeoutError(WatsonXClientError):
    """Raised when the Watsonx API does not respond within the configured timeout."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class WatsonXClient:
    """
    Async client for IBM Watsonx text-generation inference.

    Usage::

        async with WatsonXClient(api_key="…", project_id="…") as client:
            result = await client.analyze_codebase("owner/repo", file_list)
    """

    def __init__(
        self,
        api_key: str,
        project_id: str,
        model_id: str = _DEFAULT_MODEL_ID,
        max_new_tokens: int = _DEFAULT_MAX_TOKENS,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._api_key = api_key
        self._project_id = project_id
        self._model_id = model_id
        self._max_new_tokens = max_new_tokens

        self._client = httpx.AsyncClient(
            base_url=_WATSONX_API_BASE,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "WatsonXClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze_codebase(self, repo_name: str, file_list: list[dict]) -> dict:
        """
        Send the repository structure to Watsonx and return an analysis.

        Args:
            repo_name:  Full repository name, e.g. ``"owner/my-repo"``.
            file_list:  List of file-tree entry dicts as returned by
                        ``GithubClient.fetch_repo_summary``
                        (keys: ``path``, ``type``, ``size``).

        Returns:
            A dict with keys:
              - ``architecture_summary`` (str)
              - ``state_leaks`` (list[dict])

        Raises:
            WatsonXTimeoutError: When the request exceeds the configured timeout.
            WatsonXClientError:  On HTTP errors or unparseable model output.
        """
        prompt = self._build_prompt(repo_name, file_list)
        raw_text = await self._generate(prompt)
        return self._parse_response(raw_text)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, repo_name: str, file_list: list[dict]) -> str:
        formatted_files = "\n".join(
            f"  {'[dir] ' if entry.get('type') == 'tree' else '      '}{entry.get('path', '')}"
            for entry in file_list
        )
        return _PROMPT_TEMPLATE.format(repo_name=repo_name, file_list=formatted_files)

    async def _generate(self, prompt: str) -> str:
        """POST to the Watsonx generation endpoint and return the raw output text."""
        payload = {
            "model_id": self._model_id,
            "project_id": self._project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": self._max_new_tokens,
                "stop_sequences": [],
                "temperature": 0,
            },
        }

        # ----------------------------------------------------------------
        # NOTE: The actual HTTP call below is intentionally mocked.
        # Replace the block marked MOCK with the real call once credentials
        # are available:
        #
        #   response = await self._client.post(_GENERATE_PATH, json=payload)
        #   self._raise_for_status(response)
        #   data = response.json()
        #   return data["results"][0]["generated_text"]
        # ----------------------------------------------------------------

        # --- MOCK START -------------------------------------------------
        _ = payload  # payload is fully constructed; kept for real-call parity
        await self._simulate_network_latency()
        return json.dumps(
            {
                "architecture_summary": (
                    f"'{prompt[:30].strip()}…' — The repository appears to follow a "
                    "layered architecture with distinct separation between API, "
                    "business logic, and infrastructure layers. The stack suggests "
                    "a Python backend paired with a JavaScript frontend communicating "
                    "over a REST API."
                ),
                "state_leaks": [
                    {
                        "file": ".env",
                        "line": None,
                        "severity": "critical",
                        "description": "A .env file is present at the repository root. If committed to version control, secrets such as API keys and database credentials may be exposed.",
                    },
                    {
                        "file": "config/settings.py",
                        "line": 12,
                        "severity": "high",
                        "description": "Database connection string appears to be constructed from environment variables without validation, risking silent fallback to insecure defaults.",
                    },
                ],
            }
        )
        # --- MOCK END ---------------------------------------------------

    @staticmethod
    async def _simulate_network_latency() -> None:
        """Placeholder for real network I/O. Remove when the real call is wired in."""
        import asyncio
        await asyncio.sleep(0.5)

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Map Watsonx HTTP error codes to typed exceptions."""
        if response.status_code == 401:
            raise WatsonXClientError("Watsonx authentication failed (401). Check your API key.")
        if response.status_code == 429:
            raise WatsonXClientError("Watsonx rate limit exceeded (429). Retry after a short wait.")
        if not response.is_success:
            raise WatsonXClientError(
                f"Watsonx API returned {response.status_code}: {response.text[:200]}"
            )

    @staticmethod
    def _parse_response(raw_text: str) -> dict:
        """
        Extract and validate the JSON payload from the model's output text.

        The model is instructed to return only JSON, but may occasionally wrap
        it in markdown fences — this method strips those defensively.
        """
        text = raw_text.strip()

        # Strip optional ```json ... ``` fences the model may emit
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(
                line for line in lines if not line.strip().startswith("```")
            ).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise WatsonXClientError(
                f"Model returned non-JSON output. Raw text (first 300 chars): {raw_text[:300]}"
            ) from exc

        if "architecture_summary" not in data or "state_leaks" not in data:
            raise WatsonXClientError(
                "Model response is missing required keys "
                "'architecture_summary' or 'state_leaks'."
            )

        return {
            "architecture_summary": str(data["architecture_summary"]),
            "state_leaks": list(data["state_leaks"]),
        }
