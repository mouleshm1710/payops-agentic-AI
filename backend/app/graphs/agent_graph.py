from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from app.core.llm import llm
from app.services.payroll_service import handle_payroll_query
from app.services.policy_service import handle_policy_query
from app.services.general_service import handle_general_query
from app.retrieval.policy_retriever import retrieve_policy_context
from app.tools.payroll_tools import fetch_payroll_information
from app.services.combined_service import handle_combined_query

class IntentClassification(BaseModel):
    intent: Literal["payroll", "policy", "general"]


class ExecutionPlan(BaseModel):
    retrieval_required: bool
    retrieval_steps: list[Literal["payroll", "policy"]]
    reasoning_type: Literal["payroll", "policy", "general", "combined"]


intent_classifier = llm.with_structured_output(IntentClassification)
planner_llm = llm.with_structured_output(ExecutionPlan)


class AgentState(TypedDict):
    session_id: str
    employee_id: str | None
    user_question: str
    intent: str
    answer: str
    confidence: float
    workflow_trace: list[dict]
    final_response: dict
    conversation_history: list
    execution_plan: dict
    retrieved_context: dict


def format_conversation_history(conversation_history: list, max_messages: int = 6) -> str:
    recent_messages = conversation_history[-max_messages:]
    return "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in recent_messages
    ])


def build_contextual_question(state: AgentState) -> str:
    history_text = format_conversation_history(state.get("conversation_history", []))
    employee_id = state.get("employee_id")

    if not history_text:
        return state["user_question"]

    return f"""
    Current Employee ID: {employee_id or "not provided"}

    Recent Conversation:
    {history_text}

    Current User Question:
    {state["user_question"]}
    """


def is_payroll_follow_up(state: AgentState) -> bool:
    question = state["user_question"].lower()
    history_text = format_conversation_history(state.get("conversation_history", [])).lower()

    follow_up_terms = [
        "it",
        "this",
        "that",
        "next",
        "approve",
        "approval",
        "manager",
        "guarantee",
        "paid",
        "paycheck",
        "resolve",
        "do next",
        "what should i do",
    ]

    payroll_history_terms = [
        "payroll",
        "overtime",
        "paycheck",
        "manager approval",
        "timesheet",
        "net pay",
        "deduction",
        "pto",
    ]

    return (
        bool(state.get("employee_id"))
        and any(term in question for term in follow_up_terms)
        and any(term in history_text for term in payroll_history_terms)
    )


def add_trace(state, step, details):
    return state["workflow_trace"] + [
        {
            "step": step,
            "status": "completed",
            "details": details
        }
    ]


def classify_intent_node(state: AgentState) -> AgentState:
    if is_payroll_follow_up(state):
        return {
            **state,
            "intent": "payroll",
            "workflow_trace": add_trace(
                state,
                "Intent Classification",
                "Intent classified as payroll from employee-specific follow-up context"
            )
        }

    contextual_question = build_contextual_question(state)

    prompt = f"""
    Classify the user query into one category only:

    payroll: salary, paycheck, deductions, overtime, taxes, payment issues
    policy: PTO, leave, benefits, HR rules, company policy
    general: anything else

    Use the recent conversation to resolve short follow-up questions such as
    "What should I do next?", "When will my manager approve it?", or
    "Can you guarantee it will be paid next paycheck?"

    If a short follow-up refers to a previous payroll, overtime, deduction,
    PTO, approval, timesheet, or paycheck issue, classify it as payroll or policy,
    not general.

    User Query With Conversation Context:
    {contextual_question}
    """

    result = intent_classifier.invoke(prompt)

    return {
        **state,
        "intent": result.intent,
        "workflow_trace": add_trace(
            state,
            "Intent Classification",
            f"Intent classified as {result.intent}"
        )
    }


