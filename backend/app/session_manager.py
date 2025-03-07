from typing import Optional, Dict


class SessionManager:
    """
    Manages user session data, including the document link and selected feature.

    Attributes:
        sessions (dict): Stores session data for users, mapping user IDs to their session info.
    """

    def __init__(self):
        self.sessions = {}

    def set_doc_link(self, user_id: str, link: str) -> None:
        """
        Sets the document link for a given user.

        Args:
            user_id (str): The unique identifier for the user.
            link (str): The link to the Google document.
        """
        self.sessions[user_id] = {"doc_link": link, "feature": None}

    def set_feature(self, user_id: str, feature: str) -> None:
        """
        Sets the selected feature for a given user.

        Args:
            user_id (str): The unique identifier for the user.
            feature (str): The feature name related to the test case extraction.
        """
        if user_id in self.sessions:
            self.sessions[user_id]["feature"] = feature

    def get_session(self, user_id: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Retrieves the session data for a given user.

        Args:
            user_id (str): The unique identifier for the user.

        Returns:
            Optional[Dict[str, Optional[str]]]: A dictionary containing the user's session data
            or None if no session exists.
        """
        return self.sessions.get(user_id, None)

    def clear_session(self, user_id: str) -> None:
        """
        Clears the session data for a given user.

        Args:
            user_id (str): The unique identifier for the user.
        """
        if user_id in self.sessions:
            del self.sessions[user_id]


# Initialize global session manager
session_manager = SessionManager()
