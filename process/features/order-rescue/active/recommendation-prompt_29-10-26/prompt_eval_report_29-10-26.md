# Báo cáo đánh giá prompt recommendation (v1 so với v2)

Ngày: 29-10-26 | Nhánh: feat/recommendation-prompt | Trạng thái: nháp, chờ Hải xác nhận golden label

## TL;DR

- v2 cải thiện rõ ở giai đoạn sau phản hồi: all_six 18/24 lên 21/24; hypothesis 22/30 lên 26/30 ở giai đoạn đầu.
- Nhưng v2 không tốt hơn ở mọi chỗ: ở giai đoạn đầu, confidence giảm 24 xuống 22, missing_info giảm 22 xuống 18, all_six giảm 15 xuống 14.
- Phần lớn lỗi còn lại là prompt_gap về confidence và CAUSE_CLARIFICATION. Một số lỗi đến từ golden label đáng ngờ (6 câu hỏi cho Hải bên dưới).
- Đây chỉ là mô phỏng bằng LLM trên 30 ca tổng hợp. Không phải bằng chứng về độ chính xác thực tế.

## 1. Phương pháp

- Bộ dữ liệu: 30 ca tổng hợp (DEMO-001 đến DEMO-030) từ `Order_Rescue_Test_Cases_30_v2.2.json`. Đây là golden label dạng NHÁP, chưa được Hải xác nhận.
- Mỗi ca chạy 2 giai đoạn:
  - Giai đoạn 1 (initial): 30 ca, model nhận prompt và đúng một file input của ca đó.
  - Giai đoạn 2 (after_reply): 24 ca có phản hồi của buyer, model nhận input gốc cộng phản hồi của buyer (không nhận kết quả giai đoạn 1).
- Giai đoạn 1 và 2 được mô phỏng bởi các agent độc lập. Mỗi agent chỉ thấy prompt và một file input. Không agent nào thấy golden label hay các ca khác.
- Chấm điểm: một agent chấm so sánh đầu ra với golden label NHÁP trên 6 trường: hypothesis, confidence, action, question_key, missing_info, evidence. `all_six` là số ca đúng cả 6 trường.
- Mỗi sai lệch được phân loại: `prompt_gap` (prompt thiếu hoặc mơ hồ), `fixture_questionable` (golden label đáng ngờ so với rules v2.2), `model_variance` (cả hai cách đọc đều hợp lý).
- Số ca "lost" (ca không có kết quả) ở cả v1 và v2: 0.

## 2. Kết quả v1 và v2

| Giai đoạn / trường | v1 | v2 | Thay đổi |
|---|---|---|---|
| **Initial (n=30)** | | | |
| hypothesis | 22 | 26 | +4 |
| confidence | 24 | 22 | -2 |
| action | 30 | 30 | 0 |
| question_key | 30 | 30 | 0 |
| missing_info | 22 | 18 | -4 |
| evidence | 29 | 29 | 0 |
| all_six | 15 | 14 | -1 |
| **After_reply (n=24)** | | | |
| hypothesis | 22 | 24 | +2 |
| confidence | 22 | 23 | +1 |
| action | 24 | 24 | 0 |
| question_key | 23 | 24 | +1 |
| missing_info | 23 | 23 | 0 |
| evidence | 22 | 23 | +1 |
| all_six | 18 | 21 | +3 |

Nhận xét:

- action và question_key gần như đã ổn ở cả hai bản.
- v2 sửa tốt việc rơi về UNKNOWN_CAUSE (hypothesis +4 ở initial) và việc giai đoạn 2 làm mất hoặc đổi hypothesis (24/24).
- Cái giá: ở giai đoạn đầu, v2 bỏ sót CAUSE_CLARIFICATION nhiều hơn và đánh confidence thấp hơn golden ở nhiều ca. Số liệu cho thấy có đánh đổi, không phải cải thiện đều.

## 3. Thay đổi giữa v1 và v2

Các bản vá rút ra từ phân tích lỗi v1 (nguyên nhân, ca bị ảnh hưởng, quy tắc chung):

