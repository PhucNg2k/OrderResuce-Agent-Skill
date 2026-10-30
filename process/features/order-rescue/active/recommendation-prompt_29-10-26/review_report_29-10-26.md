# Báo cáo review Order Rescue v2.2 (workflow, enum, rule input -> recommendation)

Ngày: 29-10-26 | Người nhận: Lucas (PO), để gửi feedback cho Hải
Nguồn: Business Rules PDF v2.2, Test Cases 30 v2.2 (golden), Data Model v2.2.
Quy ước: mỗi finding được 2 reviewer độc lập kiểm tra lại. "Giữ lại" = không bị bác. "Bị bác" = reviewer thứ hai cho rằng PDF đã ghi đây là thiết kế có chủ đích hoặc nằm ngoài suite 30 case (xem mục 6, các điểm này vẫn đáng hỏi Hải nhưng độ ưu tiên thấp).

---

## 1. TL;DR

**Workflow: CONFIRM (luồng chính).** Luồng happy path nhất quán với data model và 30 case:
raw input -> pre-check -> assessment 1 -> lưu initial -> contact gate -> 1 câu hỏi -> WAITING_FOR_BUYER -> reply => assessment 2, hoặc USER_NO_REPLY thủ công => copy initial.
- 4 transition, max 1 câu hỏi, wait null, source=2 khi có reply, source=1 khi no-reply: khớp `runtime_contract` và `demo_policy_profile`.
- 30 case: `final_assessment_source` = 24 x 2 và 6 x 1 (005, 010, 014, 018, 022, 026), tất cả COMPLETED.

**Lưu ý trước khi code (không chặn confirm):** cả 30 case đều ở nhánh "sạch" (precheck ELIGIBLE, attempts_used=1, return NOT_STARTED, deadline có giá trị, gate PERMITTED/ESCALATED, không có BLOCKED). Nhánh pre-check chặn, contact gate từ chối, timeout, late reply không có state/test. PDF ghi các nhánh này là ngoài suite; chỉ cần team nói rõ đó là giới hạn demo có chủ đích.

**Enum: đủ cho 30 case, không cần ADD giá trị mới.** Chỉ 2/29 giá trị chưa xuất hiện (DELIVERY_ACCESS, NO_ACTION) cộng `question_key = null`. Vấn đề chính là định nghĩa/ranh giới, không phải thiếu giá trị.

**Rule input -> recommendation:** PDF 5.6 chỉ mô tả điều kiện bằng lời, không có bảng ưu tiên. Golden: `final_action` luôn bằng `candidate_action` (policy chưa từng override). 3 điểm golden đáng hỏi Hải nhất:
1. DEMO-024 vs DEMO-027: note mơ hồ ngang nhau nhưng confidence MEDIUM vs LOW.
2. DEMO-023/026: HOLD vs CLARIFY chưa có quy tắc ưu tiên.
3. DEMO-030 (emoji "👍"): được gán DIRECT_BUYER_STATEMENT, chưa có quy tắc reply không có thông tin.

---

## 2. Review workflow

| Hạng mục | Kết quả | Ghi chú |
|---|---|---|
| Happy path 4 transition | OK | Khớp data model |
| Max 1 câu hỏi, `reply_wait_duration_hours` null | OK | Nút NO_REPLY là điều khiển demo (PDF mục 2) |
| Final source 2 (reply) / 1 (no-reply) | OK | 24/6 trong 30 case |
| Guard `current_status='NEW'` ở 8.1 | OK | |
| Nhánh pre-check chặn | Chưa có state/test | Enum có `OPS_REVIEW` nhưng không transition nào tới nó; PDF: "Không gọi AI; chuyển Ops ngoài suite 30 case" |
| Contact gate từ chối | Chưa định nghĩa | Chỉ có event `PERMITTED_FIRST_QUESTION`; PDF 5.5 cho phép `question_key` null |
| Timeout / late reply / Agent 2 lỗi | Ngoài phạm vi | PDF mục cuối ghi rõ ngoài fixture |

