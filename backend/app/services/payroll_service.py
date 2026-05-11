from app.core.llm import llm


def handle_payroll_query(question: str, payroll_data: dict):
    if not payroll_data.get("success"):
        return {
            "answer": (
                "I could not retrieve payroll data from Azure SQL at the moment. "
                "Please check the database connection or try again later."
            ),
            "confidence": 0.4,
        }

    records = payroll_data.get("records", [])

    if not records:
        return {
            "answer": (
                "I could not find matching payroll records for this query. "
                "Please include a valid employee ID like EMP102 if you want a specific lookup."
            ),
            "confidence": 0.55,
        }

    prompt = f"""
    You are a payroll operations assistant.

    User Question:
    {question}

    Payroll Data Retrieved from Azure SQL:
    {payroll_data}

    Provide a clear, concise answer based only on the available payroll data.
    If the data is insufficient, say what additional payroll details may be needed.
    Format the answer in clean plain text.
    Do not use markdown symbols like **, ###, or bullet stars.
    Use short paragraphs or numbered points only when useful.
    """

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "confidence": 0.9,
    }