# IMPORTS
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import litellm
import json

# SETUP
load_dotenv()
app = Flask(__name__)

# UTILITY FUNCTION TO LOAD CONTEXT .JSON
def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

# HOMEPAGE ROUTE
@app.route("/")
# HOMEPAGE FUNCTION
def index():
    return render_template("index.html")

# CHAT ROUTE
@app.route("/chat", methods=["POST"])
# CHAT FUNCTION
def chat():
    # GET CONTEXT
    user_message = request.json.get("message")
    session = load_json("data/session.json")
    context = load_json("data/context.json")
    conversation_history = load_json("data/history.json")
    # PROMPT
    try:
        # 1. BUILD THE PROMPT
        messages_payload = [
            {
                "role": "system",
                "content": f"""
                You are a helpful assistant.

                Current session context:
                {json.dumps(session)}

                Current context:
                {json.dumps(context)}

                Conversation history:
                {json.dumps(conversation_history)}
                """
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # 2. PRINT IT TO THE TERMINAL (Your Python "Console Log")
        print("\n" + "="*40)
        print(json.dumps(messages_payload, indent=2))
        print("="*40 + "\n")

        # 3. SEND IT TO LITELLM
        response = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=messages_payload
        )
        
        # GET REPLY
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    
    # BUSY ERROR HANDLING
    except litellm.exceptions.ServiceUnavailableError:
        busy_message = "High demand. Unavailable. Try again in a moment."
        return jsonify({"reply": busy_message})
        
    # CATCH ALL ERRORS
    except Exception as e:
        error_message = "Unexpected error. Try again."
        print(f"Server Error: {e}")
        return jsonify({"reply": error_message})

# STARTING FLASK WEBSERVER
if __name__ == "__main__":
    app.run(debug=True)