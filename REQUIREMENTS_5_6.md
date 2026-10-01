# Đối chiếu mục 5 và 6

Nguồn: [2627-HK1-AI-GK.pdf](../2627-HK1-AI-GK.pdf), phần Requirements của
Task 1, trang 2-3. Phạm vi đã chốt: nhóm tự cài UCS/A*; phần này cung cấp
giao diện phát lại và mô hình cạnh tranh. Menu khởi động chọn 1/2 tác nhân;
GUI cạnh tranh điều khiển tay đã có. Mục 7 (AI quyết định trong 1.000 ms)
và các thuật toán tách file của mục 8 chưa được cài.

## Mục 5: giao diện và phát lại

| Yêu cầu | Hiện trạng |
| --- | --- |
| GUI pygame, dễ sử dụng | `SokobanApp`, board lớn, nút chuột và hướng dẫn |
| Hai lựa chọn UCS/A* | Có nút chọn và callback `app.solver`; chưa có thuật toán |
| Số hành động | Hiển thị vị trí/tổng hành động và total cost khi có lời giải |
| Space, →, ← | Phát/tạm dừng, tiến và lùi một snapshot; không đảo chiều lệnh đẩy |
| OOP, mã gọn | `Board`, `BoardRenderer`, `SokobanApp`, `Replay` tách trách nhiệm |
| macOS 13.7.8 Intel i5 | Đã kiểm tra wheel Python 3.12 / pygame-ce 2.5.8; cần chạy trên máy Mac thực |

Nhóm có hai cách nối lời giải; không sửa vòng lặp giao diện:

```python
from sokoban_ui.app import SokobanApp
from my_solver import solve  # Hàm do nhóm cài.

app = SokobanApp()
app.solver = solve  # solve(board, "UCS" hoặc "A*") -> (actions, total_cost)
app.run()
```

Callback nhận bản sao bàn ở trạng thái hiện tại. GUI kiểm tra toàn bộ kết quả
trước khi đổi lịch sử. Callback chạy cùng luồng UI; với tìm kiếm lâu, nhóm có
thể tính lời giải trước rồi dùng cách thứ hai dưới đây.

```python
from sokoban_ui.app import SokobanApp
from sokoban_ui.model import LEVELS

app = SokobanApp(levels=(LEVELS[1],))
actions = ["West", "North", "South", "East", "East", "North"]
app.load_solution(actions, total_cost=6, algorithm="UCS")
app.run()
```

Ví dụ trên là lời giải biết trước của Sân tập, không phải kết quả chạy UCS.
`load_solution()` bắt đầu ở trạng thái bàn hiện tại, kiểm tra từng bước hợp lệ,
trạng thái cuối đã thắng và cost bằng số hành động (mỗi bước cost 1). Lời giải
lỗi không làm đổi bàn. Khi nạp, trò chơi đang tạm dừng ở bước 0.

Mở hướng dẫn tạm dừng phát; đóng hướng dẫn không tự tiếp tục. Trong phát lại,
←/→ và các nút lùi/tiến dùng lịch sử đầy đủ để khôi phục cả bộ đếm. Khi kết
thúc giữ màn hiện tại và hiện “Xong rồi!”, không tự đổi màn.

## Mục 6: mô hình cạnh tranh

Đây là trò chơi thông tin đầy đủ, lượt đồng thời, giới hạn hữu hạn n.

- Bản đồ cố định: ô sàn F, tường W, tập đích G. Hai tác nhân có vị trí khác nhau.
- Trạng thái: `(p1, p2, boxes, owners, t)`. `owners` ghi tác nhân đang sở hữu
  từng thùng nằm trên đích; `t` là số lượt đã thực hiện. Chỉ số tác nhân trong
  API là 0/1, khi hiển thị là 1/2.
- Trạng thái đầu: vị trí của A và tọa độ tác nhân 2 nhập riêng; thùng C có
  sẵn trên đích là trung lập. Bản đồ một tác nhân và parser cũ không đổi.
- Mỗi tác nhân chọn một trong North/East/South/West từ cùng trạng thái trước
  lượt. `step((action1, action2))` lập cả hai ý định rồi commit một lần.
- Hành động bị tường, thùng khác hoặc xung đột chặn thì tác nhân đứng yên.
  Lượt vẫn được tính, kể cả cả hai hành động bị chặn. Chuỗi hành động sai
  định dạng bị từ chối và không tính lượt.
