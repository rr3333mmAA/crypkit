from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.endpoints import router as crypto_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    crypto_router,
    prefix="/api/cryptocurrencies",
    tags=["cryptocurrencies"]
)

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("app/static/index.html")

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.svg")
