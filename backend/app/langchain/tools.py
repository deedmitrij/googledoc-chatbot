import json
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from backend.app.document_manager import DocumentManager
from backend.app.langchain.chains import LLMChains
from backend.app.memory_manager import ChatbotMemoryManager
from backend.services.jira_service import JiraService
from backend.services.github_service import GithubService


memory_manager = ChatbotMemoryManager()
document_manager = DocumentManager()
llm_chains = LLMChains()
jira_service = JiraService()
github_service = GithubService()


class UploadDocInput(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    doc_link: str = Field(description="Link to Google document")


class FeatureNameInput(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    feature_name: str = Field(description="Name of the feature for which to generate test cases")


class UserIDInput(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")


# === Tool 1: Load Specification document ===
def load_specification_doc(user_id: str, doc_link: str) -> str:
    document_manager.load_and_store_document(doc_link=doc_link,
                                             collection='specification',
                                             user_id=user_id)

    memory_manager.set_spec_doc_link(user_id, doc_link)
    memory_manager.set_current_step(user_id, "Awaiting for a link to Test Cases document.")

    return (f"✅ Specification document has been loaded successfully.\n"
            f"Now, send a link to the Test Cases document.")


load_specification_doc_tool = StructuredTool.from_function(
    name="Load Specification from Google Doc",
    func=load_specification_doc,
    description="Use this tool to load the Specification content from Google Doc. Input should be a Google Doc link.",
    args_schema=UploadDocInput,
    return_direct=True
)


# === Tool 2: Load Test Cases document ===
def load_test_cases_doc(user_id: str, doc_link: str) -> str:
    document_manager.load_and_store_document(doc_link=doc_link,
                                             collection='test_cases',
                                             user_id=user_id)

    memory_manager.set_test_cases_doc_link(user_id, doc_link)

    memory_manager.set_current_step(user_id, "Provide feature name")
    memory_manager.set_documents_loaded(user_id, True)
    memory_manager.set_current_step(user_id, "Awaiting for specifying a feature name.")

    return (f"✅ Test Cases document has been loaded successfully.\n"
            f"Now, specify the name of the feature for which you want to generate test cases.")


load_test_cases_doc_tool = StructuredTool.from_function(
    name="Load Test Cases from Google Doc",
    func=load_test_cases_doc,
    description="Use this tool to load the Test Cases content from Google Doc. Input should be a Google Doc link.",
    args_schema=UploadDocInput,
    return_direct=True
)


# === Tool 3: Specify feature name ===
def specify_feature_name(user_id: str, feature_name: str) -> str:
    memory_manager.set_feature(user_id, feature_name)
    memory_manager.set_current_step(user_id, "Awaiting for generating test cases.")

    return 'Awaiting for generating test cases.'


specify_feature_name_tool = StructuredTool.from_function(
    name="Specify feature name",
    func=specify_feature_name,
    description="Use this tool to specify feature name or set another feature name for which to generate test cases.",
    args_schema=FeatureNameInput
)


# === Tool 4: Generate Test Cases ===
def generate_test_cases(user_id: str) -> str:
    feature_name = memory_manager.get_feature(user_id)
    relevant_specs = document_manager.find_similar_data_to_query(query=feature_name,
                                                                 collection='specification',
                                                                 user_id=user_id)
    relevant_test_cases = document_manager.find_similar_data_to_query(query=feature_name,
                                                                      collection='test_cases',
                                                                      user_id=user_id)
    test_cases = document_manager.generate_test_cases(relevant_specs=relevant_specs,
                                                      relevant_test_cases=relevant_test_cases,
                                                      feature=feature_name)

    menu = ["🔄 Extract another feature", "📄 Upload new documents", "❌ End session"]

    memory_manager.set_current_step(user_id, f"Awaiting for user to select one of the menu options: {menu}")

    return (json.dumps({
        "response": test_cases,
        "menu": ["🔄 Extract another feature", "📄 Upload new documents", "❌ End session"]
    }))


generate_test_cases_tool = StructuredTool.from_function(
    name="Generate Test Cases",
    func=generate_test_cases,
    description="Use this tool to generate test cases.",
    args_schema=UserIDInput,
    return_direct=True
)


# === Tool 5: Fetch Chat History ===
def fetch_chat_history(user_id: str):
    memory = memory_manager.get_memory(user_id)
    memory_vars = memory.load_memory_variables({})
    chat_history = memory_vars.get('chat_history', [])
    history_text = ""
    for message in chat_history:
        role = "User" if message.type == "human" else "Assistant"
        history_text += f"{role}: {message.content}\n"
    return history_text


check_chat_history_tool = StructuredTool.from_function(
    name="Show Chat History Tool",
    description=(
        "Use this tool only if you are unsure, or cannot find the information you need in the provided chat history. "
        "This tool returns the full, detailed chat history between you and the user. "
        "Use it to verify details about previous links, answers, or messages before responding, "
        "especially if you are not certain from the memory context."
    ),
    func=fetch_chat_history,
    args_schema=UserIDInput
)


# === Tool 6: Check the current context ===
def check_current_context(user_id: str):
    context = memory_manager.get_current_step(user_id)

    return context


check_current_context_tool = StructuredTool.from_function(
    name="Check the current context",
    description=(
        "**ALWAYS** use this tool before responding to the user. "
        "It returns the current dialogue context for a specific user based on what the bot expects next. "
        "The result might be a short instruction or a multi-line message with specific prompts. "
        "Use this tool to:\n"
        "- Understand what step the user is currently on\n"
        "- Interpret ambiguous replies (e.g., '1', 'yes', 'this one')\n"
        "- Determine what kind of response or document link the user is expected to provide\n"
        "This tool must be called for **EVERY** user message before generating any reply or deciding on next actions."
    ),
    func=check_current_context,
    args_schema=UserIDInput
)


# === Tool 7: Upload new documents ===
def upload_new_documents(user_id: str) -> str:
    memory_manager.clear_context(user_id)
    memory_manager.set_current_step(user_id, "Awaiting for a link to Specification document")

    return "User wants to upload new documents. Awaiting for a link to Specification document"


upload_new_documents_tool = StructuredTool.from_function(
    name="Upload new documents",
    func=upload_new_documents,
    description="Use this tool to clear previously uploaded documents and wait for uploading new documents.",
    args_schema=UserIDInput
)


# === Tool 8: Upload new documents ===
def clear_session(user_id: str) -> str:
    memory_manager.clear_session(user_id)
    memory_manager.set_current_step(user_id, "Awaiting for a link to Specification document")

    return (json.dumps({
        "response": "The user's session has been cleared.",
        "reset": True
    }))


clear_session_tool = StructuredTool.from_function(
    name="Clear user session",
    func=clear_session,
    description="Use this tool to clear the user session.",
    args_schema=UserIDInput
)


class CreateGithubFileInput(BaseModel):
    file_path: str = Field(description="Path of the file to create in the GitHub repository")
    content: str = Field(description="Content to write to the new file")
    commit_message: str = Field(description="Commit message for the file creation")

class UpdateGithubFileInput(BaseModel):
    file_path: str = Field(description="Path of the file to update in the GitHub repository")
    content: str = Field(description="New content for the file")
    commit_message: str = Field(description="Commit message for the file update")

class ReadGithubFileInput(BaseModel):
    file_path: str = Field(description="Path of the file to read from the GitHub repository")

class CreateGithubPullRequestInput(BaseModel):
    title: str = Field(description="Title of the pull request")
    body: str = Field(description="Body of the pull request")
    head_branch: str = Field(description="The name of the branch where your changes are implemented")
    base_branch: str = Field(description="The name of the branch you want the changes pulled into")


def create_github_file(file_path: str, content: str, commit_message: str) -> str:
    result = github_service.create_file(file_path, content, commit_message)
    return result

def update_github_file(file_path: str, content: str, commit_message: str) -> str:
    result = github_service.update_file(file_path, content, commit_message)
    return result

def read_github_file(file_path: str) -> str:
    content = github_service.read_file(file_path)
    return content

def create_github_pull_request(title: str, body: str, head_branch: str, base_branch: str) -> str:
    pr_url = github_service.create_pull_request(title, body, head_branch, base_branch)
    return f"Pull request created: {pr_url}"


create_github_file_tool = StructuredTool.from_function(
    name="Create GitHub File",
    func=create_github_file,
    description="Use this tool to create a new file in the GitHub repository.",
    args_schema=CreateGithubFileInput,
    return_direct=True
)

update_github_file_tool = StructuredTool.from_function(
    name="Update GitHub File",
    func=update_github_file,
    description="Use this tool to update an existing file in the GitHub repository.",
    args_schema=UpdateGithubFileInput,
    return_direct=True
)

read_github_file_tool = StructuredTool.from_function(
    name="Read GitHub File",
    func=read_github_file,
    description="Use this tool to read the contents of a file in the GitHub repository.",
    args_schema=ReadGithubFileInput
)

create_github_pull_request_tool = StructuredTool.from_function(
    name="Create GitHub Pull Request",
    func=create_github_pull_request,
    description="Use this tool to create a new pull request in the GitHub repository.",
    args_schema=CreateGithubPullRequestInput,
    return_direct=True
)


class CreateJiraTicketInput(BaseModel):
    title: str = Field(description="Title of the Jira ticket")
    description: str = Field(description="Description of the Jira ticket")
    issue_type: str = Field(description="Type of the Jira ticket (e.g., Story, Bug, Task)")

class UpdateJiraTicketInput(BaseModel):
    ticket_key: str = Field(description="Key of the Jira ticket to update")
    comment: str = Field(description="Comment to add to the Jira ticket")

class GetJiraTicketInput(BaseModel):
    ticket_key: str = Field(description="Key of the Jira ticket to retrieve")


def create_jira_ticket(title: str, description: str, issue_type: str) -> str:
    ticket_key = jira_service.create_ticket(title, description, issue_type)
    return f"Jira ticket created with key: {ticket_key}"

def update_jira_ticket(ticket_key: str, comment: str) -> str:
    result = jira_service.update_ticket(ticket_key, comment)
    return result

def get_jira_ticket(ticket_key: str) -> str:
    ticket = jira_service.get_ticket(ticket_key)
    return json.dumps(ticket)


create_jira_ticket_tool = StructuredTool.from_function(
    name="Create Jira Ticket",
    func=create_jira_ticket,
    description="Use this tool to create a new Jira ticket.",
    args_schema=CreateJiraTicketInput,
    return_direct=True
)

update_jira_ticket_tool = StructuredTool.from_function(
    name="Update Jira Ticket",
    func=update_jira_ticket,
    description="Use this tool to add a comment to an existing Jira ticket.",
    args_schema=UpdateJiraTicketInput,
    return_direct=True
)

get_jira_ticket_tool = StructuredTool.from_function(
    name="Get Jira Ticket",
    func=get_jira_ticket,
    description="Use this tool to retrieve the details of a Jira ticket.",
    args_schema=GetJiraTicketInput
)


# === Export All Tools as a List ===
all_tools = [
    load_specification_doc_tool,
    load_test_cases_doc_tool,
    specify_feature_name_tool,
    generate_test_cases_tool,
    check_chat_history_tool,
    check_current_context_tool,
    upload_new_documents_tool,
    clear_session_tool,
    # Jira Tools
    create_jira_ticket_tool,
    update_jira_ticket_tool,
    get_jira_ticket_tool,
    # GitHub Tools
    create_github_file_tool,
    update_github_file_tool,
    read_github_file_tool,
    create_github_pull_request_tool
]