1. **missing_info là checklist các mục chưa giải quyết**, không phải "điều model còn muốn hỏi". Chỉ bỏ một mã khi nguồn trong evidence hiện tại giải quyết rõ mã đó. CURRENT_BUYER_INTENT giữ lại đến khi có DIRECT_BUYER_STATEMENT về ý định nhận hàng. Phản hồi của buyer chỉ giải quyết đúng các mã nó trả lời. (DEMO-006, 009 initial/after_reply, 010)
2. **Ánh xạ trạng thái sang hypothesis**: một trạng thái chỉ về một họ nguyên nhân (liên hệ thất bại chung, buyer từ chối, chưa sẵn sàng nhận) cho hypothesis của họ đó ở LOW, hoặc MEDIUM nếu có ghi chú cụ thể chưa xác minh. UNKNOWN_CAUSE chỉ dùng khi không có gì chỉ về họ nào hoặc có từ hai họ ngang nhau. (DEMO-011, 013, 015, 016; DEMO-014 là cùng dạng nhưng xếp model_variance)
3. **Giai đoạn 2 xuất phát từ đánh giá trước**: chỉ đổi hypothesis khi có sự thật mới; phản hồi "không biết" hoặc chỉ nói về ý định không làm đổi hypothesis; confidence không giảm vì buyer thiếu thông tin. (DEMO-013, 025 after_reply)
4. **question_key sao chép nguyên văn** từ câu hỏi giai đoạn 1 ở các giai đoạn sau. (DEMO-002 after_reply)
5. **Evidence mang theo đầy đủ**: danh sách sau phản hồi = danh sách cũ + một mục cho phản hồi, luôn ghi là DIRECT_BUYER_STATEMENT, kể cả khi phản hồi chỉ là emoji hoặc mơ hồ. (DEMO-008, 030 after_reply)
6. **Ánh xạ verification theo loại nguồn**: bản ghi giao hàng của hệ thống là SOURCE_RECORD; ops_signals đã verified là VERIFIED_OPS_SIGNAL; ghi chú shipper là UNVERIFIED_REPORT; tin nhắn buyer là DIRECT_BUYER_STATEMENT. (DEMO-008)
7. **Confidence chỉ dựa trên bằng chứng nguyên nhân**: thiếu intent hoặc availability không hạ confidence; tín hiệu ops verified khớp ghi chú cho HIGH; ghi chú cụ thể cho MEDIUM; trạng thái trơ cho LOW. (DEMO-008, 018, 016)
8. **Giữ nguyên hình dạng đầu ra**: mỗi evidence item đúng 3 khóa source_ref, fact, verification; chỉ thêm mã missing_info khi có bằng chứng liên quan; loại thanh toán COD một mình không đủ để thêm COD_READINESS. (DEMO-015, 016, 027)

Lưu ý: dữ liệu đầu vào không cho biết chính xác bản vá nào vào v2 nguyên văn; bảng trên là danh sách bản vá được đề xuất từ phân tích v1.

## 4. Sai lệch còn lại của v2

### 4.1 prompt_gap (prompt cần sửa tiếp)

| Ca / giai đoạn | Trường | Kỳ vọng | Thực tế | Ghi chú |
|---|---|---|---|---|
| DEMO-004 initial | confidence | MEDIUM | LOW | Ghi chú cụ thể nhưng chưa xác minh phải là MEDIUM, không phải LOW |
| DEMO-007 initial | confidence | LOW | MEDIUM | Ghi chú mơ hồ không nâng confidence lên trên LOW |
| DEMO-007 initial | missing_info | có CAUSE_CLARIFICATION | thiếu | Hệ quả của lỗi confidence |
| DEMO-008 initial | confidence | HIGH | MEDIUM | Tín hiệu Ops address_validation đã VERIFIED bị đánh giá thấp |
| DEMO-008 initial, after_reply | evidence | VERIFIED_OPS_SIGNAL | SOURCE_RECORD | Gán nhãn sai cho mục ops_signals |
| DEMO-011 initial | missing_info | có CAUSE_CLARIFICATION | thiếu | Trạng thái chung, LOW, chưa có nguyên nhân |
| DEMO-012 initial | confidence | MEDIUM | LOW | Ghi chú nêu nguyên nhân cụ thể (mất sóng) dù có "nghi" |
| DEMO-013 initial, after_reply | missing_info | có CAUSE_CLARIFICATION | thiếu | Phản hồi chỉ giải quyết intent, không giải quyết nguyên nhân |
| DEMO-014 initial | missing_info | có CAUSE_CLARIFICATION | thiếu | Ghi chú không có thông tin nguyên nhân |
| DEMO-018 initial | missing_info | có RECEIVING_AVAILABILITY | thiếu | Rules: "Intent dương không tự đủ availability" |
| DEMO-025 initial | hypothesis, confidence | LOGISTICS_ISSUE, MEDIUM | UNKNOWN_CAUSE, LOW | Ghi chú báo tuyến tạm dừng; rules chưa nói rõ báo cáo chưa xác minh của shipper có tính là hypothesis |
| DEMO-025 initial | missing_info | không có CAUSE_CLARIFICATION | thừa | Hệ quả của lỗi hypothesis |
| DEMO-027 initial | missing_info | không có COD_READINESS | thừa | Không có bằng chứng thanh toán |

