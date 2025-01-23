from flask import Flask, render_template, request, jsonify
import google.generativeai as ai
import json
import os
from gunicorn import util
import fcntl

# Flask app setup
app = Flask(__name__)

# API Key for Google Generative AI
API_KEY = 'AIzaSyBTHPyblMw0qtXYTDpgMmMOhvZuh2MtsRo'

# Configure the AI API
try:
    ai.configure(api_key=API_KEY)
    model = ai.GenerativeModel("gemini-pro")
    chat = model.start_chat()
    app.logger.info("AI model configured successfully.")
except Exception as e:
    raise SystemExit(f"Failed to initialize AI model: {str(e)}")

# Initialize conversation log
conversation_log = []

@app.route("/")
def home():
    """
    Render the chatbot homepage.
    """
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    """
    Handle user messages and get AI responses.
    """
    try:
        user_message = request.json.get("message", "").strip()

        # Validate user input
        if not user_message:
            return jsonify({"status": "error", "message": "Empty message received."}), 400

        # Check for 'bye' message
        if user_message.lower() == 'bye':
            bot_response = "Goodbye!"
            conversation_log.append({"user": user_message, "bot": bot_response})
            return jsonify({"status": "success", "bot_response": bot_response})

        # Get AI response
        response = chat.send_message(user_message)

        # Log the conversation
        bot_response = response.text
        conversation_log.append({"user": user_message, "bot": bot_response})

        return jsonify({"status": "success", "bot_response": bot_response})

    except Exception as e:
        app.logger.error(f"Error processing message: {str(e)}")
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

@app.route("/conversation_log", methods=["GET"])
def get_conversation_log():
    """
    Get the entire conversation log as JSON.
    """
    return jsonify(conversation_log)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
