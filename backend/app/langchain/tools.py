import json
from langchain_core.tools import tool
from backend.app.document_manager import DocumentManager
from backend.app.langchain.chains import LLMChains
from backend.app.memory_manager import ChatbotMemoryManager


memory_manager = ChatbotMemoryManager()
document_manager = DocumentManager()
llm_chains = LLMChains()


@tool
def load_specification_doc(user_id: str, doc_link: str) -> str:
    """Use this tool to load the Specification content from Google Doc. Input should be a Google Doc link."""
    document_manager.load_and_store_document(doc_link=doc_link,
                                             collection='specification',
                                             user_id=user_id)

    memory_manager.set_spec_doc_link(user_id, doc_link)
    memory_manager.set_current_step(user_id, "Awaiting for a link to Test Cases document.")

    return (f"✅ Specification document has been loaded successfully.\n"
            f"Now, send a link to the Test Cases document.")


@tool
def load_test_cases_doc(user_id: str, doc_link: str) -> str:
    """Use this tool to load the Test Cases content from Google Doc. Input should be a Google Doc link."""
    document_manager.load_and_store_document(doc_link=doc_link,
                                             collection='test_cases',
                                             user_id=user_id)

    memory_manager.set_test_cases_doc_link(user_id, doc_link)

    memory_manager.set_current_step(user_id, "Provide feature name")
    memory_manager.set_documents_loaded(user_id, True)
    memory_manager.set_current_step(user_id, "Awaiting for specifying a feature name.")

    return (f"✅ Test Cases document has been loaded successfully.\n"
            f"Now, specify the name of the feature for which you want to generate test cases.")


@tool
def specify_feature_name(user_id: str, feature_name: str) -> str:
    """Use this tool to specify feature name or set another feature name for which to generate test cases."""
    memory_manager.set_feature(user_id, feature_name)
    memory_manager.set_current_step(user_id, "Awaiting for generating test cases.")

    return 'Awaiting for generating test cases.'


@tool
def generate_test_cases(user_id: str) -> str:
    """Use this tool to generate test cases."""
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


@tool
def fetch_chat_history(user_id: str) -> str:
    """
    Use this tool only if you are unsure, or cannot find the information you need in the provided chat history.
    This tool returns the full, detailed chat history between you and the user.
    Use it to verify details about previous links, answers, or messages before responding,
    especially if you are not certain from the memory context.
    """
    memory = memory_manager.get_memory(user_id)
    memory_vars = memory.load_memory_variables({})
    chat_history = memory_vars.get('chat_history', [])
    history_text = ""
    for message in chat_history:
        role = "User" if message.type == "human" else "Assistant"
        history_text += f"{role}: {message.content}\n"
    return history_text


@tool
def check_current_context(user_id: str) -> str:
    """
    **ALWAYS** use this tool before choosing other tools.
    It returns the current dialogue context for a specific user based on what the bot expects next.
    The result might be a short instruction or a multi-line message with specific prompts.
    Use this tool to:
    - Understand what step the user is currently on
    - Interpret ambiguous replies (e.g., '1', 'yes', 'this one')
    - Determine what kind of response or document link the user is expected to provide
    This tool must be called for **EVERY** user message before generating any reply or deciding on next actions.
    """
    context = memory_manager.get_current_step(user_id)
    return context


@tool
def upload_new_documents(user_id: str) -> str:
    """Use this tool to clear previously uploaded documents and wait for uploading new documents."""
    memory_manager.clear_context(user_id)
    memory_manager.set_current_step(user_id, "Awaiting for a link to Specification document")

    return "User wants to upload new documents. Awaiting for a link to Specification document"


@tool
def clear_session(user_id: str) -> str:
    """Use this tool to clear the user session."""
    memory_manager.clear_session(user_id)
    memory_manager.set_current_step(user_id, "Awaiting for a link to Specification document")

    return (json.dumps({
        "response": "The user's session has been cleared.",
        "reset": True
    }))


all_tools = [
    load_specification_doc,
    load_test_cases_doc,
    specify_feature_name,
    generate_test_cases,
    fetch_chat_history,
    check_current_context,
    upload_new_documents,
    clear_session
]
