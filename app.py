"""Pygame application shell for the standalone Sokoban UI."""

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame as pg

from .model import Board, LEVELS, Level
from .renderer import BoardRenderer

WIDTH, HEIGHT = 1280, 860
INK = "#263d32"
MUTED = "#7b8476"
GREEN = "#486447"
PAPER = "#f7f7f1"


class SokobanApp:
    # The layout is authored at this size. Opening at the authored resolution
    # keeps Pygame's text and thin UI strokes pixel-sharp on the first frame.
    def __init__(self, levels=LEVELS, size=(WIDTH, HEIGHT)):
        pg.display.init()
        pg.font.init()
        self.screen = pg.display.set_mode(size, pg.RESIZABLE)
        pg.display.set_caption("Sokoban · Kho gạch nhỏ")
        self.canvas = pg.Surface((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.fonts: dict[tuple[int, bool], pg.font.Font] = {}
        self.font_regular = self._font_path(False)
        self.font_bold = self._font_path(True)
        self.levels = tuple(levels)
        self.level_index = 0
        self.buttons: dict[str, tuple[pg.Rect, bool]] = {}
        self.mouse = (-1, -1)
        self.running = True
        self.show_help = False
        self.previous = None
        self.animation_start = -1000
        self.toast = ""
        self.toast_until = 0
        self._load_level(0)
        pg.key.set_repeat(230, 145)
        icon = self.renderer.crates[False]
        pg.display.set_icon(pg.transform.smoothscale(icon, (48, 48)))

    @staticmethod
    def _font_path(bold):
        if sys.platform == "win32":
            candidate = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("segoeuib.ttf" if bold else "segoeui.ttf")
            if candidate.exists():
                return str(candidate)
        for name in ("Arial", "DejaVu Sans", "Liberation Sans"):
            path = pg.font.match_font(name, bold=bold)
            if path:
                return path
        return None

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = pg.font.Font(self.font_bold if bold else self.font_regular, size)
        return self.fonts[key]

    def text(self, value, x, y, size=16, color=INK, bold=False, center=False):
        image = self.font(size, bold).render(str(value), True, color)
        rect = image.get_rect(midtop=(x, y)) if center else image.get_rect(topleft=(x, y))
        self.canvas.blit(image, rect)
        return rect

    def card(self, rect, color="#ffffff", radius=20, border="#e0e4d8"):
        rect = pg.Rect(rect)
        pg.draw.rect(self.canvas, "#e9ebe2", rect.move(0, 3), border_radius=radius)
        pg.draw.rect(self.canvas, color, rect, border_radius=radius)
        if border:
            pg.draw.rect(self.canvas, border, rect, 1, border_radius=radius)

    def _icon(self, name, center, color, scale=1):
        x, y = center
        def line(points, width=2):
            pg.draw.lines(self.canvas, color, False,
                          [(x+int(a*scale), y+int(b*scale)) for a, b in points], width)
        if name in ("North", "East", "South", "West"):
            points = {"North": [(-6, 3), (0, -3), (6, 3)],
                      "South": [(-6, -3), (0, 3), (6, -3)],
                      "West": [(3, -6), (-3, 0), (3, 6)],
                      "East": [(-3, -6), (3, 0), (-3, 6)]}[name]
            line(points)
        elif name == "undo":
            line([(-6, 2), (-6, -5), (1, -5)])
            line([(-6, -5), (2, 3), (7, 3), (7, -2)])
        elif name == "reset":
            pg.draw.arc(self.canvas, color, (x-7, y-7, 15, 15), -.5, 4.8, 2)
            line([(-8, -7), (-8, -1), (-2, -1)])
        elif name == "check":
            line([(-6, 0), (-1, 5), (7, -5)], 3)

    def button(self, key, rect, label="", enabled=True, primary=False, icon=None, small=False):
        rect = pg.Rect(rect)
        hover = enabled and not self.show_help and rect.collidepoint(self.mouse)
        fill = ("#3b563b" if hover else GREEN) if primary else ("#e8ede2" if hover else "#f6f7f1")
        if not enabled:
            fill = "#f5f5f0"
        color = "#ffffff" if primary else INK
        if not enabled:
            color = "#adb3a6"
        pg.draw.rect(self.canvas, fill, rect, border_radius=11)
        if not primary:
            pg.draw.rect(self.canvas, "#e1e5da" if enabled else "#eceee6", rect, 1, border_radius=11)
        if icon:
            self._icon(icon, (rect.x+25 if label else rect.centerx, rect.centery), color)
        if label:
            rendered = self.font(13 if small else 15, True).render(label, True, color)
            offset = 10 if icon else 0
            self.canvas.blit(rendered, rendered.get_rect(center=(rect.centerx+offset, rect.centery-1)))
        self.buttons[key] = (rect, enabled)

    def _load_level(self, index):
        self.level_index = index % len(self.levels)
        self.board = Board(self.levels[self.level_index])
        self.renderer = BoardRenderer(self.board)
        self.previous = None
        self.animation_start = -1000
        self.scene_cache_key = None
        self.scene_cache = None
        self.toast = ""

    def _message(self, value):
        self.toast = value
        self.toast_until = pg.time.get_ticks()+2300

    def act(self, action):
        if action == "help":
            self.show_help = not self.show_help
            return
        if self.show_help:
            return
        if action in ("North", "East", "South", "West"):
            if pg.time.get_ticks()-self.animation_start < 125:
                return
            old = self.board.state
            if self.board.move(action):
                self.previous = old
                self.animation_start = pg.time.get_ticks()
                self.toast = ""
            else:
                self._message("Lối đi bị chặn")
        elif action in ("undo", "redo"):
            getattr(self.board, action)()
            self.previous = None
            self.toast = ""
        elif action == "reset":
            self.board.reset()
            self.previous = None
            self._message("Đã đặt lại bàn chơi")
        elif action in ("next", "prev"):
            self._load_level(self.level_index+(1 if action == "next" else -1))

    def logical_position(self, pos):
        w, h = self.screen.get_size()
        scale = min(w/WIDTH, h/HEIGHT)
        return ((pos[0]-(w-WIDTH*scale)/2)/scale,
                (pos[1]-(h-HEIGHT*scale)/2)/scale)

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.VIDEORESIZE:
            self.screen = pg.display.set_mode((max(640, event.w), max(430, event.h)), pg.RESIZABLE)
        elif event.type == pg.MOUSEMOTION:
            self.mouse = self.logical_position(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            pos = self.logical_position(event.pos)
            if self.show_help:
                self.show_help = False
                return
            for key, (rect, enabled) in self.buttons.items():
                if enabled and rect.collidepoint(pos):
                    self.act(key)
                    break
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.show_help:
                    self.show_help = False
                else:
                    self.running = False
                return
            if event.key in (pg.K_F1, pg.K_h):
                self.act("help")
                return
            controls = {
                pg.K_UP: "North", pg.K_w: "North", pg.K_DOWN: "South", pg.K_s: "South",
                pg.K_LEFT: "West", pg.K_a: "West", pg.K_RIGHT: "East", pg.K_d: "East",
                pg.K_z: "undo", pg.K_BACKSPACE: "undo", pg.K_y: "redo", pg.K_r: "reset",
                pg.K_PAGEUP: "prev", pg.K_PAGEDOWN: "next",
            }
            if event.key in controls:
                self.act(controls[event.key])

    def _header(self):
        pg.draw.rect(self.canvas, "#e6ecdc", (42, 30, 50, 50), border_radius=14)
        crate = pg.transform.smoothscale(self.renderer.crates[False], (43, 46))
        self.canvas.blit(crate, (46, 29))
        self.text("Sokoban", 108, 27, 28, bold=True)
        self.text("XẾP GỌN TỪNG BƯỚC", 109, 64, 10, MUTED, True)
        pg.draw.circle(self.canvas, "#729364", (980, 55), 4)
        self.text("Chơi một người", 994, 43, 15, MUTED)
        self.button("help", (1136, 34, 102, 42), "Cách chơi", small=True)
        pg.draw.line(self.canvas, "#dfe3d6", (42, 105), (1238, 105))
        self.text(f"BÀN CHƠI {self.level_index+1:02d} / {len(self.levels):02d}", 43, 129, 11, GREEN, True)
        # Fit user-provided filenames without colliding with navigation.
        title = self.board.level.name
        title_size = 36
        while title_size > 18 and self.font(title_size, True).size(title)[0] > 760:
            title_size -= 1
        while self.font(title_size, True).size(title)[0] > 760:
            title = title[:-2].rstrip("…")+"…"
        self.text(title, 41, 151, title_size, bold=True)
        self.text(self.board.level.subtitle, 44, 204, 15, MUTED)
        self.text("CHỌN BÀN", 1029, 164, 10, MUTED, True)
        self.button("prev", (1136, 154, 46, 44), enabled=len(self.levels)>1, icon="West")
        self.button("next", (1192, 154, 46, 44), enabled=len(self.levels)>1, icon="East")

    def _board_view(self):
        self.card((42, 246, 766, 540), "#e9edde", 24, "#dde3d2")
        # Small garden details frame the playfield without competing with it.
        for x, y, radius in ((82, 703, 3), (95, 712, 2), (754, 320, 3), (741, 332, 2)):
            pg.draw.circle(self.canvas, "#cdd6bc", (x, y), radius)
        self.text("01" if self.level_index == 0 else f"{self.level_index+1:02d}", 67, 266, 16, "#9caa8c", True)
        progress = min(1.0, max(0.0, (pg.time.get_ticks()-self.animation_start)/125))
        key = (self.board.state, self.previous if progress<1 else None, progress)
        if key != self.scene_cache_key:
            scene = self.renderer.render(self.board.state, self.previous, progress)
            ratio = min(518/scene.get_width(), 518/scene.get_height())
            self.scene_cache = pg.transform.smoothscale(scene, (round(scene.get_width()*ratio), round(scene.get_height()*ratio)))
            self.scene_cache_key = key
        rect = self.scene_cache.get_rect(center=(425, 516))
        # The board PNG already includes its edge and tight contact shadow.
        self.canvas.blit(self.scene_cache, rect)
        if self.toast and pg.time.get_ticks()<self.toast_until:
            width = self.font(14).size(self.toast)[0]+36
            self.card((425-width//2, 719, width, 39), "#ffffff", 12)
            self.text(self.toast, 425, 728, 14, GREEN, center=True)

    def _progress_panel(self):
        self.card((838, 246, 400, 250))
        self.text("THÙNG VỀ ĐÍCH", 866, 269, 11, MUTED, True)
        self.text(f"{self.board.completed:02d}", 862, 291, 52, GREEN, True)
        self.text(f"/ {len(self.board.goals):02d}", 940, 316, 23, "#a4ad9c")
        crate = pg.transform.smoothscale(self.renderer.crates[True], (66, 70))
        self.canvas.blit(crate, (1145, 282))
        self.text("Hoàn thành! Thật gọn gàng." if self.board.won else "Mỗi chiếc thùng, một vị trí.", 867, 361, 14, MUTED)
        pg.draw.rect(self.canvas, "#eaf0e4", (866, 397, 344, 7), border_radius=4)
        fill = round(344*self.board.completed/len(self.board.goals))
        if fill:
            pg.draw.rect(self.canvas, "#7f9d66", (866, 397, fill, 7), border_radius=4)
        self.text("BƯỚC ĐI", 867, 425, 10, MUTED, True)
        self.text(self.board.state.moves, 867, 443, 25, bold=True)
        pg.draw.line(self.canvas, "#e5e9df", (1025, 426), (1025, 472))
        self.text("LẦN ĐẨY", 1054, 425, 10, MUTED, True)
        self.text(self.board.state.pushes, 1054, 443, 25, bold=True)

    def _controls_panel(self):
        self.card((838, 514, 400, 272))
        self.text("Điều khiển", 866, 536, 20, bold=True)
        self.text("Mũi tên hoặc W A S D để di chuyển.", 867, 571, 14, MUTED)
        self.button("undo", (866, 611, 157, 45), "Hoàn tác", self.board.can_undo, icon="undo")
        self.button("reset", (1035, 611, 175, 45), "Chơi lại", primary=True, icon="reset")
        self.button("North", (912, 671, 40, 40), icon="North")
        self.button("West", (866, 717, 40, 40), icon="West")
        self.button("South", (912, 717, 40, 40), icon="South")
        self.button("East", (958, 717, 40, 40), icon="East")
        self.text("Z  hoàn tác   ·   R  chơi lại", 1023, 685, 12, MUTED)
        self.button("redo", (1023, 719, 187, 36), "Tiến lại một bước  ·  Y", self.board.can_redo, small=True)

    def _footer(self):
        # Compact legend uses the same visual language as the board.
        pg.draw.circle(self.canvas, "#d5c84d", (52, 822), 5)
        self.text("Vị trí đích", 65, 811, 12, MUTED)
        pg.draw.rect(self.canvas, "#70b9c6", (158, 817, 11, 11), border_radius=2)
        self.text("Thùng đúng vị trí", 180, 811, 12, MUTED)
        self.text("Chỉ đẩy thùng, không kéo. Bạn luôn có thể thử lại.", 838, 811, 12, MUTED)

    def _help_overlay(self):
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((26, 41, 32, 100))
        self.canvas.blit(overlay, (0, 0))
        self.card((373, 210, 534, 424), "#fdfdf7", 24)
        self.text("Cách chơi Sokoban", 407, 239, 27, bold=True)
        self.text("Đẩy tất cả các thùng đến những ô đích màu vàng.", 409, 291, 16, MUTED)
        self.text("Thùng đúng vị trí sẽ chuyển sang màu xanh.", 409, 319, 16, MUTED)
        instructions = (("Di chuyển", "Mũi tên / W A S D"), ("Hoàn tác / tiến lại", "Z / Y"),
                        ("Chơi lại", "R"), ("Đổi bàn chơi", "Page Up / Page Down"))
        for index, (label, keys) in enumerate(instructions):
            y = 374+index*39
            self.text(label, 409, y, 15)
            self.text(keys, 641, y, 15, GREEN, True)
        self.text("Bạn chỉ có thể đẩy một thùng mỗi lần, không thể kéo.", 409, 547, 14, MUTED)
        self.text("Nhấn Esc hoặc bấm chuột để đóng", 640, 589, 13, MUTED, center=True)

    def draw(self):
        self.canvas.fill(PAPER)
        self.buttons.clear()
        self._header()
        self._board_view()
        self._progress_panel()
        self._controls_panel()
        self._footer()
        if self.show_help:
            self._help_overlay()
        return self.canvas

    def present(self):
        self.draw()
        w, h = self.screen.get_size()
        scale = min(w/WIDTH, h/HEIGHT)
        size = (round(WIDTH*scale), round(HEIGHT*scale))
        self.screen.fill(PAPER)
        position = ((w-size[0])//2, (h-size[1])//2)
        if size == (WIDTH, HEIGHT):
            # Do not resample the authored canvas at native resolution.
            self.screen.blit(self.canvas, position)
        else:
            # Resizing is still supported, but nearest scaling avoids the
            # soft interpolation that made text and card borders look hazy.
            image = pg.transform.scale(self.canvas, size)
            self.screen.blit(image, position)
        pg.display.flip()

    def run(self, frames=None):
        count = 0
        self.draw()  # Establish hit regions before processing the first click.
        while self.running:
            for event in pg.event.get():
                self.handle_event(event)
            self.present()
            self.clock.tick(60)
            count += 1
            if frames is not None and count >= frames:
                break


def main():
    parser = argparse.ArgumentParser(description="Giao diện Sokoban 2.5D, chơi thử bằng tay.")
    parser.add_argument("--map", type=Path, help="Đọc bản đồ %% A B D C từ file UTF-8.")
    parser.add_argument("--screenshot", type=Path, help="Xuất ảnh giao diện rồi thoát, không mở cửa sổ.")
    parser.add_argument("--frames", type=int, help="Thoát sau N khung hình, dùng kiểm tra khởi động.")
    args = parser.parse_args()
    if args.screenshot:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    try:
        levels = (Level.from_file(args.map),) if args.map else LEVELS
        app = SokobanApp(levels)
        if args.screenshot:
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            pg.image.save(app.draw(), str(args.screenshot))
            print(f"Đã lưu: {args.screenshot.resolve()}")
        else:
            app.run(args.frames)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Không thể mở bàn chơi: {exc}\n")
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
