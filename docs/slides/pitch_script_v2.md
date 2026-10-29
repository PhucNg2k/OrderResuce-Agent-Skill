# Order Rescue: kịch bản thuyết trình deck v2

Người trình bày: Lucas. Ngôn ngữ nói: tiếng Việt, giữ nguyên thuật ngữ tiếng Anh trên slide. Ngày: 31/10/2026.

## Cách dùng

- Có hai bản. **Bản 6 phút** đúng format của chương trình (6 phút pitch và demo, 2 phút Q&A). **Bản 9 đến 10 phút** dùng khi được cho thêm thời gian: thêm 3 slide backup, demo dài hơn, và kết quả mô phỏng prompt.
- Chữ trong khung `Nói:` là lời nói. Chữ `Thao tác:` là việc phải làm trên màn hình. Mốc giờ là thời gian cộng dồn.
- Mỗi slide có một câu **chốt**. Nếu bị trễ giờ, chỉ nói câu chốt rồi chuyển slide.
- Tiếng Việt nói khoảng 170 đến 180 âm tiết mỗi phút. Phần lời nói của bản 6 phút khoảng 800 âm tiết (khoảng 4 rưỡi phút); phần còn lại là thao tác demo và chuyển slide. Hãy bấm giờ khi tập một lần để chỉnh lại.

## Việc phải làm trước khi lên

- Chạy lại `npm run test:unit` ngay trước giờ trình bày và đọc con số mới. Ghi chú trong deck ghi 23 test trong 6 file (lần chạy 29/10).
- Chạy `npm run dev`, mở sẵn app ở tab riêng, chọn sẵn tình huống OR-SYN-001. Kiểm tra bấm được nút "Áp dụng phản hồi người mua đã chuẩn bị".
- **Cả nhóm xác nhận trước** slide 9 đúng sự thật: đã dùng Codex để làm ứng dụng demo, bộ test (Vitest và Playwright), và data model, business rule, 30 test case. Chỉ nói đúng ba phần này. Không mở rộng sang phần khác (ví dụ prompt, tài liệu kiến trúc, sơ đồ, deck) nếu nhóm không làm bằng Codex.
- **Cả nhóm thống nhất lời nói về luật hackathon:** sản phẩm phải build tại chỗ trong repo công khai mới, phần làm sẵn phải khai báo. Câu trả lời cho "hôm nay làm gì, trước đó có gì" phải khớp bản khai báo nộp lúc 17:00.
- Mở deck bằng PowerPoint một lần, xem slide 5 (nhãn xoay dọc) và slide 6 có tràn chữ không. Máy trình chiếu cần có font Georgia và Calibri.
- Chuẩn bị ảnh chụp màn hình bốn bước demo để dùng nếu app lỗi.
- **Hai chỗ trong deck cũ so với thực tế:** slide 13 ghi "Evaluation harness (not built yet)" và slide 15 chưa nhắc prompt đã viết. Hiện đã có prompt v2 và một đợt đánh giá mô phỏng bằng LLM. Nên sửa hai slide này, hoặc nói đúng bằng lời như trong bản 10 phút.

## Bản 6 phút

| Giờ | Slide | Việc |
|---|---|---|
| 0:00 | 1 | Mở đầu |
| 0:20 | 2 | Build direction |
| 0:35 | 3 | Vấn đề |
| 1:05 | 4 | Ưu tiên |
| 1:20 | 5 | Giải pháp: luồng hai assessment |
| 2:00 | 6 | Sáu trường đầu ra |
| 2:10 | 7 | Policy gate |
| 2:30 | 8 | Kiến trúc MVP |
| 2:45 | 9 | Dùng Codex |
| 3:15 | 10 | Demo trực tiếp |
| 5:30 | 11 | Giá trị và kết |
| 6:00 | | Hết giờ pitch, sang Q&A 2 phút |

### Slide 1: Order Rescue (0:00 đến 0:20)

