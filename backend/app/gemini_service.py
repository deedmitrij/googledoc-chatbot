import google.generativeai as genai
from backend.config import GEMINI_API_KEY


class GeminiService:
    """Handles AI interactions with Google Gemini."""

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def get_test_cases(self, doc_text: str, feature: str) -> str:
        """
        Extracts relevant test cases from a document based on the given feature.

        Args:
            doc_text (str): The full text content of the Google Document.
            feature (str): The specific feature to filter relevant test cases.

        Returns:
            str: extracted test cases related to the given feature.
        """
        prompt = f"""
        The following document contains test cases for multiple features.\n

        Extract and return only the test cases related to the "{feature}". 
        Don't change the text or the format. Return the test cases in their original form as written in the document. 
        Return as normal text, but just put the appropriate html tags in the places of line breaks or paragraph breaks. 
        But if the document does NOT contain relevant test cases for this feature, return exactly this response: 
        "⚠️ Error: No test cases found for the '{feature}'."\n

        Document:\n
        "{doc_text}"
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error processing request: {str(e)}"
