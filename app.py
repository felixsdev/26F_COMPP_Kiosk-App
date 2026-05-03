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
# RESET SESSION ROUTE

@app.route("/reset", methods=["POST"])
def reset():
    try:
        with open("data/session.json", "w") as f:
            json.dump([], f)
        return flask.jsonify({"status": "success", "message": "Session reset."})
    except Exception as e:
        print(f"Error resetting session: {e}")
        return flask.jsonify({"status": "error", "message": "Failed to reset session."}), 500

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
            "session chat": session,
            "context": context,
            "old sessions": conversation_history
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

        # Append both messages to the session list we loaded earlier
        session.append({"speaker": "user", "text": user_message})
        session.append({"speaker": "assistant", "text": reply})

        # Save the updated session back to the JSON file
        with open("data/session.json", "w") as f:
            json.dump(session, f, indent=4)

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