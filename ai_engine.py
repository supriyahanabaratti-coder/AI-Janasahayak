
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()


# Initialize Gemini client once
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "Gemini API key is missing. Check your .env file."
    )

client = genai.Client(api_key=api_key)


def generate_ai_response(prompt):

    start_time = time.time()

    print("AI request started...")

    try:
        response = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        print(
            "AI response received in:",
            round(time.time() - start_time, 2),
            "seconds"
        )

        return response.output_text

    except Exception as error:

        print(
            "AI request failed:",
            round(time.time() - start_time, 2),
            "seconds"
        )

        print("Error details:", error)

        raise


def explain_document(document_text, language):

    prompt = f"""
    You are AI JanSahayak, a government information assistant.

    Explain this government document in simple {language}.

    Include:
    1. Main purpose
    2. Important information
    3. Eligibility criteria
    4. Required documents
    5. Application process, if mentioned

    Be clear and concise.
    Do not invent facts.
    Mention when information is missing.

    Government Document:
    {document_text[:6000]}
    """

    return generate_ai_response(prompt)



def ask_question(document_text, question, language):

    prompt = f"""
    You are AI JanSahayak, an expert government document assistant.

    The user has uploaded a government document.
    Read and analyze the provided document carefully before answering.

    Answer the user's question in simple {language}.

    IMPORTANT INSTRUCTIONS:

    1. Search the entire provided document for information
       relevant to the user's question.

    2. Give a direct and specific answer based on the document.

    3. For eligibility questions, identify age limits,
       income limits, categories and other conditions.

    4. For required documents questions, list all documents
       mentioned in the document.

    5. For application questions, explain the steps
       mentioned in the document.

    6. Do not give generic or unrelated answers.

    7. Do not invent information or eligibility conditions.

    8. If information is genuinely missing, clearly explain
       which details are not available.

    9. Include relevant page numbers when available.

    Government Document:
    {document_text}

    User Question:
    {question}

    Give a clear, helpful and well-structured answer.
    """

    return generate_ai_response(prompt)