- Sau đúng n lượt, so số thùng hiện nằm trên đích thuộc mỗi tác nhân: nhiều
  hơn thì thắng, bằng nhau thì hòa. Không kết thúc sớm khi mọi đích được lấp,
  vì đối thủ vẫn có thể đẩy thùng ra. Utility cuối trận là `score1 - score2`.

### Quy tắc xung đột được chốt

Đề không chỉ định cách phá hòa va chạm, nên chọn hủy đối xứng, không ưu tiên
tác nhân 1 hay 2. Hai ý định bị hủy khi cùng đến một ô, đổi chỗ cho nhau,
cùng đẩy một thùng, đẩy hai thùng đến cùng ô, hoặc thùng sẽ đè lên tác nhân
ở trạng thái cuối lượt. Kiểm tra lại sau khi hủy để không đi vào ô của một
tác nhân vừa bị chặn. Có thể đi theo vào ô đối thủ vừa rời, nếu không đổi
chỗ/cắt qua nhau. Không đẩy chuỗi thùng; kiểm tra thùng cản theo trạng thái đầu.

Đẩy thùng lên đích gán quyền sở hữu cho người đẩy. Đẩy ra khỏi đích xóa
điểm sở hữu cũ. Đối thủ đẩy lại lên đích sẽ nhận điểm; không cộng điểm lặp
vô hạn khi đẩy vào/ra. `scores` được tính từ ownership hiện tại.

```python
from sokoban_ui.competition import CompetitiveBoard, COMPETITION_LEVEL

game = CompetitiveBoard(COMPETITION_LEVEL, second_player=(8, 5), step_limit=20)
game.step(("East", "North"))
print(game.state, game.scores, game.finished, game.winner)
```

`winner` là 0/1 sau khi hết n lượt; `None` khi chưa kết thúc hoặc hòa, phân
biệt bằng `finished`. Sau kết thúc, `step()` trả False và không đổi trạng thái.

### Nhập n và thử luật bằng terminal

Trong giao diện: chọn **2 tác nhân** ở menu, nhập **n > 0**, bấm **Bắt đầu**.
Tác nhân 1 chọn bằng WASD, tác nhân 2 bằng mũi tên; không hiện cụm nút di chuyển.
Thanh dưới có icon phát/tạm dừng, hoàn tác, làm lại, chơi lại, hướng dẫn;
rê chuột để xem tên và phím tắt. Khi
cả hai đã chọn, commit một lần theo luật `CompetitiveBoard.step()`, cách
các lượt tối thiểu 125 ms. Một lựa chọn riêng chưa làm đổi trạng thái.
Space tạm dừng/tiếp tục; hướng dẫn chặn thao tác và giữ tạm dừng khi đóng.
Undo/redo khôi phục đầy đủ cả điểm sở hữu, số lượt và hướng nhìn.
Thùng trên đích của 1 dùng sprite xanh; của 2 dùng sprite vàng hiện có.
Kết thúc đúng n, hiện kết quả và chơi lại; nút Menu đổi chế độ.

Đường chạy terminal dưới đây được giữ nguyên:

Trong PowerShell tại `02_BaiTap_Lab`:

```powershell
.\.venv\Scripts\python.exe -m sokoban_ui.competition --steps 20
```

Bỏ `--steps` để chương trình hỏi số n. Mỗi lượt nhập hai hành động trên cùng
một dòng, ví dụ `East North`; cả hai được thực hiện đồng thời. `q` dừng thử
mà không tuyên bố kết quả trước n. Có bản đồ lớn hơn Kho đôi; bản đồ riêng
dùng `--map path.txt --second-player X Y --steps N`. Trên macOS dùng
`.venv/bin/python` thay đường dẫn Python Windows.

## Kiểm chứng

```powershell
.\.venv\Scripts\python.exe -m unittest test_sokoban_ui -v
.\.venv\Scripts\python.exe -m sokoban_ui.check_presentation
.\.venv\Scripts\python.exe -m sokoban_ui.check_requirements
```

Giữ nguyên 18 test cũ. Kiểm tra mới dùng lời giải bên ngoài đã biết, kiểm tra
phát/lùi/tiến, trạng thái lỗi, modal, resize và luật cạnh tranh. Có trường hợp
đối thủ đẩy thùng ra rồi đặt lại, cùng ô, đổi chỗ, cùng thùng, cùng đích đẩy,
hai lần đẩy độc lập và kiểm tra đối xứng đổi tác nhân trên các lượt sinh ra.
Kết quả Windows đã đạt; chưa tuyên bố kiểm thử macOS hoặc kéo cạnh GUI thực.
