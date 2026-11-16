
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from schemas.job_schema import JobSchema
import os

load_dotenv()

# Initialize Groq
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# Prompt Template
job_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert job description information extraction assistant.

        Your task is to analyze the provided job description and
        extract its requirements into structured information.

        Follow these instructions:

        1. Extract the job title and company name.
        2. Identify all required technical and soft skills.
        3. Identify preferred skills separately from required skills.
        4. Extract the minimum required years of experience.
        5. Extract required educational qualifications.
        6. Extract key job responsibilities.
        7. Identify required certifications.
        8. Identify preferred certifications.
        9. Never invent or assume information.
        10. If information is missing, use None for optional fields
            and empty lists for list fields.
        11. Do not evaluate or score any candidate.
        12. Return the information using the provided Pydantic schema.
        """
    ),
    (
        "human",
        """
        Extract structured information from this job description:

        {job_description}
        """
    )
])

# Structured Output
structured_llm = llm.with_structured_output(JobSchema)

# Build Chain
job_chain = job_prompt | structured_llm


def extract_job_details(job_description: str):

    result = job_chain.invoke({
        "job_description": job_description
    })

    return result
