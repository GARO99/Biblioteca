from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.copy import CopyCreate, CopyUpdate, CopyRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.copy_service import CopyService

router = APIRouter()

@router.post("/", response_model=CopyRead, status_code=status.HTTP_201_CREATED)
def create_copy(payload: CopyCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = CopyService(uow)
    copy = svc.create(
        book_id=payload.book_id,
        inventory_code=payload.inventory_code,
        status=payload.status,
        location=payload.location,
    )
    return copy

@router.get("/", response_model=List[CopyRead])
def list_copies(
    book_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    uow: UnitOfWork = Depends(get_uow),
):
    svc = CopyService(uow)
    copies = svc.list(book_id=book_id, status_filter=status_filter, skip=skip, limit=limit)
    return copies

@router.get("/{copy_id}", response_model=CopyRead)
def get_copy(copy_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = CopyService(uow)
    return svc.get(copy_id)

@router.put("/{copy_id}", response_model=CopyRead)
def update_copy(copy_id: UUID, payload: CopyUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = CopyService(uow)
    copy = svc.update(
        copy_id,
        inventory_code=payload.inventory_code,
        status=(payload.status.value if payload.status is not None else None),
        location=payload.location,
    )
    return copy

@router.delete("/{copy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_copy(copy_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = CopyService(uow)
    svc.delete(copy_id)
