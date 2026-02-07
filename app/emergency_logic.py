import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_transcript(transcript: str):

    with open("prompts/emergency_detection.txt") as f:
        prompt = f.read()

    full_prompt = prompt + transcript

    response = model.generate_content(full_prompt)

    return {
        "is_emergency": "true" in response.text.lower(),
        "raw": response.text
    }