from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import logging

# إعداد Flask
app = Flask(__name__)

# إعداد API Key من Google Generative AI
API_KEY = "AIzaSyAgF_uh6-380Q1qbgsZzRVjONuzQrjFJKI"

# إعداد النموذج
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name="gemini-pro")
    chat_session = model.start_chat(history=[])
    app.logger.info("✅ AI model configured and chat session started.")
except Exception as e:
    app.logger.error(f"❌ Failed to initialize AI model: {str(e)}")
    raise SystemExit(f"Failed to initialize AI model: {str(e)}")

# سجل المحادثة
conversation_log = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    try:
        user_message = request.json.get("message", "").strip()

        if not user_message:
            return jsonify({"status": "error", "message": "Empty message received."}), 400

        # إنهاء المحادثة
        if user_message.lower() == "bye":
            bot_response = "Goodbye! 👋"
            conversation_log.append({"user": user_message, "bot": bot_response})
            return jsonify({"status": "success", "bot_response": bot_response})

        # إرسال الرسالة إلى الذكاء الاصطناعي
        response = chat_session.send_message(user_message)

        # التأكد من أن الرد موجود
        if not hasattr(response, "text"):
            raise ValueError("The AI model did not return any response.")

        bot_response = response.text.strip()
        conversation_log.append({"user": user_message, "bot": bot_response})

        return jsonify({"status": "success", "bot_response": bot_response})

    except Exception as e:
        app.logger.error(f"❌ Error processing message: {str(e)}")
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

@app.route("/conversation_log", methods=["GET"])
def get_conversation_log():
    return jsonify(conversation_log)

if __name__ == "__main__":
    # شغّل التطبيق
    app.run(debug=True, host="0.0.0.0", port=5000)
