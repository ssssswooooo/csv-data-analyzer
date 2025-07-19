#!/usr/bin/env python3
"""
CSV データ分析アプリの起動スクリプト
"""

import subprocess
import sys
import os

def main():
    """アプリケーションを起動する"""
    try:
        print("🚀 CSV データ分析アプリを起動しています...")
        print("📊 ブラウザで http://localhost:8501 にアクセスしてください")
        print("⏹️  停止するには Ctrl+C を押してください")
        print("-" * 50)

        # Streamlitアプリを起動
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)

    except KeyboardInterrupt:
        print("\n👋 アプリケーションを停止しました")
    except subprocess.CalledProcessError as e:
        print(f"❌ エラーが発生しました: {e}")
        print("💡 requirements.txt の依存関係がインストールされているか確認してください")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")

if __name__ == "__main__":
    main()