"""
アプリケーション設定管理
環境変数から設定を読み込み、デフォルト値を提供
"""

import os
from typing import Optional


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """環境変数を取得する"""
    return os.getenv(key, default)

def get_env_bool(key: str, default: bool = False) -> bool:
    """環境変数をbooleanとして取得する"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int = 0) -> int:
    """環境変数をintegerとして取得する"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

# アプリケーション設定
APP_NAME = get_env_var("APP_NAME", "CSV Data Analyzer")
APP_VERSION = get_env_var("APP_VERSION", "0.1.0")
DEBUG = get_env_bool("DEBUG", False)

# ファイルアップロード設定
MAX_UPLOAD_SIZE_MB = get_env_int("MAX_UPLOAD_SIZE_MB", 200)
ALLOWED_FILE_TYPES = get_env_var("ALLOWED_FILE_TYPES", "csv,xlsx,json").split(",")

# 将来の機能拡張用設定
DATABASE_URL = get_env_var("DATABASE_URL")
API_KEY = get_env_var("API_KEY")
SECRET_KEY = get_env_var("SECRET_KEY")