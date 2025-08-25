import uuid
from sqlmodel import Field, SQLModel


class BookAuthorLink(SQLModel, table=True):
    __tablename__ = "book_author_link"
    book_id: uuid.UUID = Field(foreign_key="book.id", primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="author.id", primary_key=True)