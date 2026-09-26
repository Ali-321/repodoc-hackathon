const BASE_URL = "http://localhost:8000";

/**
 * Submits a repository URL for analysis.
 * @param {string} repoUrl - The GitHub repository URL to analyze.
 * @returns {Promise<{status: string, repo_url: string, architecture_summary: string, state_leaks: Array}>}
 */
export async function analyzeRepo(repoUrl) {
  const response = await fetch(`${BASE_URL}/api/v1/repos/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail ?? `Request failed with status ${response.status}`);
  }

  return response.json();
}
