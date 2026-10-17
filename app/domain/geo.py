import math


def distance_km(a: dict, b: dict) -> float:
    """Khoảng cách đường chim bay (haversine) giữa 2 địa điểm có lat/lon."""
    r = 6371.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dphi = p2 - p1
    dl = math.radians(b["lon"] - a["lon"])
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))
