import json
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from backend.app.document_manager import DocumentManager
from backend.app.langchain.chains import LLMChains
from backend.app.memory_manager import ChatbotMemoryManager


memory_manager = ChatbotMemoryManager()
document_manager = DocumentManager()
llm_chains = LLMChains()


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


# === Export All Tools as a List ===
all_tools = [
    load_specification_doc_tool,
    load_test_cases_doc_tool,
    specify_feature_name_tool,
    generate_test_cases_tool,
    check_chat_history_tool,
    check_current_context_tool,
    upload_new_documents_tool,
    clear_session_tool
]
