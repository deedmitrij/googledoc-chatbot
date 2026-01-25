from langchain_classic.agents import AgentExecutor, StructuredChatAgent
from langchain_classic.prompts import MessagesPlaceholder
from langchain_classic.prompts.chat import ChatPromptTemplate
from backend.app.langchain.tools import all_tools
from backend.services.llm_service import LLMService
from backend.app.memory_manager import ChatbotMemoryManager


llm_service = LLMService()
memory_manager = ChatbotMemoryManager()


def run_agent_with_tools(user_input: str, user_id: str) -> str:
    memory_manager.current_user_id = user_id
    memory = memory_manager.get_memory(user_id)
    current_step = memory_manager.get_current_step(user_id)

    prompt = ChatPromptTemplate.from_messages([
        ('system',
         f"You are a helpful assistant guiding users through a multi-step task "
         f"(e.g., uploading and analyzing specification and test case documents). "
         f"Current conversation step: {current_step}. Choose the correct tool based ONLY on the current step. "
         f"Do NOT call tools that do not match this step. "
         f"If the context is ambiguous or if the user replies with a vague answer "
         f"(e.g., 'yes', '1', 'ok', or a document link), use the context to determine what was expected. "
         f"If the context shows a prompt like a list of options, "
         f"and the user responds with a number or partial phrase, match that to the expected option. "
         f"If the user says something unrelated to the current context or skips steps, "
         f"guide them gently back to the expected step. "
         f"If you need more information or context, ask for clarification."),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{input}')
    ])

    agent = StructuredChatAgent.from_llm_and_tools(
        llm=llm_service.langchain_model,
        tools=all_tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        llm=llm_service.langchain_model,
        tools=all_tools,
        memory=memory,
        memory_key='chat_history',
        verbose=True,
        handle_parsing_errors=True
    )

    response = agent_executor.invoke({"input": user_input})
    return response['output']
