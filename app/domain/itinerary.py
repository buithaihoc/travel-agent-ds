"""Itinerary Service: gom địa điểm thành lịch trình từng ngày.

Thuật toán đơn giản (đủ cho Phần 1): mỗi ngày bắt đầu từ địa điểm điểm cao nhất còn lại,
rồi chọn tiếp địa điểm gần nhất cho tới khi hết quỹ thời gian trong ngày.
"""
from app.domain.geo import distance_km
from app.domain.knowledge_repo import KnowledgeRepository


def travel_minutes(repo: KnowledgeRepository, a: dict, b: dict) -> int:
    r = repo.rules
    return round(r["travel_base_minutes"] + distance_km(a, b) * r["travel_minutes_per_km"])


def build(repo: KnowledgeRepository, candidates: list[dict], days: int) -> list[dict]:
    max_minutes = repo.rules["minutes_per_day"]
    remaining = list(candidates[: days * 5])
    plan = []
    for day in range(1, days + 1):
        if not remaining:
            break
        first = remaining.pop(0)
        stops, used = [first], first["duration_min"]
        while remaining:
            nxt = min(remaining, key=lambda p: distance_km(stops[-1], p))
            cost = travel_minutes(repo, stops[-1], nxt) + nxt["duration_min"]
            if used + cost > max_minutes:
                break
            remaining.remove(nxt)
            stops.append(nxt)
            used += cost
        plan.append({"day": day, "stops": stops, "total_minutes": used})
    return plan
