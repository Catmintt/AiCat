from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_PORT: int = 3306

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    VERIFICATION_CODE_EXPIRE_SECONDS: int = 300 # 验证码过期时间 (5分钟)

    # 超级管理员
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # 邮箱
    EMAIL_USER: str
    EMAIL_PASS: str
    EMAIL_HOST: str
    EMAIL_PORT: int

    # ComfyUI 配置
    COMFYUI_HTTP_URL: str
    COMFYUI_WS_URL: str

    # 语音识别
    STT_API_KEY: str
    MINIMAX_GROUP_ID: str
    MINIMAX_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()