from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.author import AuthorCreate, AuthorUpdate, AuthorRead
from api.security.deps import require_employee
from domain.uow.unit_of_work import UnitOfWork
from api.deps import get_uow
from domain.services.author_service import AuthorService

router = APIRouter()

@router.post("/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_employee)])
def create_author(payload: AuthorCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = AuthorService(uow)
    author = svc.create(full_name=payload.full_name, bio=payload.bio)
    return author

@router.get("/", response_model=List[AuthorRead])
def list_authors(q: Optional[str] = None, skip: int = 0, limit: int = 50,
                 uow: UnitOfWork = Depends(get_uow)):
    svc = AuthorService(uow)
    authors = svc.list(q=q, skip=skip, limit=limit)
    return authors

@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = AuthorService(uow)
    author = svc.get(author_id)
    return author

@router.put("/{author_id}", response_model=AuthorRead, dependencies=[Depends(require_employee)])
def update_author(author_id: UUID, payload: AuthorUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = AuthorService(uow)
    author = svc.update(author_id, full_name=payload.full_name, bio=payload.bio)
    return author

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_employee)])
def delete_author(author_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = AuthorService(uow)
    svc.delete(author_id)
