"""数据库连接"""
import sqlite3
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# 延迟初始化引擎，避免导入时的配置问题
_engine = None
_AsyncSessionLocal = None

def get_engine():
    """获取异步引擎（延迟初始化）"""
    global _engine, _AsyncSessionLocal
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
        _AsyncSessionLocal = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _engine

def get_async_session_local():
    """获取异步会话工厂"""
    if _AsyncSessionLocal is None:
        get_engine()
    return _AsyncSessionLocal

Base = declarative_base()

async def init_db():
    """初始化数据库"""
    pass

async def get_db() -> AsyncSession:
    session_local = get_async_session_local()
    async with session_local() as session:
        try:
            yield session
        finally:
            await session.close()

def get_db_connection():
    """获取同步SQLite连接（用于非异步操作）"""
    import sqlite3
    import os
    
    db_path = settings.DATABASE_URL
    
    # 如果带有 sqlite:// 前缀,去掉
    if "sqlite" in db_path:
        db_path = db_path.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    
    # 如果是相对路径,转为绝对路径
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", db_path))
    
    return sqlite3.connect(db_path)

