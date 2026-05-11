from app.core.llm import llm


def handle_policy_query(question: str, conversation_history: list, context: str):
    history_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in conversation_history
    ])

    if not context or context == "No relevant policy context found.":
        return {
            "answer": (
                "I could not find enough relevant policy context for this question. "
                "Please ask about a specific policy such as PTO, overtime, deductions, benefits, or approvals."
            ),
            "confidence": 0.55,
        }

    prompt = f"""
    You are an HR/payroll policy assistant.

    Previous Conversation:
    {history_text}

    Retrieved Policy Context from Azure AI Search:
    {context}

    Current User Question:
    {question}

    Provide a concise and helpful answer using only the retrieved policy context.
    If the policy context does not contain enough information, clearly say so.
    Format the answer in clean plain text.
    Do not use markdown symbols like **, ###, or bullet stars.
    Use short paragraphs or numbered points only when useful.
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "confidence": 0.9,
    }