# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import routes_llm, routes_health, routes_rag
from utils.logger import logger 

app = FastAPI(title="LLM Server with RAG")

origins = [
    "http://localhost",            # frontend local
    "http://localhost:3000",       # si React est sur 3000
    "http://127.0.0.1:3000",      # alternative
    "http://192.168.42.131:3000",      # network
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # domains autorisés
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE ...
    allow_headers=["*"],            # Headers autorisés
)

# --- Routers ---
app.include_router(routes_llm.router, prefix="/llm", tags=["LLM"])
app.include_router(routes_health.router, prefix="/health", tags=["Health"])
app.include_router(routes_rag.router, prefix="/rag", tags=["RAG"])

@app.on_event("startup")
async def startup_event():
    logger.info("LLM Server with RAG is starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("LLM Server is shutting down...")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server at 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

