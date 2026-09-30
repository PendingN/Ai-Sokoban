# Giao diện Sokoban

Bản giao diện Pygame theo `Template.png`: nhìn từ trên xuống, tường gạch nổi,
sàn xi măng, viền cỏ, thùng gỗ và nhân vật áo vàng. Toàn bộ hình ảnh của bàn
cờ, gồm nền cỏ, bóng, sàn, đích, tường, thùng và nhân vật, đều nằm trong
`assets/` dưới dạng PNG; renderer chỉ ghép các ảnh đó theo trạng thái bàn cờ.

Phạm vi hiện tại: giao diện và chơi thử bằng tay. **Chưa cài UCS, A* hoặc
heuristic.** Phần thuật toán sẽ do nhóm thêm theo hướng dẫn ở dưới; thư mục
giao diện không phụ thuộc vào cách tìm kiếm.

## Chạy trên Windows

Mở PowerShell tại thư mục `02_BaiTap_Lab`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r sokoban_ui\requirements.txt
.\.venv\Scripts\python.exe -m sokoban_ui
```

Nếu chưa có môi trường ảo, chạy `python -m venv .venv` trước.

Hoặc dùng Python từ môi trường đang kích hoạt:

```sh
python -m pip install -r sokoban_ui/requirements.txt
python -m sokoban_ui
```

Yêu cầu Python 3.10 trở lên. Dependency là `pygame-ce` (bản community của
Pygame), mã nguồn dùng `import pygame`. Không cài đồng thời `pygame` và
`pygame-ce` trong cùng môi trường. Bản này đã chạy thử trên Windows với
Python 3.14.7 và pygame-ce 2.5.8; chưa kiểm thử macOS Ventura.

## Điều khiển

| Thao tác | Phím |
| --- | --- |
| Di chuyển, đẩy một thùng | Mũi tên hoặc W A S D |
| Hoàn tác | Z hoặc Backspace |
| Tiến lại bước vừa hoàn tác | Y |
| Đặt lại bàn chơi | R |
| Chuyển bàn chơi | Page Up / Page Down hoặc nút cạnh tên bàn |
| Mở / đóng hướng dẫn | H hoặc F1 |
| Đóng hướng dẫn / thoát cửa sổ | Esc |

Các nút trên giao diện có thể bấm bằng chuột. Bộ đếm chỉ tính bước đi hợp lệ.
Thùng trên đích đổi sang màu xanh, kèm dấu tích. Bản mặc định dựng lại bố cục
ảnh mẫu; bàn thứ hai là sân tập với hai thùng. Cửa sổ mở ở kích thước thiết kế
`1280×860` để chữ và đường viền sắc nét. Khi thu nhỏ cửa sổ, giao diện vẫn giữ
tỷ lệ và dùng scale điểm ảnh rõ nét; không còn lớp nội suy mềm phủ lên toàn bộ
màn hình. Viền cỏ có góc trong suốt và bóng sát chân nằm sẵn trong PNG;
không chồng thêm lớp bóng mờ quanh bàn.

## Bản đồ riêng

```powershell
.\.venv\Scripts\python.exe -m sokoban_ui --map sokoban_ui\maps\template.txt
```

Đọc file UTF-8 theo quy ước: `%` là tường, `A` là người, `B` là thùng,
`D` là đích, `C` là thùng trên đích, dấu cách là sàn. Hỗ trợ thêm `+` là
người trên đích. Giữ nguyên khoảng trắng, không dùng tab. Ô bị thiếu ở cuối
dòng ngắn không thể đi vào. Cần đúng một người và số thùng bằng số đích.
Trình đọc chỉ kiểm tra định dạng, không xác định bản đồ có lời giải hay không.

## Cấu trúc

- `model.py`: bản đồ, trạng thái, luật di chuyển và lịch sử hoàn tác.
- `renderer.py`: tải asset một lần, ghép bàn chơi, vật thể có chiều sâu và chuyển động.
- `assets/`: 11 PNG dùng khi chạy; sprite có nền trong suốt, texture sàn/tường kín màu.
- `app.py`: cửa sổ, các nút, bàn phím, bộ đếm và bố cục.
- `__main__.py`: điểm chạy `python -m sokoban_ui`.
- `maps/template.txt`: bản đồ theo ảnh tham khảo.
- `../test_sokoban_ui.py`: kiểm tra luật tương tác, sự kiện UI và co giãn cửa sổ.

`BoardRenderer` nhận một `Board` và vẽ `Snapshot`. Khi tích hợp thuật toán,
chỉ cần truyền danh sách hành động `North`, `East`, `West`, `South` qua
`Board.move()`; không phải sửa renderer hoặc luật di chuyển.

## Cách đưa thuật toán của nhóm vào code

PDF [2627-HK1-AI-GK.pdf](../2627-HK1-AI-GK.pdf) yêu cầu Task 1 có UCS và A*,
đầu ra là danh sách hành động cùng total cost, và heuristic của A* không được
là khoảng cách Manhattan hoặc Euclidean. README này chỉ mô tả điểm nối; phần
cài đặt thuật toán và heuristic để nhóm tự viết 
### 1. Giữ đúng hợp đồng trạng thái

`Board` đã cung cấp các dữ liệu cần cho state-space search:

```python
board.state.player   # (x, y) hiện tại của người
board.state.boxes    # frozenset[(x, y)] của các thùng
board.goals          # tập ô đích
board.floor          # tập ô có thể đứng/đẩy vào
```

Khi sinh trạng thái con, kiểm tra ô đích nằm trong `board.floor`. Nếu ô đó là
thùng, ô ngay phía sau cũng phải nằm trong `board.floor` và không có thùng
khác. Tên hành động phải giữ nguyên bốn chuỗi mà model dùng:
`North`, `East`, `West`, `South`.

### 2. Tạo file solver riêng

Để không trộn thuật toán vào giao diện, nhóm có thể đặt API tối thiểu sau trong
`sokoban_ui/solver.py`:

```python
from sokoban_ui.model import Board