Nói:
> Chào hội đồng. Chúng tôi là Lucas, Phúc, Hải và Kha. Sản phẩm của chúng tôi là Order Rescue: một lớp quyết định cho những đơn giao hàng thất bại ở lần giao đầu. Nó không tự hành động. Nó đề xuất cho Ops, kèm bằng chứng. Toàn bộ chạy trên dữ liệu giả lập và chúng tôi gắn nhãn rõ điều đó. Và nói thẳng ngay từ đầu: bản chạy hôm nay dùng bộ đánh giá theo luật thay cho LLM agent. Phần LLM là bước tiếp theo, chúng tôi đã viết sẵn hợp đồng dữ liệu và prompt cho nó.

Chốt: không tự hành động, dữ liệu giả lập, LLM là bước kế tiếp.

### Slide 2: Why this fits the build directions (0:20 đến 0:35)

Nói:
> Chúng tôi chọn hướng Autonomous và Adaptive AI: một agent đánh giá, hỏi một câu, rồi đánh giá lại, và luôn nằm trong giới hạn cứng. Hướng thứ hai là Deep Domain AI: luật nghiệp vụ lấy từ cách đội vận hành giao hàng thực sự suy nghĩ, ví dụ ghi chú của shipper chưa được xác minh, và im lặng không có nghĩa là từ chối.

Chốt: Autonomous và Adaptive là chính, Deep Domain là phụ.

### Slide 3: Problem (0:35 đến 1:05)

Nói:
> Khi lần giao đầu thất bại, Ops chỉ thấy một mã như "recipient unavailable" hoặc "refused". Chính hướng dẫn công khai của Shopee cũng nói trạng thái giao hàng có thể sai hoặc thiếu. Mã đó có thể là người mua đang đi làm, địa chỉ thiếu mốc, điện thoại mất sóng, hoặc tuyến bị gián đoạn. Giao lại mù thì phí một chuyến của shipper. Đóng đơn quá sớm thì mất đơn hàng. Và hiện không có bản ghi có cấu trúc nào cho biết vì sao Ops quyết định như vậy.

Chốt: một mã trạng thái không phải là nguyên nhân.

Nếu còn thời gian (bản 10 phút): chèn slide 12 ở đây.

### Slide 4: Priorities (1:05 đến 1:20)

Nói:
> Chúng tôi ưu tiên một quyết định đáng tin, không phải một tích hợp hào nhoáng. Trong phạm vi: đánh giá có bằng chứng, tối đa một câu hỏi cho người mua, policy gate xác định, và nhật ký kiểm toán. Ngoài phạm vi: mọi thứ chạm vào thế giới thật, như dữ liệu Shopee hay SPX, nhắn tin thật, điều phối shipper, đổi địa chỉ, hoàn tiền.

Chốt: tin cậy trước, tích hợp sau.

### Slide 5: The two-assessment flow (1:20 đến 2:00)

Thao tác: dùng con trỏ đi theo sơ đồ từ trái sang phải, nhanh.

Nói:
> Đây là luồng. Dữ liệu thô đi qua bước pre-check: ca hỏng dữ liệu hoặc đã đóng thì không bao giờ tới AI. Assessment 1 tạo ra bằng chứng và giả thuyết nguyên nhân. Nếu còn thiếu thông tin, backend cho phép đúng một câu hỏi cho người mua. Nếu người mua trả lời, chúng tôi chạy assessment 2. Nếu không trả lời, chúng tôi giữ assessment 1, và không coi im lặng là từ chối. Cuối cùng policy engine quyết định điều gì được phép, và Ops nhận khuyến nghị. Điểm mới là thiết kế có giới hạn: một câu hỏi, từ vựng cố định, LLM đề xuất, policy quyết định, Ops thực thi.

Chốt: LLM đề xuất, policy quyết định, Ops thực thi.

### Slide 6: Six fields (2:00 đến 2:10)

Nói:
> Agent trả về đúng sáu trường, và giá trị phải nằm trong danh sách đã duyệt: 7 giả thuyết nguyên nhân, 8 mã thông tin còn thiếu, 5 hành động đề xuất. Confidence đo mức độ bằng chứng ủng hộ giả thuyết, không phải khả năng giao thành công.

Chốt: sáu trường, từ vựng cố định.

### Slide 7: Policy gate (2:10 đến 2:30)

