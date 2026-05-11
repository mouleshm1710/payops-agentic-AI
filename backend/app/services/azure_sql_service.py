import re
import urllib.parse
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from app.config import (
    AZURE_SQL_SERVER,
    AZURE_SQL_DATABASE,
    AZURE_SQL_USERNAME,
    AZURE_SQL_PASSWORD,
)


def get_sql_engine():
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER=tcp:{AZURE_SQL_SERVER},1433;"
        f"DATABASE={AZURE_SQL_DATABASE};"
        f"UID={AZURE_SQL_USERNAME};"
        f"PWD={AZURE_SQL_PASSWORD};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=180;"
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        pool_pre_ping=True,
        pool_recycle=300
    )


engine = get_sql_engine()


def extract_employee_id(user_question: str):
    match = re.search(r"\b(E\d+|EMP\d+)\b", user_question.upper())
    return match.group(0) if match else None


def run_query(query: str, params: dict | None = None):
    try:
        engine = get_sql_engine()
        df = pd.read_sql(text(query), engine, params=params or {})
        df = df.replace([np.nan, np.inf, -np.inf], None)

        return {
            "success": True,
            "records": df.to_dict(orient="records"),
            "error": None,
        }

    except Exception as error:
        return {
            "success": False,
            "records": [],
            "error": str(error),
        }


def fetch_payroll_records_for_question(user_question: str, employee_id: str | None = None):
    employee_id = employee_id or extract_employee_id(user_question)

    if employee_id:
        query = """
            SELECT TOP 10 *
            FROM payroll_enriched
            WHERE employee_id = :employee_id
            ORDER BY risk_score DESC
        """
        result = run_query(query, {"employee_id": employee_id})
    else:
        query = """
            SELECT TOP 5 *
            FROM payroll_enriched
            ORDER BY risk_score DESC
        """
        result = run_query(query)

    return {
        "source": "Azure SQL - payroll_enriched",
        "query": user_question,
        "employee_id_filter": employee_id,
        "success": result["success"],
        "records": result["records"],
        "error": result["error"],
    }


def get_payroll_exception_summary():
    query = """
        SELECT
            risk_level,
            COUNT(*) AS count_records
        FROM payroll_enriched
        GROUP BY risk_level
        ORDER BY count_records DESC
    """
    return run_query(query)


def get_overtime_trends():
    query = """
        SELECT
            timesheet_status,
            COUNT(*) AS count_records,
            AVG(net_pay_change) AS avg_net_pay_change
        FROM payroll_enriched
        GROUP BY timesheet_status
        ORDER BY count_records DESC
    """
    return run_query(query)


def get_ticket_status_summary():
    query = """
        SELECT
            ticket_status,
            COUNT(*) AS ticket_count
        FROM payroll_tickets
        GROUP BY ticket_status
    """
    return run_query(query)


def get_deduction_summary():
    query = """
        SELECT TOP 10
            anomaly_type,
            COUNT(*) AS count_records,
            AVG(net_pay) AS avg_net_pay,
            AVG(net_pay_change) AS avg_net_pay_change
        FROM payroll_enriched
        WHERE anomaly_type IS NOT NULL
        GROUP BY anomaly_type
        ORDER BY count_records DESC
    """
    return run_query(query)

def get_high_risk_records():
    query = """
        SELECT TOP 12
            employee_id,
            risk_level,
            risk_score,
            approval_status,
            timesheet_status,
            net_pay_change,
            issue_summary
        FROM payroll_enriched
        WHERE risk_level = 'High'
        ORDER BY risk_score DESC
    """
    return run_query(query)
