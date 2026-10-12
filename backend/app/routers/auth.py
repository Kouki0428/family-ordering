"""用户认证 API"""
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    is_cooker: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    """加密密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册（首次使用创建管理员）"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建用户
    db_user = User(
        username=user.username,
        password=hash_password(user.password),
        is_admin=user.is_admin,
        is_cooker=user.is_cooker,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成简单 token（生产环境建议使用 JWT）
    token = f"{user.id}:{user.username}:{user.is_admin}:{user.is_cooker}"
    return Token(access_token=token, token_type="bearer")


@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    try:
        parts = token.split(":")
        if len(parts) != 4:
            raise ValueError("Invalid token")
        user_id = int(parts[0])
        username = parts[1]
        is_admin = parts[2] == "True"
        is_cooker = parts[3] == "True"
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        return {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_cooker": user.is_cooker,
        }
    except Exception:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
