# IMPORTS
from litellm import completion
from dotenv import load_dotenv
import json

# .ENV
load_dotenv()

# LOAD JSON DATA
with open("data/history.json", "r") as f:
    history = json.load(f)
with open("data/context.json", "r") as f:
    context = json.load(f)

# PROMPT
response = completion(
    model="gemini/gemini-2.5-flash",
    messages=[
        {
            "role": "system",
            "content": f"""
            Your role:
            You are a helpfull assistant.
            Current context:
            {json.dumps(context, indent=2)}
            Conversation history:
            {json.dumps(history, indent=2)}
            """
        },
        {   
            "role": "user", 
            "content": "Hello, how are you? Tell me about me. And whats the wheater?"
         }
    ]
)

# PRINT ANSWER
print(response.choices[0].message.content)