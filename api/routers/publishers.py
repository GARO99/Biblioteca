from __future__ import annotations
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status

from api.schemas.publisher import PublisherCreate, PublisherUpdate, PublisherRead
from api.deps import get_uow
from api.security.deps import require_employee
from domain.uow.unit_of_work import UnitOfWork
from domain.services.publisher_service import PublisherService

router = APIRouter()

@router.post("/", response_model=PublisherRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_employee)])
def create_publisher(payload: PublisherCreate, uow: UnitOfWork = Depends(get_uow)):
    svc = PublisherService(uow)
    pub = svc.create(name=payload.name, website=payload.website)
    return pub

@router.get("/", response_model=List[PublisherRead])
def list_publishers(q: Optional[str] = None, skip: int = 0, limit: int = 50,
                    uow: UnitOfWork = Depends(get_uow)):
    svc = PublisherService(uow)
    return svc.list(q=q, skip=skip, limit=limit)

@router.get("/{publisher_id}", response_model=PublisherRead)
def get_publisher(publisher_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = PublisherService(uow)
    return svc.get(publisher_id)

@router.put("/{publisher_id}", response_model=PublisherRead, dependencies=[Depends(require_employee)])
def update_publisher(publisher_id: UUID, payload: PublisherUpdate, uow: UnitOfWork = Depends(get_uow)):
    svc = PublisherService(uow)
    return svc.update(publisher_id, name=payload.name, website=payload.website)

@router.delete("/{publisher_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_employee)])
def delete_publisher(publisher_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    svc = PublisherService(uow)
    svc.delete(publisher_id)
