# Travel Agent Hà Nội - Phần 1 (M1 Build)

## Chạy
    python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
Mở http://localhost:8000/docs để thử API trên trình duyệt.

## Thử nhanh
    curl http://localhost:8000/health
    curl http://localhost:8000/.well-known/agent-card.json
    curl -X POST http://localhost:8000/v1/tasks -H "Content-Type: application/json" \
      -d '{"days":2,"travelers":2,"budget_vnd":1500000,"interests":["history","food"]}'

## Test
    pytest -q

## Đổi danh tính (biến môi trường)
    AGENT_ID=travel-hanoi-g07 GROUP_ID=g07 PUBLIC_URL=http://IP-may-ban:8000 uvicorn app.main:app --port 8000

    
## Tài liệu hướng dẫn
- [HUONG_DAN_TRIEN_KHAI.md](HUONG_DAN_TRIEN_KHAI.md): Bức tranh tổng thể 6 giai đoạn và lộ trình BTL môn Hệ thống phân tán.
- [README_TRIEN_KHAI_KHO_DU_LIEU.md](README_TRIEN_KHAI_KHO_DU_LIEU.md): Hướng dẫn chi tiết từng bước xây dựng và kiểm chứng kho dữ liệu (40-60 địa điểm).
- [README_TICH_HOP_LLM.md](README_TICH_HOP_LLM.md): Hướng dẫn tích hợp LLM (Gemini) với kho tri thức theo mô hình RAG (Input người dùng ➡️ Context ➡️ LLM).




## Cấu trúc file và thành phần kiến trúc
| File | Ô trong kiến trúc |
|---|---|
| `app/main.py` | Inbound API và log (nền cho Telemetry). Có `/health`, `/.well-known/agent-card.json`, `/v1/tasks` |
| `app/core/orchestrator.py` | Orchestrator, điều phối các domain service và xử lý vượt ngân sách |
| `app/domain/destination.py`, `itinerary.py`, `budget.py` | Ba domain service |
| `app/domain/knowledge_repo.py` + `data/hanoi_places.json` | Knowledge Repository |
| `app/config.py` | Identity (`AGENT_ID`, `GROUP_ID`, `PUBLIC_URL`), đọc từ biến môi trường |
| `scripts/validate_data.py`, `merge_drafts.py` | Công cụ kiểm tra và gộp kho dữ liệu |