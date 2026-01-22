from flask import Flask
from backend.app.routes import chat_bp

# Create Flask app
app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# Register Blueprint
app.register_blueprint(chat_bp)

if __name__ == "__main__":
    app.run(debug=False)
