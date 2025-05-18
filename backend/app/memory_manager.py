from typing import Optional, Dict, Any
from langchain.memory import ConversationBufferMemory
from backend.services.gemini_service import GeminiService


gemini_service = GeminiService()


class ChatbotMemoryManager:
    """
    Manages both user-specific chat history (via LangChain) and context variables
    (like links, flags, etc.) using a separate in-memory store.
    Also tracks the current step in the user conversation flow.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatbotMemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.user_memories: Dict[str, ConversationBufferMemory] = {}
        self.user_contexts: Dict[str, Dict[str, Any]] = {}

    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
        return self.user_memories[user_id]

    def store_message(self, user_id: str, user_message: str, ai_message: str) -> None:
        memory = self.get_memory(user_id)
        memory.save_context({"input": user_message}, {"output": ai_message})

    # --- Context Storage: key-value per user ---
    def set_context(self, user_id: str, key: str, value: Any) -> None:
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        self.user_contexts[user_id][key] = value

    def get_context(self, user_id: str, key: str) -> Any:
        return self.user_contexts.get(user_id, {}).get(key, "")

    def clear_memory(self, user_id: str) -> None:
        self.user_memories.pop(user_id, None)

    def clear_context(self, user_id: str) -> None:
        self.user_contexts.pop(user_id, None)

    def clear_session(self, user_id: str) -> None:
        self.clear_memory(user_id)
        self.user_contexts.pop(user_id, None)

    # --- Conversation Flow Tracking ---
    def set_current_step(self, user_id: str, step: str) -> None:
        """Tracks where the user is in the conversation flow."""
        self.set_context(user_id, "current_step", step)

    def get_current_step(self, user_id: str) -> str:
        return self.get_context(user_id, "current_step") or "Awaiting for a link to Specification document"

    # --- Context-specific shortcuts ---
    def set_spec_doc_link(self, user_id: str, link: Optional[str]) -> None:
        self.set_context(user_id, "spec_doc_link", link or "")

    def get_spec_doc_link(self, user_id: str) -> str:
        return self.get_context(user_id, "spec_doc_link") or ""

    def set_test_cases_doc_link(self, user_id: str, link: Optional[str]) -> None:
        self.set_context(user_id, "test_cases_doc_link", link or "")

    def get_test_cases_doc_link(self, user_id: str) -> str:
        return self.get_context(user_id, "test_cases_doc_link") or ""

    def set_feature(self, user_id: str, feature: Optional[str]) -> None:
        self.set_context(user_id, "feature", feature or "")

    def get_feature(self, user_id: str) -> str:
        return self.get_context(user_id, "feature") or ""

    def set_documents_loaded(self, user_id: str, loaded: bool) -> None:
        self.set_context(user_id, "documents_loaded", loaded)

    def is_documents_loaded(self, user_id: str) -> bool:
        return bool(self.get_context(user_id, "documents_loaded"))

    def get_session(self, user_id: str) -> Dict[str, Any]:
        return self.user_contexts.get(user_id, {})