def planning_node(state: AgentState) -> AgentState:
    if is_payroll_follow_up(state):
        execution_plan = {
            "retrieval_required": True,
            "retrieval_steps": ["payroll", "policy"],
            "reasoning_type": "combined"
        }

        return {
            **state,
            "execution_plan": execution_plan,
            "workflow_trace": add_trace(
                state,
                "Execution Planning",
                f"Execution plan created from follow-up context: {execution_plan}"
            )
        }

    contextual_question = build_contextual_question(state)

    prompt = f"""
    Create an execution plan for this user question.

    User Question With Conversation Context:
    {contextual_question}

    Detected Intent:
    {state["intent"]}

    Rules:
    - If the question requires both payroll data and policy context, set reasoning_type to "combined".
    - If only payroll data is needed, set reasoning_type to "payroll".
    - If only policy context is needed, set reasoning_type to "policy".
    - If no retrieval is needed, set reasoning_type to "general".
    """

    result = planner_llm.invoke(prompt)

    execution_plan = {
        "retrieval_required": result.retrieval_required,
        "retrieval_steps": result.retrieval_steps,
        "reasoning_type": result.reasoning_type
    }

    return {
        **state,
        "execution_plan": execution_plan,
        "workflow_trace": add_trace(
            state,
            "Execution Planning",
            f"Execution plan created: {execution_plan}"
        )
    }


def retrieval_executor_node(state: AgentState) -> AgentState:
    retrieval_steps = state["execution_plan"].get("retrieval_steps", [])
    retrieved_context = dict(state["retrieved_context"])
    trace = state["workflow_trace"]
    contextual_question = build_contextual_question(state)

    if "payroll" in retrieval_steps:
        payroll_data = fetch_payroll_information(contextual_question, state.get("employee_id"))
        retrieved_context["payroll_data"] = payroll_data

        if payroll_data.get("success"):
            trace = trace + [
                {
                    "step": "Payroll SQL Retrieval",
                    "status": "completed",
                    "details": "Payroll data retrieved from Azure SQL",
                }
            ]
        else:
            trace = trace + [
                {
                    "step": "Payroll SQL Retrieval",
                    "status": "warning",
                    "details": f"Azure SQL retrieval failed: {payroll_data.get('error')}",
                }
            ]

    if "policy" in retrieval_steps:
        policy_result = retrieve_policy_context(contextual_question)
        retrieved_context["policy_context"] = policy_result.get("context", "")
        retrieved_context["policy_documents"] = policy_result.get("documents", [])

        if policy_result.get("success"):
            trace = trace + [
                {
                    "step": "Policy RAG Retrieval",
                    "status": "completed",
                    "details": "Policy context retrieved from Azure AI Search",
                }
            ]
        else:
            trace = trace + [
                {
                    "step": "Policy RAG Retrieval",
                    "status": "warning",
                    "details": f"Azure AI Search retrieval failed: {policy_result.get('error')}",
                }
            ]

    if not retrieval_steps:
        trace = trace + [
            {
                "step": "Retrieval Skipped",
                "status": "completed",
                "details": "No retrieval required for this query",
            }
        ]

    return {
        **state,
        "retrieved_context": retrieved_context,
        "workflow_trace": trace,
    }


def retrieval_merge_node(state: AgentState) -> AgentState:
    return {
        **state,
        "workflow_trace": add_trace(
            state,
            "Retrieval Merge",
            "Retrieved context consolidated into shared workflow state"
        )
    }


def payroll_node(state: AgentState) -> AgentState:
    payroll_data = state["retrieved_context"].get("payroll_data", {})

    result = handle_payroll_query(
        state["user_question"],
        payroll_data
    )

    return {
        **state,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "workflow_trace": add_trace(
            state,
            "Payroll Reasoning",
            "Payroll response generated using Azure SQL context"
        )
    }


def policy_node(state: AgentState) -> AgentState:
    policy_context = state["retrieved_context"].get("policy_context", "")

    result = handle_policy_query(
        state["user_question"],
        state["conversation_history"],
        policy_context
    )

    return {
        **state,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "workflow_trace": add_trace(
            state,
            "Policy Reasoning",
            "Policy response generated using RAG context"
        )
    }

def combined_node(state: AgentState) -> AgentState:
    payroll_data = state["retrieved_context"].get("payroll_data", {})
    policy_context = state["retrieved_context"].get("policy_context", "")

    result = handle_combined_query(
        state["user_question"],
        state["conversation_history"],
        payroll_data,
        policy_context,
    )

    return {
        **state,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "workflow_trace": add_trace(
            state,
            "Combined Reasoning",
            "Response generated using both Azure SQL payroll data and RAG policy context"
        ),
    }

