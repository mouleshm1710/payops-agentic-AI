from fastapi import APIRouter
from app.services.azure_sql_service import get_high_risk_records

from app.services.azure_sql_service import (
    get_payroll_exception_summary,
    get_overtime_trends,
    get_ticket_status_summary,
    get_deduction_summary,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/payroll-exceptions")
def payroll_exceptions():
    return get_payroll_exception_summary()


@router.get("/overtime-trends")
def overtime_trends():
    return get_overtime_trends()


@router.get("/ticket-status")
def ticket_status():
    return get_ticket_status_summary()


@router.get("/deduction-summary")
def deduction_summary():
    return get_deduction_summary()

@router.get("/high-risk-records")
def high_risk_records():
    return get_high_risk_records()