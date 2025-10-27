# api/synthesizer.py

# 1. 标准库和第三方库导入
import os
import uuid
import shutil
import subprocess
import requests
from pydub import AudioSegment
from gradio_client import Client, handle_file
from pathlib import Path # 推荐使用 pathlib 处理路径

# FastAPI 相关导入
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from core.config import settings

router = APIRouter()

# --- API密钥和配置 ---
STT_API_KEY = settings.STT_API_KEY
MINIMAX_GROUP_ID = settings.MINIMAX_GROUP_ID
MINIMAX_API_KEY = settings.MINIMAX_API_KEY# --- 字典和常量 ---
MINIMAX_VOICES = {
    # 通用与主持
    "男性主持人": "presenter_male",
    "女性主持人": "presenter_female",
    # 青年男声
    "磁性男声 (俊朗男友)": "junlang_nanyou",
    "青涩青年": "male-qn-qingse",
    "精英青年": "male-qn-jingying",
    "霸道青年": "male-qn-badao",
    "青年大学生": "male-qn-daxuesheng",
    # 青年女声
    "温柔女声 (淡雅学姐)": "danya_xuejie",
    "活力女声 (少女音-beta)": "female-shaonv-jingpin",
    "成熟女声": "female-chengshu",
    "少女音": "female-shaonv",
    "御姐音": "female-yujie",
    "甜美女性": "female-tianmei",
    # 剧情与角色
    "病娇弟弟": "bingjiao_didi",
    "纯真学弟": "chunzhen_xuedi",
    "冷淡学长": "lengdan_xiongzhang",
    "霸道少爷": "badao_shaoye",
    "甜心小玲": "tianxin_xiaoling",
    "俏皮萌妹": "qiaopi_mengmei",
    "妩媚御姐": "wumei_yujie",
    "嗲嗲学妹": "diadia_xuemei",
    # Beta精品音色
    "青涩青年-beta": "male-qn-qingse-jingpin",
    "精英青年-beta": "male-qn-jingying-jingpin",
    "霸道青年-beta": "male-qn-badao-jingpin",
    "青年大学生-beta": "male-qn-daxuesheng-jingpin",
    "御姐音-beta": "female-yujie-jingpin",
    "成熟女性-beta": "female-chengshu-jingpin",
    "甜美女性-beta": "female-tianmei-jingpin",
    # 有声书
    "男性有声书1": "audiobook_male_1",
    "男性有声书2": "audiobook_male_2",
    "女性有声书1": "audiobook_female_1",
    "女性有声书2": "audiobook_female_2",
    # 童声
    "聪明男童": "clever_boy",
    "可爱男童": "cute_boy",
    "萌萌女童": "lovely_girl",
    "卡通猪小琪": "cartoon_pig",
    # 英文与节日
    "Santa Claus": "Santa_Claus",
    "Grinch": "Grinch",
    "Rudolph": "Rudolph",
    "Arnold": "Arnold",
    "Charming Santa": "Charming_Santa",
    "Charming Lady": "Charming_Lady",
    "Sweet Girl": "Sweet_Girl",
    "Cute Elf": "Cute_Elf",
    "Attractive Girl": "Attractive_Girl",
    "Serene Woman": "Serene_Woman"
}

TARGET_LANGUAGES = {
    "自动检测": "auto",
    "中文 (普通话)": "Chinese",
    "中文 (粤语)": "Chinese,Yue",
    "英语": "English",
    "阿拉伯语": "Arabic",
    "俄语": "Russian",
    "西班牙语": "Spanish",
    "法语": "French",
    "葡萄牙语": "Portuguese",
    "德语": "German",
    "土耳其语": "Turkish",
    "荷兰语": "Dutch",
    "乌克兰语": "Ukrainian",
    "越南语": "Vietnamese",
    "印尼语": "Indonesian",
    "日语": "Japanese",
    "意大利语": "Italian",
    "韩语": "Korean",
    "泰语": "Thai",
    "波兰语": "Polish",
    "罗马尼亚语": "Romanian",
    "希腊语": "Greek",
    "捷克语": "Czech",
    "芬兰语": "Finnish",
    "印地语": "Hindi"
}

LIPSYNC_API_URL = "http://192.168.88.57:7860"

# --- 路径定义 ---
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp_files"
STATIC_RESULTS_DIR = BASE_DIR / "static_results"
FFMPEG_DIR = BASE_DIR / "ffmpeg-7.1.1-essentials_build"

# --- Pydantic 模型，用于请求体验证 ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TTSRequest(BaseModel):
    text: str
    voice: str
    speed: float
    language: str

class LipsyncRequest(BaseModel):
    video_path: str
    audio_path: str
    guidance_scale: float
    inference_steps: int
    seed: int


