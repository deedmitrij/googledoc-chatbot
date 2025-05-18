import json
from flask import Blueprint, request, jsonify, render_template
from backend.app.document_manager import DocumentManager
from backend.app.langchain.agent import run_agent_with_tools
from backend.app.memory_manager import ChatbotMemoryManager


memory_manager = ChatbotMemoryManager()
document_manager = DocumentManager()

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot interactions."""
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("message")

    response = run_agent_with_tools(user_input=user_message, user_id=user_id)
    try:
        response_as_dict = json.loads(response)
        return response_as_dict
    except json.JSONDecodeError:
        return jsonify({"response": response})
