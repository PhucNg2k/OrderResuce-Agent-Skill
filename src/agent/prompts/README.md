# Prompt tạo Recommendation (Order Rescue Assessment Agent) - v1

## Mục đích
`recommendation_system_prompt.md` là system prompt cho Agent đánh giá một ca giao hàng thất bại và trả về MỘT object JSON gồm sáu trường: `evidence`, `hypothesis`, `confidence`, `missing_info`, `question_key`, `candidate_action`. Agent chỉ ĐỀ XUẤT; Policy Engine của backend quyết định hành động cuối cùng. `assessment.schema.json` là JSON Schema để backend kiểm tra đầu ra (`additionalProperties: false`, các enum đã duyệt).

## Đầu vào
Backend gửi `core_input` (failed_event, attempts_used, return_state, deadline, buyer_history, operational_context gồm route/payment/source_refs, tùy chọn buyer_messages_t0, address_validation, disruption) và `runtime_context` (các tương tác đã được phát hành), kèm source registry nếu có. KHÔNG đưa expected/golden của bộ test vào input.

Lưu ý: object `disruption` cần được serialize đúng các khóa `verification`, `status` (ACTIVE), `route_match`, `time_match`, `reassess_required` như prompt mô tả.

## Dùng ở stage 1 và stage 2
- Stage 1: `runtime_context` rỗng (chưa có `BUYER_REPLY`). Agent trả đánh giá đầy đủ; thường là `CLARIFY`, hoặc `HOLD_DISRUPTION` / `ESCALATE_REVIEW` nếu bảng quyết định yêu cầu.
- Stage 2: có `BUYER_REPLY` cho `AI_QUESTION`. Agent trả lại đánh giá ĐẦY ĐỦ (không phải diff), giữ `question_key` đã hỏi, không bao giờ `CLARIFY`. Reply không có nội dung, từ chối, hoặc yêu cầu ngoài MVP đều ra `ESCALATE_REVIEW`.
- `USER_NO_REPLY` do backend xử lý, không gọi Agent.
- Viết nội dung câu hỏi là một lời gọi riêng (prompt có hướng dẫn ngắn ở mục 10).

## Cách đánh giá
1. Validate đầu ra bằng `assessment.schema.json`; từ chối và retry nếu sai enum hoặc thừa khóa.
2. Chạy 30 test case của Hải ở cả hai stage; so sánh `hypothesis`, `confidence`, `missing_info`, `question_key`, `candidate_action` với bản golden (chỉ ở phía chấm điểm, không đưa vào prompt).
3. Kiểm tra riêng: `source_ref` có tồn tại trong input; `verification` đúng provenance; HIGH có nguồn trực tiếp hoặc Ops đã xác minh; không có CLARIFY ở stage 2; không có STANDARD_REATTEMPT khi còn missing_info chặn.
4. Chạy các case kiểm tra prompt injection và ghi chú mơ hồ ("giờ cao điểm") để đảm bảo cùng nhãn UNKNOWN_CAUSE/LOW.

## Giới hạn đã biết
- Một số quy tắc là diễn giải của team, chưa được ghi rõ trong PDF: stage 1 chỉ còn `LOGISTICS_VERIFICATION` thì `ESCALATE_REVIEW`; xung đột payment thì `ESCALATE_REVIEW`; case lifecycle không đủ điều kiện nhưng vẫn lọt vào thì `ESCALATE_REVIEW`.
- Ranh giới "cụ thể" và "mơ hồ" cho `LOGISTICS_ISSUE` (D1) là diễn giải; cần xác nhận với Hải.
- `NO_ACTION` chỉ dành cho trigger trùng/cũ do backend gắn cờ, nằm ngoài 30 case.
- Prompt dài; ví dụ chỉ có 3 ca tổng hợp để tránh model sao chép. Cần đo độ ổn định giữa nhiều lần chạy.
- Prompt chưa được chạy với model thật; chưa có số liệu độ chính xác.

## v2 changes
Prompt nâng từ v1 lên v2 (chỉnh theo các nhóm lỗi chung, không gắn với case cụ thể):
- `missing_info` là checklist các mục chưa giải quyết: chỉ bỏ mã khi có nguồn giải quyết đúng mã đó; `CURRENT_BUYER_INTENT` giữ đến khi có DIRECT_BUYER_STATEMENT; reply chỉ giải quyết các mã nó trả lời (đổi/giao sang địa chỉ khác chỉ giải quyết intent); không thay mã khác khi chưa có bằng chứng mới.
- Thêm bảng ánh xạ status sang hypothesis (contact failure -> CONTACT_ISSUE, refusal/not ready -> BUYER_INTENT_ISSUE, ...) ở LOW/MEDIUM; `UNKNOWN_CAUSE` chỉ khi không có họ nguyên nhân nào hoặc từ hai họ ngang nhau; có tie-break một họ duy nhất.
- Stage 2 bắt đầu từ đánh giá trước: hypothesis/confidence chỉ đổi khi reply có fact mới về nguyên nhân; "không biết" hoặc chỉ nêu intent không làm giảm confidence.
- `question_key` ở stage 2 sao chép nguyên từ câu hỏi stage 1, không sinh mới.
- Evidence ở stage 2 = toàn bộ evidence cũ + đúng một item cho reply; mọi reply (kể cả emoji/mơ hồ) được ghi dạng DIRECT_BUYER_STATEMENT (thay đổi so với v1, vốn không ghi reply không có nội dung).
- Nhãn verification theo nguồn: system record -> SOURCE_RECORD, `ops_signals` verified có provenance -> VERIFIED_OPS_SIGNAL, courier note -> UNVERIFIED_REPORT, tin nhắn buyer -> DIRECT_BUYER_STATEMENT.
- Confidence chỉ đo bằng chứng nguyên nhân: Ops verified khớp note -> HIGH; note cụ thể -> MEDIUM; chỉ status -> LOW; không bị hạ vì missing_info khác.
- Hình dạng đầu ra: mỗi evidence đúng ba khóa; chỉ thêm mã `missing_info` khi có bằng chứng liên quan (payment type đơn thuần không đủ cho `COD_READINESS`).
- Chưa chạy lại với model thật; cần đánh giá lại trên 30 case.
