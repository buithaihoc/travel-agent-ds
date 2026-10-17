"""Gộp các file nháp data/drafts/*.json vào data/hanoi_places.json (có sao lưu trước khi ghi).

    python scripts/merge_drafts.py --dry-run     # chỉ báo sẽ thêm/bỏ qua gì, không ghi file
    python scripts/merge_drafts.py               # gộp thật (địa điểm trùng id sẽ bị bỏ qua)
    python scripts/merge_drafts.py --overwrite   # địa điểm trùng id: bản nháp ghi đè bản chính
"""
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "data" / "hanoi_places.json"
DRAFTS = ROOT / "data" / "drafts"
ARCHIVE = ROOT / "data" / "archive"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))  # chịu được file lưu có BOM


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    data = load(MAIN)
    by_id = {p["id"]: p for p in data["places"]}
    added, replaced, skipped = [], [], []

    for f in sorted(DRAFTS.glob("*.json")):
        items = load(f)
        if not isinstance(items, list):
            print(f"BỎ QUA {f.name}: nội dung phải là một mảng JSON dạng [ {{...}}, {{...}} ]")
            continue
        for p in items:
            pid = p.get("id")
            if not pid:
                print(f"BỎ QUA một thẻ trong {f.name}: thiếu id")
            elif pid in by_id and not args.overwrite:
                skipped.append(f"{pid} ({f.name})")
            elif pid in by_id:
                by_id[pid] = p
                replaced.append(pid)
            else:
                by_id[pid] = p
                added.append(pid)

    print(f"Thêm mới: {len(added)} | Ghi đè: {len(replaced)} | Bỏ qua do trùng id: {len(skipped)}")
    for s in skipped:
        print("  trùng id:", s)
    if args.dry_run:
        print("(dry-run: chưa ghi gì)")
        return

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    backup = ARCHIVE / f"hanoi_places_{datetime.now():%Y%m%d_%H%M%S}.json"
    shutil.copy2(MAIN, backup)
    data["places"] = list(by_id.values())
    MAIN.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã ghi {MAIN.name} ({len(data['places'])} địa điểm). Bản sao lưu: {backup.name}")
    print("Bước tiếp theo: python scripts/validate_data.py")


if __name__ == "__main__":
    main()
