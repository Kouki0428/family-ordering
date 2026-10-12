"""餐桌管理 API"""
import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models import Table

router = APIRouter(prefix="/api/tables", tags=["tables"])


class TableCreate(BaseModel):
    name: str  # 餐桌名称


class TableUpdate(BaseModel):
    name: str


@router.get("/", response_model=List[Table])
def list_tables(db: Session = Depends(get_db)):
    """获取所有餐桌"""
    return db.query(Table).all()


@router.get("/by-token/{token}", response_model=Table)
def get_table_by_token(token: str, db: Session = Depends(get_db)):
    """通过 token 获取餐桌信息（扫码用）"""
    table = db.query(Table).filter(Table.token == token).first()
    if not table:
        raise HTTPException(status_code=404, detail="餐桌不存在")
    return table


@router.get("/{table_id}", response_model=Table)
def get_table(table_id: int, db: Session = Depends(get_db)):
    """获取餐桌详情"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="餐桌不存在")
    return table


@router.post("/", response_model=Table)
def create_table(table: TableCreate, db: Session = Depends(get_db)):
    """创建新餐桌（自动生成扫码 token）"""
    # 生成唯一 token
    token = secrets.token_urlsafe(16)
    db_table = Table(name=table.name, token=token)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table


@router.put("/{table_id}", response_model=Table)
def update_table(table_id: int, table: TableUpdate, db: Session = Depends(get_db)):
    """更新餐桌名称"""
    db_table = db.query(Table).filter(Table.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="餐桌不存在")
    db_table.name = table.name
    db.commit()
    db.refresh(db_table)
    return db_table


@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    """删除餐桌"""
    db_table = db.query(Table).filter(Table.id == table_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="餐桌不存在")
    db.delete(db_table)
    db.commit()
    return {"message": "已删除"}
