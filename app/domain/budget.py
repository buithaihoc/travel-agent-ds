"""Budget Service: ước tính và kiểm tra chi phí. Mọi giá là ước tính từ Knowledge Repository."""
from app.domain.knowledge_repo import KnowledgeRepository


def estimate(repo: KnowledgeRepository, plan: list[dict], travelers: int, budget_vnd: int | None) -> dict:
    r = repo.rules
    days = len(plan)
    tickets = sum(s["price_vnd"] for d in plan for s in d["stops"]) * travelers
    meals = r["other_meals_per_person_per_day_vnd"] * days * travelers
    transport = r["transport_per_day_vnd"] * days            # tính theo nhóm (taxi/xe công nghệ đi chung)
    total = tickets + meals + transport
    if budget_vnd is None:
        status, gap = "no_budget_given", 0
    elif total <= budget_vnd:
        status, gap = "within_budget", budget_vnd - total
    else:
        status, gap = "over_budget", total - budget_vnd
    return {
        "tickets_and_food_stops_vnd": tickets,
        "other_meals_vnd": meals,
        "transport_vnd": transport,
        "total_vnd": total,
        "status": status,
        "gap_vnd": gap,
    }