def general_node(state: AgentState) -> AgentState:
    result = handle_general_query(state["user_question"])

    return {
        **state,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "workflow_trace": add_trace(
            state,
            "General Reasoning",
            "General response generated"
        )
    }


def route_reasoning(state: AgentState) -> str:
    reasoning_type = state["execution_plan"].get("reasoning_type", "general")
    retrieval_steps = state["execution_plan"].get("retrieval_steps", [])

    if reasoning_type == "combined":
        return "combined_node"

    if "payroll" in retrieval_steps and "policy" in retrieval_steps:
        return "combined_node"

    if reasoning_type == "payroll":
        return "payroll_node"

    if reasoning_type == "policy":
        return "policy_node"

    return "general_node"


def final_response_node(state: AgentState) -> AgentState:
    updated_trace = add_trace(
        state,
        "Final Packaging",
        "Final response packaged for frontend"
    )

    final_response = {
        "question": state["user_question"],
        "intent": state["intent"],
        "execution_plan": state["execution_plan"],
        "answer": state["answer"],
        "confidence": state["confidence"],
        "workflow_trace": updated_trace,
        "retrieved_context": state["retrieved_context"]
    }

    return {
        **state,
        "final_response": final_response,
        "workflow_trace": updated_trace
    }


def build_basic_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent_node", classify_intent_node)
    graph.add_node("planning_node", planning_node)
    graph.add_node("retrieval_executor_node", retrieval_executor_node)
    graph.add_node("retrieval_merge_node", retrieval_merge_node)

    graph.add_node("payroll_node", payroll_node)
    graph.add_node("policy_node", policy_node)
    graph.add_node("general_node", general_node)
    graph.add_node("combined_node", combined_node)
    graph.add_node("final_response_node", final_response_node)

    graph.set_entry_point("classify_intent_node")

    graph.add_edge("classify_intent_node", "planning_node")
    graph.add_edge("planning_node", "retrieval_executor_node")
    graph.add_edge("retrieval_executor_node", "retrieval_merge_node")

    graph.add_conditional_edges(
        "retrieval_merge_node",
        route_reasoning,
        {
            "payroll_node": "payroll_node",
            "policy_node": "policy_node",
            "general_node": "general_node",
            "combined_node": "combined_node",
        }
    )

    graph.add_edge("payroll_node", "final_response_node")
    graph.add_edge("policy_node", "final_response_node")
    graph.add_edge("combined_node", "final_response_node")
    graph.add_edge("general_node", "final_response_node")

    graph.add_edge("final_response_node", END)

    return graph.compile()

# from typing import TypedDict, Literal
# from pydantic import BaseModel, Field
# from langgraph.graph import StateGraph, END

# from app.core.llm import llm
# from app.services.payroll_service import handle_payroll_query
# from app.services.policy_service import handle_policy_query
# from app.services.general_service import handle_general_query
# from app.retrieval.policy_retriever import retrieve_policy_context
# from app.tools.payroll_tools import fetch_payroll_information
# from app.services.combined_service import handle_combined_query

# class IntentClassification(BaseModel):
#     intent: Literal["payroll", "policy", "general"]


# class ExecutionPlan(BaseModel):
#     retrieval_required: bool
#     retrieval_steps: list[Literal["payroll", "policy"]]
#     reasoning_type: Literal["payroll", "policy", "general", "combined"]


# intent_classifier = llm.with_structured_output(IntentClassification)
# planner_llm = llm.with_structured_output(ExecutionPlan)


# class AgentState(TypedDict):
#     session_id: str
#     employee_id: str | None
#     user_question: str
#     intent: str
#     answer: str
#     confidence: float
#     workflow_trace: list[dict]
#     final_response: dict
#     conversation_history: list
#     execution_plan: dict
#     retrieved_context: dict

# def add_trace(state, step, details):
#     return state["workflow_trace"] + [
#         {
#             "step": step,
#             "status": "completed",
#             "details": details
#         }
#     ]