Nói:
> Đây là phần về niềm tin. Confidence cao không bao giờ ghi đè policy. Giao lại chỉ được đề xuất khi có ý định trực tiếp của người mua, có thời gian nhận hàng, và thông tin giao đủ. Mọi yêu cầu ngoài MVP, như đổi địa chỉ, bị chặn và chuyển lên người xem xét. Các kiểm tra này là code xác định, và chúng tôi có test cho nó.

Chốt: LLM không tự cấp quyền cho chính nó.

### Slide 8: MVP architecture (2:30 đến 2:45)

Nói:
> Hôm nay đây là ứng dụng React, Vite, TypeScript chạy cục bộ. Fixture thay cho kho dữ liệu, bộ đánh giá theo luật thay cho LLM agent, còn policy gate và nhật ký kiểm toán là code thật chạy cục bộ. Thiết kế đích có cùng ba lớp, dựa trên mô hình dữ liệu chín bảng.

Chốt: phần thật là policy gate, audit và test.

Nếu còn thời gian (bản 10 phút): chèn slide 13 và 14 ở đây.

### Slide 9: How we used Codex (2:45 đến 3:15)

Thao tác: mở nhanh cây thư mục repo (`src/`, `e2e/`, file data model và test case). Chỉ nói những gì cả nhóm đã xác nhận.

Nói:
> Về Codex: chúng tôi dùng Codex để làm ứng dụng demo cục bộ, gồm giao diện, bộ đánh giá, policy gate và nhật ký kiểm toán. Chúng tôi cũng dùng nó cho bộ test: một bộ Vitest với [đọc con số mới] test và một spec Playwright cho luồng demo. Và chúng tôi dùng nó để chuẩn bị data model, business rule và 30 test case giả lập. Bản thân LLM agent là bước tiếp theo.

Chốt: ba phần, nói thẳng, cho xem repo. Không nói về độ chính xác.

### Slide 10: Demo (3:15 đến 5:30, trực tiếp, 2 phút 15 giây)

Thao tác và lời nói theo thứ tự. Giao diện app bằng tiếng Việt, vì vậy dẫn thêm một câu tiếng Anh cho khách quốc tế.

1. **Nhãn minh bạch (15 giây).** Chỉ vào khung "Nhãn minh bạch".
   > Trước hết là ba nhãn: "Chạy thật cục bộ" là giao diện, bộ đánh giá, policy gate, nhật ký và test. "Mô phỏng" là đơn hàng, sự kiện, ghi chú, câu trả lời của người mua. "Tương lai, chưa xác minh" là dữ liệu Shopee hay SPX, nhắn tin, điều phối.
2. **Ca OR-SYN-001, người mua đang đi làm (40 giây).** Chọn sẵn ca này. Chỉ vào trạng thái "recipient unavailable" và ghi chú "lần giao diễn ra trong giờ làm việc".
   > Mã chỉ nói người nhận vắng mặt. Hệ thống nghi xung đột thời gian nhưng chưa chứng minh được, nên khuyến nghị chỉ là "Hỏi xác nhận từ người mua", một câu duy nhất. Nó không giao lại và không quy lỗi cho người mua.
3. **Áp dụng phản hồi (40 giây).** Bấm "Áp dụng phản hồi người mua đã chuẩn bị". Chỉ vào kết quả mới và nhật ký kiểm toán đã có hai mục.
   > Người mua mô phỏng xác nhận xung đột thời gian và đồng ý nhận lại. Khuyến nghị đổi thành "Đề xuất giao lại theo quy trình thường", confidence tăng. Cùng một mã trạng thái, hai khuyến nghị khác nhau vì bằng chứng khác nhau. Mỗi bước đều nằm trong nhật ký.
4. **Yêu cầu bị chặn (40 giây).** Chọn OR-SYN-003 (mốc nhận diện chưa rõ). Chỉ vào khối "Đã chặn cục bộ: Đổi địa chỉ nhận".
   > Ở ca này người mua cần làm rõ mốc nhận diện. Hệ thống chỉ cho phép làm rõ. Nếu có yêu cầu đổi địa chỉ, policy gate chặn và ghi lý do. Không có thao tác nào được thực hiện.

