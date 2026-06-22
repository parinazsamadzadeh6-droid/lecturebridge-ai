import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    timeout=60.0
)

AUDIO_FILE = "test_audio.m4a"
TARGET_LANGUAGE = "Persian (Farsi)"

def transcribe(audio_path):
    print("Step 1: Transcribing audio...")
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo"
        )
    print("  Transcription complete.")
    return transcription.text

def translate(transcript):
    print("Step 2: Translating transcript...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": f"""You are a professional academic translator. Translate the following lecture transcript into formal, proper {TARGET_LANGUAGE} using correct script throughout. Do not mix in English words except for standard technical symbols and units. Respond with ONLY the translated text — no introduction, no alternate versions, no notes.

Transcript:
{transcript}"""
            }
        ]
    )
    print("  Translation complete.")
    return response.choices[0].message.content.strip()

def get_glossary(transcript):
    print("Step 3: Extracting glossary...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": f"""You are an academic glossary builder. Extract key technical terms from this lecture transcript.

For each term provide:
- the original English term
- its {TARGET_LANGUAGE} translation
- a short one-sentence definition in {TARGET_LANGUAGE}

Respond with ONLY valid JSON in this exact format, nothing else:
[
  {{"term": "...", "translation": "...", "definition": "..."}}
]

Transcript:
{transcript}"""
            }
        ]
    )
    print("  Glossary complete.")
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []

def get_notes(transcript):
    print("Step 4: Generating study notes...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert academic note-taker helping an international student study.

Generate structured study notes in {TARGET_LANGUAGE} from the following lecture transcript.

Your notes must follow this exact structure:
# [Title of the lecture topic]

## مفاهیم کلیدی (Key Concepts)
- List each key concept as a bullet point with a clear explanation

## فرمول‌ها و روابط (Formulas and Relationships)
- List any formulas or mathematical relationships mentioned

## نکات مهم (Important Points)
- List the most important things a student must remember

## خلاصه (Summary)
One short paragraph summarizing the entire lecture in simple {TARGET_LANGUAGE}.

Rules:
- Write everything in formal {TARGET_LANGUAGE} except for technical symbols and formulas
- Be clear and concise
- Do not add information not in the transcript
- Respond with ONLY the notes

Transcript:
{transcript}"""
            }
        ]
    )
    print("  Notes complete.")
    return response.choices[0].message.content.strip()

def get_summary(transcript):
    print("Step 5: Generating summary...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": f"""You are an academic assistant helping an international student understand a lecture.

Write a concise summary of the following lecture transcript in {TARGET_LANGUAGE}.

Rules:
- Keep it short and proportional to the transcript length
- Written in clear, simple {TARGET_LANGUAGE}
- Cover the most important concept, key formula if any, and why it matters
- Do not add information not in the transcript
- Respond with ONLY the summary

Transcript:
{transcript}"""
            }
        ]
    )
    print("  Summary complete.")
    return response.choices[0].message.content.strip()

def get_quiz(transcript):
    print("Step 6: Generating quiz questions...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.4,
        messages=[
            {
                "role": "user",
                "content": f"""You are an academic exam question generator helping an international student prepare for exams.

Generate exam questions and answers in {TARGET_LANGUAGE} based on the following lecture transcript.

Generate exactly 3 types of questions:
1. One multiple choice question with 4 options
2. One short answer question
3. One essay question

Format each clearly with Persian labels and mark correct answers.

Rules:
- Write all questions and answers in formal {TARGET_LANGUAGE}
- Base questions ONLY on content from the transcript
- Respond with ONLY the questions and answers

Transcript:
{transcript}"""
            }
        ]
    )
    print("  Quiz complete.")
    return response.choices[0].message.content.strip()

def save_outputs(transcript, translation, glossary, notes, summary, quiz):
    print("\nSaving outputs...")

    with open("output_transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

    with open("output_translation.txt", "w", encoding="utf-8") as f:
        f.write(translation)

    with open("output_glossary.json", "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)

    with open("output_notes.md", "w", encoding="utf-8") as f:
        f.write(notes)

    with open("output_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    with open("output_quiz.md", "w", encoding="utf-8") as f:
        f.write(quiz)

    print("  All outputs saved.")

def run_pipeline(audio_path):
    print(f"\nLectureBridge AI Pipeline")
    print(f"Audio file: {audio_path}")
    print(f"Target language: {TARGET_LANGUAGE}")
    print("="*40)

    transcript = transcribe(audio_path)
    translation = translate(transcript)
    glossary = get_glossary(transcript)
    notes = get_notes(transcript)
    summary = get_summary(transcript)
    quiz = get_quiz(transcript)

    save_outputs(transcript, translation, glossary, notes, summary, quiz)

    print("\n" + "="*40)
    print("Pipeline complete! Files saved:")
    print("  output_transcript.txt")
    print("  output_translation.txt")
    print("  output_glossary.json")
    print("  output_notes.md")
    print("  output_summary.txt")
    print("  output_quiz.md")

run_pipeline(AUDIO_FILE)
