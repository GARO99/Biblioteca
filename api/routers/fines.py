from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.fine import FineCreate, FineUpdate, FinePay, FineRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.fine_service import FineService

router = APIRouter()

@router.post("/", response_model=FineRead, status_code=status.HTTP_201_CREATED)
def create_fine(payload: FineCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = FineService(uow)
    fine = svc.create(
        member_id=payload.member_id,
        amount_cents=payload.amount_cents,
        reason=payload.reason,
        loan_id=payload.loan_id,
    )
    return fine

@router.get("/", response_model=List[FineRead])
def list_fines(member_id: Optional[UUID] = None, skip: int = 0, limit: int = 50,
               uow: UnitOfWork = Depends(get_uow)):
    svc = FineService(uow)
    return svc.list(member_id=member_id, skip=skip, limit=limit)

@router.get("/{fine_id}", response_model=FineRead)
def get_fine(fine_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = FineService(uow)
    return svc.get(fine_id)

@router.put("/{fine_id}", response_model=FineRead)
def update_fine(fine_id: UUID, payload: FineUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = FineService(uow)
    fine = svc.update(
        fine_id,
        amount_cents=payload.amount_cents,
        reason=payload.reason,
        paid=payload.paid,
        paid_at=payload.paid_at,
        loan_id=payload.loan_id,
    )
    return fine

@router.post("/{fine_id}/pay", response_model=FineRead)
def pay_fine(fine_id: UUID, payload: FinePay, uow: UnitOfWork = Depends(get_uow)):
    svc = FineService(uow)
    fine = svc.pay(fine_id, paid_at=payload.paid_at)
    return fine

@router.delete("/{fine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fine(fine_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = FineService(uow)
    svc.delete(fine_id)
