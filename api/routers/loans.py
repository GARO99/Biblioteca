from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.loan import LoanCreate, LoanUpdate, LoanReturn, LoanRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.loan_service import LoanService

router = APIRouter()

@router.post("/", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = LoanService(uow)
    loan = svc.create(copy_id=payload.copy_id, member_id=payload.member_id, due_date=payload.due_date)
    return loan

@router.post("/{loan_id}/return", response_model=LoanRead)
def return_loan(loan_id: UUID, payload: LoanReturn, uow: UnitOfWork = Depends(get_uow)):
    svc = LoanService(uow)
    loan = svc.return_loan(loan_id, return_date=payload.return_date)
    return loan

@router.get("/", response_model=List[LoanRead])
def list_loans(member_id: Optional[UUID] = None, status_filter: Optional[str] = None,
               skip: int = 0, limit: int = 50, uow: UnitOfWork = Depends(get_uow)):
    svc = LoanService(uow)
    loans = svc.list(member_id=member_id, status_filter=status_filter, skip=skip, limit=limit)
    return loans

@router.get("/{loan_id}", response_model=LoanRead)
def get_loan(loan_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = LoanService(uow)
    return svc.get(loan_id)

@router.put("/{loan_id}", response_model=LoanRead)
def update_loan(loan_id: UUID, payload: LoanUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = LoanService(uow)
    loan = svc.update(loan_id, due_date=payload.due_date, status=payload.status)
    return loan

@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(loan_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = LoanService(uow)
    svc.delete(loan_id)
