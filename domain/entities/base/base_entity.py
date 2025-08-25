from datetime import datetime
import uuid
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel, func

class BaseEntity(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default=func.now()
    )
    updated_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default=func.now(),
        sa_column_kwargs={"onupdate": func.now(), "nullable": True}
    )