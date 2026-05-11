from fastapi import APIRouter
from pydantic import BaseModel

from app.graphs.agent_graph import build_basic_agent_graph
from app.memory.conversation_memory import add_message, get_conversation

router = APIRouter(prefix="/agent", tags=["Agent"])

graph = build_basic_agent_graph()


class AgentRequest(BaseModel):
    session_id: str
    user_question: str
    employee_id: str | None = None


@router.post("/ask")
def ask_agent(request: AgentRequest):
    conversation_history = get_conversation(request.session_id)

    add_message(
        request.session_id,
        "user",
        request.user_question
    )

    result = graph.invoke({
        "user_question": request.user_question,
        "employee_id": request.employee_id,
        "intent": "",
        "answer": "",
        "confidence": 0.0,
        "workflow_trace": [],
        "final_response": {},
        "conversation_history": conversation_history,
        "execution_plan": {},
        "retrieved_context": {}
    })

    add_message(
        request.session_id,
        "assistant",
        result["final_response"]["answer"]
    )

    return result["final_response"]