import uuid
import random
import aiomysql
from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.database import get_db_pool
from core.security import get_password_hash, verify_password, create_access_token, generate_random_password
from core.email import send_email
from core.redis_client import get_redis_pool
from core.config import settings

router = APIRouter()

# --- 模拟验证码存储 ---
# 警告：这是一个非常简化的实现，仅用于演示。
# 在生产环境中，你应该使用 Redis 或其他缓存数据库来存储验证码，并设置过期时间。
verification_codes = {} 

# --- Pydantic 模型 (用于数据校验和序列化) ---
class User(BaseModel):
    id: str
    nickname: str
    email: EmailStr
    role: str
    balance: float
    avatar: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    
class EmailSchema(BaseModel):
    email: EmailStr

class LoginWithCodeSchema(BaseModel):
    email: EmailStr
    code: str

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    code: str
    new_password: str


# --- 数据库辅助函数 (保持不变) ---
async def get_user_by_email(pool, email: str):
    """根据邮箱查询用户"""
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return await cursor.fetchone()

async def create_user(pool, email: str, password: str, nickname: Optional[str] = None, role: str = 'user', balance: float = 0.00):
    """创建新用户"""
    hashed_password = get_password_hash(password)
    user_id = str(uuid.uuid4())
    if not nickname:
        nickname = email.split('@')[0] # 默认昵称为邮箱前缀

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "INSERT INTO users (id, nickname, email, password, role, balance) VALUES (%s, %s, %s, %s, %s, %s)"
            await cursor.execute(sql, (user_id, nickname, email, hashed_password, role, balance))
    # 返回创建的用户的完整信息，以便后续使用
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return await cursor.fetchone()

async def update_user_password(pool, email: str, new_password: str):
    """更新用户的密码"""
    hashed_password = get_password_hash(new_password)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "UPDATE users SET password = %s WHERE email = %s"
            await cursor.execute(sql, (hashed_password, email))
            return cursor.rowcount # 返回受影响的行数

async def check_and_create_admin(pool):
    """检查并创建超级管理员"""
    from core.config import settings
    admin_email = settings.SUPER_ADMIN_EMAIL
    admin_password = settings.SUPER_ADMIN_PASSWORD
    
    admin = await get_user_by_email(pool, admin_email)
    if not admin:
        print(f"超级管理员 '{admin_email}' 不存在，正在创建...")
        await create_user(
            pool,
            email=admin_email,
            password=admin_password,
            nickname='Admin',
            role='admin',
            balance=9999.99
        )
        print("超级管理员创建成功。")
    else:
        print("超级管理员已存在。")


# --- API 路由 ---

@router.post("/send-code", summary="发送邮箱验证码")
async def send_verification_code(data: EmailSchema, background_tasks: BackgroundTasks, redis=Depends(get_redis_pool)): # 2. 依赖注入 Redis
    code = f"{random.randint(100000, 999999)}"
    
    # 3. 将验证码存储到 Redis 并设置过期时间
    redis_key = f"verification_code:{data.email}"
    await redis.set(redis_key, code, ex=settings.VERIFICATION_CODE_EXPIRE_SECONDS)
    
    print(f"为 {data.email} 生成的验证码是: {code} (已存入 Redis)")

    # 4. 异步发送邮件
    email_body = f"您好！\n\n您的 AiCat 登录验证码是：{code}\n\n该验证码 {settings.VERIFICATION_CODE_EXPIRE_SECONDS // 60} 分钟内有效，请勿泄露给他人。\n\n如非本人操作，请忽略此邮件。"
    background_tasks.add_task(
        send_email,
        to_email=data.email,
        subject="[AiCat] 您的登录验证码",
        body=email_body
    )
    return {"message": "Verification code has been sent. Please check your email."}


@router.post("/login-code", response_model=Token, summary="验证码登录或注册")
async def login_with_code(data: LoginWithCodeSchema, pool=Depends(get_db_pool), redis=Depends(get_redis_pool)): # 5. 依赖注入 Redis
    
    redis_key = f"verification_code:{data.email}"
    # 6. 从 Redis 获取验证码
    stored_code = await redis.get(redis_key)
    
    if not stored_code or stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )
    
    # 7. 验证成功后，删除 Redis 中的验证码
    await redis.delete(redis_key)

    user = await get_user_by_email(pool, data.email)
    
    if not user:
        print(f"用户 {data.email} 不存在，正在自动注册...")
        random_password = generate_random_password()
        user = await create_user(pool, email=data.email, password=random_password)
    
    access_token = create_access_token(data={"sub": user['email'], "user_id": user['id']})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token, summary="用户密码登录")
async def login_for_access_token(
    pool=Depends(get_db_pool),
    username: str = Form(...),
    password: str = Form(...)
):
    user = await get_user_by_email(pool, username)

    if not user or not verify_password(password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user['email'], "user_id": user['id']})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password", summary="重置用户密码")
async def reset_password(
    data: ResetPasswordSchema,
    pool=Depends(get_db_pool),
    redis=Depends(get_redis_pool)
):
    # 1. 验证用户是否存在
    user = await get_user_by_email(pool, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该邮箱未注册",
        )

    # 2. 验证验证码
    redis_key = f"verification_code:{data.email}"
    stored_code = await redis.get(redis_key)
    if not stored_code or stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )

    # 3. 验证通过，更新密码并删除验证码
    await update_user_password(pool, data.email, data.new_password)
    await redis.delete(redis_key)

    return {"message": "密码重置成功"}