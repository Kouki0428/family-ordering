"""FastAPI 应用入口"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import init_db
from app.websocket import manager
from app.routers import menus, orders, auth, users

# 创建 FastAPI 应用
app = FastAPI(
    title="家庭点餐系统 API",
    description="基于 FastAPI + SQLite + WebSocket 的家庭点餐服务",
    version="1.0.0",
)

# CORS 配置（允许内网所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(menus.router)
app.include_router(orders.router)


@app.on_event("startup")
def on_startup():
    """启动时初始化数据库"""
    init_db()


@app.get("/")
def root():
    """健康检查"""
    return {"message": "家庭点餐系统运行中", "docs": "/docs"}


@app.get("/health")
def health():
    """健康检查端点"""
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端点：客户端连接后实时接收订单推送
    消息格式示例：
    {
        "type": "order_created",
        "data": { "order": {...} }
    }
    """
    await manager.connect(websocket)
    try:
        # 保持连接，接收客户端心跳
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 提供前端静态文件（如果存在）
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