Mẫu chung: CAUSE_CLARIFICATION (4 ca) và ranh giới LOW/MEDIUM cho ghi chú shipper (4 ca) là hai lỗ hổng lớn nhất.

### 4.2 fixture_questionable (golden label đáng ngờ)

| Ca / giai đoạn | Trường | Golden | Model | Ghi chú |
|---|---|---|---|---|
| DEMO-009 initial | confidence | LOW | MEDIUM | Ghi chú "không tìm thấy lối vào" khá cụ thể; golden LOW chỉ hợp lý nếu coi ghi chú là mỏng |
| DEMO-009 after_reply | confidence | LOW | MEDIUM | Lỗi kế thừa từ giai đoạn 1 |
| DEMO-020 initial | hypothesis | PAYMENT_ISSUE | UNKNOWN_CAUSE | Chỉ có ghi chú mơ hồ "chưa rõ vì sao"; rules 5.2 nói COD một mình không phải bằng chứng |

### 4.3 model_variance (hai cách đọc đều hợp lý)

| Ca / giai đoạn | Trường | Golden | Model |
|---|---|---|---|
| DEMO-002 initial | missing_info | có CAUSE_CLARIFICATION | thiếu |
| DEMO-012 initial | missing_info | có CONTACT_CLARIFICATION | thiếu |
| DEMO-015 initial | missing_info | CURRENT_BUYER_INTENT, CAUSE_CLARIFICATION | CURRENT_BUYER_INTENT, RECEIVING_AVAILABILITY |
| DEMO-016 initial | confidence | MEDIUM | LOW |
| DEMO-016 initial | missing_info | có CAUSE_CLARIFICATION | thiếu |
| DEMO-020 initial | missing_info | có COD_READINESS | thiếu |
| DEMO-024 initial | hypothesis, confidence | LOGISTICS_ISSUE, MEDIUM | UNKNOWN_CAUSE, LOW |
| DEMO-027 initial | hypothesis | LOGISTICS_ISSUE | UNKNOWN_CAUSE |

Lưu ý về phân loại: phân tích prompt_gap và bộ câu hỏi fixture dùng cùng dữ liệu nhưng không hoàn toàn khớp phân loại của agent chấm. Ví dụ DEMO-007, 016, 024, 027 xuất hiện trong danh sách câu hỏi fixture dù agent chấm xếp prompt_gap hoặc model_variance. Phân loại là phán đoán của LLM, chưa được người kiểm.

## 5. Câu hỏi cho Hải về golden label đáng ngờ

1. **DEMO-020** (hypothesis, missing_info): golden là PAYMENT_ISSUE, nhưng bằng chứng nguyên nhân duy nhất là ghi chú mơ hồ "chưa bàn giao được đơn COD, chưa rõ vì sao" cộng DELIVERY_FAILED_OTHER. missing_info golden lại có CAUSE_CLARIFICATION, hàm ý nguyên nhân chưa chốt. Nên là UNKNOWN_CAUSE, hay có rule nào khiến PAYMENT_ISSUE đúng? (Rules 5.2: COD một mình không phải bằng chứng khó khăn thanh toán.)
2. **DEMO-024** (hypothesis, confidence): golden LOGISTICS_ISSUE ở MEDIUM, nhưng ghi chú chỉ nói đường đông và "chưa xác định trở ngại tại điểm nhận", không có tín hiệu hub, ngập hay quá tải. Nên là UNKNOWN_CAUSE ở LOW?
3. **DEMO-027** (hypothesis): golden LOGISTICS_ISSUE nhưng ghi chú chung chung, chưa xác minh (cùng dạng DEMO-024). DEMO-011/013/014 gán CONTACT_ISSUE cho trạng thái trơ. Vậy ghi chú chung chung ánh xạ về họ nguyên nhân hay về UNKNOWN_CAUSE?
4. **DEMO-007** (confidence): golden LOW; ghi chú nói shipper đến tòa nhà nhưng không tìm thấy điểm bàn giao. Rules 5.3 chưa nói đây có phải "cụ thể" cho ADDRESS_ISSUE. Xin định nghĩa ranh giới LOW/MEDIUM cho ghi chú về vị trí.
5. **DEMO-009** (confidence, cả hai giai đoạn): golden LOW. "Không tìm thấy lối vào" có thể là địa chỉ hoặc lối tiếp cận. LOW có chủ ý vì nguyên nhân mơ hồ? Nếu có, rules nên ghi rõ.
6. **DEMO-002** (missing_info): golden có CAUSE_CLARIFICATION cùng LOW và đoán chưa xác minh của shipper. Rules 5.4 nói chỉ liệt kê mã liên quan ca. CAUSE_CLARIFICATION có bắt buộc mỗi khi confidence LOW không? (Ví dụ DEMO-001 trong rules không có mã này.)
7. **DEMO-016** (hypothesis, confidence): golden BUYER_INTENT_ISSUE ở MEDIUM từ ghi chú chưa xác minh "buyer chưa đồng ý nhận". DEMO-015 (REFUSED trơ) cùng hypothesis nhưng LOW. Xác nhận ghi chú về ý định là thứ nâng lên MEDIUM, và khác với DEMO-018.

