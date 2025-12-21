from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from backend.services.gemini_service import GeminiService
from backend.config import PROJECT_ROOT


class LLMChains:

    def __init__(self):
        gemini_service = GeminiService()
        self.llm = gemini_service.langchain_model

    @staticmethod
    def _get_prompt(prompt_file):
        prompt_path = PROJECT_ROOT / f'backend/prompts/{prompt_file}'
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        return prompt

    def build_test_case_chain(self) -> RunnableSequence:
        prompt = PromptTemplate(
            input_variables=['specification', 'test_cases', 'feature'],
            template=self._get_prompt(prompt_file='generate_test_cases.txt'),
        )
        return prompt | self.llm

    def summarization_chain(self):
        prompt = PromptTemplate(
            input_variables=['content'],
            template=self._get_prompt(prompt_file='summarize_content.txt'),
        )
        return prompt | self.llm
