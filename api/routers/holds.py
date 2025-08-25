from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.hold import HoldCreate, HoldFulfill, HoldRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.hold_service import HoldService

router = APIRouter()

@router.post("/", response_model=HoldRead, status_code=status.HTTP_201_CREATED)
def place_hold(payload: HoldCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = HoldService(uow)
    hold = svc.place(member_id=payload.member_id, book_id=payload.book_id)
    return hold

@router.post("/{hold_id}/cancel", response_model=HoldRead)
def cancel_hold(hold_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = HoldService(uow)
    return svc.cancel(hold_id)

@router.post("/{hold_id}/fulfill", response_model=HoldRead)
def fulfill_hold(hold_id: UUID, payload: HoldFulfill, uow: UnitOfWork = Depends(get_uow)):
    svc = HoldService(uow)
    return svc.fulfill(hold_id, copy_id=payload.copy_id)

@router.get("/", response_model=List[HoldRead])
def list_holds(member_id: Optional[UUID] = None, status_filter: Optional[str] = None,
               skip: int = 0, limit: int = 50, uow: UnitOfWork = Depends(get_uow)):
    svc = HoldService(uow)
    return svc.list(member_id=member_id, status_filter=status_filter, skip=skip, limit=limit)

@router.get("/{hold_id}", response_model=HoldRead)
def get_hold(hold_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = HoldService(uow)
    return svc.get(hold_id)

@router.delete("/{hold_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hold(hold_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = HoldService(uow)
    svc.delete(hold_id)