Chốt: cùng một mã, khuyến nghị khác nhau theo bằng chứng, và yêu cầu ngoài phạm vi bị chặn.

Nếu app lỗi: chuyển sang ảnh chụp màn hình bốn bước và nói "Đây là ảnh chụp từ lần chạy trước."

### Slide 11: Where AI could create value (5:30 đến 6:00)

Nói:
> Về giá trị, chúng tôi cố ý không đưa con số tiết kiệm hay độ chính xác, vì chúng tôi chưa có. Bốn điều dưới đây là giả thuyết cần kiểm chứng với dữ liệu thật: ít chuyến giao lại lãng phí hơn, Ops phân loại nhanh hơn, quyết định giải thích được, và trải nghiệm người mua tốt hơn với một câu hỏi. Con số trên slide chỉ là số ca trong bộ 30 ca giả lập: 9 ca đổi giả thuyết sau khi người mua trả lời. Cơ chế đã chạy được: quyết định có bằng chứng, giải thích được, và nằm trong giới hạn. Cảm ơn hội đồng.

Chốt: cơ chế đã chạy, giá trị là giả thuyết.

## Phần thêm cho bản 9 đến 10 phút

Tổng thời gian khoảng 9 phút 30 giây.

| Chèn ở đâu | Nội dung | Thêm |
|---|---|---|
| Sau slide 3 | Slide 12: ai bị ảnh hưởng | 30 giây |
| Sau slide 8 | Slide 13 (mở rộng) và 14 (tích hợp) | 60 giây |
| Trong demo | Thêm ca OR-SYN-004 và OR-SYN-005 | 60 giây |
| Sau slide 11 | Slide 15 (lộ trình) cùng kết quả mô phỏng prompt | 60 giây |

### Slide 12: Who is hurt (+30 giây)

Nói:
> Bốn bên cùng chịu thiệt: người mua phải chờ rồi bị liên hệ mù, shipper tốn lượt giao hạn chế, Ops phân loại từng ca, người bán đối mặt với đơn bị trả. Khó ở chỗ một trạng thái ứng với nhiều nguyên nhân, và chỉ người mua mới giải quyết được một số điều chưa biết.

### Slide 13: How it scales (+30 giây)

Nói:
> Mở rộng là một lộ trình, không phải một tuyên bố. Hiện là bản cục bộ với fixture. Bước tiếp theo là dữ liệu hãng vận chuyển thật, rồi hàng đợi ca và agent chạy bất đồng bộ, rồi hồ sơ policy theo từng phiên bản. Bộ 30 ca giả lập là nền cho bộ kiểm thử hồi quy.

Lưu ý: slide ghi "Evaluation harness (not built yet)". Hiện đã có một đợt chạy đánh giá mô phỏng bằng LLM, chưa phải harness nằm trong repo. Nói đúng như vậy nếu chưa sửa slide.

### Slide 14: Integration (+30 giây)

Nói:
> Tích hợp mới ở mức thiết kế. Agent sẽ chỉ đọc kho đơn hàng và sự kiện giao hàng, hỏi người mua qua một kênh do backend kiểm soát, và hiển thị khuyến nghị trên một console cho Ops quyết định. Nói rõ: hôm nay MVP không tích hợp với hệ thống thật nào.

### Demo mở rộng (+60 giây)

Thao tác: sau bước 4 của demo, chọn OR-SYN-004 rồi OR-SYN-005.

Nói:
> Ca 004 có gián đoạn dịch vụ: hệ thống chọn "Tạm giữ do gián đoạn dịch vụ" thay vì đổ lỗi cho người mua. Ca 005 chỉ có mã "refused" mà không có bằng chứng đã liên hệ: hệ thống chuyển cho người rà soát. Một mã từ chối không đủ để quy kết lỗi hay đề nghị hoàn hàng.

### Slide 15: Roadmap (+60 giây)

