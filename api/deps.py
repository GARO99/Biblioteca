from __future__ import annotations
from typing import Generator
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from domain.uow.unit_of_work import UnitOfWork, UnitOfWorkFactory


def get_uow(request: Request) -> Generator[UnitOfWork, None, None]:
    factory: UnitOfWorkFactory = request.app.state.uow_factory
    uow = factory()
    with uow as tx:
        yield tx 