Điểm giữ lại sau verify:
- `as_of` cố định 2026-10-24T15:00 cho cả 30 case, trong khi event reply có `occurred_at` null (gán lúc phát). PDF 4.4 lọc `occurred_at <= :as_of`, PDF 4.5 nói "cập nhật cutoff nếu clock thay đổi". Một reviewer thấy thiếu cơ chế tường minh, reviewer kia coi 4.4+4.5 đã đủ. **Khuyến nghị: hỏi Hải một câu xác nhận** (xem mục 5).
- Nhỏ: 4.4 yêu cầu khớp `question_id`, không khớp ngữ nghĩa, nên reply lạc đề vẫn kích hoạt assessment 2.

---

## 3. Review enum

Ký hiệu usage: [initial / after_reply / final] trên 30 / 24 / 30 assessment (6 case no-reply không có after_reply). Mặc định KEEP trừ khi ghi khác. "CLARIFY_DEF" = giữ giá trị, siết định nghĩa.

### 3.1 hypothesis (7 giá trị)

| Giá trị | Usage | Verdict | Lý do |
|---|---|---|---|
| AVAILABILITY_ISSUE | 5/6/7 | KEEP + CLARIFY_DEF | Nên ưu tiên hơn CONTACT khi buyer nói bận/vắng (DEMO-011) |
| ADDRESS_ISSUE | 5/6/7 | KEEP + CLARIFY_DEF | Làm rõ landmark trong địa chỉ đã đăng ký thì trong scope; đổi địa chỉ thì ESCALATE (DEMO-009) |
| CONTACT_ISSUE | 4/3/4 | KEEP + CLARIFY_DEF | Ranh giới yếu nhất; chỉ khi kênh liên lạc hỏng (sóng, SIM, sai số) |
| BUYER_INTENT_ISSUE | 4/2/3 | KEEP + CLARIFY_DEF | Gộp "từ chối" (015 -> ESCALATE) và "chưa biết có quà" (017 -> STANDARD_REATTEMPT); hành động phụ thuộc reply, không phụ thuộc hypothesis |
| PAYMENT_ISSUE | 4/4/5 | KEEP + CLARIFY_DEF | COD không phải evidence; DEMO-020 và 016/027 thay đổi hypothesis |
| LOGISTICS_ISSUE | 5/2/3 | KEEP | HIGH chỉ với VERIFIED_OPS_SIGNAL (023, 026); không tách weather vs capacity |
| UNKNOWN_CAUSE | 3/1/1 | KEEP | Fallback trung thực; luôn LOW, đi cùng CAUSE_CLARIFICATION |
| WRONG_RECIPIENT / CHANGED_MIND | - | không ADD | Chỉ 1 case (017), nằm trong BUYER_INTENT_ISSUE |
| DAMAGED_PARCEL / ADDRESS_CHANGE / WEATHER | - | không ADD | Đã có ESCALATE_REVIEW, `disruption.kind`, PDF 5.2 loại OUT_OF_SCOPE_REQUEST |

9/30 case đổi hypothesis sau reply (HYPOTHESIS_CHANGED: 002, 007, 011, 016, 020, 024, 027, 028, 029). PDF 5.2 chỉ có tie-break chung "chọn rào cản chính được evidence hỗ trợ tốt nhất"; thêm thứ tự ưu tiên trong prompt là tùy chọn (xem mục 6).

### 3.2 verification

| Giá trị | Usage | Verdict | Lý do |
|---|---|---|---|
| SOURCE_RECORD | 30/24/30 | KEEP | Provenance bắt buộc (1 dòng FAIL mỗi case) |
| UNVERIFIED_REPORT | 30/24/30 | KEEP | Note shipper; DEMO-026 ghi "Ops xác nhận" vẫn là UNVERIFIED (đúng PDF 5.1) |
| DIRECT_BUYER_STATEMENT | 3/27/27 | KEEP | Nguồn duy nhất nâng intent/availability lên HIGH |
| VERIFIED_OPS_SIGNAL | 3/2/3 | KEEP + CLARIFY_DEF | Nêu rõ áp dụng cho mọi key Ops có cấu trúc (DEMO-008 dùng cho address_validation) |

### 3.3 confidence

