"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import chat, memory, materials, analysis, users

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(materials.router, prefix="/api/materials", tags=["素材"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["分析"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])

@app.get("/")
async def root():
    return {"message": "儿童学习记录AI系统", "version": settings.APP_VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
