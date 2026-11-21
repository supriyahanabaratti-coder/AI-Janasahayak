
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(".env")

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=api_key,
    http_options={"timeout": 120000}
)

print("Sending request to Gemini...")

try:
    response = client.interactions.create(
        model="gemini-3.6-flash",
        input="Say hello in one short sentence."
    )

    print("\nSUCCESS!")
    print(response.output_text)

except Exception as e:
    print("\nFAILED!")
    print(type(e).__name__)
    print(e)
