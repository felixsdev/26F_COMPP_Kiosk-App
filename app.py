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
import datetime

dotenv.load_dotenv()
app = flask.Flask(__name__)

#===================
# CONTEXT.JSON UPDATER

def update_context_loop():
    while True:
        try:
            now = datetime.datetime.now()
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
        return flask.jsonify({"status": "success"})
    except Exception as e:
        print(f"Error resetting session: {e}")
        return flask.jsonify({"status": "error"}), 500

#===================
# CHAT ROUTE

@app.route("/chat", methods=["POST"])
def chat():

     # Get user msg & selected personality
    user_message = flask.request.json.get("message")
    personality = flask.request.json.get("personality")
    is_initial = flask.request.json.get("is_initial", False)

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
        system_instructions = f"""You are a smart, efficient kiosk assistant helping people choose a product. Your personality: {personality}.

        YOUR MISSION:
        Find the perfect product for the user by asking EXACTLY 3 sequential, creative lifestyle questions. After the 3rd question, you must stop asking questions and only output the final product.

        STRICT RULES:
        1. NO SMALL TALK: NEVER say "Hello", "Welcome", or "How are you?". Jump immediately into the first question.
        2. CREATIVE QUESTIONS: Ask quirky/lifestyle questions (e.g., "How long did you sleep?", "What is your energy level?").
        3. SPECIFIC OPTIONS: Provide exactly 3 short options that are direct answers to your question. NEVER include generic options like "Show all products".
        4. TRACK PROGRESSION & MODES: Count the user's previous answers in the "session chat" to know your current step.
           - Step 1 (0 answers): Ask Question 1.
           - Step 2 (1 answer): Ask Question 2.
           - Step 3 (2 answers): Ask Question 3.
           - Step 4 (3 answers - RESULT MODE): The questions are done. Provide ONLY the product_name and product_id based on their answers. Do not include a message or any options.

        CRITICAL: Respond ONLY with raw, valid JSON without markdown formatting. 
        Your JSON must exactly match this schema:
        {{
            "message": "Your short question (leave as empty string \"\" if in Result Mode)",
            "options": ["Option 1", "Option 2", "Option 3"] (leave as empty array [] if in Result Mode),
            "product_name": "The final product name (leave as null if in Steps 1-3)",
            "product_id": "The final product ID (leave as null if in Steps 1-3)"
        }}
        """
        system_data = {
            "instructions": system_instructions,
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

        '''
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
        '''

        # Call llm & get reply
        response = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=messages_payload,
            response_format={ "type": "json_object" }
        )
        reply = response.choices[0].message.content
        reply_json = json.loads(reply)
            
        session.append({"speaker": "user", "text": user_message})
        session.append({"speaker": "assistant", "text": reply_json.get("message")})

        with open("data/session.json", "w") as f:
            json.dump(session, f, indent=4)

        # Send the parsed JSON back to the frontend
        return flask.jsonify(reply_json)
    
    # Error handling
    except Exception as e:
        print(f"Error: {e}")
        return flask.jsonify({
            "message": "I'm having a little trouble connecting right now. Let's try that again."
        })

# STARING UPDATER & WEBSERVER
#===================
if __name__ == "__main__":
    updater_thread = threading.Thread(target=update_context_loop, daemon=True)
    updater_thread.start()

    app.run(debug=True)