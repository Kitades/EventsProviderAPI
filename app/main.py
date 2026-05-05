from fastapi import FastAPI

from app import routers
from app.routers import lifespan


def main():
    app = FastAPI(lifespan=lifespan)
    app.include_router(routers.router)


if __name__ == "__main__":
    main()