# def classify_intent_node(state: AgentState) -> AgentState:
#     prompt = f"""
#     Classify the user query into one category only:

#     payroll: salary, paycheck, deductions, overtime, taxes, payment issues
#     policy: PTO, leave, benefits, HR rules, company policy
#     general: anything else

#     User Query:
#     {state["user_question"]}
#     """

#     result = intent_classifier.invoke(prompt)

#     return {
#         **state,
#         "intent": result.intent,
#         "workflow_trace": add_trace(
#             state,
#             "Intent Classification",
#             f"Intent classified as {result.intent}"
#         )
#     }


# def planning_node(state: AgentState) -> AgentState:
#     prompt = f"""
#     Create an execution plan for this user question.

#     User Question:
#     {state["user_question"]}

#     Detected Intent:
#     {state["intent"]}

#     Rules:
#     - If the question requires both payroll data and policy context, set reasoning_type to "combined".
#     - If only payroll data is needed, set reasoning_type to "payroll".
#     - If only policy context is needed, set reasoning_type to "policy".
#     - If no retrieval is needed, set reasoning_type to "general".
#     """

#     result = planner_llm.invoke(prompt)

#     execution_plan = {
#         "retrieval_required": result.retrieval_required,
#         "retrieval_steps": result.retrieval_steps,
#         "reasoning_type": result.reasoning_type
#     }

#     return {
#         **state,
#         "execution_plan": execution_plan,
#         "workflow_trace": add_trace(
#             state,
#             "Execution Planning",
#             f"Execution plan created: {execution_plan}"
#         )
#     }


# def retrieval_executor_node(state: AgentState) -> AgentState:
#     retrieval_steps = state["execution_plan"].get("retrieval_steps", [])
#     retrieved_context = dict(state["retrieved_context"])
#     trace = state["workflow_trace"]

#     if "payroll" in retrieval_steps:
#         payroll_data = fetch_payroll_information(state["user_question"],state.get("employee_id"))
#         retrieved_context["payroll_data"] = payroll_data

#         if payroll_data.get("success"):
#             trace = trace + [
#                 {
#                     "step": "Payroll SQL Retrieval",
#                     "status": "completed",
#                     "details": "Payroll data retrieved from Azure SQL",
#                 }
#             ]
#         else:
#             trace = trace + [
#                 {
#                     "step": "Payroll SQL Retrieval",
#                     "status": "warning",
#                     "details": f"Azure SQL retrieval failed: {payroll_data.get('error')}",
#                 }
#             ]

#     if "policy" in retrieval_steps:
#         policy_result = retrieve_policy_context(state["user_question"])
#         retrieved_context["policy_context"] = policy_result.get("context", "")
#         retrieved_context["policy_documents"] = policy_result.get("documents", [])

#         if policy_result.get("success"):
#             trace = trace + [
#                 {
#                     "step": "Policy RAG Retrieval",
#                     "status": "completed",
#                     "details": "Policy context retrieved from Azure AI Search",
#                 }
#             ]
#         else:
#             trace = trace + [
#                 {
#                     "step": "Policy RAG Retrieval",
#                     "status": "warning",
#                     "details": f"Azure AI Search retrieval failed: {policy_result.get('error')}",
#                 }
#             ]

#     if not retrieval_steps:
#         trace = trace + [
#             {
#                 "step": "Retrieval Skipped",
#                 "status": "completed",
#                 "details": "No retrieval required for this query",
#             }
#         ]

#     return {
#         **state,
#         "retrieved_context": retrieved_context,
#         "workflow_trace": trace,
#     }


# def retrieval_merge_node(state: AgentState) -> AgentState:
#     return {
#         **state,
#         "workflow_trace": add_trace(
#             state,
#             "Retrieval Merge",
#             "Retrieved context consolidated into shared workflow state"
#         )
#     }


# def payroll_node(state: AgentState) -> AgentState:
#     payroll_data = state["retrieved_context"].get("payroll_data", {})

#     result = handle_payroll_query(
#         state["user_question"],
#         payroll_data
#     )

