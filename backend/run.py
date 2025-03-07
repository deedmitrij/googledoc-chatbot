from flask import Flask
from backend.app.routes import chat_bp
import os

# Create Flask app
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "../frontend/templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "../frontend/static"))

# Register Blueprint
app.register_blueprint(chat_bp)

if __name__ == "__main__":
    app.run(debug=True)
