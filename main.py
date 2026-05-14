from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start server")
    try:
        yield
    finally:
        print("Stop server")


app = FastAPI(lifespan=lifespan)

app.include_router(router)

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