# --- 核心业务逻辑函数 (将 gr.Error 改为 HTTPException) ---

def extract_audio_from_video(video_path: str) -> str:
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="视频文件路径无效或文件不存在！")
    try:
        ffmpeg_exe_path = FFMPEG_DIR / "bin" / "ffmpeg.exe"
        if not ffmpeg_exe_path.exists():
            raise FileNotFoundError(f"FFmpeg executable not found at: {ffmpeg_exe_path}")
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"无法构造FFmpeg路径: {e}")

    output_audio_path = TEMP_DIR / f"{Path(video_path).stem}_{uuid.uuid4().hex[:6]}.mp3"
    command = [ str(ffmpeg_exe_path), '-i', video_path, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', '-y', str(output_audio_path) ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        if not output_audio_path.exists():
             raise Exception("FFmpeg 执行完毕但未生成目标音频文件。")
        print(f"音频提取成功，已保存至: {output_audio_path}")
        return str(output_audio_path)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"使用 FFmpeg 处理视频文件时出错: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理视频文件时发生未知错误: {str(e)}")

def call_stt_api(audio_path: str) -> str:
    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(status_code=400, detail="音频文件路径无效或文件不存在")
    print(f"调用STT API (硅基流动) 处理文件: {audio_path}")
    API_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
    MODEL_NAME = "FunAudioLLM/SenseVoiceSmall"
    headers = {"Authorization": f"Bearer {STT_API_KEY}"}
    payload_data = {'model': MODEL_NAME, 'language': 'zh'}
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {'file': (os.path.basename(audio_path), audio_file)}
            response = requests.post(API_URL, headers=headers, data=payload_data, files=files, timeout=120)
            response.raise_for_status()
        result_text = response.json().get("text", "")
        return result_text
    except requests.exceptions.RequestException as e:
        error_content = e.response.text if e.response else "No response"
        raise HTTPException(status_code=502, detail=f"语音识别API请求失败: {error_content}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理音频时发生内部错误: {str(e)}")

def call_translation_api(text: str, target_language_name: str) -> str:
    if not text or text.strip() == "":
        return ""
    print(f"调用翻译API (Qwen模型) 翻译文本: {text}")
    API_URL = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {STT_API_KEY}", "Content-Type": "application/json"}
    system_prompt = f"你是一个专业的翻译引擎。将输入的文本翻译成语句通顺准确地{target_language_name}，只输出翻译后的{target_language_name}内容，不添加任何解释或注释。/no_think"
    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
        "stream": False, "max_tokens": 2048, "temperature": 0.1, "top_p": 0.7,
        "frequency_penalty": 0.5, "response_format": {"type": "text"}
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result_json = response.json()
        translated_text = result_json["choices"][0]["message"]["content"]
        return translated_text.strip()
    except requests.exceptions.RequestException as e:
        error_content = e.response.text if e.response else "No response"
        raise HTTPException(status_code=502, detail=f"翻译API请求失败: {error_content}")
    except (KeyError, IndexError):
        raise HTTPException(status_code=500, detail="无法从API响应中解析翻译结果。")

