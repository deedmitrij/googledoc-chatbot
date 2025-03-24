from typing import Optional, Dict


class SessionManager:
    """
    Manages user session data, including document links, selected feature, and document load status.

    Attributes:
        sessions (dict): Stores session data for users, mapping user IDs to their session info.
    """

    def __init__(self):
        self.sessions = {}

    def set_spec_doc_link(self, user_id: str, spec_link: str | None) -> None:
        """
        Sets the specification document link for a given user.

        Args:
            user_id (str): The unique identifier for the user.
            spec_link (str | None): The link to the specification document.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        self.sessions[user_id]["spec_doc_link"] = spec_link

    def set_test_cases_doc_link(self, user_id: str, test_cases_link: str | None) -> None:
        """
        Sets the test cases document link for a given user.

        Args:
            user_id (str): The unique identifier for the user.
            test_cases_link (str | None): The link to the test cases document.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        self.sessions[user_id]["test_cases_doc_link"] = test_cases_link

    def set_feature(self, user_id: str, feature: str) -> None:
        """
        Sets the selected feature for a given user.

        Args:
            user_id (str): The unique identifier for the user.
            feature (str): The name of the selected feature.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        self.sessions[user_id]["feature"] = feature

    def set_documents_loaded(self, user_id: str, loaded: bool) -> None:
        """
        Marks whether documents have been loaded for a given user.

        Args:
            user_id (str): The unique identifier for the user.
            loaded (bool): A flag indicating whether documents have been loaded.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        self.sessions[user_id]["documents_loaded"] = loaded

    def get_session(self, user_id: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Retrieves the session data for a given user.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            dict: The session data for the user, or an empty dictionary if no session exists.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        return self.sessions[user_id]

    def clear_session(self, user_id: str) -> None:
        """
        Clears the session data for a given user.

        Args:
            user_id (str): The unique identifier for the user.
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
