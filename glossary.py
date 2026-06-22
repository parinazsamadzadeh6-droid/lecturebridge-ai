import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

transcript = """Today we are going to talk about Ohm's Law. One of the fundamental principles in electrical engineering. Ohm's Law states that the current following through the conductor is directly proportional to the voltage across it and inversely proportional to its resistance. We write this as V equals I times R where V is voltage in volts, I is current in amps, and R is resistance in ohms."""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    messages=[
        {
            "role": "user",
            "content": f"""You are an academic glossary builder. Extract key technical terms from this lecture transcript.

For each term provide:
- the original English term
- its Persian (Farsi) translation
- a short one-sentence definition in Persian

Respond with ONLY valid JSON in this exact format, nothing else:
[
  {{"term": "...", "translation": "...", "definition": "..."}}
]

Transcript:
{transcript}"""
        }
    ]
)

print(response.choices[0].message.content)