Nói:
> Bước tiếp theo là nối LLM agent vào hợp đồng dữ liệu phiên bản 2.2. Chúng tôi đã viết prompt cho agent và chạy thử mô phỏng trên 30 ca. Trung thực về kết quả: hành động đề xuất khớp nhãn ở 30 trên 30 ca ở giai đoạn đầu và 24 trên 24 sau khi người mua trả lời. Nhưng cả sáu trường cùng khớp chỉ 14 trên 30 và 21 trên 24. Chỗ yếu là confidence và thông tin còn thiếu. Kết quả này do LLM mô phỏng, so với nhãn nháp chưa được duyệt, nên chúng tôi coi đây là chỉ dẫn, không phải độ chính xác. Sau đó là chạy cả 30 ca qua bộ đánh giá, và chỉ thử với dữ liệu thật khi được cấp quyền.

## Hỏi đáp (2 phút)

Trả lời ngắn, thẳng, không vượt quá những gì đã xác minh.

| Câu hỏi | Trả lời |
|---|---|
| LLM thật đã chạy chưa? | Chưa tích hợp vào app. Bộ đánh giá theo luật đứng thay. Hợp đồng sáu trường, JSON schema và prompt đã viết, và đã chạy mô phỏng trên 30 ca. |
| Độ chính xác bao nhiêu? | Chúng tôi không tuyên bố độ chính xác. Mô phỏng cho thấy hành động khớp nhãn nhưng confidence và thông tin còn thiếu chưa ổn, và nhãn còn là nhãn nháp. |
| Làm sao tránh LLM bịa hành động? | Ba lớp. Từ vựng cố định và schema kiểm tra đầu ra. Mọi bằng chứng phải trỏ về nguồn có thật. Policy gate là code xác định, quyết định hành động, LLM chỉ đề xuất. Ghi chú và câu trả lời của người mua được coi là dữ liệu, không phải lệnh. |
| Vì sao chỉ một câu hỏi? | Đây là cấu hình demo của policy: tối đa một câu hỏi, để không làm phiền người mua và để Ops có kết quả nhanh. Nếu câu trả lời chưa đủ thì chuyển cho người rà soát, không hỏi thêm vòng hai. |
| Người mua im lặng thì sao? | Không coi là từ chối. Giữ nguyên assessment 1. Trong demo có nút "không phản hồi" do người điều khiển bấm. Chúng tôi chưa đặt thời gian chờ vì chưa biết chính sách thật của Shopee. |
| Có dùng dữ liệu thật không? | Không. Toàn bộ là dữ liệu giả lập. Dữ liệu liên hệ và vị trí là dữ liệu cá nhân, cần cơ sở pháp lý và quyền truy cập trước khi dùng. |
| Tiết kiệm được bao nhiêu? | Chúng tôi không có con số. Đó là giả thuyết. Bước đầu cần chạy ở chế độ bóng trên dữ liệu lịch sử và thống nhất mức nền với Ops. |
| Khác gì một chatbot? | Ba lớp tách riêng: dữ liệu thô, đánh giá của agent, quyết định của policy. Agent không tự hành động. Mỗi quyết định có bằng chứng và nhật ký. |
| Nhóm dùng Codex thế nào? | Dùng cho ứng dụng demo, bộ test (Vitest và Playwright), và data model, business rule, 30 test case. LLM agent chưa làm xong. Không thêm gì ngoài ba phần đó. |
| Hôm nay làm gì, trước đó có gì? | Trả lời theo bản khai báo nộp lúc 17:00. Cả nhóm thống nhất câu này trước khi lên. |

## Không nói

- Không nói đã tích hợp hay được Shopee hoặc SPX duyệt. Không nói đọc dữ liệu thật hay gửi tin nhắn thật.
- Không nói độ chính xác trên đơn thật, số tiền tiết kiệm, hay phần trăm GMV cứu được.
- Không nói agent biết nguyên nhân thật từ một mã trạng thái.
- Không nói Codex tạo toàn bộ sản phẩm.
- Không gọi con số mô phỏng là độ chính xác.

## Khi bị trễ giờ

- Còn 1 phút mà đang ở slide 8: nhảy sang demo bước 1 và 3, bỏ bước 4.
- Hết giờ: chỉ nói câu chốt slide 11 và cảm ơn.
