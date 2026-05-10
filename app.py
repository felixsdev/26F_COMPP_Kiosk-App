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
                "weather": "sunny, 22C" # replace with api or something
            }
            with open("data/context.json", "w") as f:
                json.dump(context_data, f, indent=4)
            print("updated context.json")
        except Exception as e:
            print(f"failed updating context.json {e}")
        time.sleep(60)

#===================
# UI ROUTES

# home
@app.route("/")
@app.route("/index.html")
def index():
    return flask.render_template("index.html")

# ai
@app.route("/ai.html")
def ai():
    return flask.render_template("ai.html")

# products
@app.route("/products.html")
def products():
    with open('data/products.json', 'r') as file:
        inventory = json.load(file)
    return flask.render_template('products.html', products=inventory)

# checkout
@app.route("/checkout.html")
def checkout():
    clicked_id = flask.request.args.get('item_id')
    with open('data/products.json', 'r') as file:
        inventory = json.load(file)
        
    selected_product = None
    for item in inventory:
        if item['id'] == clicked_id:
            selected_product = item
            break
            
    if not selected_product:
        return flask.render_template('products.html', products=inventory)

    return flask.render_template('checkout.html', product=selected_product)

#===================
# RESET SESSION ROUTE

@app.route("/reset", methods=["POST"])
def reset():
    try:
        with open("data/session.json", "w") as f:
            json.dump([], f)
        print(f"resetted session")
        return flask.jsonify({"status": "success"})
    except Exception as e:
        print(f"failed resetting session: {e}")
        return flask.jsonify({"status": "error"})

#===================
# CHAT ROUTE

@app.route("/chat", methods=["POST"])
def chat():

     # get message & personality
    user_message = flask.request.json.get("message")
    personality = flask.request.json.get("personality")

    try:
        # prepare context
        with open("data/session.json", "r") as f:
            session = json.load(f)
        with open("data/context.json", "r") as f:
            context = json.load(f)
        with open("data/history.json", "r") as f:
            history = json.load(f)
        with open("data/products.json", "r") as f:
            products = json.load(f)

        # add user message to session.json
        session.append({"speaker": "user", "text": user_message})

        # calculate current step from session
        user_answers_count = sum(1 for msg in session if msg.get("speaker") == "user")

        # instructions based on current step
        if user_answers_count == 1:
            step_instructions = f"""
            You are a smart, efficient kiosk assistant helping people choose a product. 
            The interaction is in Step 1/4: The user just clicked start. Ask the first quirky/lifestyle question.
            Your Personality: {personality}.
            
            STRICT RULES:
            1. NO SMALL TALK: NEVER say "Hello", "Welcome", or "How are you?".
            2. SPECIFIC OPTIONS: Provide exactly 3 short options that are direct answers to your question. NEVER include generic options like "Show all products".
            3. CRITICAL: Respond ONLY with raw, valid JSON without markdown formatting. 
            4. Your JSON must exactly match this schema:
            {{
                "message": "Your short question",
                "options": ["Option 1", "Option 2", "Option 3"] (leave as empty array [] if in Result Mode),
            }}
            """
        
        elif user_answers_count == 2:
            step_instructions = f"""
            You are a smart, efficient kiosk assistant helping people choose a product. 
            The interaction is in Step 2/4: Ask the SECOND quirky/lifestyle question based on their previous answer. 
            Your Personality: {personality}.
            
            STRICT RULES:
            1. NO SMALL TALK: NEVER say "Hello", "Welcome", or "How are you?".
            2. SPECIFIC OPTIONS: Provide exactly 3 short options that are direct answers to your question. NEVER include generic options like "Show all products".
            3. CRITICAL: Respond ONLY with raw, valid JSON without markdown formatting. 
            4. Your JSON must exactly match this schema:
            {{
                "message": "Your short question",
                "options": ["Option 1", "Option 2", "Option 3"] (leave as empty array [] if in Result Mode),
            }}
            """
        
        elif user_answers_count == 3:
            step_instructions = f"""
            You are a smart, efficient kiosk assistant helping people choose a product. 
            The interaction is in Step 3/4: Ask the THIRD and final quirky/lifestyle question. 
            Your Personality: {personality}.
            
            STRICT RULES:
            1. NO SMALL TALK: NEVER say "Hello", "Welcome", or "How are you?".
            2. SPECIFIC OPTIONS: Provide exactly 3 short options that are direct answers to your question. NEVER include generic options like "Show all products".
            3. CRITICAL: Respond ONLY with raw, valid JSON without markdown formatting. 
            4. Your JSON must exactly match this schema:
            {{
                "message": "Your short question",
                "options": ["Option 1", "Option 2", "Option 3"] (leave as empty array [] if in Result Mode),
            }}
            """
        
        else:
            step_instructions = f"""
            You are a smart, efficient kiosk assistant helping people choose a product. 
            The interaction is in Step 4/4: Result mode. The questions are done. Provide the product_name and product_id from the available products.json list based on their answers. 
            Your Personality: {personality}.

            STRICT RULES:
            1. NO SMALL TALK: NEVER say "Hello", "Welcome", or "How are you?".
            2. SPECIFIC OPTIONS: Provide exactly 3 short options that are direct answers to your question. NEVER include generic options like "Show all products".
            3. CRITICAL: Respond ONLY with raw, valid JSON without markdown formatting. 
            4. Your JSON must exactly match this schema:            
            {{
                "product_name": "The final product name (leave as null if in Steps 1-3)",
                "product_id": "The final product ID (leave as null if in Steps 1-3)"
            }}
            """

        # build the prompt        
        system_data = {
            "instructions": step_instructions,
            "session chat": session,
            "context": context,
            "sessions history": history,
            "available products": products
        }

        # create payload
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

        # call llm & get reply
        response = litellm.completion(
            model="replicate/google/gemini-2.5-flash", 
            messages=messages_payload,
        )
        reply = response.choices[0].message.content
        
        # clean up potential markdown formatting
        reply = reply.strip()
        if reply.startswith("```json"):
            reply = reply[7:]
        if reply.startswith("```"):
            reply = reply[3:]
        if reply.endswith("```"):
            reply = reply[:-3]
        reply = reply.strip()
        reply_json = json.loads(reply)
            
        # add reply to session.json
        session.append({"speaker": "assistant", "text": reply_json.get("message")})

        with open("data/session.json", "w") as f:
            json.dump(session, f, indent=4)

        # back to frontend
        return flask.jsonify(reply_json)
    
    # error handling
    except Exception as e:
        print(f"Error: {e}")
        return flask.jsonify({
            "message": "I'm having a little trouble connecting right now. Let's try that again.",
            "options": ["Retry"],
            "product_name": None,
            "product_id": None
        })

# STARING UPDATER & WEBSERVER
#===================

if __name__ == "__main__":
    updater_thread = threading.Thread(target=update_context_loop, daemon=True)
    updater_thread.start()

    app.run(debug=True)