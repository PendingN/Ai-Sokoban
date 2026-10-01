# Sokoban indie pixel assets

Bộ 11 PNG dùng ảnh **imagegen tích hợp** ngày 2026-10-01. Cảnh vật giữ lại
màu và chi tiết của ảnh generated; nhân vật chỉ được tinh gọn nhẹ bằng
imagegen, giữ tóc rối, khuôn mặt, quần yếm vàng, tay và giày.
Bốn ảnh môi trường được chỉnh lại để dễ đọc bàn: một ô sàn ứng với một
bước đi, gạch lớn với vữa dịu, đất và rêu bớt nét vụn. Bảy ảnh nhân vật,
thùng và đích giữ nguyên. Prompt cuối cùng được lưu trong [PROMPTS.md](PROMPTS.md). Game chỉ tải các
PNG đã xuất; không cần API key, công cụ tạo ảnh hoặc dependency mới.

| File | Kích thước | Vai trò |
| --- | --- | --- |
| `board_frame.png` | 512 × 512 | Đất nâu dịu, viền rêu gọn và vài cụm cỏ, góc trong suốt |
| `floor.png` | 144 × 144 | Một tấm đá kem xám sáng trên mỗi ô; viền mảnh, không chia giữa |
| `wall_top.png` | 144 × 144 | Bốn hàng gạch cũ lớn, vữa nâu dịu, lát liền |
| `wall_front.png` | 144 × 24 | Mặt gạch tối ở cạnh dưới hở |
| `goal.png` | 144 × 144 | Dấu đích vàng mật ong |
| `box.png`, `box_goal.png` | 144 × 168 | Gỗ có thanh chéo; thùng đúng đích xanh rêu, dấu tích kem |
| `player_north/east/south/west.png` | 144 × 176 | Nhân vật tóc rối, đồ vàng, bốn hướng |

## Quy ước xuất ảnh

- Một pixel nét vẽ là một khối **2 × 2 pixel PNG**. Không ép xuống lưới
  8×8 hoặc bảng 12 màu. Giữ các sắc độ gốc để tóc, khuôn mặt và chất liệu
  không bị mất chi tiết. Alpha xuất thành 0/255 để viền không mờ.
- Ánh sáng ở trên trái, bóng cứng ở dưới/phải. Không có quầng bóng.
- Sàn, đích và mặt tường giữ nguyên góc đặt so với ô 72 × 72 logic.
  Renderer ghép ở 2×; mặt trên tường nâng 24 pixel PNG, mặt đứng bù 24 pixel
  chỉ tại cạnh hở. Thứ tự vẽ theo hàng bảo toàn che khuất.
- Thùng đặt tại `(16, 28)`, phần ảnh 112 × 128: **chân y=156**.
  Cả hai trạng thái giữ cùng canvas và cùng điểm chân.
- Nhân vật giữ tỷ lệ ảnh generated, chiều cao phần ảnh 144 pixel,
  đặt ở y=18, căn giữa theo chiều ngang: **chân y=162**.
  Chiều rộng: nam 84, bắc 72, đông/tây 80 pixel. Không kéo ngang hoặc
  cắt đầu/chân. Cả bốn hướng giữ nguyên canvas 144×176 và điểm neo cũ.
  Các offset renderer (thùng −24, người −32 pixel PNG) không đổi.
- Điểm neo được giữ chính xác, nên lưới nét vẽ trong mỗi nhóm sprite có
  offset riêng trên canvas trong suốt. Không làm tròn lại các điểm neo.
- Viền đất dùng chín phần với góc 64 pixel PNG cho bản đồ dài/cao.
  Mọi phép scale dùng nearest-neighbor. Bàn chơi chọn số nguyên pixel
  màn hình trên mỗi pixel nét vẽ khi kích thước đạt ít nhất 95% kích thước
  vừa khít; nếu nhỏ hơn, dùng tỷ lệ vừa vùng chơi. Bàn mặc định đạt 678×678.

Bảng màu giữ các sắc độ nâu đất, vàng mật ong, kem và xanh rêu trong
ảnh generated. Cảnh vật dùng bốn bản chỉnh môi trường dễ đọc; nhân vật giữ
bản tinh gọn nhẹ đã chọn, không thay thiết kế hoặc cắt thêm chi tiết.

Ảnh tổng hợp: [preview_assets.png](../preview_assets.png).
So sánh nhân vật: [preview_character_comparison.png](../preview_character_comparison.png).
