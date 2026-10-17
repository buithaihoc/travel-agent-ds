from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    """Yêu cầu lập kế hoạch du lịch Hà Nội (Phần 1: dùng input có cấu trúc, chưa cần LLM)."""
    days: int = Field(1, ge=1, le=3, description="Số ngày (1-3)")
    travelers: int = Field(1, ge=1, le=20, description="Số người")
    budget_vnd: int | None = Field(None, ge=0, description="Ngân sách cả nhóm (VND), có thể bỏ trống")
    interests: list[str] = Field(default_factory=list, description="history, culture, museum, nature, food, shopping, ...")
