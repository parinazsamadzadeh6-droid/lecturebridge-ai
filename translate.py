import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

transcript = """Today we are going to talk about Ohm's Law. One of the fundamental principles in electrical engineering. Ohm's Law states that the current following through the conductor is directly proportional to the voltage across it and inversely proportional to its resistance. We write this as V equals I times R where V is voltage in volts, I is current in amps, and R is resistance in ohms."""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": f"You are a professional academic translator. Translate the following lecture transcript into formal, proper Persian (Farsi) using correct Persian script throughout. Do not mix in English words except for standard technical symbols and units (V, I, R) which may stay as-is. Respond with ONLY the translated text — no introduction, no alternate versions, no notes, no explanations, nothing before or after the translation itself.\n\nTranscript:\n{transcript}"
        }
    ]
)

print(response.choices[0].message.content)