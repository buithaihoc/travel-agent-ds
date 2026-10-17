"""Destination Service: tìm và xếp hạng địa điểm theo sở thích."""
from app.domain.knowledge_repo import KnowledgeRepository


def search(repo: KnowledgeRepository, interests: list[str]) -> list[dict]:
    wanted = set(interests)
    places = repo.all_places()
    if "food" not in wanted:           # chỉ đưa quán ăn vào lịch khi người dùng quan tâm ẩm thực
        places = [p for p in places if p["type"] != "food"]
    # Điểm = số tag trùng sở thích; sort ổn định nên các điểm bằng điểm giữ nguyên thứ tự trong dữ liệu
    return sorted(places, key=lambda p: -len(wanted & set(p["tags"])))
