"""Knowledge Repository: nguồn dữ liệu du lịch Hà Nội của riêng nhóm.

Hiện đọc từ file JSON. Sau này có thể đổi sang SQLite mà không ảnh hưởng nơi gọi,
miễn là giữ nguyên các method công khai.
"""
import json
from pathlib import Path


class KnowledgeRepository:
    def __init__(self, path: str):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.version: str = data["version"]
        self.rules: dict = data["rules"]
        self._places: list[dict] = data["places"]

    def all_places(self) -> list[dict]:
        return list(self._places)

    def get(self, place_id: str) -> dict | None:
        return next((p for p in self._places if p["id"] == place_id), None)
