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
                "day": now.strftime("%A")
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
# INCREMENT SOLD COUNT ROUTE

@app.route("/increment_sold", methods=["POST"])
def increment_sold():
    product_id = flask.request.json.get("product_id")
    if not product_id:
        return flask.jsonify({"status": "error", "message": "Product ID is required"}), 400

    try:
        with open("data/products.json", "r+") as f:
            products = json.load(f)
            for product in products:
                if product.get("id") == product_id:
                    product["sold"] = product.get("sold", 0) + 1
                    break
            f.seek(0)
            json.dump(products, f, indent=4)
            f.truncate()
        return flask.jsonify({"status": "success"})
    except Exception as e:
        print(f"failed to increment sold count: {e}")
        return flask.jsonify({"status": "error", "message": str(e)}), 500

#===================
# INCREMENT DECLINED COUNT ROUTE

@app.route("/increment_declined", methods=["POST"])
def increment_declined():
    product_id = flask.request.json.get("product_id")
    if not product_id:
        return flask.jsonify({"status": "error", "message": "Product ID is required"}), 400

    try:
        with open("data/products.json", "r+") as f:
            products = json.load(f)
            for product in products:
                if product.get("id") == product_id:
                    product["declined"] = product.get("declined", 0) + 1
                    break
            f.seek(0)
            json.dump(products, f, indent=4)
            f.truncate()
        return flask.jsonify({"status": "success"})
    except Exception as e:
        print(f"failed to increment declined count: {e}")
        return flask.jsonify({"status": "error", "message": str(e)}), 500

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
        with open("data/products.json", "r") as f:
            products = json.load(f)

        # add user message to session.json
        session.append({"speaker": "user", "text": user_message})

        # instructions
        instructions = f"""
        You are the sassy, unhinged AI living inside a university snack kiosk. 
        You serve a tight-knit micro-community of 50 stressed "HSLU Digital Ideation" students. 
        Current Time & Weather: {context}.
        Your Personality: {personality}.

        YOUR MISSION:
        Help the user pick a snack/drink quickly, while aggressively judging their lifestyle choices. 
        Read the chat history. You must operate in ONE of these two modes:

        MODE A: QUESTION MODE (If you need more info)
        - Ask ONE highly specific, slightly unhinged question to gauge their vibe. 
        - Tie the question to the current time, weather, or bizarre global events.
        - Keep it to 1-2 short sentences.
        - Provide exactly 3 short, funny options.

        MODE B: RECOMMENDATION & ROAST MODE (If they gave enough info)
        - Pick a specific item from `products.json`.
        - Brutally roast them for their choice or their current state (e.g., studying late, horrible weather).
        - Use the `products.json` sales data to mock the group's collective habits (e.g., "You guys drink too much Mate").
        - Do NOT provide options in this mode.

        STRICT RULES:
        1. NO SMALL TALK. Never say Hello, Welcome, or talk about cooking.
        2. Keep all responses punchy and short.
        3. CRITICAL: Respond ONLY with raw, valid JSON. Do not use markdown. Do not include comments in the JSON.
        4. MAX 3 questions, try 2.
        5. Never add the product names into the answer options. You should recomend.
        
        JSON SCHEMA:
        {{
            "message": "Your sassy question OR your final roasting recommendation",
            "options": ["Option 1", "Option 2", "Option 3"], 
            "product_name": "Name of product", 
            "product_id": "ID of product"
        }}
        
        Note: If in Mode B, set "options" to an empty array []. If in Mode A, set "product_name" and "product_id" to null.
        """

        # build the prompt        
        system_data = {
            "instructions": instructions,
            "session chat": session,
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
            # model="replicate/meta/meta-llama-3-8b-instruct", # asks to many questions (10+)
            # model="replicate/qwen/qwen3-235b-a22b-instruct-2507", # fast but doesnt get the session.json
            # model="replicate/google/gemini-2.5-flash", # really slow but best interaction
            # model="replicate/google/gemini-3-flash", # similar to 2.5
            # model="replicate/google/gemini-3.1-pro", # really slow but really good and funny questions
            model="replicate/anthropic/claude-4.5-haiku", # 
            messages=messages_payload,
            temperature=0.9
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