Câu hỏi chung: quy tắc CAUSE_CLARIFICATION bị golden áp dụng không đều giữa các ca (xuất hiện ở DEMO-002, 011, 013, 014, 016, 020; không ở DEMO-012, 025). Cần một quy tắc rõ ràng cho cả golden lẫn prompt.

## 6. Giới hạn trung thực

- **Mô phỏng bằng LLM**: cả người sinh đầu ra lẫn người chấm đều là LLM. Không có người dùng hay vận hành thật tham gia.
- **Cùng họ model với tác giả prompt**: có thể cùng thiên lệch diễn giải với người viết prompt, nên kết quả có thể lạc quan hơn so với model khác.
- **Bộ dữ liệu nhỏ và tổng hợp**: 30 ca (24 ca có phản hồi), mỗi ca là một mẫu. Chênh lệch 1 đến 4 ca nằm trong dao động ngẫu nhiên. Không có lặp lại để đo phương sai.
- **Không phải bằng chứng về độ chính xác thực tế**: không có dữ liệu Shopee/SPX thật.
- **Golden label là NHÁP**: chưa được Hải xác nhận; một số lỗi "còn lại" có thể là lỗi của golden (mục 4.2 và 5). Phân loại lỗi do LLM chấm, chưa được người kiểm.
- **Rủi ro overfit do bản vá**: các bản vá v2 được rút ra từ chính các ca dùng để đo, nhiều bản vá nêu đích danh ca. Cải thiện v2 có thể một phần là học thuộc 30 ca. Cần tập ca mới, chưa từng dùng để vá, để kiểm.
- **Đánh đổi chưa giải quyết**: v2 làm giảm confidence và missing_info ở giai đoạn đầu; cần xem lại trước khi coi v2 là tốt hơn tổng thể.

## 7. Bước tiếp theo đề xuất

1. Chờ Hải trả lời mục 5, rồi chấm lại với golden đã chốt.
2. Sửa prompt cho các prompt_gap còn lại: ghi chú cụ thể chưa xác minh là MEDIUM; CAUSE_CLARIFICATION khi dựa vào trạng thái trơ hoặc LOW; ops verified là VERIFIED_OPS_SIGNAL và HIGH; báo cáo shipper về logistics tính là hypothesis.
3. Viết 10 ca mới, không dùng để vá, làm tập kiểm độc lập; chạy lặp nhiều lần để ước lượng phương sai.

## 8. Chạy lại v3 sau khi Hải trả lời (29-10-26)

Thay đổi so với v2: định nghĩa `CONTACT_CLARIFICATION` (lỗi đường truyền) và rule D9 (PREPAID chỉ nâng confidence). Nhãn DEMO-020 lượt đầu đổi sang UNKNOWN_CAUSE theo Hải. Nhãn còn lại vẫn là nháp.

Khác phương pháp mục 1: 10 agent, mỗi agent chạy 3 ca và coi mỗi giai đoạn là độc lập (không phải mỗi ca một agent). Chấm bằng script, so khớp chính xác 5 trường (hypothesis, confidence, action, question_key, missing_info; bỏ evidence). Vì vậy số liệu **không so trực tiếp** được với bảng v1/v2.

| Trường | Initial (n=30) | After_reply (n=24) |
|---|---|---|
| hypothesis | 28 | 24 |
| confidence | 24 | 22 |
| action | 30 | 24 |
| question_key | 30 | 24 |
| missing_info | 25 | 24 |
| cả 5 trường | 20 | 22 |

Lệch còn lại (initial): confidence ở DEMO-004, 007, 008, 009, 016, 024; missing_info thiếu CAUSE_CLARIFICATION ở 002, 007, 015, 016 và thiếu COD_READINESS ở 020; hypothesis ở 024 và 027 (model ra UNKNOWN_CAUSE, nhãn là LOGISTICS_ISSUE). Sau reply lệch ở DEMO-004 và 009 (confidence).

Nhận xét: D9 chưa giúp DEMO-024 vì rule D1 (note chung chung) vẫn thắng. Muốn đạt nhãn của Hải thì cần ngoại lệ D1 rõ ràng cho 024. Kết quả chỉ là mô phỏng LLM.
