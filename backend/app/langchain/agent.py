from langchain.agents import AgentExecutor, StructuredChatAgent
from langchain.prompts import MessagesPlaceholder
from langchain.prompts.chat import ChatPromptTemplate
from backend.app.langchain.tools import all_tools
from backend.services.gemini_service import GeminiService
from backend.app.memory_manager import ChatbotMemoryManager


gemini_service = GeminiService()
memory_manager = ChatbotMemoryManager()


def run_agent_with_tools(user_input: str, user_id: str) -> str:
    memory = memory_manager.get_memory(user_id)

    prompt = ChatPromptTemplate.from_messages([
        ('system',
         "You are a helpful assistant guiding users through a multi-step task "
         "(e.g., uploading and analyzing specification and test case documents). "
         "Before answering any message from the user, you must **always call the `check_current_context` tool** "
         "to understand the current step of the conversation and what the bot is expecting. "
         "Do not make assumptions or respond without consulting this context. "
         "If the context is ambiguous or if the user replies with a vague answer "
         "(e.g., 'yes', '1', 'ok', or a document link), use the context to determine what was expected. "
         "If the context shows a prompt like a list of options, "
         "and the user responds with a number or partial phrase, match that to the expected option. "
         "If the user says something unrelated to the current context or skips steps, "
         "guide them gently back to the expected step. "
         "Always interpret the user’s reply based on the context returned by `check_current_context`. "
         "If you need more information or context, ask for clarification."),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{input}')
    ])

    agent = StructuredChatAgent.from_llm_and_tools(
        llm=gemini_service.langchain_model,
        tools=all_tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        llm=gemini_service.langchain_model,
        tools=all_tools,
        memory=memory,
        memory_key='chat_history',
        verbose=True,
        handle_parsing_errors=True
    )

    # Add user_id to the input string
    user_input_with_id = f"(User ID: {user_id}) {user_input}"
    response = agent_executor.run(user_input_with_id)

    return response
