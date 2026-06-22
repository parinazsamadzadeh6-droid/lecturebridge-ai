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
            "content": f"""You are an expert academic note-taker helping an international student study.

Generate structured study notes in Persian (Farsi) from the following lecture transcript.

Your notes must follow this exact structure:
# [Title of the lecture topic]

## مفاهیم کلیدی (Key Concepts)
- List each key concept as a bullet point with a clear explanation

## فرمول‌ها و روابط (Formulas and Relationships)
- List any formulas or mathematical relationships mentioned

## نکات مهم (Important Points)
- List the most important things a student must remember

## خلاصه (Summary)
One short paragraph summarizing the entire lecture in simple Persian.

Rules:
- Write everything in formal Persian (Farsi) except for technical symbols and formulas
- Be clear and concise — a student should be able to study directly from these notes
- Do not add information that was not in the transcript
- Respond with ONLY the notes, no introduction or explanation

Transcript:
{transcript}"""
        }
    ]
)

print(response.choices[0].message.content)

