# Giao diện Sokoban

Kho nhỏ theo phong cách indie pixel: gạch cũ, sàn đá, đất nâu có viền rêu,
thùng gỗ thanh chéo và nhân vật đồ vàng tóc rối. Cả 11 PNG trong `assets/`
giữ các sắc độ nâu đất, vàng mật ong, kem và xanh rêu; ánh sáng ở trên trái,
bóng cứng, nét pixel rõ. Bộ runtime dùng chi tiết và màu của ảnh generated,
không ép thành lưới 8×8 hoặc bảng 12 màu. Nhân vật chỉ tinh gọn nhẹ, giữ tóc,
khuôn mặt và bộ đồ; các hướng giữ tỷ lệ gốc và điểm chân y=162.
Renderer tải và ghép ảnh theo trạng thái bàn chơi. Bốn ảnh môi trường được
chỉnh bằng imagegen: mỗi ô sàn là một tấm đá kem xám sáng, tường có bốn hàng
gạch lớn với vữa dịu, đất và rêu bớt nét vụn. Nhân vật, thùng và dấu đích
giữ nguyên bộ ảnh đã chọn.

Bàn chơi ở giữa trên nền beige dịu `#d7c4a4`. Chữ nâu đậm, nút nền kem viền nâu
và trạng thái nhấn vàng mật ong giúp nhìn rõ hơn. Thanh trên có tên màn, đổi
màn, Menu, số hành động, chi phí, thùng đúng đích, bước đi và lần đẩy.
Thanh dưới gom ba nhóm: UCS/A* và tìm lời giải; lùi/phát/tiến; hoàn tác,
làm lại/chơi lại/hướng dẫn. Các nút chức năng dùng icon nét vuông 44×44 px;
rê chuột để xem tên và phím tắt, kể cả nút đang vô hiệu. UCS/A* và lựa chọn
chế độ giữ chữ. Thanh nút cao 68 px và nằm một hàng ở mọi kích thước hỗ trợ.
Không hiển thị cụm nút di chuyển ở cả hai chế độ;
di chuyển bằng bàn phím. Nút có viền vuông và đổi màu,
hạ mặt khi nhấn. Không có các thẻ bên phải hoặc thanh tiến độ.

Khi khởi động, menu cho chọn **1 tác nhân** hoặc **2 tác nhân**. Nút **Menu**
trong màn chơi đưa về lựa chọn này. Chế độ 1 giữ giao diện chơi tay và phát
lại lời giải bên ngoài (mục 5); chế độ 2 dùng luật cạnh tranh đồng thời (mục 6).
**Chưa cài UCS, A*, heuristic hoặc AI cạnh tranh.** Nhóm nối thuật toán qua
`app.solver` hoặc đưa lời giải đã tính vào `app.load_solution()`.
Chi tiết đối chiếu đề và luật đồng thời: [REQUIREMENTS_5_6.md](REQUIREMENTS_5_6.md).

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

## Chạy trên macOS 13.7.8 Intel

