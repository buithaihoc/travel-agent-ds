"""Orchestrator (phiên bản Phần 1): chỉ điều phối các module nội bộ.

Phần 4-5 sẽ mở rộng để gọi thêm agent khác (Weather, Finance...) qua Peer client port.
"""
from app.domain import budget, destination, itinerary
from app.domain.knowledge_repo import KnowledgeRepository
from app.schemas import TaskRequest


def _slim(plan: list[dict]) -> list[dict]:
    return [
        {
            "day": d["day"],
            "total_minutes": d["total_minutes"],
            "stops": [
                {k: s[k] for k in ("id", "name", "area", "price_vnd", "duration_min", "summary")}
                for s in d["stops"]
            ],
        }
        for d in plan
    ]


def plan_trip(repo: KnowledgeRepository, req: TaskRequest) -> dict:
    candidates = destination.search(repo, req.interests)
    plan = itinerary.build(repo, candidates, req.days)
    cost = budget.estimate(repo, plan, req.travelers, req.budget_vnd)
    adjusted = False

    if cost["status"] == "over_budget":
        # Thử lại với ưu tiên địa điểm rẻ hơn (sort ổn định nên vẫn giữ thứ tự theo sở thích khi cùng giá)
        cheaper = sorted(candidates, key=lambda p: p["price_vnd"])
        plan2 = itinerary.build(repo, cheaper, req.days)
        cost2 = budget.estimate(repo, plan2, req.travelers, req.budget_vnd)
        if cost2["total_vnd"] < cost["total_vnd"]:
            plan, cost, adjusted = plan2, cost2, True

    return {
        "city": "Hà Nội",
        "knowledge_version": repo.version,
        "adjusted_for_budget": adjusted,
        "itinerary": _slim(plan),
        "cost": cost,
    }
