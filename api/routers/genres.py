from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.genre import GenreCreate, GenreUpdate, GenreRead
from api.deps import get_uow
from domain.uow.unit_of_work import UnitOfWork
from domain.services.genre_service import GenreService

router = APIRouter()

@router.post("/", response_model=GenreRead, status_code=status.HTTP_201_CREATED)
def create_genre(payload: GenreCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = GenreService(uow)
    genre = svc.create(name=payload.name, description=payload.description)
    return genre

@router.get("/", response_model=List[GenreRead])
def list_genres(q: Optional[str] = None, skip: int = 0, limit: int = 50,
                uow: UnitOfWork = Depends(get_uow)):
    svc = GenreService(uow)
    return svc.list(q=q, skip=skip, limit=limit)

@router.get("/{genre_id}", response_model=GenreRead)
def get_genre(genre_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = GenreService(uow)
    return svc.get(genre_id)

@router.put("/{genre_id}", response_model=GenreRead)
def update_genre(genre_id: UUID, payload: GenreUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = GenreService(uow)
    return svc.update(genre_id, name=payload.name, description=payload.description)

@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(genre_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = GenreService(uow)
    svc.delete(genre_id)
