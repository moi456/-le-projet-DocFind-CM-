from fastapi import APIRouter
import ollama

router = APIRouter(
    prefix="/chat",
    tags=["LLM"]
)

@router.post("/")
def chat(prompt: str):

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response