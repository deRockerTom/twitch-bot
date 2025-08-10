import uvicorn
from api import api_router
from api.v1.models.default import DefaultAPIResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)


@app.get("/", response_model=DefaultAPIResponse)
async def root():
    return {"message": "Welcome to the Twitch Bot API"}


app.include_router(
    api_router,
    prefix="/api",
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
