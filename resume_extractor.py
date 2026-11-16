from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from schemas.resume_schema import UserInput
import os

load_dotenv()

# Initialize Groq
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


resume_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are an expert resume information extraction assistant.

        Your task is to carefully analyze the candidate's resume
        and extract all relevant information.

        Follow these instructions:

        1. Extract information only from the provided resume.
        2. Never invent, assume, or fabricate information.
        3. Extract the candidate's name, email, phone, and address.
        4. Identify all technical and soft skills.
        5. Extract work experience, including job titles,
           company names, responsibilities, and duration.
        6. Extract educational qualifications.
        7. Extract projects and their descriptions.
        8. Extract professional certifications.
        9. Extract languages and hobbies if available.
        10. Extract LinkedIn, GitHub, and portfolio URLs.
        11. If information is missing, use None for optional
            fields and an empty list for list fields.
        12. Preserve the original meaning of the information.
        13. Do not evaluate, rank, or score the candidate.

        Return the extracted information using the
        required Pydantic schema.
        """
    ),

    (
        "human",
        """
        Extract structured information from this resume:

        {resume_text}
        """
    )

])


# Structured Output
structured_llm = llm.with_structured_output(UserInput)

# Build Chain
resume_chain = resume_prompt | structured_llm


def extract_resume_details(resume_text: str):

    result = resume_chain.invoke({
        "resume_text": resume_text
    })

    return result