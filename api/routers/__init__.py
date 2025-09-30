from fastapi import APIRouter
from api.routers.auth import router as auth_router
from api.routers.books import router as books_router
from api.routers.authors import router as authors_router
from api.routers.genres import router as genres_router
from api.routers.publishers import router as publishers_router
from api.routers.members import router as members_router
from api.routers.copies import router as copies_router
from api.routers.loans import router as loans_router
from api.routers.holds import router as holds_router
from api.routers.fines import router as fines_router

routers = APIRouter()
routers.include_router(auth_router,      prefix="/auth",      tags=["auth"])
routers.include_router(books_router,      prefix="/books",      tags=["books"])
routers.include_router(authors_router,    prefix="/authors",    tags=["authors"])
routers.include_router(genres_router,     prefix="/genres",     tags=["genres"])
routers.include_router(publishers_router, prefix="/publishers", tags=["publishers"])
routers.include_router(members_router,    prefix="/members",    tags=["members"])
routers.include_router(copies_router,     prefix="/copies",     tags=["copies"])
routers.include_router(loans_router,      prefix="/loans",      tags=["loans"])
routers.include_router(holds_router,      prefix="/holds",      tags=["holds"])
routers.include_router(fines_router,      prefix="/fines",      tags=["fines"])
