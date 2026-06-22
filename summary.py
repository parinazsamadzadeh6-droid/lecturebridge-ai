import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

transcript = """Today we are going to talk about Ohm's Law. One of the fundamental principles in electrical engineering. Ohm's Law states that the current following through the conductor is directly proportional to the voltage across it and inversely proportional to its resistance. We write this as V equals I times R where V is voltage in volts, I is current in amps, and R is resistance in ohms."""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    messages=[
        {
            "role": "user",
            "content": f"""You are an academic assistant helping an international student understand a lecture.

Write a concise summary of the following lecture transcript in Persian (Farsi).

Rules:
- Maximum 3 sentences
- Written in clear, simple Persian that a non-native speaker can understand
- Cover the single most important concept, its key formula if any, and why it matters
- Do not add information not present in the transcript
- Respond with ONLY the summary, no introduction or labels

Transcript:
{transcript}"""
        }
    ]
)

print(response.choices[0].message.content)