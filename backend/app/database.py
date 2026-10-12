"""SQLite 数据库连接与表初始化"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库路径可通过环境变量配置，便于挂载到 NAS 共享文件夹
DB_PATH = os.environ.get("DB_PATH", "/data/ordering.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 确保数据目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表结构"""
    from app.models import Menu, Order, Table  # noqa: F401
    Base.metadata.create_all(bind=engine)