| Giá trị | Usage | Verdict | Lý do |
|---|---|---|---|
| HIGH | 6/19/20 | KEEP | HIGH không đồng nghĩa đủ điều kiện retry (PDF 5.3) |
| MEDIUM | 12/2/6 | KEEP | Mức giữa cho note cụ thể chưa xác minh |
| LOW | 12/3/4 | KEEP | 11/12 case LOW có CAUSE_CLARIFICATION |

### 3.4 missing_info (8 giá trị)

| Giá trị | Usage | Verdict | Lý do |
|---|---|---|---|
| CURRENT_BUYER_INTENT | 30/1/7 | KEEP | Gap mặc định ở T0 |
| RECEIVING_AVAILABILITY | 29/4/10 | KEEP | Gap mặc định (vắng ở 015 vì đã từ chối) |
| ADDRESS_CLARIFICATION | 5/1/2 | KEEP | Có question_key riêng (CLARIFY_LANDMARK) |
| CONTACT_CLARIFICATION | 1/0/0 | MERGE (đề xuất) | Chỉ 1 lần (DEMO-012); các case contact anh em (011, 013, 014) dùng CAUSE_CLARIFICATION. Merge vào CAUSE_CLARIFICATION hoặc thu hẹp thành "kênh liên lạc không dùng được" |
| COD_READINESS | 4/0/1 | KEEP | Nhất quán trên 019-022 |
| DELIVERY_ACCESS | 0/0/0 | MERGE hoặc giữ "reserved" (tùy chọn) | Chồng lấn ADDRESS_CLARIFICATION ("lối vào"); PDF coi đây là enum đã user xác nhận nên đây là câu hỏi cho Hải, không phải lỗi |
| LOGISTICS_VERIFICATION | 1/1/1 | KEEP + CLARIFY_DEF | Buyer không gỡ được cờ này (PDF 5.4); không nên kích hoạt câu hỏi cho buyer |
| CAUSE_CLARIFICATION | 13/2/3 | KEEP + CLARIFY_DEF | **Giữ lại sau verify.** Gần như hàm của LOW (11/12 case LOW + 016, 024); PDF 5.4 #8 cảnh báo không thay mã cụ thể nhưng không nói khi nào chọn #4 hay #8. Định nghĩa: "nhiều hypothesis ngang nhau, không nguồn nào tách được" |

### 3.5 question_key

| Giá trị | Usage | Verdict | Lý do |
|---|---|---|---|
| CONFIRM_INTENT | 25/20/25 | KEEP + CLARIFY_DEF | Catch-all (83% case), PDF định nghĩa có chủ đích là nhóm gộp |
| CLARIFY_LANDMARK | 5/4/5 | KEEP | Đúng 5 case ADDRESS (006-010) |
| null | 0/0/0 | KEEP + thêm test | Schema cho phép, chưa test; nên dùng cho case chỉ còn LOGISTICS_VERIFICATION (DEMO-025 hiện hỏi CONFIRM_INTENT) |

Đề xuất cho prompt: bảng ánh xạ cố định ADDRESS_CLARIFICATION -> CLARIFY_LANDMARK; chỉ-LOGISTICS_VERIFICATION -> null; còn lại -> CONFIRM_INTENT. Không thêm key mới (CONFIRM_PAYMENT là tùy chọn, 4 case).

### 3.6 candidate_action

