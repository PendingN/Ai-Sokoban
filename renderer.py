"""Asset-only board renderer for the Sokoban interface."""

import math
from pathlib import Path

import pygame as pg

from .model import Board, Snapshot


class BoardRenderer:
    """Compose checked-in PNG assets into an animated board surface.

    The renderer owns no drawing primitives and never creates replacement art.
    Visual changes are made by replacing files in ``assets/``.
    """

    TILE = 72
    MARGIN = 32
    SCALE = 2
    WALL_HEIGHT = 12
    ASSET_SIZES = {
        "board_frame": (512, 512),
        "floor": (144, 144),
        "wall_top": (144, 144),
        "wall_front": (144, 24),
        "goal": (144, 144),
        "box": (144, 168),
        "box_goal": (144, 168),
        **{f"player_{direction}": (144, 176)
           for direction in ("north", "east", "south", "west")},
    }
    ASSET_NAMES = tuple(ASSET_SIZES)
    DIRECTIONS = ("North", "East", "South", "West")

    def __init__(self, board: Board):
        self.board = board
        self.tile = self.TILE
        self.size = (board.level.width * self.tile + self.MARGIN * 2,
                     board.level.height * self.tile + self.MARGIN * 2)
        self.asset_dir = Path(__file__).with_name("assets")
        self.assets = self._load_assets()
        self.walls = self._wall_sprites()
        self.crates = {
            False: self.assets["box"],
            True: self.assets["box_goal"],
        }
        self.people = {
            direction: self.assets[f"player_{direction.lower()}"]
            for direction in self.DIRECTIONS
        }
        self.ground = self._ground()

    def _load_assets(self) -> dict[str, pg.Surface]:
        missing = [
            name for name in self.ASSET_NAMES
            if not (self.asset_dir / f"{name}.png").is_file()
        ]
        if missing:
            names = ", ".join(f"{name}.png" for name in missing)
            raise FileNotFoundError(
                f"Thiếu Sokoban image asset: {names}. "
                "Hãy khôi phục thư mục sokoban_ui/assets."
            )
        try:
            assets = {
                name: pg.image.load(self.asset_dir / f"{name}.png").convert_alpha()
                for name in self.ASSET_NAMES
            }
        except (OSError, pg.error) as exc:
            raise RuntimeError(
                f"Không thể tải image asset trong {self.asset_dir}."
            ) from exc
        for name, expected in self.ASSET_SIZES.items():
            if assets[name].get_size() != expected:
                raise ValueError(
                    f"Asset {name}.png phải có kích thước {expected}, "
                    f"nhận được {assets[name].get_size()}."
                )
        return assets

    def _blit(self, surface: pg.Surface, image: pg.Surface,
              position: tuple[float, float]) -> None:
        surface.blit(
            image,
            (round(position[0] * self.SCALE), round(position[1] * self.SCALE)),
        )

    def _wall_sprites(self) -> dict[tuple[int, int], pg.Surface]:
        """Join wall tops without seams; show depth only at exposed fronts."""
        top = self.assets["wall_top"]
        front = self.assets["wall_front"]
        exposed = pg.Surface((top.get_width(), top.get_height() + front.get_height()),
                             pg.SRCALPHA)
        exposed.blit(top, (0, 0))
        exposed.blit(front, (0, top.get_height()))
        return {
            (x, y): top if (x, y + 1) in self.board.walls else exposed
            for x, y in self.board.walls
        }

    def _backdrop(self, size: tuple[int, int]) -> pg.Surface:
        """Nine-slice the PNG border, retaining its transparent rounded corners."""
        frame = self.assets["board_frame"]
        surface = pg.Surface(size, pg.SRCALPHA)
        cap = 64
        source_x = (0, cap, frame.get_width() - cap, frame.get_width())
        source_y = (0, cap, frame.get_height() - cap, frame.get_height())
        dest_x = (0, cap, size[0] - cap, size[0])
        dest_y = (0, cap, size[1] - cap, size[1])
        for row in range(3):
            for column in range(3):
                source = pg.Rect(source_x[column], source_y[row],
                                 source_x[column + 1] - source_x[column],
                                 source_y[row + 1] - source_y[row])
                dest = pg.Rect(dest_x[column], dest_y[row],
                               dest_x[column + 1] - dest_x[column],
                               dest_y[row + 1] - dest_y[row])
                patch = frame.subsurface(source)
                if patch.get_size() != dest.size:
                    patch = pg.transform.smoothscale(patch, dest.size)
                surface.blit(patch, dest)
        return surface

    def _ground(self) -> pg.Surface:
        """Tile the asset-only backdrop and floor layer once per board."""
        output_size = (self.size[0] * self.SCALE, self.size[1] * self.SCALE)
        surface = self._backdrop(output_size)

        for y, row in enumerate(self.board.level.rows):
            for x, _ in enumerate(row):
                position = (self.MARGIN + x * self.tile,
                            self.MARGIN + y * self.tile)
                self._blit(surface, self.assets["floor"], position)
                if (x, y) in self.board.goals:
                    self._blit(surface, self.assets["goal"], position)
        return surface

    def render(self, state: Snapshot, previous: Snapshot | None = None,
               progress: float = 1.0) -> pg.Surface:
        """Return one frame for ``state`` using only loaded image assets."""
        surface = self.ground.copy()
        t, m = self.tile, self.MARGIN
        progress = max(0.0, min(1.0, progress))
        eased = 1 - (1 - progress) ** 3
        px, py = state.player
        removed, added = set(), set()

        if previous and progress < 1:
            px = previous.player[0] + (px - previous.player[0]) * eased
            py = previous.player[1] + (py - previous.player[1]) * eased
            removed = previous.boxes - state.boxes
            added = state.boxes - previous.boxes

        objects = []
        for (x, y), wall in self.walls.items():
            objects.append((y, 0, wall, (m + x * t, m + y * t - self.WALL_HEIGHT)))

        for x, y in state.boxes:
            bx, by = float(x), float(y)
            on_goal = (x, y) in self.board.goals
            if (x, y) in added and len(removed) == 1:
                old_x, old_y = next(iter(removed))
                bx = old_x + (x - old_x) * eased
                by = old_y + (y - old_y) * eased
                # Keep the departure appearance until the push reaches its end.
                on_goal = (old_x, old_y) in self.board.goals
            sprite = self.crates[on_goal]
            objects.append((by, 1, sprite,
                            (m + bx * t, m + by * t - 12)))

        bob = math.sin(progress * math.pi) * 2 if previous and progress < 1 else 0
        objects.append((py, 2, self.people[state.facing],
                        (m + px * t, m + py * t - 16 - bob)))

        for _, _, sprite, position in sorted(objects, key=lambda item: (item[0], item[1])):
            self._blit(surface, sprite, position)
        return surface
