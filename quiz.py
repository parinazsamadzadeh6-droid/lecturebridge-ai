import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

transcript = """Today we are going to talk about Ohm's Law. One of the fundamental principles in electrical engineering. Ohm's Law states that the current following through the conductor is directly proportional to the voltage across it and inversely proportional to its resistance. We write this as V equals I times R where V is voltage in volts, I is current in amps, and R is resistance in ohms."""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    messages=[
        {
            "role": "user",
            "content": f"""You are an academic exam question generator helping an international student prepare for exams.

Generate exam questions and answers in Persian (Farsi) based on the following lecture transcript.

Generate exactly 3 types of questions:

1. یک سوال چندگزینه‌ای (One multiple choice question with 4 options, mark the correct answer)
2. یک سوال کوتاه‌پاسخ (One short answer question with a concise answer)
3. یک سوال تشریحی (One essay/explanatory question with a detailed answer)

Format each question clearly like this:

### سوال ۱ - چندگزینه‌ای
[Question in Persian]
الف) [option]
ب) [option]
ج) [option]
د) [option]
✓ پاسخ صحیح: [correct option letter]

### سوال ۲ - کوتاه‌پاسخ
[Question in Persian]
پاسخ: [concise answer in Persian]

### سوال ۳ - تشریحی
[Question in Persian]
پاسخ: [detailed answer in Persian]

Rules:
- Write all questions and answers in formal Persian (Farsi)
- Base questions ONLY on content from the transcript
- Make questions genuinely useful for exam preparation
- Respond with ONLY the questions and answers, no introduction

Transcript:
{transcript}"""
        }
    ]
)

print(response.choices[0].message.content)