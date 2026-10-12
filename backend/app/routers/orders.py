"""订单管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models import Order, User

router = APIRouter(prefix="/api/orders", tags=["orders"])


class OrderItem(BaseModel):
    menu_id: int
    name: str
    quantity: int = 1


class OrderCreate(BaseModel):
    items: List[OrderItem]
    note: str = ""


class OrderStatusUpdate(BaseModel):
    status: str  # 预订/待确认


@router.get("/all", response_model=List[Order])
def list_all_orders(db: Session = Depends(get_db)):
    """获取所有订单（管理后台用）"""
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """创建新订单"""
    # 存储点餐项（转换为字典列表）
    items_data = [
        {"menu_id": item.menu_id, "name": item.name, "quantity": item.quantity}
        for item in order.items
    ]

    db_order = Order(
        status="待确认",
        items=items_data,
        note=order.note,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # TODO: 触发 WebSocket 推送通知
    return db_order


@router.put("/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, update: OrderStatusUpdate, db: Session = Depends(get_db)):
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    valid_statuses = ["预订", "待确认"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效状态，可选：{valid_statuses}")

    order.status = update.status
    db.commit()
    db.refresh(order)

    # TODO: 触发 WebSocket 推送通知
    return order
