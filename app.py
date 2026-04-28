from litellm import completion
from dotenv import load_dotenv

load_dotenv()

response = completion(
    model="gemini/gemini-2.5-flash",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

print(response.choices[0].message.content)