| Giá trị | Usage | Verdict | Lý do |
|---|---|---|---|
| CLARIFY | 28/0/5 | KEEP | Ở final của no-reply nghĩa là "nhu cầu làm rõ chưa giải quyết" (PDF 5.6 #1) |
| STANDARD_REATTEMPT | 0/17/17 | KEEP | 17/24 case có reply |
| HOLD_DISRUPTION | 2/1/2 | KEEP | Chỉ với VERIFIED_OPS_SIGNAL |
| ESCALATE_REVIEW | 0/6/6 | KEEP | 004, 009, 013, 015, 025, 030 |
| NO_ACTION | 0/0/0 | KEEP trong dim_action, bỏ khỏi danh sách Agent được phát (đề xuất) | Dành cho backend bypass (duplicate/stale); PDF cấm dùng làm tên khác của no-reply. Validator mục 10 hiện chấp nhận nó như enum hợp lệ |

### 3.7 policy_gate / eligibility

ELIGIBLE 100%; PERMITTED hoặc ESCALATED (6 final: 004, 009, 013, 015, 025, 030); BLOCKED và INELIGIBLE/UNKNOWN = 0. Ghi "reserved, ngoài suite". Recommendation prompt chỉ phục vụ case ELIGIBLE.

---

## 4. Review rule input -> recommendation

### 4.1 Rule còn thiếu hoặc mơ hồ (giữ lại sau verify)

| # | Vấn đề | Case | Đề xuất |
|---|---|---|---|
| R1 | **HOLD vs CLARIFY chưa có thứ tự ưu tiên.** DEMO-023/026 có missing_info [CURRENT_BUYER_INTENT, RECEIVING_AVAILABILITY] nên cả CLARIFY (5.6 #1) và HOLD (5.6 #3) cùng kích hoạt; golden chọn HOLD và vẫn hỏi 1 câu. PDF đã nói reply không gỡ verified signal, nhưng chưa nói HOLD ưu tiên hơn CLARIFY, vẫn cho 1 câu hỏi, và khi nào HOLD kết thúc | 023, 026 | Ghi rõ "HOLD_DISRUPTION ưu tiên hơn CLARIFY và vẫn cho đúng 1 câu hỏi; HOLD kết thúc khi Ops reassess, không có vòng thứ ba tự động" |
| R2 | **Reply không có thông tin** (emoji, cảm ơn, lạc đề): "👍" được gán DIRECT_BUYER_STATEMENT; PDF không nói loại này có tính là evidence không. Confidence giữ nguyên nhưng không có quy tắc | 030 (và 004, 009, 013 về cách bỏ CURRENT_BUYER_INTENT) | Thêm "reply classes": trả lời intent / availability-nguyên nhân / ngoài MVP (đổi địa chỉ) / không thông tin (0 evidence mới) |
| R3 | **Label 024 vs 027 không nhất quán.** Cả hai là note logistics mơ hồ ("đường đông, chưa xác định trở ngại" vs "cao điểm, chưa hoàn tất") nhưng 024 = LOGISTICS_ISSUE/MEDIUM, 027 = LOGISTICS_ISSUE/LOW. PDF 5.3 chỉ cho MEDIUM khi có "chi tiết liên quan nguyên nhân từ báo cáo cụ thể"; 025 ("tuyến tạm ngừng") mới là MEDIUM đúng nghĩa | 024, 027, 025 | Đưa cả hai về cùng mức (LOW, hoặc UNKNOWN_CAUSE/LOW); giữ MEDIUM cho 025 |

### 4.2 Golden label trông không nhất quán nhưng reviewer bác (vẫn nên cho Hải xem)

| Case | Điểm lệch | Trạng thái |
|---|---|---|
| DEMO-020 | Initial = PAYMENT_ISSUE/LOW chỉ dựa trên note "chưa bàn giao được đơn COD, chưa rõ vì sao"; PDF 5.2: "COD tự nó không phải evidence" | Một reviewer đề xuất UNKNOWN_CAUSE/LOW, reviewer kia coi note có nhắc COD là đủ; case mô tả "Nghi COD; thực tế nhầm lối vào" có vẻ là bẫy có chủ đích. Hỏi Hải |
| DEMO-011/013/014 vs 028/029/030 | CONTACT_FAILED status-only -> CONTACT_ISSUE/LOW; DELIVERY_FAILED_OTHER mơ hồ -> UNKNOWN_CAUSE/LOW | PDF 5.2 ghi CONTACT_FAILED chung chung "thường LOW", nên khớp rule; ranh giới LOW vs UNKNOWN chỉ ngầm |
| DEMO-015 vs 017 | Cùng BUYER_INTENT_ISSUE/HIGH/missing=[] nhưng ESCALATE vs STANDARD_REATTEMPT | PDF 5.4 nói rõ "không còn missing_info không đồng nghĩa phải retry"; thiết kế có chủ đích |
| 005, 010, 014, 018, 022 | Final = CLARIFY/PERMITTED sau no-reply, dễ bị đọc là "được hỏi lần nữa" | PDF 5.6 #1 đã định nghĩa lại CLARIFY ở final là "chưa giải quyết"; nên đổi nhãn UI/reason cho dễ hiểu |

### 4.3 Khoảng trống rule ghi nhận (bị bác là lỗi, nhưng không có test)

- Không có bảng quyết định có thứ tự từ assessment -> candidate -> final (PDF 5.6: "không phải mapping cứng"; policy đọc `demo_policy_profile`).
- Confidence không có ngưỡng; không case nào test intent+availability xác nhận mà cause MEDIUM.
- Policy chưa từng override candidate (final_action = candidate_action ở 30/30).
- attempts / deadline / return_state: không có case, không rõ ngưỡng `>=3` hay `+1`.
- COD "liên quan" chưa định nghĩa; không case COD + hypothesis phi-payment + reply bỏ qua COD.

---

## 5. Câu hỏi cho Hải (theo thứ tự quan trọng)

1. **024 vs 027:** cùng loại note mơ hồ, tại sao MEDIUM vs LOW? Có đồng ý đưa về cùng mức không? (R3)
2. **HOLD vs CLARIFY:** xác nhận HOLD_DISRUPTION ưu tiên hơn CLARIFY và vẫn hỏi đúng 1 câu cho 023/026? Khi nào HOLD kết thúc? (R1)
3. **Reply không thông tin (👍):** có tính là DIRECT_BUYER_STATEMENT không? Quy tắc cho emoji / cảm ơn / lạc đề? (R2)
4. **CAUSE_CLARIFICATION vs CONTACT_CLARIFICATION:** khi nào dùng mã nào? Vì sao 011/013/014 dùng CAUSE còn 012 dùng CONTACT? Có merge CONTACT_CLARIFICATION không?
5. **DEMO-020:** có chủ ý PAYMENT_ISSUE chỉ từ note có chữ COD không, hay nên là UNKNOWN_CAUSE?
6. **as_of ở stage 2:** backend đặt `as_of` = thời điểm phát reply (hay so sánh theo phase/sequence) để query `occurred_at <= :as_of` không loại reply?
7. **Nhánh ngoài suite:** pre-check chặn và contact gate từ chối có kết thúc ở OPS_REVIEW không? Có cần thêm vài case ngoài 30 (return STARTED, deadline null, attempts hết, malformed input)?
8. **question_key null:** xác nhận dùng cho case chỉ còn LOGISTICS_VERIFICATION (DEMO-025)? Có thêm 1 test?
9. **DELIVERY_ACCESS:** giữ (reserved + thêm 1 case) hay merge vào ADDRESS_CLARIFICATION?
10. **NO_ACTION:** có đồng ý bỏ khỏi danh sách Agent được phát (backend-only)?
11. **Ngưỡng policy:** `attempts_used >= 3` hay `+1 >= 3`? "expired" so với `as_of` cố định hay giờ thật? COD "relevant" = `payment_type == COD`?
12. **Confidence:** có ngưỡng tối thiểu cho STANDARD_REATTEMPT không, hay confidence chỉ để hiển thị?

---

## 6. Finding bị bác khi verify (không giấu)

Lưu ý: hầu hết "bác" nghĩa là reviewer thứ hai tìm thấy PDF ghi đây là thiết kế có chủ đích hoặc ngoài suite, không phải finding sai về dữ kiện. Các dữ kiện được cả hai reviewer xác nhận.

- Workflow F1 (nhánh pre-check chặn không có state/test): PDF ghi "ngoài suite 30 case"; dữ kiện đúng, đã đưa vào câu hỏi 7.
- Workflow F2 (contact gate từ chối chưa định nghĩa): PDF 5.5 nói mọi case hiện có đều có câu hỏi, schema vẫn cho null; chuyển thành ghi chú ngoài suite.
- Workflow F3 (`occurred_at <= :as_of` mâu thuẫn): PDF 4.4+4.5 ngụ ý cutoff được cập nhật; vẫn đưa vào câu hỏi 6 vì hai reviewer bất đồng.
- Workflow F4 (idempotency / late reply / Agent 2 lỗi): PDF ghi "late reply sau COMPLETED" và timeout là ngoài fixture, cùng 8.3 kiểm tra affected rows = 1.
- Workflow F5 (no-reply final CLARIFY/PERMITTED không actionable): PDF 5.6 #1 đã định nghĩa lại; chỉ còn là vấn đề nhãn hiển thị (xem mục 4.2).
- Workflow F6 (không có timeout/SLA, judge sẽ hỏi): PDF cố ý dùng nút demo; vẫn nên chuẩn bị 1 slide trả lời production (đưa vào deck).
- Workflow F7 (ngưỡng attempts/deadline/return_state): PDF giao cho backend ngoài suite; ngưỡng chính xác vẫn chưa nêu (câu hỏi 11).
- Enum F1 (2 question_key cho 8 missing_info, CONFIRM_INTENT catch-all): PDF 5.5 định nghĩa có chủ đích; chỉ giữ đề xuất bảng ánh xạ + null.
- Enum F3 (DELIVERY_ACCESS chưa dùng, chồng lấn ADDRESS): enum đã user xác nhận, PDF 5.4 nói không liệt kê cả tám; còn lại là câu hỏi 9.
- Enum F4 (4 cặp hypothesis không loại trừ nhau): PDF 5.2 có tie-break chung và quy tắc chuyển cho 2 cặp; thêm precedence là cải tiến tùy chọn.
- Enum F5 (BUYER_INTENT_ISSUE gộp từ chối và chưa biết): PDF định nghĩa gộp có chủ đích.
- Enum F6 (NO_ACTION không bao giờ phát): PDF 5.6 #5 nêu đúng; chỉ còn lựa chọn cách viết prompt.
- Rules F1 (không có decision table): PDF cố ý "không phải mapping cứng", quyền quyết định cuối ở backend policy; vẫn là khoảng trống tài liệu.
- Rules F2 (confidence không có vai trò): PDF 5.3/5.4/7 nói confidence không thay evidence threshold; đề xuất ngưỡng tối thiểu mâu thuẫn thiết kế.
- Rules F3 (no-reply CLARIFY vs ESCALATE): PDF 5.6 #1 đã có câu định nghĩa lại.
- Rules F4 (DEMO-020): hai reviewer bất đồng, đã đưa vào mục 4.2.
- Rules F6 (LOW vs UNKNOWN_CAUSE): PDF 5.2 nói CONTACT_FAILED chung chung "thường LOW", golden khớp rule.
- Rules F8 (attempts/deadline/return_state): ngoài suite theo PDF; xem F7 workflow.
- Rules F10 (BUYER_INTENT_ISSUE polarity 015 vs 017): PDF 5.4 nêu đúng trường hợp này.
- Rules F11 (COD relevance): PDF cố ý để Agent đánh giá; đề xuất "COD luôn relevant" trái với 5.2.
- Enum/rules phụ (low severity), giữ làm ghi chú: BLOCKED/INELIGIBLE chưa xuất hiện; SOURCE_RECORD và UNVERIFIED_REPORT gần hằng số; CURRENT_BUYER_INTENT và RECEIVING_AVAILABILITY gần hằng số; "delivery information sufficient" chưa định nghĩa ngưỡng (DEMO-028 chấp nhận, DEMO-009 từ chối).

## 7. Ghi chú phương pháp

- Số đếm usage lấy từ reviewer, đã được voter đối chiếu với JSON golden. Một số voter ghi rõ chưa tự đếm lại cột "final" cho vài enum.
- File test case là golden để kiểm tra, không nên đưa vào prompt Agent (dùng bản paraphrase làm few-shot).


## 6. Hải trả lời (29-10-26) và tác động lên prompt

| Câu hỏi | Hải trả lời | Xử lý |
|---|---|---|
| 024 vs 027 | 024 là PREPAID, lý do không giao là đường đông, buyer chưa kịp nhận. 027 là COD (dễ bom hàng hơn). Hai kịch bản giống nhau nhưng khác trạng thái thanh toán, và note của 024 ghi rõ hơn. | Giữ nhãn khác nhau có chủ đích (024 MEDIUM, 027 LOW). **Xung đột với rule D1** trong prompt (note chung chung cùng xử lý như nhau). Cần quyết: thêm rule "note có nêu buyer chưa kịp nhận + PREPAID" hay bỏ D1 cho 024. Chưa sửa prompt. |
| 023/026 HOLD vs CLARIFY | Đúng, không reply thì HOLD. Thời gian hold theo policy Shopee Express. Hai case chỉ để demo chuyển trạng thái khi buyer không reply bằng nút trên UI. | Khớp row 1 của bảng action. HOLD kết thúc do Ops/policy, không do prompt. Không đổi prompt. |
| 030 (emoji) | ESCALATE_REVIEW. | Khớp row 5 (reply không thông tin). Không đổi prompt. |
| 020 | Đang là giả định PAYMENT_ISSUE. Sau reply sẽ đánh giá lại, nếu không có thì HOLD để escalated review. | Ghi nhận là giả định. Prompt hiện cho UNKNOWN_CAUSE, nên 020 vẫn lệch nhãn; cần Hải/Kha xác nhận có đổi nhãn sang UNKNOWN_CAUSE hay thêm rule. |
| CONTACT vs CAUSE | CONTACT là lỗi đường truyền: bắt máy nhưng không nghe rõ, không có mạng, tắt giữa chừng. Không liên lạc được trong điều kiện tốt thì là CAUSE. | Đã cập nhật định nghĩa CONTACT_CLARIFICATION trong prompt. |

Chưa trả lời: câu 6 đến 9 (as_of, nhánh ngoài suite, question_key null, DELIVERY_ACCESS), và 7 câu còn lại của mục 4.

### 6.1 Vòng trả lời thứ hai của Hải (29-10-26)

| # | Câu hỏi | Hải trả lời | Xử lý |
|---|---|---|---|
| 1 | 024 vs 027 | PREPAID là đã trả trước nên khả năng nhận hàng cao hơn, vì vậy hypothesis có confidence cao hơn. | Đã thêm rule D9 (payment type chỉ ảnh hưởng confidence). |
| 2 | DEMO-020 lượt đầu | PAYMENT_ISSUE chỉ là giả định, để UNKNOWN_CAUSE cũng được. | Đổi nhãn 020 lượt đầu sang UNKNOWN_CAUSE, khớp prompt. Cần Hải/Kha sửa file nhãn. |
| 3 | Hết hạn HOLD ở 023/026 | ESCALATE_REVIEW | Ghi nhận, nằm ngoài prompt (do Ops/backend). |
| 4 | 030: missing_info và confidence giữ nguyên | Đúng | Khớp row 5. |
| 5 | as_of ở lượt 2 | Đúng | Backend đặt as_of bằng thời điểm reply. |
| 6 | Case ngoài 30 | Không, phần đó chỉ để giám khảo biết (aware). | Không thêm case. |
| 7 | question_key null cho 025 | Hải chưa hiểu câu hỏi. | Chưa xác nhận, giữ mặc định null. |
| 8 | DELIVERY_ACCESS | Giữ enum. Khác ADDRESS_CLARIFICATION: ADDRESS là thiếu thông tin địa chỉ, DELIVERY_ACCESS là đủ thông tin nhưng shipper không biết đi. Khi missing_info là DELIVERY_ACCESS thì khả năng giao lại cao, không phải lỗi buyer. Trong hội thoại Hải cũng nói gộp hoặc bỏ cũng được. | Giữ enum. Thêm 1 case là việc của Hải nếu muốn. |

### 6.2 Họp nhóm 29-10-26: kết luận về 024/027 và 020

- **024 và 027:** Hải xác nhận cả hai note đều mơ hồ, khác nhau ở thanh toán (024 trả trước nên MEDIUM, 027 COD nên LOW). Lucas phản biện theo kinh nghiệm vận hành: shipper không tự hoàn đơn vì đường đông, hệ thống tự cập nhật thời gian dự kiến; chỉ khi có tác động từ phía buyer mới hoàn. Hai bên đồng ý nên bỏ nhóm case logistics mơ hồ này, giữ các case về payment và buyer. Chưa xóa khỏi file nhãn; việc đó thuộc Hải. Prompt không thêm ngoại lệ D1.
- **020:** Hải xác nhận PAYMENT_ISSUE chỉ là giả định, UNKNOWN_CAUSE chấp nhận được. Lucas đồng ý.
- **Dữ liệu 30 case:** giữ nguyên file hiện có, không tạo lại. Hải rà lại business rule và 30 case rồi gửi Kha.
