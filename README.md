# Order Rescue: Prototype AI stack

Prototype demo cho Order Rescue. Agent được viết theo dạng **agent skills**: [AGENTS.md](AGENTS.md) mô tả agent và luồng xử lý, mỗi bước trong pipeline là một skill trong `skills/` (gồm `SKILL.md` mô tả + `skill.py` chứa code).

> Dữ liệu giả lập · Luật minh họa · Kết quả mô phỏng. Không kết nối Shopee/SPX.

## Chạy demo

Cần [uv](https://docs.astral.sh/uv/). Lệnh `uv` tự tải Python 3.12 và thư viện.

```bash
uv run --python 3.12 python -m runtime.cli demo           # chạy cả 5 tình huống
uv run --python 3.12 python -m runtime.cli demo CASE-03   # chạy 1 tình huống
uv run --python 3.12 --extra dev --extra api pytest -q    # chạy test
```

Mặc định chạy chế độ **REPLAY**: dùng output AI đã lưu sẵn, không cần mạng hay API key, nên an toàn khi trình diễn.

> ⚠️ Output trong `fixtures/replay/` hiện là **bản soạn tay** (`"source": "hand_authored_seed"`), không phải output thật của model. Muốn có output thật: chạy LIVE_AI với `ORDER_RESCUE_RECORD=1` để ghi đè.

```bash
OPENAI_API_KEY=sk-... ORDER_RESCUE_RECORD=1 \
  uv run --python 3.12 --extra live python -m runtime.cli demo --mode LIVE_AI
```

## Nối với UI

```bash
uv run --python 3.12 --extra api uvicorn runtime.api:app --reload
```

| Nút trên UI | API |
|---|---|
| Chọn tình huống | `POST /runs {"case_id": "CASE-01"}` |
| Áp dụng sự kiện (trả lời, hết ngập…) | `POST /runs/{run_id}/events {"event_id": "C01-E02"}` |
| Tua thời gian | `POST /runs/{run_id}/advance {"minutes": 150}` |
| Xem lịch sử quyết định | `GET /runs/{run_id}` |
| Danh sách tình huống + sự kiện | `GET /cases` |

## 5 tình huống

| Case | Thao tác | Kết quả |
|---|---|---|
| CASE-01 Người mua đi làm | Áp dụng `C01-E02` (trả lời) | Hỏi xác nhận → giao lại |
| CASE-02 Không trả lời | Tua 150 phút | Hỏi → hết giờ → chuyển người xử lý (không coi là từ chối) |
| CASE-03 Địa chỉ không rõ | Áp dụng `C03-E03` (đổi địa chỉ) | Hỏi mốc → đổi địa chỉ **bị chặn** |
| CASE-04 Mưa ngập | Áp dụng `C04-E02` (hết ngập) | Tạm giữ → giao lại |
| CASE-05 "Từ chối" không bằng chứng | Chỉ cần mở case | Chuyển người xem xét, không tự hoàn hàng |

## Cấu trúc

```
AGENTS.md                 luật và luồng của agent
runtime/                  pipeline runner, simulator (đồng hồ ảo), CLI, API
skills/<tên>/             7 skill: SKILL.md + skill.py
fixtures/scenarios/       5 case giả lập
fixtures/policies/        luật minh họa demo-v1
fixtures/replay/          output AI đã lưu (REPLAY)
fixtures/expected/        kết quả mong đợi (chỉ dùng cho test, không gửi cho model)
tests/                    25 test
```
