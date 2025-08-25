from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.member import MemberCreate, MemberUpdate, MemberRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.member_service import MemberService

router = APIRouter()

@router.post("/", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = MemberService(uow)
    member = svc.create(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        active=payload.active,
    )
    return member

@router.get("/", response_model=List[MemberRead])
def list_members(q: Optional[str] = None, skip: int = 0, limit: int = 50, uow: UnitOfWork = Depends(get_uow)):
    svc = MemberService(uow)
    members = svc.list(q=q, skip=skip, limit=limit)
    return members

@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = MemberService(uow)
    return svc.get(member_id)

@router.put("/{member_id}", response_model=MemberRead)
def update_member(member_id: UUID, payload: MemberUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = MemberService(uow)
    member = svc.update(
        member_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        active=payload.active,
    )
    return member

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = MemberService(uow)
    svc.delete(member_id)
