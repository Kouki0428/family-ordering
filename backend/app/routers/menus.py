"""菜单管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models import Menu

router = APIRouter(prefix="/api/menus", tags=["menus"])


class MenuCreate(BaseModel):
    name: str
    category: str = "其他"
    meal_type: str = "早餐"  # 早餐/午餐/晚餐/夜宵
    description: str = ""
    image_url: str = ""
    is_available: bool = True


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    meal_type: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None


@router.get("/", response_model=List[Menu])
def list_menus(meal_type: Optional[str] = None, db: Session = Depends(get_db)):
    """获取所有可售菜单，可按餐段筛选"""
    query = db.query(Menu).filter(Menu.is_available == 1)
    if meal_type:
        query = query.filter(Menu.meal_type == meal_type)
    return query.all()


@router.get("/{menu_id}", response_model=Menu)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """获取单个菜单详情"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return menu


@router.post("/", response_model=Menu)
def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    """创建新菜单"""
    db_menu = Menu(
        name=menu.name,
        category=menu.category,
        meal_type=menu.meal_type,
        description=menu.description,
        image_url=menu.image_url,
        is_available=1 if menu.is_available else 0,
    )
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


@router.put("/{menu_id}", response_model=Menu)
def update_menu(menu_id: int, menu: MenuUpdate, db: Session = Depends(get_db)):
    """更新菜单"""
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    for field, value in menu.dict(exclude_unset=True).items():
        if field == "is_available" and value is not None:
            value = 1 if value else 0
        setattr(db_menu, field, value)
    db.commit()
    db.refresh(db_menu)
    return db_menu


@router.delete("/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """删除菜单"""
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    db.delete(db_menu)
    db.commit()
    return {"message": "已删除"}
