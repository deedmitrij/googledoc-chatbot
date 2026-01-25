import json
from flask import Blueprint, request, jsonify, render_template
from backend.app.langchain.agent import run_agent_with_tools


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

    try:
        # Call the Agent
        response = run_agent_with_tools(user_input=user_message, user_id=user_id)

        # Handle JSON response from LLM
        if isinstance(response, str):
            try:
                # Attempt to parse if it's a JSON string
                parsed_response = json.loads(response)
                return jsonify(parsed_response)
            except json.JSONDecodeError:
                # Fallback if the LLM returned raw text
                return jsonify({"response": response})

        # If the response is already a dict
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Agent Error: {str(e)}"}), 500
