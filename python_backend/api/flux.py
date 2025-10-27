# api/flux.py

import requests
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from typing import Dict, Any

from core.config import settings
# 导入新的认证依赖和用户模型
from core.dependencies import get_current_user, UserInDB

router = APIRouter()

# --- 1. 代理 /upload/image 接口 ---
@router.post("/upload-image")
def upload_image_proxy(
    image: UploadFile = File(...),
    overwrite: bool = Form(False),
    # 使用新的依赖注入来保护此路由
    current_user: UserInDB = Depends(get_current_user)
):
    comfy_url = f"{settings.COMFYUI_HTTP_URL}/upload/image"
    
    try:
        files = {'image': (image.filename, image.file, image.content_type)}
        data = {'overwrite': str(overwrite).lower()}
        
        print("--- [Flux] 准备通过 requests 转发 [图片上传] 请求 ---")
        
        response = requests.post(comfy_url, files=files, data=data, timeout=60)
        response.raise_for_status() 
        
        print(f"✅ [Flux] 用户 {current_user.email} [图片上传] 转发成功！")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ [Flux] [图片上传] 错误: {e}")
        raise HTTPException(status_code=502, detail=f"无法连接到 AI 服务进行图片上传: {e}")
    except Exception as e:
        print(f"❌ [Flux] [图片上传] 未知错误: {e}")
        raise HTTPException(status_code=500, detail="转发请求时发生未知错误。")


# --- 2. 代理 /prompt 接口 ---
@router.post("/queue-prompt")
def queue_prompt_proxy(
    payload: Dict[str, Any] = Body(...),
    # 使用新的依赖注入来保护此路由
    current_user: UserInDB = Depends(get_current_user)
):
    comfy_url = f"{settings.COMFYUI_HTTP_URL}/prompt"
    
    try:
        print("--- [Flux] 准备通过 requests 转发 [任务提交] 请求 ---")
        
        response = requests.post(comfy_url, json=payload, timeout=300)
        response.raise_for_status()

        print(f"✅ [Flux] 用户 {current_user.email} [任务提交] 转发成功！")
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ [Flux] [任务提交] 错误: {e}")
        raise HTTPException(status_code=502, detail=f"无法连接到 AI 服务提交任务: {e}")
    except Exception as e:
        print(f"❌ [Flux] [任务提交] 未知错误: {e}")
        raise HTTPException(status_code=500, detail="提交任务时发生未知错误。")