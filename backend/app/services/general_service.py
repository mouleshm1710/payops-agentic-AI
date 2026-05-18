def handle_general_query(question: str):
    normalized_question = question.lower().strip()

    thanks_terms = [
        "thank",
        "thanks",
        "thank you",
        "cool",
        "great",
        "awesome",
        "perfect",
        "got it",
        "that helps",
    ]

    greeting_terms = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if any(term in normalized_question for term in thanks_terms):
        return {
            "answer": (
                "You're welcome. Happy to help with any payroll, overtime, PTO, "
                "deduction, benefits, or policy question."
            ),
            "confidence": 0.9
        }

    if any(term in normalized_question for term in greeting_terms):
        return {
            "answer": (
                "Hi, how can I help with payroll, overtime, deductions, PTO, "
                "benefits, or policy today?"
            ),
            "confidence": 0.9
        }

    return {
        "answer": (
            "This looks like a general HR/payroll operations question. "
            "Please ask about payroll, overtime, deductions, PTO, benefits, or policy details."
        ),
        "confidence": 0.75
    }
