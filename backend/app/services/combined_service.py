from app.core.llm import llm


def handle_combined_query(
    question: str,
    conversation_history: list,
    payroll_data: dict,
    policy_context: str,
):
    history_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in conversation_history
    ])

    prompt = f"""
    You are a payroll and HR policy operations assistant.

    Previous Conversation:
    {history_text}

    User Question:
    {question}

    Payroll Data from Azure SQL:
    {payroll_data}

    Policy Context from Azure AI Search:
    {policy_context}

    Provide a clear answer that connects the employee-specific payroll facts
    with the relevant HR/payroll policy rules.

    Do not assume facts that are not present in the payroll data or policy context.
    If something is unclear, mention what additional detail is needed.
    Format the answer in clean plain text.
    Do not use markdown symbols like **, ###, or bullet stars.
    Use short paragraphs or numbered points only when useful.
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "confidence": 0.9,
    }