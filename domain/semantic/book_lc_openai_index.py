from __future__ import annotations
import os
from typing import List
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy
from domain.entities.catalog.book import Book
from domain.entities.catalog.author import Author
from domain.entities.catalog.genre import Genre

PERSIST_DIR = "var/semantic_books"  # carpeta local para el índice
load_dotenv()

def _book_text(b: Book) -> str:
    authors = ", ".join(a.full_name for a in getattr(b, "authors", []) or [])
    genres  = ", ".join(g.name for g in getattr(b, "genres",  []) or [])
    parts = [b.title or "", b.title.lower() or ""]
    if b.language: parts.append(b.language)
    if b.published_year: parts.append(str(b.published_year))
    if authors: parts.append(f"Autores: {authors}, {authors.lower()}")
    if genres:  parts.append(f"Géneros: {genres}, {genres.lower()}")
    if b.isbn_13: parts.append(f"isbn:{b.isbn_13}")
    return " | ".join(parts)

class BookOpenAILCIndex:
    def __init__(self, session):
        self.session = session
        model = os.getenv("OPENAI_EMBEDDING_MODEL")
        # OpenAIEmbeddings usa OPENAI_API_KEY del entorno
        self.emb = OpenAIEmbeddings(model=model)  # :contentReference[oaicite:7]{index=7}

    def rebuild(self) -> None:
        os.makedirs(PERSIST_DIR, exist_ok=True)
        rows: List[Book] = (
            self.session.execute(
                select(Book)
                .options(selectinload(Book.authors), selectinload(Book.genres))
                .order_by(Book.id)
            ).scalars().all()
        )
        docs = [
            Document(page_content=_book_text(b), metadata={"book_id": str(b.id)})
            for b in rows
        ]
        vs = FAISS.from_documents(
            docs, 
            embedding=self.emb
        )  # crea y embebe en un paso :contentReference[oaicite:8]{index=8}
        vs.save_local(PERSIST_DIR)  # guarda index y metadatos en carpeta :contentReference[oaicite:9]{index=9}

    def _load(self) -> FAISS:
        # Si no existe, construye por primera vez
        if not os.path.exists(PERSIST_DIR):
            self.rebuild()
        return FAISS.load_local(
            PERSIST_DIR,
            embeddings=self.emb,
            allow_dangerous_deserialization=True  # requerido por FAISS load_local
        )  # :contentReference[oaicite:10]{index=10}

    def search(self, q: str, k: int = 10) -> list[str]:
        vs = self._load()
        retriever = vs.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": max(1, k), "score_threshold": 0.25}  # ajusta 0.25–0.5
        )
        docs = retriever.invoke(q)  # retorna Document con metadata
        return [d.metadata["book_id"] for d in docs]
