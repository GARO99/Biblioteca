# domain/repositories/base_repository.py
from __future__ import annotations
from typing import Any, Generic, Iterable, Optional, Sequence, Type, TypeVar

from sqlalchemy import select, func
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """Repositorio genérico, sin commits; deja la transacción al Service/UoW."""

    def __init__(self, model: Type[T], session: Session) -> None:
        self.model = model
        self.session = session

    def get(
        self,
        id_: Any,
        *,
        options: Sequence[Any] = (),
        for_update: bool = False,
        populate_existing: Optional[bool] = None,
        execution_options: Optional[dict] = None,
    ) -> Optional[T]:
        """
        Carga por PK (simple o compuesta). Soporta eager loading y SELECT..FOR UPDATE.
        - Si el objeto ya está en el identity map y necesitas que se aplique el lock
          o las options, usa populate_existing=True para forzar el SELECT.
        """
        # comportamiento por defecto sensato:
        # si pides lock y no especificaste populate_existing, lo forzamos
        if populate_existing is None and for_update:
            populate_existing = True

        return self.session.get(
            self.model,
            id_,  # para PK compuesta: (pk1, pk2) ó {"pk1": v1, "pk2": v2}
            options=options,
            with_for_update=for_update,
            populate_existing=populate_existing or False,
            execution_options=execution_options or {},
        )

    def list(
        self,
        *,
        filters: Sequence[Any] = (),
        order_by: Sequence[Any] = (),
        offset: int = 0,
        limit: Optional[int] = None,
        options: Sequence[Any] = (),
    ) -> list[T]:
        stmt: Select = select(self.model).options(*options)
        for f in filters:
            stmt = stmt.where(f)
        for ob in order_by:
            stmt = stmt.order_by(ob)
        if offset:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def count(self, *, filters: Sequence[Any] = ()) -> int:
        stmt = select(func.count()).select_from(self.model)
        for f in filters:
            stmt = stmt.where(f)
        return int(self.session.execute(stmt).scalar_one())

    def exists(self, *, filters: Sequence[Any]) -> bool:
        stmt = select(func.count()).select_from(self.model)
        for f in filters:
            stmt = stmt.where(f)
        return self.session.execute(stmt).scalar_one() > 0

    def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def add_many(self, entities: Iterable[T]) -> Iterable[T]:
        self.session.add_all(list(entities))
        return entities

    def delete(self, entity: T) -> None:
        self.session.delete(entity)

    def flush(self) -> None:
        self.session.flush()

    def refresh(self, entity: T) -> T:
        self.session.refresh(entity)
        return entity
