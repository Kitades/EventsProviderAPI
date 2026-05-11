from fastapi import FastAPI

from app import routers
from app.routers import lifespan

app = FastAPI(lifespan=lifespan)


def main():
    app.include_router(routers.router)


if __name__ == "__main__":
    main()
