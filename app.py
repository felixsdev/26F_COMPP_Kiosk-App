# Flask app for handling DI Kiosk chat requests to LiteLLM.
# Loads system context from local JSON files and communicates with ai.

#===================
# IMPORT & SETUP

import flask
import dotenv
import litellm
import json

dotenv.load_dotenv()
app = flask.Flask(__name__)

#===================
# HOMEPAGE ROUTE

@app.route("/")
def index():
    return flask.render_template("index.html")

#===================
# CHAT ROUTE

@app.route("/chat", methods=["POST"])
def chat():

     # Get user msg
    user_message = flask.request.json.get("message")

    try:

        # Combine system context
        with open("data/session.json", "r") as f:
            session = json.load(f)
        with open("data/context.json", "r") as f:
            context = json.load(f)
        with open("data/history.json", "r") as f:
            conversation_history = json.load(f)
        system_data = {
            "instructions": "You are a helpful assistant.",
            "session": session,
            "context": context,
            "history": conversation_history
        }

        # Create payload
        messages_payload = [
            {
                "role": "system",
                "content": json.dumps(system_data, separators=(',', ':'))
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Print for debugging
        print("\n" + "="*40)
        print("USER MESSAGE:")
        print("-"*40)
        print(json.dumps(user_message))
        print("="*40)
        print("SYSTEM CONTEXT")
        print("-"*40)
        print(json.dumps(system_data, indent=4))
        print("="*40 + "\n")

        # Call llm & get reply
        response = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=messages_payload
        )
        reply = response.choices[0].message.content
        return flask.jsonify({"reply": reply})
    
    # Error handling
    except litellm.exceptions.ServiceUnavailableError:
        return flask.jsonify({"reply": "High demand. Unavailable. Try again in a moment."})
    except Exception as e:
        print(f"Server Error: {e}")
        return flask.jsonify({"reply": "Unexpected error. Try again."})

# STARING WEBSERVER
#===================
if __name__ == "__main__":
    app.run(debug=True)