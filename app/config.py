"""Cấu hình agent. Mọi thứ đọc từ biến môi trường để sau này đổi không phải sửa code."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

AGENT_ID = os.getenv("AGENT_ID", "travel-hanoi-agent")
GROUP_ID = os.getenv("GROUP_ID", "group-xx")          # TODO: thay bằng mã nhóm của bạn
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")
KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", str(BASE_DIR / "data" / "hanoi_places.json"))
