# Sokoban image assets

Bộ 11 PNG được tạo bằng công cụ imagegen tích hợp, sau đó cắt phần ảnh cần
dùng, thu nhỏ và căn trên canvas chung. Xem [PROMPTS.md](PROMPTS.md) để biết
prompt tạo từng ảnh. Đây là tài nguyên có sẵn; chạy game không cần công cụ
tạo ảnh, API key hoặc script `build_assets.py`.

Renderer chỉ tải và ghép PNG. Không có cách vẽ procedural dự phòng.

| File | Kích thước pixel | Vai trò |
| --- | --- | --- |
| `board_frame.png` | 512 × 512 | Nền cỏ, góc trong suốt, cạnh đất và bóng sát chân |
| `floor.png` | 144 × 144 | Xi măng xám ấm, lát kín các ô đi được |
| `wall_top.png` | 144 × 144 | Mặt trên gạch nung, lát liền các ô tường |
| `wall_front.png` | 144 × 24 | Mặt đứng chỉ xuất hiện ở cạnh dưới hở |
| `goal.png` | 144 × 144 | Đích đồng, căn giữa ô, nền trong suốt |
| `box.png`, `box_goal.png` | 144 × 168 | Thùng thường và thùng xanh có dấu tích |
| `player_north/east/south/west.png` | 144 × 176 | Cùng nhân vật ở bốn hướng |

Một ô logic là 72 × 72; ảnh được ghép ở tỷ lệ 2× rồi thu nhỏ một lần trong
khung bàn chơi. Khi thay ảnh, giữ đúng tên và kích thước; loader báo lỗi rõ
nếu thiếu file hoặc canvas sai kích thước.

- Gốc của sàn và đích trùng góc trên trái ô.
- Mặt trên tường nâng 24 pixel so với ô; mặt đứng cao 24 pixel bù lại ở chân.
  Không có mặt đứng giữa hai ô tường nối theo chiều dọc.
- Canvas thùng đặt cao hơn ô 24 pixel; nhân vật đặt cao hơn 32 pixel.
  Hai loại thùng dùng cùng kích thước và cùng vị trí chân để tránh nhảy hình
  khi đổi trạng thái. Bốn hướng nhân vật căn theo chân ở cùng cao độ.
- Nền cỏ chia chín phần với góc 64 pixel, giữ nguyên hình góc trên bản đồ dài
  hoặc rộng. Bóng đã có trong ảnh, không thêm quầng bóng bên ngoài.
- Sprite được thu nhỏ với alpha nhân trước rồi đổi về alpha thường, tránh
  viền đen do màu RGB ở vùng trong suốt lọt vào cạnh khi nội suy.

Các file `wall_0`–`wall_7`, `floor_0`–`floor_3` và `board_shadow` thuộc bộ
cũ đã được thay thế và không còn dùng. `floor.png` là texture sàn runtime;
`board_frame.png` chỉ làm viền cỏ và bóng ngoài bàn.
