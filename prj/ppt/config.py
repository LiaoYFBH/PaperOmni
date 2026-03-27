"""
Configuration module - loads OCR/LLM settings from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
print(f"[CONFIG] .env path: {env_path}, exists: {env_path.exists()}")
load_dotenv(env_path, override=True)

LLM_API_TOKEN = os.getenv("LLM_API_TOKEN", "").strip()
OCR_API_URL = os.getenv("OCR_API_URL", "").strip()
OCR_API_TOKEN = os.getenv("OCR_API_TOKEN", "").strip()
LLM_API_URL_CONFIG = os.getenv("LLM_API_URL", "https://aistudio.baidu.com/llm/lmapi/v3")
MODEL_NAME = os.getenv("MODEL_NAME", "ernie-4.5-turbo-128k-preview")
VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "ernie-4.5-turbo-vl")

print(f"[CONFIG] LLM_API_TOKEN loaded: {'YES' if LLM_API_TOKEN else 'EMPTY'}")

def get_ocr_config():
    return {
        "api_url": OCR_API_URL,
        "api_token": OCR_API_TOKEN,
    }

def get_llm_config():
    return {
        "api_url": LLM_API_URL_CONFIG,
        "api_token": LLM_API_TOKEN,
        "model_name": MODEL_NAME,
        "vision_model_name": VISION_MODEL_NAME,
    }