def solve(board: Board, algorithm: str) -> tuple[list[str], int]:
    """Trả về (actions, total_cost); nêu lỗi nếu không có lời giải."""
    # UCS hoặc A* làm việc trên bản sao bất biến của board.state.
    # Không gọi board.move() trong lúc mở rộng node.
    # actions chỉ chứa North/East/West/South.
    raise NotImplementedError
```

Nên lưu `parent[state] = (previous_state, action)` để dựng lại đường đi khi
gặp trạng thái mà mọi thùng đều nằm trên đích. Với UCS, ưu tiên `g(n)`; với A*,
ưu tiên `f(n) = g(n) + h(n)`. `total_cost` phải bằng số hành động nếu mỗi bước
có cost 1.

### 3. Nối lời giải vào giao diện

Trong `SokobanApp`, nút tự giải chỉ cần gọi API ở trên rồi phát từng action:

```python
actions, total_cost = solve(self.board, "A*")
self.solution = actions
self.solution_index = 0

# Trong vòng lặp khung hình:
if self.solution_index < len(self.solution):
    old = self.board.state
    self.board.move(self.solution[self.solution_index])
    self.previous = old
    self.animation_start = pg.time.get_ticks()
    self.solution_index += 1
```

Nút chọn `UCS` hoặc `A*` chỉ thay chuỗi truyền vào `solve`. Renderer tự đọc
`self.board.state`, nên không cần biết node, frontier hay heuristic là gì.
Nếu muốn đúng yêu cầu điều khiển của đề, dùng `Space` để tạm dừng phát lại,
mũi tên phải để tiến một action và mũi tên trái để lùi một snapshot. Lịch sử
`Board.undo()`/`Board.redo()` có thể dùng cho phần lùi/tiến khi lời giải đã
được phát.

### 4. Kiểm tra trước khi ghép vào UI

Chạy thuật toán độc lập trên một `Board`, replay toàn bộ `actions` bằng
`board.move(action)`, rồi kiểm tra `board.won`. Sau đó mới gọi từ nút để dễ
tách lỗi tìm kiếm khỏi lỗi hiển thị:

```powershell
.\.venv\Scripts\python.exe -m unittest test_sokoban_ui -v
```

Nếu nhóm đổi tên action, thay luật đẩy hoặc thay cấu trúc state, cần cập nhật
model và test tương ứng; chỉ sửa `renderer.py` sẽ không nối được thuật toán.

Nếu cần đổi phong cách hình ảnh, thay các PNG trong `assets/` rồi chạy lại
chương trình; không phải sửa luật chơi. Renderer yêu cầu đủ bộ asset và báo rõ
tên file nếu có file bị thiếu; không có fallback sang cách vẽ procedural.

Bộ ảnh mới có gạch nung, sàn xi măng, thùng gỗ với thanh chéo, đích đồng và nhân vật áo
vàng ở đủ bốn hướng. Tường dùng `wall_top.png` và `wall_front.png`: chỉ ghép
mặt đứng ở cạnh dưới hở, tránh sọc bóng giữa các ô liền nhau. Không còn tám
file `wall_0`–`wall_7`. Kích thước và điểm đặt sprite được ghi trong
[`assets/README.md`](assets/README.md); bộ prompt tạo ảnh nằm trong
[`assets/PROMPTS.md`](assets/PROMPTS.md). Ảnh xem trước: [`preview_assets.png`](preview_assets.png).

## Kiểm tra và xuất ảnh

```powershell
.\.venv\Scripts\python.exe -m unittest test_sokoban_ui -v
.\.venv\Scripts\python.exe -m sokoban_ui --screenshot sokoban_ui\preview.png
```

Lệnh xuất ảnh không mở cửa sổ. `--frames 10` mở cửa sổ rồi tự thoát sau 10
khung hình để kiểm tra khởi động.
