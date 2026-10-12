"""数据模型：用户、菜单、订单"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)  # bcrypt 加密
    is_admin = Column(Boolean, nullable=False, default=False)  # 是否管理员
    created_at = Column(DateTime, default=datetime.utcnow)


class Menu(Base):
    """菜单表"""
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 菜品名称
    category = Column(String(50), nullable=False, default="其他")  # 分类（热菜/凉菜/饮品等）
    meal_type = Column(String(20), nullable=False, default="早餐")  # 餐段（早餐/午餐/晚餐/夜宵）
    description = Column(Text, default="")  # 描述
    image_url = Column(String(500), default="")  # 图片 URL 或路径
    is_available = Column(Integer, nullable=False, default=1)  # 是否可售（1=是，0=否）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 下单用户
    status = Column(String(20), nullable=False, default="预订")  # 预订/待确认
    items = Column(JSON, nullable=False)  # 点餐项列表 [{menu_id, name, quantity}]
    note = Column(Text, default="")  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
