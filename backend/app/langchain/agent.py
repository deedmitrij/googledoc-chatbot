from langchain.agents.factory import create_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from backend.app.langchain.tools import all_tools
from backend.services.llm_service import LLMService
from backend.app.memory_manager import ChatbotMemoryManager


llm_service = LLMService()
memory_manager = ChatbotMemoryManager()


def run_agent_with_tools(user_input: str, user_id: str) -> str:
    system_prompt = (
        "You are a helpful assistant guiding users through a multi-step task "
        "(e.g., uploading and analyzing specification and test case documents). "
        "Before choosing any tool, you must **ALWAYS** call the `Check the current context` tool "
        "to understand the current step of the conversation and what the bot is expecting. "
        "Do not make assumptions or respond without consulting this context. "
        "If the context is ambiguous or if the user replies with a vague answer "
        "(e.g., 'yes', '1', 'ok', or a document link), use the context to determine what was expected. "
        "If the context shows a prompt like a list of options, "
        "and the user responds with a number or partial phrase, match that to the expected option. "
        "If the user says something unrelated to the current context or skips steps, "
        "guide them gently back to the expected step. "
        "Always interpret the user’s reply based on the context returned by `check_current_context`. "
        "If you need more information or context, ask for clarification."
    )

    graph = create_agent(
        model=llm_service.langchain_model,
        tools=all_tools,
        system_prompt=system_prompt,
    )

    agent_with_chat_history = RunnableWithMessageHistory(
        graph,
        lambda session_id: memory_manager.get_memory(session_id),
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    # Add user_id to the input string
    user_input_with_id = f"(User ID: {user_id}) {user_input}"
    response = agent_with_chat_history.invoke(
        {"input": user_input_with_id},
        config={"configurable": {"session_id": user_id}},
    )

    return response['output']