Chọn Python 3.12 và giữ `pygame-ce==2.5.8`. [PyPI của pygame-ce 2.5.8](https://pypi.org/project/pygame-ce/2.5.8/#files)
có wheel `cp312-cp312-macosx_10_13_universal2`, hỗ trợ Intel x86-64 và
macOS từ 10.13. Đây là kiểm tra gói tương thích, **chưa phải kiểm thử máy Mac thực**.
Tại thư mục `02_BaiTap_Lab`, chạy trong Terminal:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r sokoban_ui/requirements.txt
.venv/bin/python -m unittest test_sokoban_ui -v
.venv/bin/python -m sokoban_ui.check_requirements
.venv/bin/python -m sokoban_ui
```

Sau kiểm tra tự động, thử font tiếng Việt, Space/←/→ với lời giải, nút chuột
và kéo cửa sổ trên máy Mac. Font dùng Arial/fallback; không cần font Windows.

## Điều khiển

| Thao tác | Phím |
| --- | --- |
| Di chuyển, đẩy một thùng | Mũi tên hoặc W A S D |
| Phát / tạm dừng lời giải đã nạp | Space |
| Lùi / tiến một hành động trong lời giải | ← / → |
| Hoàn tác | Z hoặc Backspace |
| Tiến lại bước vừa hoàn tác | Y |
| Đặt lại bàn chơi | R |
| Chuyển bàn chơi | Page Up / Page Down hoặc nút cạnh tên bàn |
| Mở / đóng hướng dẫn | H hoặc F1 |
| Đóng hướng dẫn / thoát cửa sổ | Esc |

Các nút bấm được bằng chuột. Bộ đếm chỉ tính bước hợp lệ. Thùng đúng đích
chuyển xanh rêu, có dấu tích kem. Khi hoàn thành, hiện **“Xong rồi!”** và nút
**“Màn tiếp”**; chỉ đổi màn khi bấm nút hoặc dùng hotkey. Nút **“Đổi màn”**
ở thanh trên vẫn hoạt động sau khi thắng. Hướng dẫn chặn mọi thao tác chơi;
Esc, H/F1 hoặc một lần bấm chuột đóng hộp và không kích hoạt nút bên dưới.
Bản đồ riêng chỉ có một màn nên các nút đổi màn bị vô hiệu.

Trong chế độ lời giải, mũi tên trái/phải dùng lùi/tiến; thao tác di chuyển
tay bị khóa. Mở hướng dẫn sẽ tạm dừng phát. Khi đóng, bấm Space để tiếp tục.
Lùi khôi phục snapshot đầy đủ, gồm vị trí, hướng nhìn, số bước và số lần đẩy.
Đổi thuật toán bỏ phần phát lại còn lại; chơi lại/đổi màn trở về chơi tay.
Nút **Tìm lời giải** bị vô hiệu cho đến khi nhóm nối `app.solver`.

Cửa sổ mặc định **1280×860**, tối thiểu 640×430. Giao diện bố trí theo kích
thước cửa sổ thực: dưới 1000 px, bộ đếm xuống hàng; thanh nút icon vẫn nằm
một hàng, chia nhóm bằng khoảng cách đều. Tên quá dài có
ellipsis. Chữ tiếng Việt vẫn dùng Segoe UI trên Windows và font fallback cũ,
vẽ ở kích thước thực, không scale toàn màn hình. Sprite dùng nearest-neighbor;
chỉ chọn tỷ lệ nguyên trên mỗi pixel nét vẽ khi kích thước đạt ít nhất **95%**
kích thước vừa khít vùng chơi. Các trường hợp khác phóng vừa vùng chơi:
bàn màn đầu ở cửa sổ mặc định đạt **704×704** sau khi thu gọn thanh nút.
Chữ trên nút UCS/A* dùng 16 px, menu dùng 18 px, căn giữa và chừa lề;
icon phát/tạm dừng đổi theo trạng thái. Tỷ lệ lẻ có
thể khiến một số pixel rộng hơn pixel bên cạnh, nhưng không nội suy làm mờ.
Timing chuyển động giữ **125 ms**;
bobbing là pixel nguyên; điểm chân và thứ tự che khuất không đổi.

Windows được khai báo DPI awareness trước khi khởi tạo video để tránh hệ
điều hành nội suy bitmap. Xem [SDL DPI awareness](https://wiki.libsdl.org/SDL2/SDL_HINT_WINDOWS_DPI_AWARENESS).

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
- `replay.py`: kiểm tra lời giải bên ngoài, dùng lịch sử snapshot để phát/lùi/tiến.
- `competition.py`: luật hai tác nhân đồng thời, điểm sở hữu đích và bản thử terminal.
- `__main__.py`: điểm chạy `python -m sokoban_ui`.
- `maps/template.txt`: bản đồ theo ảnh tham khảo.
- `../test_sokoban_ui.py`: kiểm tra luật tương tác, sự kiện UI và co giãn cửa sổ.

`BoardRenderer` nhận một `Board` và vẽ `Snapshot`. Khi tích hợp thuật toán,
chỉ cần truyền danh sách hành động `North`, `East`, `West`, `South` qua
`Board.move()`; không phải sửa renderer hoặc luật di chuyển.

## Nối thuật toán của nhóm

Chọn UCS/A* trên thanh trên. Gán hàm do nhóm cài vào `app.solver`:

```python
from sokoban_ui.app import SokobanApp
from my_solver import solve

app = SokobanApp()
app.solver = solve  # solve(board, algorithm) -> (actions, total_cost)
app.run()
```

Hoặc gọi `app.load_solution(actions, total_cost, algorithm="A*")` với lời
giải đã tính cho trạng thái bàn hiện tại. Lời giải phải dùng North/East/South/West,
mọi bước hợp lệ, kết thúc đã thắng và total_cost bằng số hành động. GUI bắt
đầu ở trạng thái tạm dừng. Các bước được kiểm tra trước khi đổi lịch sử;
hướng dẫn nhóm và ví dụ hoàn chỉnh ở [REQUIREMENTS_5_6.md](REQUIREMENTS_5_6.md).

## Mô hình hai tác nhân (mục 6)

Chạy `python -m sokoban_ui`, chọn **2 tác nhân**, nhập số lượt n rồi bấm
**Bắt đầu**. Tác nhân **1** dùng **WASD**, tác nhân **2** dùng **mũi tên**.
Phím di chuyển chỉ được nhắc trong hướng dẫn; thanh trên hiển thị lựa chọn
đang chờ của từng tác nhân. Mỗi bên chọn một hướng; chỉ khi có đủ
hai lựa chọn mới thực hiện một lượt. Có thể sửa lựa chọn đang chờ trước khi
bên kia chọn. Số 1/2 trên đầu giúp nhận ra từng nhân vật, giữ nguyên bộ sprite.

**Space** tạm dừng/tiếp tục; mở hướng dẫn hoặc hoàn tác cũng tạm dừng.
Hoàn tác/tiến lại khôi phục cả hai vị trí, thùng, điểm và số lượt. Thùng trên
đích thuộc tác nhân 1 màu xanh, thuộc tác nhân 2 màu vàng. Sau đúng n lượt,
hiện kết quả thắng/hòa và nút chơi lại. Đây là điều khiển tay để nhóm nối AI sau.

`CompetitiveBoard` nhận bản đồ, vị trí tác nhân 2 và số lượt n. Hai hành động
được xét trên cùng trạng thái và commit đồng thời; cấm chung ô, đổi chỗ và
xung đột thùng. Sau n lượt, ai sở hữu nhiều thùng trên đích hơn sẽ thắng.
Đẩy thùng của đối thủ ra rồi đưa lại lên đích sẽ chuyển quyền ghi điểm.

Thử bằng terminal, tại `02_BaiTap_Lab`:

```powershell
.\.venv\Scripts\python.exe -m sokoban_ui.competition --steps 20
```

Bỏ `--steps` để nhập n khi chạy. Mỗi lượt nhập hai hành động trên một dòng,
ví dụ `East North`. Bản thử terminal vẫn giữ nguyên. Chưa cài AI của mục 7
hoặc các thuật toán tách file của mục 8. Quy tắc chi tiết nằm trong
[REQUIREMENTS_5_6.md](REQUIREMENTS_5_6.md).

Nếu cần đổi phong cách hình ảnh, thay các PNG trong `assets/` rồi chạy lại
chương trình; không phải sửa luật chơi. Renderer yêu cầu đủ bộ asset và báo rõ
tên file nếu có file bị thiếu; không có fallback sang cách vẽ procedural.

Thông số bộ art và điểm neo nằm trong [`assets/README.md`](assets/README.md).
Prompt cuối cùng nằm trong [`assets/PROMPTS.md`](assets/PROMPTS.md), bộ art
được tạo bằng imagegen tích hợp. Không thêm solver, âm thanh hoặc dependency.

## Kiểm tra và xuất ảnh

```powershell
.\.venv\Scripts\python.exe -m unittest test_sokoban_ui -v
.\.venv\Scripts\python.exe -m sokoban_ui.check_presentation
.\.venv\Scripts\python.exe -m sokoban_ui.check_requirements
.\.venv\Scripts\python.exe -m sokoban_ui --screenshot sokoban_ui\preview.png
```

Lệnh xuất ảnh không mở cửa sổ. `--frames 10` mở cửa sổ rồi tự thoát sau 10
khung hình để kiểm tra khởi động.


Ngày 2026-10-01: **18/18 test hiện có đạt** trên Python 3.14.7 / pygame-ce
2.5.8. `check_presentation` kiểm tra chính sách scale ở hai phía mốc 95%,
kích thước bàn mặc định 704×704, nút, trạng thái nhấn, hướng dẫn chặn
thao tác, undo/redo khi thắng, cả hai nút đổi màn, timing 125 ms, alpha,
điểm chân và các kích thước 1280×860, 720×900, 960×645, 1280×500,
1280×1000, 640×430 và hai phía mốc đổi bố cục 999/1000 px. Kiểm tra cả
nút không chồng nhau, chữ vừa nút ở cỡ chuẩn, icon khác nhau và chú thích
rê chuột tại cửa sổ mặc định/tối thiểu. Script xuất ảnh Pygame thật
để xem lại bố cục; không
thay đổi bộ 18 test cũ. Các sự kiện resize tự động đã được kiểm tra; thao tác
kéo cạnh cửa sổ qua GUI chưa xác nhận được: công cụ liên tục báo phát hiện
thao tác người dùng và không lấy đúng ảnh cửa sổ game, nên chưa thực hiện kéo.

`check_requirements` đã đạt: kiểm tra lời giải lỗi không làm đổi bàn, Space,
phím trái/phải, nút sau resize, hướng dẫn chặn phát lại, kết thúc không tự
đổi màn; hai hành động đồng thời, cấm chung ô/đổi chỗ, xung đột đẩy thùng,
hai lần đẩy độc lập, cướp điểm, giới hạn n và đối xứng khi đổi tên tác nhân.
Kiểm tra thêm menu và cả hai lựa chọn, nhập n lỗi/hợp lệ, các nút của chế độ
2 tác nhân, chờ đủ hai hướng, timing 125 ms, tạm dừng, modal, undo/redo sau
kết thúc và quay về menu ở cả bốn kích thước mặc định/hẹp/thấp/tối thiểu.

| Ảnh kiểm chứng | Nội dung |
| --- | --- |
| [preview_menu.png](preview_menu.png) | Menu chọn 1 hoặc 2 tác nhân |
| [preview_tooltip.png](preview_tooltip.png) | Chú thích nút icon khi rê chuột |
| [preview_tooltip_small.png](preview_tooltip_small.png) | Thanh icon và chú thích ở 640×430 |
| [preview_setup_small.png](preview_setup_small.png) | Nhập n ở cửa sổ tối thiểu |
| [preview_competition.png](preview_competition.png) | Hai tác nhân trong cửa sổ game |
| [preview_competition_narrow.png](preview_competition_narrow.png) | Hai tác nhân ở 720×900 |
| [preview_competition_short.png](preview_competition_short.png) | Hai tác nhân ở 1280×500 |
| [preview_competition_small.png](preview_competition_small.png) | Hai tác nhân ở 640×430 |
| [preview_competition_help_small.png](preview_competition_help_small.png) | Hướng dẫn chế độ 2 |
| [preview_competition_end_small.png](preview_competition_end_small.png) | Kết quả sau n lượt |
| [preview.png](preview.png) | Kho gạch nhỏ, 1280×860 |
| [preview_level2.png](preview_level2.png) | Sân tập |
| [preview_help.png](preview_help.png) | Hướng dẫn |
| [preview_victory.png](preview_victory.png) | “Xong rồi!” và “Màn tiếp” |
| [preview_rectangular.png](preview_rectangular.png) | Bản đồ ngoài dài |
| [preview_tall.png](preview_tall.png) | Bản đồ cao |
| [preview_narrow.png](preview_narrow.png) | Cửa sổ hẹp 720×900 |
| [preview_short.png](preview_short.png) | Cửa sổ thấp 1280×500 |
| [preview_help_small.png](preview_help_small.png) | Hướng dẫn ở 640×430 |
| [preview_replay.png](preview_replay.png) | Phát lại, số hành động và chi phí |
| [preview_replay_narrow.png](preview_replay_narrow.png) | Phát lại ở 720×900 |
| [preview_replay_small.png](preview_replay_small.png) | Phát lại ở 640×430 |
| [preview_replay_short.png](preview_replay_short.png) | Phát lại ở 1280×500 |
| [preview_pressed.png](preview_pressed.png) | Nút đang nhấn |
| [preview_assets.png](preview_assets.png) | Cả 11 PNG mới |
| [preview_character_comparison.png](preview_character_comparison.png) | Nhân vật trước và sau: giữ chi tiết generated |
