# Kịch bản pitch Order Rescue v3 (6 phút + 2 phút hỏi đáp)

Khớp với `Order_Rescue_Pitch_Deck.pptx` (12 slide: 9 chính, 3 backup). Cập nhật sau buổi họp nhóm 29/10. Người nghe là manager, không phải kỹ sư. Nói bằng ngôn ngữ đơn giản, để thuật ngữ kỹ thuật cho phần hỏi đáp. Lời nói trên sân khấu bằng tiếng Anh theo bản EN.

## Thời gian

| Slide | Thời gian | Nội dung |
|---|---|---|
| 1 | 0:00-0:15 | Bìa |
| 2 | 0:15-0:55 | Vì sao bài toán đáng giải (số liệu của Hải) |
| 3 | 0:55-1:25 | Vấn đề |
| 4 | 1:25-2:15 | Giải pháp 4 bước |
| 5 | 2:15-2:45 | Niềm tin: AI gợi ý, luật quyết định |
| 6 | 2:45-3:25 | Cách dùng Codex |
| 7 | 3:25-3:45 | Khai báo: làm trước và làm trong ngày |
| 8 | 3:45-5:45 | Demo trực tiếp |
| 9 | 5:45-6:00 | Tác động và bước tiếp theo |

## Ý chính từng slide

1. **Bìa:** giới thiệu 4 người; Order Rescue giúp Ops hiểu vì sao giao thất bại và nên làm gì; chỉ gợi ý, không tự hành động; dữ liệu giả lập.
2. **Số liệu:** Hải cung cấp: số liệu vận hành Shopee, một case study bên ngoài, rồi câu "vì vậy chúng tôi xây giải pháp này". Chưa có số thì xóa slide, không bịa.
3. **Vấn đề:** Ops chỉ thấy mã trạng thái. "Người nhận vắng" có thể là đi làm, sai mốc, tắt máy, hoặc tuyến bị gián đoạn. Đoán sai thì tốn chuyến hoặc mất đơn, và không ai ghi lại lý do.
4. **Giải pháp:** đọc ca, hỏi buyer đúng một câu (chỉ khi thiếu thông tin), kiểm tra bằng luật, đưa Ops khuyến nghị kèm bằng chứng. Hiện tại bộ đánh giá theo luật đóng vai AI; LLM là bước tiếp theo.
5. **Niềm tin:** AI gợi ý, luật quyết định. Tự tin cao cũng không vượt luật. Im lặng không phải từ chối. Ghi chú shipper không phải bằng chứng. AI không đổi địa chỉ hay hoàn tiền.
6. **Codex:** chỉ nói: ứng dụng demo, test, data model, business rule và 30 test case. Quy trình: luật và case trước, rồi build, rồi test. Không nói thêm.
7. **Khai báo:** trước hackathon: data model, rule, 30 case, prototype đầu tiên. Trong ngày: điền theo bản khai báo 5 giờ chiều. Phải khớp tuyệt đối.
8. **Demo (2 phút, chạy thật):** OR-SYN-001 xem bằng chứng và đánh giá; bấm "Áp dụng phản hồi người mua đã chuẩn bị" xem đánh giá lại; OR-SYN-003 (đổi địa chỉ) bị chặn và chuyển cho người. Một câu chú thích: app, luật, test là thật; đơn, ghi chú, phản hồi là giả lập; không kết nối Shopee hay SPX.
9. **Tác động:** đây là giả thuyết, không phải kết quả; không nêu số tiết kiệm. Tiếp theo: nối LLM, chạy 30 case qua bộ đánh giá, thí điểm khi được phép.

## Hỏi đáp và điều không được nói

Dùng bảng trả lời ở bản EN (`pitch_script_v3_en.md`). Không nói: đã tích hợp hoặc được Shopee/SPX duyệt, đã đọc dữ liệu thật, độ chính xác trên đơn thật, số tiền tiết kiệm, agent biết nguyên nhân thật chỉ từ một mã trạng thái, Codex làm ra toàn bộ sản phẩm.

## Nếu bị chậm

- Còn 1 phút trước demo: bỏ slide 7, vào thẳng bước 1 và bước 3 của demo.
- Hết giờ: chỉ nói câu đầu slide 9 rồi cảm ơn.
