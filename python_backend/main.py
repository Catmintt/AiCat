from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api import users, flux, comfyui_sys, synthesizer
from core.database import get_db_pool, close_db_pool
from core.redis_client import get_redis_pool, close_redis_pool
from api.users import check_and_create_admin

from core.config import settings

BASE_DIR = Path(__file__).resolve().parent
STATIC_RESULTS_DIR = BASE_DIR / "static_results"
TEMP_DIR = BASE_DIR / "temp_files"

app = FastAPI(title="AiCat Backend API")

# --- 中间件 ---
# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源的请求。在生产环境中，你应该将其限制为你的前端域名，例如 ['http://localhost:5173']
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# +++ 挂载静态文件目录 +++
STATIC_RESULTS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True) # 确保临时目录也存在
app.mount("/api/results", StaticFiles(directory=STATIC_RESULTS_DIR), name="results")

# --- 事件处理器 ---
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("应用启动中...")
    # 初始化 Redis 连接池
    await get_db_pool()
    await get_redis_pool() 

    pool = await get_db_pool()
    await check_and_create_admin(pool)
    print("数据库和 Redis 连接池以及管理员检查完成。")
    print("浏览器中访问 http://localhost:8000/docs 查看自动生成的API文档。")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("应用关闭中...")
    await close_db_pool()
    await close_redis_pool() # 关闭 Redis 连接池
    print("数据库连接池已关闭。")


# --- 包含路由 ---
# 将 user.py 中定义的路由包含进来
# 所有在 user.router 上的路由都会自动加上 /api/users 前缀
app.include_router(users.router, prefix="/api/users", tags=["Users"])

app.include_router(
    flux.router, 
    prefix="/api/flux", 
    tags=["Flux Editor"]
)
app.include_router(
    comfyui_sys.router, 
    prefix="/api/comfyui_sys",
    tags=["ComfyUI System"]
)

app.include_router(
    synthesizer.router,
    prefix="/api/synthesizer",
    tags=["Synthesizer"]
)

# --- 根路由 ---
@app.get("/")
def read_root():
    return {"message": "Welcome to AiCat Backend API"}


# 在终端中，在创建的env环境下，确保已安装所有依赖:
#    conda activate cat  （根据个人环境命名进行调整和安装）
#    pip install -r requirements.txt
# 3. 然后运行服务器:
#    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# 4. 在浏览器中访问 http://localhost:8000/docs 查看自动生成的API文档。
# 在Comfyui目录启动并监听
# python main.py --listen --enable-cors-header