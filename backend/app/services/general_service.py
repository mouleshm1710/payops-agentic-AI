def handle_general_query(question: str):
    return {
        "answer": (
            "This looks like a general HR/payroll operations question. "
            "Please ask about payroll, overtime, deductions, PTO, benefits, or policy details."
        ),
        "confidence": 0.75
    }