#     return {
#         **state,
#         "answer": result["answer"],
#         "confidence": result["confidence"],
#         "workflow_trace": add_trace(
#             state,
#             "Payroll Reasoning",
#             "Payroll response generated using Azure SQL context"
#         )
#     }


# def policy_node(state: AgentState) -> AgentState:
#     policy_context = state["retrieved_context"].get("policy_context", "")

#     result = handle_policy_query(
#         state["user_question"],
#         state["conversation_history"],
#         policy_context
#     )

#     return {
#         **state,
#         "answer": result["answer"],
#         "confidence": result["confidence"],
#         "workflow_trace": add_trace(
#             state,
#             "Policy Reasoning",
#             "Policy response generated using RAG context"
#         )
#     }

# def combined_node(state: AgentState) -> AgentState:
#     payroll_data = state["retrieved_context"].get("payroll_data", {})
#     policy_context = state["retrieved_context"].get("policy_context", "")

#     result = handle_combined_query(
#         state["user_question"],
#         state["conversation_history"],
#         payroll_data,
#         policy_context,
#     )

#     return {
#         **state,
#         "answer": result["answer"],
#         "confidence": result["confidence"],
#         "workflow_trace": add_trace(
#             state,
#             "Combined Reasoning",
#             "Response generated using both Azure SQL payroll data and RAG policy context"
#         ),
#     }

# def general_node(state: AgentState) -> AgentState:
#     result = handle_general_query(state["user_question"])

#     return {
#         **state,
#         "answer": result["answer"],
#         "confidence": result["confidence"],
#         "workflow_trace": add_trace(
#             state,
#             "General Reasoning",
#             "General response generated"
#         )
#     }


# def route_reasoning(state: AgentState) -> str:
#     reasoning_type = state["execution_plan"].get("reasoning_type", "general")
#     retrieval_steps = state["execution_plan"].get("retrieval_steps", [])

#     if reasoning_type == "combined":
#         return "combined_node"

#     if "payroll" in retrieval_steps and "policy" in retrieval_steps:
#         return "combined_node"

#     if reasoning_type == "payroll":
#         return "payroll_node"

#     if reasoning_type == "policy":
#         return "policy_node"

#     return "general_node"


# def final_response_node(state: AgentState) -> AgentState:
#     updated_trace = add_trace(
#         state,
#         "Final Packaging",
#         "Final response packaged for frontend"
#     )

#     final_response = {
#         "question": state["user_question"],
#         "intent": state["intent"],
#         "execution_plan": state["execution_plan"],
#         "answer": state["answer"],
#         "confidence": state["confidence"],
#         "workflow_trace": updated_trace,
#         "retrieved_context": state["retrieved_context"]
#     }

#     return {
#         **state,
#         "final_response": final_response,
#         "workflow_trace": updated_trace
#     }


# def build_basic_agent_graph():
#     graph = StateGraph(AgentState)

#     graph.add_node("classify_intent_node", classify_intent_node)
#     graph.add_node("planning_node", planning_node)
#     graph.add_node("retrieval_executor_node", retrieval_executor_node)
#     graph.add_node("retrieval_merge_node", retrieval_merge_node)

#     graph.add_node("payroll_node", payroll_node)
#     graph.add_node("policy_node", policy_node)
#     graph.add_node("general_node", general_node)
#     graph.add_node("combined_node", combined_node)
#     graph.add_node("final_response_node", final_response_node)

#     graph.set_entry_point("classify_intent_node")

#     graph.add_edge("classify_intent_node", "planning_node")
#     graph.add_edge("planning_node", "retrieval_executor_node")
#     graph.add_edge("retrieval_executor_node", "retrieval_merge_node")

#     graph.add_conditional_edges(
#         "retrieval_merge_node",
#         route_reasoning,
#         {
#             "payroll_node": "payroll_node",
#             "policy_node": "policy_node",
#             "general_node": "general_node",
#             "combined_node": "combined_node",
#         }
#     )

#     graph.add_edge("payroll_node", "final_response_node")
#     graph.add_edge("policy_node", "final_response_node")
#     graph.add_edge("combined_node", "final_response_node")
#     graph.add_edge("general_node", "final_response_node")

#     graph.add_edge("final_response_node", END)

#     return graph.compile()
