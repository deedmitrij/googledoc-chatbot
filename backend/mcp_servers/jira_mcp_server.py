from langchain_mcp_adapters.server import  run_mcp_server
from backend.services.jira_service import JiraService
from langchain.tools import StructuredTool

jira_service = JiraService()

tools = [
    StructuredTool.from_function(
        name="create_jira_ticket",
        func=jira_service.create_ticket,
        description="Create a new Jira ticket.",
    ),
    StructuredTool.from_function(
        name="update_jira_ticket",
        func=jira_service.update_ticket,
        description="Update an existing Jira ticket.",
    ),
    StructuredTool.from_function(
        name="get_jira_ticket",
        func=jira_service.get_ticket,
        description="Get the details of a Jira ticket.",
    ),
]

if __name__ == "__main__":
    run_mcp_server(tools)