def call_tts_api(text: str, selected_voice_name: str, speed: float, target_language_name: str) -> str:
    if not text or text.strip() == "":
        raise HTTPException(status_code=400, detail="没有文本可以转换为语音。")
    if not target_language_name:
        raise HTTPException(status_code=400, detail="请先选择一个目标语言。")
    
    voice_id = MINIMAX_VOICES.get(selected_voice_name, "presenter_male")
    tts_code = TARGET_LANGUAGES.get(target_language_name)
    if not tts_code:
        raise HTTPException(status_code=400, detail=f"为语言 '{target_language_name}' 找到了无效的TTS配置。")
    
    print(f"调用 Minimax TTS API，语言: {tts_code}, 音色: {voice_id}, 语速: {speed}")
    url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={MINIMAX_GROUP_ID}"
    headers = {"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "speech-02-hd", "text": text,
        "voice_setting": {"voice_id": voice_id, "speed": speed},
        "audio_setting": {"format": "mp3"},
        "language_boost": tts_code
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result_json = response.json()
        # print(f"DEBUG: Minimax API 响应内容: {result_json}")
        if result_json.get("base_resp", {}).get("status_code") != 0:
            error_msg = result_json.get("base_resp", {}).get("status_msg", "未知错误")
            raise HTTPException(status_code=502, detail=f"Minimax API 错误: {error_msg}")
        hex_audio_data = result_json.get('data', {}).get('audio')
        if not hex_audio_data:
            raise HTTPException(status_code=500, detail=f"Minimax API 未在响应中返回音频数据。")
        
        binary_audio_data = bytes.fromhex(hex_audio_data)
        output_path = TEMP_DIR / f"{uuid.uuid4()}.mp3"
        with open(output_path, 'wb') as audio_file:
            audio_file.write(binary_audio_data)
        print(f"TTS音频已保存到: {output_path}")
        return str(output_path)
    except requests.exceptions.RequestException as e:
        error_content = e.response.text if e.response else "No response"
        raise HTTPException(status_code=502, detail=f"语音合成请求失败: {error_content}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成时发生未知错误: {str(e)}")

def call_lipsync_api(original_video_path, generated_audio_path, guidance_scale, inference_steps, seed):
    if not original_video_path or not os.path.exists(original_video_path): 
        raise HTTPException(status_code=400, detail="错误：找不到用于口型同步的原始视频文件路径。")
    if not generated_audio_path or not os.path.exists(generated_audio_path): 
        raise HTTPException(status_code=400, detail="错误：找不到用于口型同步的生成音频文件路径。")

    print("将MP3转换为WAV以提高兼容性...")
    try:
        audio = AudioSegment.from_mp3(generated_audio_path)
        wav_path = TEMP_DIR / f"{uuid.uuid4()}.wav" # 已正确使用 pathlib
        audio.export(str(wav_path), format="wav") # pydub 需要字符串路径
        print(f"WAV文件已生成: {wav_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频格式转换失败: {str(e)}")

    print(f"开始调用口型同步API at {LIPSYNC_API_URL}...")
    try:
        client = Client(LIPSYNC_API_URL)
        result = client.predict(
            video_path={"video": handle_file(original_video_path)},
            audio_path=handle_file(wav_path),
            guidance_scale=guidance_scale,
            inference_steps=inference_steps,
            seed=seed,
            api_name="/process_video",
        )
        print("口型同步API调用成功，结果路径:", result)
        
        video_file_path = result.get('video')
        if not video_file_path:
            raise HTTPException(status_code=500, detail="口型同步API调用成功，但返回结果中没有找到视频文件。")
        return video_file_path
    except Exception as e:
        print(f"调用口型同步API时发生错误: {str(e)}")
        raise HTTPException(status_code=502, detail=f"调用口型同步服务失败: {str(e)}")


# --- FastAPI API Endpoints ---

@router.post("/upload-and-transcribe/", summary="上传视频并识别语音")
async def api_upload_and_transcribe(video_file: UploadFile = File(...)):
    temp_video_path = TEMP_DIR / f"{uuid.uuid4().hex}_{video_file.filename}"
    try:
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        audio_path = extract_audio_from_video(str(temp_video_path))
        transcribed_text = call_stt_api(audio_path)
        
        return {"transcribed_text": transcribed_text, "server_video_path": str(temp_video_path)} # 【优化】: 明确返回字符串
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传和转写过程中发生未知错误: {str(e)}")

@router.post("/translate/", summary="翻译文本")
async def api_translate(request: TranslationRequest):
    try:
        translated_text = call_translation_api(request.text, request.target_language)
        return {"translated_text": translated_text}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译过程中发生未知错误: {str(e)}")

@router.post("/synthesize-audio/", summary="合成语音")
async def api_synthesize_audio(request: TTSRequest):
    try:
        temp_audio_path_str = call_tts_api(request.text, request.voice, request.speed, request.language)
        
        temp_audio_path = Path(temp_audio_path_str)
        final_audio_path = STATIC_RESULTS_DIR / temp_audio_path.name
        shutil.move(temp_audio_path, final_audio_path)

        audio_url = f"/results/{final_audio_path.name}"
        return {"audio_url": audio_url, "server_audio_path": str(final_audio_path)}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成过程中发生未知错误: {str(e)}")

@router.post("/lipsync/", summary="进行口型同步")
async def api_lipsync(request: LipsyncRequest):
    try:
        temp_video_path = call_lipsync_api(
            request.video_path, 
            request.audio_path, 
            request.guidance_scale, 
            request.inference_steps, 
            request.seed
        )
        
        final_video_path = STATIC_RESULTS_DIR / Path(temp_video_path).name
        shutil.move(temp_video_path, final_video_path)
        
        video_url = f"/results/{final_video_path.name}"
        return {"final_video_url": video_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"口型同步过程中发生未知错误: {str(e)}")
    

@router.get("/config/", summary="获取前端需要的配置信息")
def get_config():
    """提供语言和音色列表给前端，让前端动态生成下拉框"""
    return {
        "voices": MINIMAX_VOICES,
        "languages": list(TARGET_LANGUAGES.keys()) # 前端只需要 key 的列表来生成选项
    }