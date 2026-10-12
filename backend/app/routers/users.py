"""用户管理 API（管理员专用）"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/api/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: str


class UserUpdate(BaseModel):
    is_admin: Optional[bool] = None


def get_current_admin(token: str, db: Session = Depends(get_db)) -> User:
    """获取当前管理员用户"""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid token")
        user_id = int(parts[0])
        is_admin = parts[2] == "True"
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        if not is_admin:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="无效的认证令牌")


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_admin)
):
    """获取所有用户列表"""
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_admin)
):
    """更新用户权限"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 防止管理员取消自己的管理员权限
    if user_id == current_user.id and update.is_admin is False:
        raise HTTPException(status_code=400, detail="不能取消自己的管理员权限")
    
    if update.is_admin is not None:
        user.is_admin = update.is_admin
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_admin)
):
    """删除用户"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"message": "已删除"}
