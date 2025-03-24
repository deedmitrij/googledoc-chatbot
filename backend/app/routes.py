import re
from flask import Blueprint, request, jsonify, render_template
from .document_manager import DocumentManager
from backend.app.session_manager import SessionManager


document_manager = DocumentManager()
session_manager = SessionManager()

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

    session = session_manager.get_session(user_id)

    if not session.get("documents_loaded"):
        google_docs_regex = r"https:\/\/docs\.google\.com\/document\/d\/[a-zA-Z0-9_-]+"
        # Step 1: Expect first Google Doc link (Specification)
        if not session.get("spec_doc_link"):
            if not bool(re.match(google_docs_regex, user_message)):
                return jsonify(
                    {"response": "⚠️ Invalid Google Docs link! Please provide a valid specification document link."}
                )
            session_manager.set_spec_doc_link(user_id, user_message)
            try:
                document_manager.load_and_store_document(doc_link=session["spec_doc_link"],
                                                         collection='specification',
                                                         user_id=user_id)
            except Exception as e:
                session_manager.set_spec_doc_link(user_id, None)
                return jsonify({'response': f"{e}<br><br>🔄 Send a new Google Doc link."})
            return jsonify({"response": "Got it! Now, send me a Google Doc link to the test cases."})

        # Step 2: Expect second Google Doc link (Test Cases)
        elif not session.get("test_cases_doc_link"):
            if not bool(re.match(google_docs_regex, user_message)):
                return jsonify(
                    {"response": "⚠️ Invalid Google Docs link! Please provide a valid specification document link."}
                )
            session_manager.set_test_cases_doc_link(user_id, user_message)
            try:
                document_manager.load_and_store_document(doc_link=session["test_cases_doc_link"],
                                                         collection='test_cases',
                                                         user_id=user_id)
            except Exception as e:
                session_manager.set_test_cases_doc_link(user_id, None)
                return jsonify({'response': f"{e}<br><br>🔄 Send a new Google Doc link."})
            session_manager.set_documents_loaded(user_id, True)
            return jsonify({"response": "Thanks! Now, which feature's test cases do you need?"})

    # Step 3: Expect feature name
    elif not session.get("feature"):
        session_manager.set_feature(user_id, user_message)

        # Retrieve relevant data
        relevant_specs = document_manager.find_similar_data_to_query(query=user_message,
                                                                     collection='specification',
                                                                     user_id=user_id)
        relevant_test_cases = document_manager.find_similar_data_to_query(query=user_message,
                                                                          collection='test_cases',
                                                                          user_id=user_id)

        # Generate test cases
        test_cases = document_manager.generate_test_cases(relevant_specs=relevant_specs,
                                                          relevant_test_cases=relevant_test_cases,
                                                          feature=user_message)

        return jsonify({
            "response": test_cases,
            "menu": ["🔄 Extract another feature", "📄 Upload new documents", "❌ End session"]
        })

    # Step 4: Handle menu selection
    elif "extract another feature" in user_message.lower():
        session_manager.set_feature(user_id, None)
        return jsonify({"response": "Which feature's test cases do you need next?"})

    elif "upload new documents" in user_message.lower():
        session_manager.clear_session(user_id)
        return jsonify({"response": "Send me the new specification document link!"})

    elif "end session" in user_message.lower():
        session_manager.clear_session(user_id)
        return jsonify({
            "response": "Session ended. Have a great day!",
            "reset": True
        })

    else:
        return jsonify({"response": "I didn’t understand that. Please choose an option from the menu."})
