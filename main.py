from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from api.routers import routers
from core.project_config import ProjectConfig
from db.db_context import DbContext
from domain.seeds.seed_admin import seed_default_admin
from domain.uow.unit_of_work import UnitOfWorkFactory
from middlewares.exception_handler_middleware import ExceptionHandlerMiddleware
from utils.singleton import singleton


app = FastAPI()

@singleton
class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=ProjectConfig.PROJECT_NAME(),
            version="0.0.1",
        )

        self.app.state.db_context = DbContext(ProjectConfig().DATABASE_URI)
        self.app.state.uow_factory = UnitOfWorkFactory(self.app.state.db_context.session_factory)

        # set cors
        if ProjectConfig.BACKEND_CORS_ORIGINS():
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in ProjectConfig.BACKEND_CORS_ORIGINS()],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        #middlewares
        self.app.add_middleware(ExceptionHandlerMiddleware)

        # set routes
        @self.app.get("/")
        def root():
            return "service is working"

        self.app.include_router(
            routers,
            prefix=ProjectConfig.API_PREFIX()
        )
        
        def _run_seed() -> None:
            # usa la fábrica de UoW del state (patrón recomendado: app.state) 
            seed_default_admin(self.app.state.uow_factory)
        self.app.add_event_handler("startup", _run_seed)


app_creator = AppCreator()
app = app_creator.app