from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from API_for_library.app.user import user_router
from API_for_library.app.books import books_router
from API_for_library.app.author import author_router
from API_for_library.app.auth import auth_router
from API_for_library.app.Issue import issue_router


def init_cors(api: FastAPI) -> None:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routers(api: FastAPI) -> None:
    api.include_router(user_router)
    api.include_router(books_router)
    api.include_router(author_router)
    api.include_router(auth_router)
    api.include_router(issue_router)


def create_api():
    api = FastAPI(
        title="Library",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    init_routers(api)
    init_cors(api)

    return api


api = create_api()
