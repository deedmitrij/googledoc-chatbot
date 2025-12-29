from github import Github, GithubException
from backend.config import GITHUB_TOKEN, GITHUB_REPO

class GithubService:
    def __init__(self):
        try:
            self.github = Github(GITHUB_TOKEN)
            self.repo = self.github.get_repo(GITHUB_REPO)
        except GithubException as e:
            self.github = None
            print(f"Error connecting to Github: {e}")

    def create_file(self, file_path, content, commit_message):
        if not self.github:
            return "Error: Github connection not established."
        try:
            self.repo.create_file(file_path, commit_message, content)
            return f"File {file_path} created successfully."
        except GithubException as e:
            return f"Error creating Github file: {e}"

    def update_file(self, file_path, content, commit_message):
        if not self.github:
            return "Error: Github connection not established."
        try:
            contents = self.repo.get_contents(file_path)
            self.repo.update_file(contents.path, commit_message, content, contents.sha)
            return f"File {file_path} updated successfully."
        except GithubException as e:
            return f"Error updating Github file: {e}"

    def read_file(self, file_path):
        if not self.github:
            return "Error: Github connection not established."
        try:
            contents = self.repo.get_contents(file_path)
            return contents.decoded_content.decode()
        except GithubException as e:
            return f"Error reading Github file: {e}"

    def create_pull_request(self, title, body, head_branch, base_branch):
        if not self.github:
            return "Error: Github connection not established."
        try:
            pr = self.repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
            return pr.html_url
        except GithubException as e:
            return f"Error creating pull request: {e}"
