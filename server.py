"""
Local Production Server Launcher
區域產業 × 高教人才供需錯配預警系統 (System Spec v1.0)
Runs on http://127.0.0.1:8888
"""
import uvicorn
import socket

def find_available_port(preferred_port=8888):
    for port in [preferred_port, 8088, 8008, 9000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred_port

if __name__ == "__main__":
    port = find_available_port(8888)
    print("="*65)
    print("🚀 啟動本機端服務：區域產業 × 高教人才供需錯配預警系統 (v1.0)")
    print(f"👉 請開啟瀏覽器訪問: http://127.0.0.1:{port}")
    print(f"📖 API 交互文件: http://127.0.0.1:{port}/docs")
    print("="*65)
    uvicorn.run("api.main:app", host="127.0.0.1", port=port, log_level="info")
