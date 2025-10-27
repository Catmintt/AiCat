import aiomysql
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from typing import Optional

from .config import settings
from .database import get_db_pool

# 定义一个与数据库字段匹配的用户模型，用于内部传递
class UserInDB(BaseModel):
    id: str
    nickname: str
    email: EmailStr
    role: str
    balance: float
    avatar: Optional[str] = None
    password: str # 包含哈希密码

# 定义从哪里获取 Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    pool: aiomysql.Pool = Depends(get_db_pool)
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = await cursor.fetchone()

    if user is None:
        raise credentials_exception
    
    return UserInDB(**user)