from app.infrastructure.git.github_client import GithubClient, GithubClientError
from app.infrastructure.llm.watsonx_client import WatsonXClient, WatsonXClientError, WatsonXTimeoutError

async def execute_repo_analysis(repo_url: str) -> dict:
    """
    Orchestrates the analysis:
    1. Fetches REAL repo data via GithubClient
    2. Sends data to WatsonxClient (currently using internal mock)
    3. Formats the final response
    """
    try:
        # Step 1: Fetch real GitHub data
        async with GithubClient() as git_client:
            repo_data = await git_client.fetch_repo_summary(repo_url)
        
        files_found = [item['path'] for item in repo_data.get('tree', []) if item['type'] == 'blob']
        repo_name = repo_data.get("metadata", {}).get("full_name", "unknown/repo")
        
        # Step 2: Send to Watsonx Client
        # We initialize with fake keys because Bob's mock block bypasses the actual network call
        async with WatsonXClient(api_key="mock_key", project_id="mock_id") as llm_client:
            llm_result = await llm_client.analyze_codebase(
                repo_name=repo_name,
                file_list=files_found
            )
            
        # Step 3: Combine and return
        return {
            "status": "success",
            "repo_url": repo_data.get("metadata", {}).get("html_url", repo_url),
            "architecture_summary": llm_result.get("architecture_summary", "Analysis unavailable."),
            "state_leaks": llm_result.get("state_leaks", [])
        }
        
    except (GithubClientError, WatsonXClientError, WatsonXTimeoutError) as e:
        return {
            "status": "error",
            "message": str(e)
        }