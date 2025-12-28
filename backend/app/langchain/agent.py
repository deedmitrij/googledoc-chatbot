import asyncio
from langchain_classic.agents import AgentExecutor, StructuredChatAgent
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient, load_mcp_tools
from backend.services.gemini_service import GeminiService
from backend.app.memory_manager import ChatbotMemoryManager


gemini_service = GeminiService()
memory_manager = ChatbotMemoryManager()

# Configure the MCP client
mcp_client = MultiServerMCPClient({
    "jira": {
        "transport": "stdio",
        "command": "python",
        "args": ["-m", "backend.mcp_servers.jira_mcp_server"],
    },
    "github": {
        "transport": "stdio",
        "command": "python",
        "args": ["-m", "backend.mcp_servers.github_mcp_server"],
    },
})

async def load_tools():
    async with mcp_client.session("jira") as jira_session:
        async with mcp_client.session("github") as github_session:
            jira_tools = await load_mcp_tools(jira_session)
            github_tools = await load_mcp_tools(github_session)
            return jira_tools + github_tools

def run_agent_with_tools(user_input: str, user_id: str) -> str:
    memory = memory_manager.get_memory(user_id)
    all_tools = asyncio.run(load_tools())

    prompt = ChatPromptTemplate.from_messages([
        ('system',
         "You are a helpful assistant with powerful capabilities to interact with Jira and GitHub. "
         "You can create, update, and retrieve Jira tickets. "
         "You can also create, update, and read files in a GitHub repository, and create pull requests. "
         "When a user asks to create a Jira ticket or a test script, you should first gather the necessary information from the provided documents or by asking clarifying questions. "
         "For example, to create a Jira ticket, you need a title, description, and issue type. "
         "To create a test script, you need to understand the feature from the specification and the existing test cases. "
         "You can use the 'Get Jira Ticket' tool to get the details of an existing ticket. "
         "You can use the 'Read GitHub File' tool to read the contents of a file in the repository. "
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
