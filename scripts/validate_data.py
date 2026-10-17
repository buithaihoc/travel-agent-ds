"""Kiểm tra chất lượng data/hanoi_places.json.

Cách dùng:
    python scripts/validate_data.py                  # kiểm tra thường: lỗi cấu trúc = ERROR, thiếu nguồn = WARN
    python scripts/validate_data.py --strict         # bản nộp: mọi cảnh báo về nguồn/kiểm chứng thành ERROR
    python scripts/validate_data.py path/to/file.json

Thoát với mã 1 nếu có ERROR (dùng được trong CI hoặc trước khi commit).
"""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.domain.geo import distance_km  # noqa: E402

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "hanoi_places.json"

TYPES = {"sight", "food", "experience"}
ALLOWED_TAGS = {"history", "culture", "museum", "architecture", "spiritual", "nature", "view",
                "food", "shopping", "craft", "nightlife", "family", "art"}
MEAL_SLOTS = {"breakfast", "lunch", "dinner", "snack"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RULE_KEYS = {"minutes_per_day", "travel_base_minutes", "travel_minutes_per_km",
             "other_meals_per_person_per_day_vnd", "transport_per_day_vnd"}
MIN_PLACES = 40
STALE_DAYS = 180
# Hà Nội mở rộng (ERROR nếu ngoài) và vùng nội thành + ven đô gần (WARN nếu ngoài)
HARD_BOX = (20.5, 21.5, 105.3, 106.2)
CORE_BOX = (20.90, 21.15, 105.70, 106.00)


class Report:
    def __init__(self, strict: bool):
        self.strict, self.errors, self.warnings = strict, [], []

    def err(self, pid, msg):
        self.errors.append(f"[{pid}] {msg}")

    def warn(self, pid, msg):  # cảnh báo về nguồn/kiểm chứng -> lỗi khi --strict
        (self.errors if self.strict else self.warnings).append(f"[{pid}] {msg}")

    def note(self, pid, msg):  # luôn chỉ là cảnh báo
        self.warnings.append(f"[{pid}] {msg}")


def in_box(p, box):
    return box[0] <= p["lat"] <= box[1] and box[2] <= p["lon"] <= box[3]


def check_place(p, r: Report, today: date):
    pid = p.get("id", "<thiếu id>")
    for key in ("id", "name", "type", "area", "tags", "price_vnd", "duration_min", "lat", "lon", "summary"):
        if key not in p:
            r.err(pid, f"thiếu trường bắt buộc '{key}'")
    if "id" in p and not SLUG.match(str(p["id"])):
        r.err(pid, "id phải là slug chữ thường-không-dấu, ví dụ 'van-mieu'")
    if p.get("type") not in TYPES:
        r.err(pid, f"type phải thuộc {sorted(TYPES)}")
    tags = p.get("tags")
    if not isinstance(tags, list) or not tags:
        r.err(pid, "tags phải là danh sách không rỗng")
    else:
        unknown = set(tags) - ALLOWED_TAGS
        if unknown:
            r.note(pid, f"tag lạ {sorted(unknown)} (không nằm trong danh sách chuẩn)")
    if not isinstance(p.get("price_vnd"), int) or p.get("price_vnd", -1) < 0:
        r.err(pid, "price_vnd phải là số nguyên >= 0")
    d = p.get("duration_min")
    if not isinstance(d, int) or not 15 <= d <= 300:
        r.err(pid, "duration_min phải là số nguyên trong khoảng 15-300")
    if isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lon"), (int, float)):
        if not in_box(p, HARD_BOX):
            r.err(pid, "tọa độ nằm ngoài Hà Nội, có thể nhầm lat/lon")
        elif not in_box(p, CORE_BOX):
            r.note(pid, "tọa độ ngoài vùng nội thành + ven đô gần, cần ghi lý do trong price_note/summary")
    else:
        r.err(pid, "lat/lon phải là số")
    if len(str(p.get("summary", ""))) < 20:
        r.err(pid, "summary quá ngắn (>= 20 ký tự)")

    # Trường mở rộng cho kiểm chứng
    if "opening_hours" not in p:
        r.warn(pid, "thiếu opening_hours")
    if "indoor" not in p:
        r.warn(pid, "thiếu indoor (true/false) - cần cho Weather Agent ở Phần 5")
    elif not isinstance(p["indoor"], bool):
        r.err(pid, "indoor phải là true/false")
    if p.get("type") == "food" and p.get("meal_slot") not in MEAL_SLOTS:
        r.warn(pid, f"quán ăn cần meal_slot thuộc {sorted(MEAL_SLOTS)}")
    srcs = p.get("sources")
    if not isinstance(srcs, list) or not srcs:
        r.warn(pid, "thiếu sources (cần >= 1 nguồn, giá và giờ mở cửa nên >= 2 nguồn độc lập)")
    else:
        for s in srcs:
            if not (isinstance(s, dict) and str(s.get("url", "")).startswith("http") and s.get("accessed")):
                r.err(pid, "mỗi source cần dạng {'url': 'http...', 'accessed': 'YYYY-MM-DD'}")
                break
        if len(srcs) < 2 and p.get("price_vnd", 0) > 0:
            r.warn(pid, "địa điểm có thu phí nên có >= 2 nguồn cho giá")
    va = p.get("verified_at")
    if not va or not p.get("verified_by"):
        r.warn(pid, "thiếu verified_at hoặc verified_by")
    else:
        try:
            age = (today - date.fromisoformat(va)).days
            if age > STALE_DAYS:
                r.warn(pid, f"verified_at đã {age} ngày, cần kiểm chứng lại")
        except ValueError:
            r.err(pid, "verified_at phải dạng YYYY-MM-DD")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=str(DEFAULT_PATH))
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    r, today = Report(args.strict), date.today()
    if not data.get("version"):
        r.err("root", "thiếu version")
    missing = RULE_KEYS - set(data.get("rules", {}))
    if missing:
        r.err("root", f"thiếu rules: {sorted(missing)}")

    places = data.get("places", [])
    ids = Counter(p.get("id") for p in places)
    for pid, n in ids.items():
        if n > 1:
            r.err(pid, f"id bị trùng {n} lần")
    for p in places:
        check_place(p, r, today)

    usable = [p for p in places if isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lon"), (int, float))]
    for i, a in enumerate(usable):
        for b in usable[i + 1:]:
            if a.get("id") != b.get("id") and distance_km(a, b) < 0.03:
                r.note(a.get("id"), f"cách '{b.get('id')}' dưới 30m, có thể trùng địa điểm")

    n = len(places)
    if n < MIN_PLACES:
        r.warn("root", f"mới có {n} địa điểm, mục tiêu tối thiểu {MIN_PLACES}")
    print(f"Tổng: {n} địa điểm | theo loại: {dict(Counter(p.get('type') for p in places))}")
    print(f"Theo khu vực: {dict(Counter(p.get('area') for p in places))}")
    print(f"Indoor: {sum(1 for p in places if p.get('indoor') is True)} | "
          f"Miễn phí hoặc <= 50.000đ: {sum(1 for p in places if isinstance(p.get('price_vnd'), int) and p['price_vnd'] <= 50000)} | "
          f"Đã có nguồn: {sum(1 for p in places if p.get('sources'))}")
    for w in r.warnings:
        print("WARN ", w)
    for e in r.errors:
        print("ERROR", e)
    print(f"\nKết quả: {len(r.errors)} lỗi, {len(r.warnings)} cảnh báo" + (" (chế độ strict)" if args.strict else ""))
    sys.exit(1 if r.errors else 0)


if __name__ == "__main__":
    main()
