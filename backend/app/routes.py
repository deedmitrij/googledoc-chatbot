import re
from flask import Blueprint, request, jsonify, render_template
from backend.app.gemini_service import GeminiService
from backend.app.google_drive_loader import GoogleDocLoader
from backend.app.session_manager import session_manager

gemini_service = GeminiService()
google_doc_loader = GoogleDocLoader()

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot interactions."""
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    session = session_manager.get_session(user_id)

    # Step 1: User sends Google Doc link
    if not session:
        google_docs_regex = r"https:\/\/docs\.google\.com\/document\/d\/[a-zA-Z0-9_-]+"
        if not re.match(google_docs_regex, user_message):
            return jsonify({"response": "⚠️ Invalid Google Docs link! Please provide a valid link."})

        session_manager.set_doc_link(user_id, user_message)
        return jsonify({"response": "Got it! Now, which feature's test cases do you need?"})

    # Step 2: User sends feature name
    elif session["feature"] is None:
        session_manager.set_feature(user_id, user_message)
        doc_link = session["doc_link"]

        # Load document & extract test cases
        doc_text = google_doc_loader.load_document(doc_link)
        if 'Error' in doc_text:
            session_manager.clear_session(user_id)
            return jsonify({'response': f"{doc_text}<br><br>🔄 Send a new Google Doc link."})

        # Ask Gemini to extract test cases
        feature = user_message
        test_cases = gemini_service.get_test_cases(doc_text, feature)
        if 'Error' in test_cases:
            session_manager.set_feature(user_id, None)
            return jsonify({
                "response": f"{test_cases}<br><br>🔄 Please enter a valid feature name."
            })
        return jsonify({
            "response": f"Here are the test cases for <b>{feature}</b>:<br>{test_cases}",
            "menu": ["🔄 Extract another feature", "📄 Upload new document", "❌ End session"]
        })

    # Step 3: Handle menu selection
    elif "extract another feature" in user_message.lower():
        session_manager.set_feature(user_id, None)
        return jsonify({"response": "Which feature's test cases do you need next?"})

    elif "upload new document" in user_message.lower():
        session_manager.clear_session(user_id)
        return jsonify({"response": "Send me the new Google Doc link!"})

    elif "end session" in user_message.lower():
        session_manager.clear_session(user_id)
        return jsonify({
            "response": "Session ended. Have a great day!",
            "reset": True
        })

    else:
        return jsonify({"response": "I didn’t understand that. Please choose an option from the menu."})
