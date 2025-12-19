from jira import JIRA, JIRAError
from backend.config import JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT

class JiraService:
    def __init__(self):
        try:
            self.jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
            self.project = JIRA_PROJECT
        except JIRAError as e:
            self.jira = None
            print(f"Error connecting to Jira: {e}")

    def create_ticket(self, title, description, issue_type="Story"):
        if not self.jira:
            return "Error: Jira connection not established."
        try:
            issue_dict = {
                'project': {'key': self.project},
                'summary': title,
                'description': description,
                'issuetype': {'name': issue_type},
            }
            new_issue = self.jira.create_issue(fields=issue_dict)
            return new_issue.key
        except JIRAError as e:
            return f"Error creating Jira ticket: {e.text}"

    def update_ticket(self, ticket_key, comment):
        if not self.jira:
            return "Error: Jira connection not established."
        try:
            issue = self.jira.issue(ticket_key)
            self.jira.add_comment(issue, comment)
            return f"Comment added to {ticket_key}"
        except JIRAError as e:
            return f"Error updating Jira ticket: {e.text}"

    def get_ticket(self, ticket_key):
        if not self.jira:
            return "Error: Jira connection not established."
        try:
            issue = self.jira.issue(ticket_key)
            return {
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "status": issue.fields.status.name,
                "comments": [comment.body for comment in issue.fields.comment.comments]
            }
        except JIRAError as e:
            return f"Error getting Jira ticket: {e.text}"
