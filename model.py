"""Small, renderer-independent board model for manual UI interactions."""

from dataclasses import dataclass
from pathlib import Path

Cell = tuple[int, int]
DIRECTIONS: dict[str, Cell] = {
    "North": (0, -1), "East": (1, 0), "South": (0, 1), "West": (-1, 0)
}


@dataclass(frozen=True)
class Level:
    name: str
    rows: tuple[str, ...]
    subtitle: str = "Đưa từng thùng hàng về đúng vị trí."

    def __post_init__(self) -> None:
        if not self.rows or not max(map(len, self.rows)):
            raise ValueError("Bản đồ trống.")
        symbols = "".join(self.rows)
        invalid = set(symbols) - set("%ABDC +")
        if invalid:
            raise ValueError(f"Ký hiệu bản đồ không hợp lệ: {sorted(invalid)!r}")
        if symbols.count("A") + symbols.count("+") != 1:
            raise ValueError("Bản đồ phải có đúng một nhân vật (A hoặc +).")
        boxes = symbols.count("B") + symbols.count("C")
        goals = symbols.count("D") + symbols.count("C") + symbols.count("+")
        if boxes == 0 or boxes != goals:
            raise ValueError("Số thùng phải bằng số đích và lớn hơn 0.")

    @classmethod
    def from_file(cls, path: str | Path) -> "Level":
        path = Path(path)
        return cls(path.stem, tuple(path.read_text(encoding="utf-8-sig").splitlines()))

    @property
    def width(self) -> int:
        return max(map(len, self.rows))

    @property
    def height(self) -> int:
        return len(self.rows)


LEVELS = (
    Level("Kho gạch nhỏ", (
        "%%%%%%%",
        "%  C%%%",
        "%  %B %",
        "%D   D%",
        "% B% A%",
        "%% C  %",
        "%%%%%%%",
    )),
    Level("Sân tập", (
        "%%%%%%%",
        "%     %",
        "% D D %",
        "% B B %",
        "%  A  %",
        "%     %",
        "%%%%%%%",
    ), "Làm quen với những bước đẩy đầu tiên."),
)


@dataclass(frozen=True)
class Snapshot:
    player: Cell
    boxes: frozenset[Cell]
    moves: int
    pushes: int
    facing: str


class Board:
    """Only movement rules and history; deliberately has no solver."""

    def __init__(self, level: Level):
        self.level = level
        self.walls: set[Cell] = set()
        self.floor: set[Cell] = set()
        self.goals: set[Cell] = set()
        boxes: set[Cell] = set()
        player = (0, 0)
        for y, row in enumerate(level.rows):
            for x, symbol in enumerate(row):
                cell = (x, y)
                if symbol == "%":
                    self.walls.add(cell)
                    continue
                self.floor.add(cell)
                if symbol in "DC+":
                    self.goals.add(cell)
                if symbol in "BC":
                    boxes.add(cell)
                if symbol in "A+":
                    player = cell
        self.initial = Snapshot(player, frozenset(boxes), 0, 0, "South")
        self.history: list[Snapshot] = [self.initial]
        self.cursor = 0

    @property
    def state(self) -> Snapshot:
        return self.history[self.cursor]

    @property
    def completed(self) -> int:
        return len(self.state.boxes & self.goals)

    @property
    def won(self) -> bool:
        return self.completed == len(self.goals)

    @property
    def can_undo(self) -> bool:
        return self.cursor > 0

    @property
    def can_redo(self) -> bool:
        return self.cursor < len(self.history) - 1

    def move(self, direction: str) -> bool:
        dx, dy = DIRECTIONS[direction]
        old = self.state
        dest = (old.player[0] + dx, old.player[1] + dy)
        if dest not in self.floor:
            return False
        boxes = set(old.boxes)
        pushed = dest in boxes
        if pushed:
            beyond = (dest[0] + dx, dest[1] + dy)
            if beyond not in self.floor or beyond in boxes:
                return False
            boxes.remove(dest)
            boxes.add(beyond)
        self.history = self.history[:self.cursor + 1]
        self.history.append(Snapshot(dest, frozenset(boxes), old.moves + 1,
                                     old.pushes + int(pushed), direction))
        self.cursor += 1
        return True

    def undo(self) -> bool:
        if not self.can_undo:
            return False
        self.cursor -= 1
        return True

    def redo(self) -> bool:
        if not self.can_redo:
            return False
        self.cursor += 1
        return True

    def reset(self) -> None:
        self.history = [self.initial]
        self.cursor = 0
