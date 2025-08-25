from __future__ import annotations
from typing import Callable, Optional
from sqlalchemy.orm import Session

class UnitOfWork:
    """
    Orquesta una transacción: abre Session, comienza transacción,
    hace commit/rollback y cierra. No crea repos ni los conoce.
    """
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self.session: Optional[Session] = None
        self._begun = False

    def __enter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self._txn = self.session.begin()
        self._begun = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()
            self._begun = False

    def commit(self) -> None:
        assert self.session is not None
        self.session.commit()

    def rollback(self) -> None:
        assert self.session is not None
        self.session.rollback()


class UnitOfWorkFactory:
    """
    Pequeña fábrica para producir UoWs frescos cuando se necesiten (por request o por caso de uso).
    """
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def __call__(self) -> UnitOfWork:
        return UnitOfWork(self._session_factory)
