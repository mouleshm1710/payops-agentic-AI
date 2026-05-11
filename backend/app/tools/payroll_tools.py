from app.services.azure_sql_service import fetch_payroll_records_for_question


def fetch_payroll_information(user_question: str, employee_id: str | None = None):
    return fetch_payroll_records_for_question(user_question, employee_id)