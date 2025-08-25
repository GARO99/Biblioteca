import uuid
from sqlmodel import Field, SQLModel


class BookGenreLink(SQLModel, table=True):
    __tablename__ = "book_genre_link"
    book_id: uuid.UUID = Field(foreign_key="book.id", primary_key=True)
    genre_id: uuid.UUID = Field(foreign_key="genre.id", primary_key=True)