# Flask app for handling DI Kiosk chat requests to LiteLLM.
# Loads system context from local JSON files and communicates with ai.

#===================
# IMPORT & SETUP

import flask
import dotenv
import litellm
import json
import threading
import time
from datetime import datetime

dotenv.load_dotenv()
app = flask.Flask(__name__)

#===================
# CONTEXT.JSON UPDATER

def update_context_loop():
    while True:
        try:
            now = datetime.now()
            context_data = {
                "time": now.strftime("%H:%M"),
                "day": now.strftime("%A"),
                "weather": "sunny, 22C" # Replace with real API later
            }
            with open("data/context.json", "w") as f:
                json.dump(context_data, f, indent=4)
            print("updated: context.json")
        except Exception as e:
            print(f"error: context.json {e}")
            
        time.sleep(60)

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
            history = json.load(f)
        with open("data/products.json", "r") as f:
            products = json.load(f)
        system_data = {
            "instructions": "You are a kiosk app, helping people choose what to buy.",
            "session chat": session,
            "context": context,
            "sessions history": history,
            "available products": products
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

# STARING UPDATER & WEBSERVER
#===================
if __name__ == "__main__":
    updater_thread = threading.Thread(target=update_context_loop, daemon=True)
    updater_thread.start()

    app.run(debug=True)