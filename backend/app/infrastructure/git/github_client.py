import re
from typing import Any

import httpx

# Matches both https://github.com/owner/repo and https://github.com/owner/repo.git
_GITHUB_URL_RE = re.compile(
    r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/?.#]+?)(?:\.git)?/?$"
)

_GITHUB_API = "https://api.github.com"
_DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GithubClientError(Exception):
    """Raised when the GitHub API returns an error or the URL is invalid."""


class GithubClient:
    """Async client for fetching public GitHub repository metadata."""

    def __init__(self, token: str | None = None, timeout: float = 15.0) -> None:
        headers = _DEFAULT_HEADERS.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(headers=headers, timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "GithubClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch_repo_summary(self, repo_url: str) -> dict:
        """
        Fetch repository metadata and root file tree from the GitHub API.

        Args:
            repo_url: Public GitHub repository URL
                      (e.g. https://github.com/owner/repo).

        Returns:
            A dict with keys:
              - owner (str)
              - repo  (str)
              - metadata (dict)  — subset of the GitHub Repos API response
              - file_tree (list) — root-level entries from the Git Trees API

        Raises:
            GithubClientError: On invalid URL or a non-2xx GitHub API response.
        """
        owner, repo = self._parse_url(repo_url)

        metadata  = await self._fetch_metadata(owner, repo)
        file_tree = await self._fetch_file_tree(owner, repo, metadata.get("default_branch", "main"))

        return {
            "owner": owner,
            "repo": repo,
            "metadata": metadata,
            "file_tree": file_tree,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_url(repo_url: str) -> tuple[str, str]:
        match = _GITHUB_URL_RE.match(repo_url.strip())
        if not match:
            raise GithubClientError(
                f"Invalid or unsupported GitHub URL: '{repo_url}'. "
                "Expected format: https://github.com/owner/repo"
            )
        return match.group("owner"), match.group("repo")

    async def _get(self, url: str) -> dict:
        """Perform a GET request and raise GithubClientError on failure."""
        try:
            response = await self._client.get(url)
        except httpx.RequestError as exc:
            raise GithubClientError(f"Network error contacting GitHub API: {exc}") from exc

        if response.status_code == 404:
            raise GithubClientError(
                f"Repository not found (404). Check that the URL is correct and the repo is public. URL: {url}"
            )
        if response.status_code == 403:
            raise GithubClientError(
                "GitHub API rate limit exceeded or access forbidden (403). "
                "Provide a personal access token to increase the rate limit."
            )
        if not response.is_success:
            raise GithubClientError(
                f"GitHub API returned {response.status_code} for {url}: {response.text[:200]}"
            )

        return response.json()

    async def _fetch_metadata(self, owner: str, repo: str) -> dict:
        """Fetch core repo metadata and return a clean subset."""
        raw = await self._get(f"{_GITHUB_API}/repos/{owner}/{repo}")

        return {
            "full_name":        raw.get("full_name"),
            "description":      raw.get("description"),
            "default_branch":   raw.get("default_branch", "main"),
            "language":         raw.get("language"),
            "topics":           raw.get("topics", []),
            "stargazers_count": raw.get("stargazers_count", 0),
            "forks_count":      raw.get("forks_count", 0),
            "open_issues":      raw.get("open_issues_count", 0),
            "license":          raw.get("license", {}).get("spdx_id") if raw.get("license") else None,
            "visibility":       raw.get("visibility", "public"),
            "created_at":       raw.get("created_at"),
            "updated_at":       raw.get("updated_at"),
            "html_url":         raw.get("html_url"),
        }

    async def _fetch_file_tree(self, owner: str, repo: str, branch: str) -> list[dict]:
        """Fetch the root-level file/directory tree for the given branch."""
        raw = await self._get(f"{_GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}")

        return [
            {
                "path": entry.get("path"),
                "type": entry.get("type"),   # "blob" | "tree"
                "size": entry.get("size"),    # None for directories
            }
            for entry in raw.get("tree", [])
        ]
