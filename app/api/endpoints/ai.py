from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ...services.ai_service import get_ai_response
from ...models.user import User
from ..dependencies import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        response = get_ai_response(chat_request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable"
        )