# api/comfyui_sys.py

from fastapi import APIRouter
from pydantic import BaseModel
from core.config import settings

# --- 定义 Pydantic 模型 ---
class ComfyUIConfig(BaseModel):
    httpUrl: str
    wsUrl: str

class AppConfigResponse(BaseModel):
    comfyUI: ComfyUIConfig

router = APIRouter()

# --- 定义 /config 路由 ---
@router.get(
    "/config", 
    response_model=AppConfigResponse, 
    summary="获取前端应用所需配置"
)
def get_application_config():
    """
    为前端提供必要的后端服务地址和其他配置。
    """
    return {
        "comfyUI": {
            "httpUrl": settings.COMFYUI_HTTP_URL,
            "wsUrl": settings.COMFYUI_WS_URL
        }
    }