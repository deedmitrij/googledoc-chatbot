from langchain_mcp_adapters.server import run_mcp_server
from backend.services.github_service import GithubService
from langchain.tools import StructuredTool

github_service = GithubService()

tools = [
    StructuredTool.from_function(
        name="create_github_file",
        func=github_service.create_file,
        description="Create a new file in the GitHub repository.",
    ),
    StructuredTool.from_function(
        name="update_github_file",
        func=github_service.update_file,
        description="Update an existing file in the GitHub repository.",
    ),
    StructuredTool.from_function(
        name="read_github_file",
        func=github_service.read_file,
        description="Read the contents of a file in the GitHub repository.",
    ),
    StructuredTool.from_function(
        name="create_github_pull_request",
        func=github_service.create_pull_request,
        description="Create a new pull request in the GitHub repository.",
    ),
]

if __name__ == "__main__":
    run_mcp_server(tools)
