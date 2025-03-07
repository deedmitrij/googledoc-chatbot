import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from backend.config import GOOGLE_CREDENTIALS_PATH


class GoogleDocLoader:
    """
    A loader for fetching content from Google Docs using the Google Docs API.

    This class handles authentication with the Google API using a service account
    and provides access to Google Docs content in read-only mode.
    """

    def __init__(self) -> None:
        self.service = self._authenticate()

    @staticmethod
    def _authenticate() -> build:
        """
        Authenticates with the Google Docs API using service account credentials.

        Returns:
            build: A Google Docs API service resource for making requests.
        """
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/documents.readonly"]
        )
        return build("docs", "v1", credentials=creds)

    @staticmethod
    def extract_doc_id(doc_url: str) -> str:
        """
        Extracts the document ID from a Google Docs URL.

        Args:
            doc_url (str): The full URL of the Google Document.

        Returns:
            str: The extracted document ID.
        """
        match = re.search(r"document/d/([a-zA-Z0-9-_]+)", doc_url)
        return match.group(1)

    def load_document(self, doc_url: str) -> str:
        """
        Extracts text content from a Google Doc given its document URL.

        Args:
            doc_url (str): The URL of the Google Document.

        Returns:
            str: The extracted text content from the document.
        """
        doc_id = self.extract_doc_id(doc_url)
        try:
            doc = self.service.documents().get(documentId=doc_id).execute()
        except HttpError as e:
            return f"⚠️ Google Docs API Error: {e.error_details}"
        except Exception as e:
            return f"⚠️ Unexpected Error: {str(e)}"
        text = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for run in element["paragraph"].get("elements", []):
                    if "textRun" in run:
                        text.append(run["textRun"]["content"])
        return "".join(text).strip()
