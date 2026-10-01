"""Pygame application shell for the standalone Sokoban UI."""

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
# Prevent Windows display scaling from blurring the finished pixel canvas.
os.environ.setdefault("SDL_WINDOWS_DPI_AWARENESS", "permonitorv2")

import pygame as pg

from .model import Board, LEVELS, Level
from .renderer import BoardRenderer
from .replay import Replay
from .competition import CompetitiveBoard, COMPETITION_LEVEL

WIDTH, HEIGHT = 1280, 860
INK = "#3c2c23"
MUTED = "#73624f"
GREEN = "#58703d"
PAPER = "#d7c4a4"
BUTTON_HINTS = {
    "prev": "Màn trước · Page Up", "next": "Đổi màn · Page Down", "menu": "Chọn chế độ",
    "solve": "Tìm lời giải", "replay_prev": "Lùi một bước · ←", "replay_next": "Tiến một bước · →",
    "undo": "Hoàn tác · Z", "redo": "Làm lại · Y", "reset": "Chơi lại · R", "help": "Hướng dẫn · H / F1",
}


class SokobanApp:
    def __init__(self, levels=LEVELS, size=(WIDTH, HEIGHT)):
        pg.display.init()
        pg.font.init()
        self.screen = pg.display.set_mode(size, pg.RESIZABLE)
        pg.display.set_caption("Sokoban · Kho gạch nhỏ")
        self.canvas = pg.Surface(size)
        self.clock = pg.time.Clock()
        self.fonts: dict[tuple[int, bool], pg.font.Font] = {}
        self.font_regular = self._font_path(False)
        self.font_bold = self._font_path(True)
        self.levels = tuple(levels)
        self.level_index = 0
        self.algorithm = "UCS"
        self.solver = None
        self.replay = None
        self.page = "game"
        self.competition = None
        self.round_input = "20"
        self.setup_error = ""
        self.buttons: dict[str, tuple[pg.Rect, bool]] = {}
        self.mouse = (-1, -1)
        self.pressed_action = None
        self.pressed_until = 0
        self.running = True
        self.show_help = False
        self.previous = None
        self.animation_start = -1000
        self.toast = ""
        self.toast_until = 0
        self._load_level(0)
        pg.key.set_repeat(230, 145)
        icon = self.renderer.crates[False]
        pg.display.set_icon(pg.transform.scale(icon, (48, 56)))

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

    def card(self, rect, color="#fff2d8", radius=0, border="#8b6849"):
        rect = pg.Rect(rect)
        pg.draw.rect(self.canvas, "#b69a75", rect.move(4, 4))
        pg.draw.rect(self.canvas, color, rect)
        if border:
            pg.draw.rect(self.canvas, border, rect, 2)

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
        elif name in ("undo", "redo"):
            sign = -1 if name == "redo" else 1
            line([(sign*a, b) for a, b in [(-3, -7), (-8, -2), (-3, 3)]])
            line([(sign*a, b) for a, b in [(-7, -2), (3, -2), (7, 2), (7, 7)]])
        elif name == "reset":
            line([(-7, -2), (-7, 5), (-3, 8), (4, 8), (8, 4), (8, -4), (4, -8), (-2, -8)])
            line([(-7, -7), (-7, -1), (-1, -1)])
        elif name == "menu":
            for offset in (-6, 0, 6):
                line([(-8, offset), (8, offset)])
        elif name == "help":
            line([(-6, -5), (-6, -8), (4, -8), (7, -5), (7, -1), (0, 3), (0, 5)])
            pg.draw.rect(self.canvas, color, (x-1, y+8, 3, 3))
        elif name == "play":
            pg.draw.polygon(self.canvas, color, [(x-5, y-8), (x+8, y), (x-5, y+8)])
        elif name == "pause":
            for offset in (-7, 3):
                pg.draw.rect(self.canvas, color, (x+offset, y-8, 4, 16))
        elif name in ("step_back", "step_next"):
            sign = -1 if name == "step_back" else 1
            line([(sign*8, -8), (sign*8, 8)])
            pg.draw.polygon(self.canvas, color, [(x-sign*7, y-8), (x+sign*4, y), (x-sign*7, y+8)])
        elif name == "search":
            line([(-7, -3), (-7, -6), (-4, -9), (1, -9), (5, -5), (5, 0), (1, 4), (-4, 4), (-7, 1), (-7, -3)])
            line([(4, 3), (9, 8)], 3)
        elif name == "check":
            line([(-6, 0), (-1, 5), (7, -5)], 3)

    def button(self, key, rect, label="", enabled=True, primary=False, icon=None, small=False):
        rect = pg.Rect(rect)
        # Keep the existing logical hit-coordinate contract while drawing UI
        # directly at the current window size, without resampling Vietnamese text.
        left, top = self.logical_position(rect.topleft)
        right, bottom = self.logical_position(rect.bottomright)
        hit = pg.Rect(round(left), round(top), round(right-left), round(bottom-top))
        hover = enabled and not self.show_help and hit.collidepoint(self.mouse)
        pressed = (enabled and not self.show_help and self.pressed_action == key
                   and pg.time.get_ticks() < self.pressed_until)
        fill = GREEN if primary else "#f7ead0"
        if hover:
            fill = "#496331" if primary else "#efd4a0"
        if pressed:
            fill = "#dfb653"
        if not enabled:
            fill = "#e2d5bf"
        color = (INK if pressed else "#fff4d9" if primary else INK) if enabled else MUTED
        if not pressed:
            pg.draw.rect(self.canvas, "#b69a75", rect.move(0, 4))
        face = rect.move(0, 3 if pressed else 0)
        pg.draw.rect(self.canvas, fill, face)
        pg.draw.rect(self.canvas, "#846345" if enabled else "#aa967a", face, 2)
        if icon:
            self._icon(icon, (face.x+22 if label else face.centerx, face.centery), color)
        if label:
            size = 14 if small else 18 if face.height >= 52 else 16
            available = face.width-(44 if icon else 16 if face.width <= 64 else 24)
            while size > 14 and self.font(size, True).size(label)[0] > available:
                size -= 1
            while self.font(size, True).size(label)[0] > available:
                label = label[:-2].rstrip("…")+"…"
            rendered = self.font(size, True).render(label, True, color)
            offset = 10 if icon else 0
            self.canvas.blit(rendered, rendered.get_rect(center=(face.centerx+offset, face.centery-1)))
        self.buttons[key] = (hit, enabled)

    def _load_level(self, index):
        self.page = "game"
        self.competition = None
        self.level_index = index % len(self.levels)
        self.board = Board(self.levels[self.level_index])
        self.renderer = BoardRenderer(self.board)
        self.previous = None
        self.animation_start = -1000
        self.scene_cache_key = None
        self.scene_cache = None
        self.toast = ""
        self.replay = None

    def open_menu(self):
        if self.replay:
            self.replay.paused = True
        self.show_help = False
        self.page = "menu"
        pg.key.stop_text_input()

    def _start_competition(self):
        try:
            n = int(self.round_input)
            game = CompetitiveBoard(COMPETITION_LEVEL, (8, 5), n)
        except ValueError:
            self.setup_error = "Nhập số lượt n là số nguyên dương."
            return
        self.competition = game
        self.board = Board(game.level)
        self.renderer = BoardRenderer(self.board)
        self.replay = None
        self.previous = None
        self.animation_start = -1000
        self.scene_cache_key = None
        self.pending = [None, None]
        self.facings = ("South", "South")
        self.competition_history = [(game.state, self.facings)]
        self.competition_cursor = 0
        self.competition_paused = False
        self.toast = ""
        self.page = "game"
        pg.key.stop_text_input()

    def _advance_competition(self):
        game = self.competition
        if (self.page != "game" or not game or game.finished or self.show_help
                or self.competition_paused or not all(self.pending)
                or pg.time.get_ticks()-self.animation_start < 125):
            return
        self.previous = game.state
        self.facings = tuple(self.pending)
        game.step(self.facings)
        self.pending = [None, None]
        self.animation_start = pg.time.get_ticks()
        self.competition_cursor += 1
        self.competition_history = self.competition_history[:self.competition_cursor]
        self.competition_history.append((game.state, self.facings))

    def _competition_action(self, action):
        if action.startswith(("p1_", "p2_")):
            if not self.competition.finished:
                self.pending[int(action[1])-1] = action[3:]
                self._advance_competition()
        elif action == "play":
            self.competition_paused = not self.competition_paused
        elif action in ("undo", "redo"):
            cursor = self.competition_cursor+(-1 if action == "undo" else 1)
            if 0 <= cursor < len(self.competition_history):
                self.competition_cursor = cursor
                self.competition.state, self.facings = self.competition_history[cursor]
                self.previous = None
                self.pending = [None, None]
                self.competition_paused = True
        elif action in ("reset", "competition_restart"):
            self._start_competition()

    def load_solution(self, actions, total_cost, algorithm=None):
        """Install a complete external solution, paused at its starting state."""
        if algorithm is not None and algorithm not in ("UCS", "A*"):
            raise ValueError("Thuật toán phải là UCS hoặc A*.")
        replay = Replay(self.board, actions, total_cost)
        self.replay = replay
        if algorithm is not None:
            self.algorithm = algorithm
        self.previous = None
        self.animation_start = pg.time.get_ticks()
        self.toast = ""

    def _advance_replay(self):
        if (self.replay and not self.replay.paused and not self.show_help
                and pg.time.get_ticks()-self.animation_start >= 125):
            old = self.board.state
            if self.board.redo():
                self.previous = old
                self.animation_start = pg.time.get_ticks()
            if self.replay.finished:
                self.replay.paused = True

    def _message(self, value):
        self.toast = value
        self.toast_until = pg.time.get_ticks()+2300

    def act(self, action):
        if action == "help":
            if self.replay:
                self.replay.paused = True
            if self.competition:
                self.competition_paused = True
            self.show_help = not self.show_help
            return
        if self.show_help:
            return
        self.pressed_action = action
        self.pressed_until = pg.time.get_ticks()+125
        if action == "menu":
            self.open_menu()
            return
        if self.page == "menu":
            if action == "single":
                self._load_level(self.level_index)
            elif action == "dual":
                self.page = "setup"
                self.setup_error = ""
                pg.key.start_text_input()
            return
        if self.page == "setup":
            if action == "start":
                self._start_competition()
            return
        if self.competition:
            self._competition_action(action)
            return
        if action in ("UCS", "A*"):
            if action != self.algorithm:
                self.algorithm = action
                self.replay = None
                # A planned future must not remain as manual redo history.
                self.board.history = self.board.history[:self.board.cursor+1]
            return
        if action == "solve":
            if self.solver is None:
                self._message("Chưa có thuật toán được nối vào")
                return
            candidate = Board(self.board.level)
            candidate.initial = self.board.state
            candidate.history = [self.board.state]
            try:
                actions, cost = self.solver(candidate, self.algorithm)
                self.load_solution(actions, cost, self.algorithm)
            except Exception as exc:
                self._message(f"Không thể tải lời giải: {str(exc)[:65]}")
            return
        if action == "play":
            if self.replay and not self.replay.finished:
                self.replay.paused = not self.replay.paused
                self.animation_start = pg.time.get_ticks()
            return
        if action in ("replay_prev", "replay_next"):
            if self.replay:
                self.replay.paused = True
                old = self.board.state
                if getattr(self.board, "undo" if action == "replay_prev" else "redo")():
                    self.previous = old
                    self.animation_start = pg.time.get_ticks()
            return
        if action in ("North", "East", "South", "West"):
            if self.replay:
                return
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
            if self.replay:
                self.replay.paused = True
            getattr(self.board, action)()
            self.previous = None
            self.toast = ""
        elif action == "reset":
            self.replay = None
            self.board.reset()
            self.previous = None
            self._message("Đã đặt lại bàn chơi")
        elif action in ("next", "prev", "victory_next"):
            self._load_level(self.level_index+(-1 if action == "prev" else 1))

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
            self.draw()
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.pressed_action = None
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
        elif event.type == pg.TEXTINPUT and self.page == "setup":
            self.round_input = (self.round_input+''.join(c for c in event.text if c in "0123456789"))[:6]
            self.setup_error = ""
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.show_help:
                    self.show_help = False
                elif self.page == "setup":
                    self.open_menu()
                else:
                    self.running = False
                return
            if event.key in (pg.K_F1, pg.K_h):
                self.act("help")
                return
            if self.show_help:
                if event.key in (pg.K_F1, pg.K_h):
                    self.act("help")
                return
            if self.page == "menu":
                if event.key in (pg.K_1, pg.K_KP1):
                    self.act("single")
                elif event.key in (pg.K_2, pg.K_KP2):
                    self.act("dual")
                return
            if self.page == "setup":
                if event.key == pg.K_BACKSPACE:
                    self.round_input = self.round_input[:-1]
                elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                    self.act("start")
                return
            if event.key == pg.K_SPACE:
                if not getattr(event, "repeat", False):
                    self.act("play")
                return
            if self.competition:
                dual_controls = {pg.K_w: "p1_North", pg.K_s: "p1_South", pg.K_a: "p1_West", pg.K_d: "p1_East",
                                 pg.K_UP: "p2_North", pg.K_DOWN: "p2_South", pg.K_LEFT: "p2_West", pg.K_RIGHT: "p2_East",
                                 pg.K_z: "undo", pg.K_BACKSPACE: "undo", pg.K_y: "redo", pg.K_r: "reset"}
                if event.key in dual_controls:
                    self.act(dual_controls[event.key])
                return
            if self.replay and event.key in (pg.K_LEFT, pg.K_RIGHT):
                self.act("replay_prev" if event.key == pg.K_LEFT else "replay_next")
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
        w, _ = self.canvas.get_size()
        self.footer_height = 68
        if self.competition:
            game = self.competition
            self.header_height = 96
            pg.draw.rect(self.canvas, "#f4e6cc", (0, 0, w, self.header_height))
            self.text("Kho đôi · 2 tác nhân", 20, 14, 22, bold=True)
            self.button("menu", (w-64, 12, 44, 44), icon="menu")
            self.text(f"Lượt {game.state.steps}/{game.step_limit}", 20, 52, 16, bold=True)
            self.text(f"1 · Điểm {game.scores[0]}", 220, 52, 16, GREEN, True)
            self.text(f"2 · Điểm {game.scores[1]}", 350, 52, 16, "#855321", True)
            names = {None: "chờ chọn", "North": "lên", "East": "phải", "South": "xuống", "West": "trái"}
            for i in (0, 1):
                self.text(f"Tác nhân {i+1}: {names[self.pending[i]]}", 20+i*(w//2), 74, 14, MUTED)
            pg.draw.line(self.canvas, "#b69a75", (0, 95), (w, 95), 2)
            return
        narrow = w < 1000
        self.header_height = 96 if narrow else 70
        pg.draw.rect(self.canvas, "#f4e6cc", (0, 0, w, self.header_height))
        pg.draw.line(self.canvas, "#b69a75", (0, self.header_height-1), (w, self.header_height-1), 2)
        title_width = w-200 if narrow else w-620
        title = f"{self.level_index+1:02d}  {self.board.level.name}"
        while self.font(22, True).size(title)[0] > title_width:
            title = title[:-2].rstrip("…")+"…"
        self.text(title, 20, 12, 22, bold=True)
        self.button("prev", (w-180, 12, 44, 44), enabled=len(self.levels)>1, icon="West")
        self.button("next", (w-128, 12, 44, 44), enabled=len(self.levels)>1, icon="East")
        self.button("menu", (w-64, 12, 44, 44), icon="menu")
        stats_x, stats_y = (20, 62) if narrow else (w-526, 24)
        self.text(f"Đích {self.board.completed}/{len(self.board.goals)}", stats_x, stats_y, 16, "#855321", True)
        self.text(f"Bước {self.board.state.moves}", stats_x+124, stats_y, 16)
        self.text(f"Đẩy {self.board.state.pushes}", stats_x+238, stats_y, 16)
        rx, ry = (370, 54) if narrow else (20, 42)
        count = f"{self.replay.index}/{len(self.replay.actions)}" if self.replay else "—"
        cost = f"Chi phí {self.replay.total_cost}" if self.replay else "Chưa có lời giải"
        if narrow:
            self.text(f"Hành động {count}", rx, ry, 14, bold=True)
            self.text(cost, rx, ry+20, 13, MUTED)
        else:
            self.text(f"Hành động {count}   ·   {cost}", rx, ry, 14, MUTED)

    def _playback_controls(self, x, y):
        replay = self.replay
        self.button("replay_prev", (x, y, 44, 44), icon="step_back",
                    enabled=bool(replay and replay.index > 0))
        self.button("play", (x+52, y, 44, 44), enabled=bool(replay and not replay.finished),
                    icon="pause" if replay and not replay.paused else "play", primary=bool(replay))
        self.button("replay_next", (x+104, y, 44, 44), icon="step_next",
                    enabled=bool(replay and not replay.finished))

    def _board_view(self):
        w, h = self.canvas.get_size()
        game = self.competition
        state = game.state if game else self.board.state
        finished = game.finished if game else self.board.won
        self.board_area = pg.Rect(16, self.header_height+8, w-32,
                                  h-self.header_height-self.footer_height-18)
        if finished:
            self.board_area.height -= 60
        progress = min(1.0, max(0.0, (pg.time.get_ticks()-self.animation_start)/125))
        key = (state, self.previous if progress<1 else None, progress, self.board_area.size,
               self.facings if game else None)
        if key != self.scene_cache_key:
            scene = (self.renderer.render_competition(state, self.previous, progress, self.facings)
                     if game else self.renderer.render(state, self.previous, progress))
            ratio = min(self.board_area.width/scene.get_width(), self.board_area.height/scene.get_height())
            # Prefer whole screen pixels per art pixel only when the board
            # stays within 5% of the largest fit. Always use nearest-neighbor.
            units = int(ratio*self.renderer.PIXEL)
            integer_ratio = units/self.renderer.PIXEL
            if units >= 1 and integer_ratio >= ratio*.95:
                ratio = integer_ratio
            size = (max(1, round(scene.get_width()*ratio)), max(1, round(scene.get_height()*ratio)))
            self.scene_cache = pg.transform.scale(scene, size)
            self.scene_cache_key = key
        self.board_rect = self.scene_cache.get_rect(center=self.board_area.center)
        self.canvas.blit(self.scene_cache, self.board_rect)
        if game:
            # Number badges identify the two actors while preserving the PNG art.
            eased = 1-(1-progress)**3
            sx = self.board_rect.width/(self.renderer.size[0]*self.renderer.SCALE)
            sy = self.board_rect.height/(self.renderer.size[1]*self.renderer.SCALE)
            for i, (px, py) in enumerate(state.players):
                if self.previous and progress < 1:
                    ox, oy = self.previous.players[i]
                    px, py = ox+(px-ox)*eased, oy+(py-oy)*eased
                x = round(self.board_rect.x+(32+px*72+36)*2*sx)
                y = round(self.board_rect.y+(32+py*72-14)*2*sy)-18
                badge = pg.Rect(x-10, y, 20, 20)
                pg.draw.rect(self.canvas, GREEN if i == 0 else "#855321", badge)
                self.text(i+1, x, y-1, 14, "#fff4d9", True, center=True)
        if finished:
            y = self.board_area.bottom+10
            message = ("Hòa!" if game.winner is None else f"Tác nhân {game.winner+1} thắng!") if game else "Xong rồi!"
            self.text(message, w//2-200, y+5, 24, "#855321", True)
            # Distinct hit key keeps the top level switch clickable after victory.
            self.button("competition_restart" if game else "victory_next", (w//2+70, y, 140, 44),
                        "Chơi lại" if game else "Màn tiếp", bool(game) or len(self.levels)>1, primary=True)
        elif self.toast and pg.time.get_ticks()<self.toast_until:
            width = self.font(14).size(self.toast)[0]+32
            rect = pg.Rect((w-width)//2, self.board_area.bottom-40, width, 34)
            self.card(rect)
            self.text(self.toast, w//2, rect.y+6, 14, center=True)

    def _controls_panel(self):
        w, h = self.canvas.get_size()
        top = h-self.footer_height
        pg.draw.rect(self.canvas, "#f4e6cc", (0, top, w, self.footer_height))
        pg.draw.line(self.canvas, "#b69a75", (0, top), (w, top), 2)
        y = top+10
        if self.competition:
            x = (w-264)//2
            self.button("play", (x, y, 44, 44), enabled=not self.competition.finished,
                        icon="play" if self.competition_paused else "pause", primary=True)
            x += 64
            undo = self.competition_cursor > 0
            redo = self.competition_cursor < len(self.competition_history)-1
        else:
            x = (w-560)//2
            self.button("UCS", (x, y, 56, 44), "UCS", primary=self.algorithm == "UCS")
            self.button("A*", (x+64, y, 56, 44), "A*", primary=self.algorithm == "A*")
            self.button("solve", (x+128, y, 44, 44), enabled=self.solver is not None, icon="search")
            self._playback_controls(x+192, y)
            x += 360
            undo, redo = self.board.can_undo, self.board.can_redo
        for key, enabled in (("undo", undo), ("redo", redo), ("reset", True), ("help", True)):
            self.button(key, (x, y, 44, 44), enabled=enabled, icon=key)
            x += 52

    def _help_overlay(self):
        w, h = self.canvas.get_size()
        overlay = pg.Surface((w, h), pg.SRCALPHA)
        overlay.fill((60, 43, 30, 112))
        self.canvas.blit(overlay, (0, 0))
        rect = pg.Rect(0, 0, min(560, w-40), min(408, h-32))
        rect.center = (w//2, h//2)
        self.card(rect, "#fff2d8", border="#846345")
        x, y = rect.x+24, rect.y+20
        self.text("Cách chơi Sokoban", x, y, 23, "#855321", True)
        self.text("Chọn hướng cho cả hai; mỗi lượt đi đồng thời." if self.competition else
                  "Đẩy tất cả thùng đến ô đích vàng. Chỉ đẩy, không kéo.", x, y+50, 15)
        self.text("Đích thuộc 1: thùng xanh · thuộc 2: thùng vàng." if self.competition else
                  "Thùng đúng đích chuyển xanh và có dấu tích.", x, y+78, 15)
        instructions = (("Di chuyển tay", "Mũi tên / W A S D"),
                        ("Tạm dừng / phát", "Space"), ("Lùi / tiến lời giải", "← / →"),
                        ("Hoàn tác / tiến lại", "Z / Y (Backspace)"),
                        ("Chơi lại", "R"), ("Đổi màn", "Page Up / Page Down"), ("Hướng dẫn", "H / F1"))
        if self.competition:
            instructions = (("Tác nhân 1", "W A S D"), ("Tác nhân 2", "Mũi tên"),
                            ("Tạm dừng / tiếp tục", "Space"), ("Hoàn tác / tiến lại", "Z / Y (Backspace)"),
                            ("Chơi lại", "R"), ("Kết thúc", "Đúng n lượt, so điểm"), ("Đổi chế độ", "Nút Menu"))
        for index, (label, keys) in enumerate(instructions):
            row_y = y+126+index*28
            self.text(label, x, row_y, 15)
            self.text(keys, x+228, row_y, 15, "#855321", True)
        self.text("Esc hoặc bấm chuột để đóng", rect.centerx, rect.bottom-46, 14, MUTED, center=True)

    def draw(self):
        if self.page == "game":
            self._advance_replay()
            self._advance_competition()
        if self.canvas.get_size() != self.screen.get_size():
            self.canvas = pg.Surface(self.screen.get_size())
        self.canvas.fill(PAPER)
        self.buttons.clear()
        if self.page != "game":
            self._menu_view()
            return self.canvas
        self._header()
        self._board_view()
        self._controls_panel()
        if self.show_help:
            self._help_overlay()
        else:
            self._button_hint()
        return self.canvas

    def _button_hint(self):
        for key, (hit, _) in self.buttons.items():
            if not hit.collidepoint(self.mouse):
                continue
            hint = BUTTON_HINTS.get(key)
            if key == "play":
                paused = self.competition_paused if self.competition else not self.replay or self.replay.paused
                hint = ("Phát / tiếp tục" if paused else "Tạm dừng")+" · Space"
            if hint:
                w, h = self.canvas.get_size()
                scale = min(w/WIDTH, h/HEIGHT)
                x = round((w-WIDTH*scale)/2+hit.centerx*scale)
                top = round((h-HEIGHT*scale)/2+hit.top*scale)
                bottom = round((h-HEIGHT*scale)/2+hit.bottom*scale)
                image = self.font(14).render(hint, True, "#fff4d9")
                rect = image.get_rect().inflate(20, 14)
                rect.midbottom = (x, top-10)
                if rect.top < 8:
                    rect.top = bottom+10
                rect.clamp_ip(self.canvas.get_rect().inflate(-16, -16))
                pg.draw.rect(self.canvas, INK, rect)
                self.canvas.blit(image, image.get_rect(center=rect.center))
            break

    def _menu_view(self):
        w, h = self.canvas.get_size()
        rect = pg.Rect(0, 0, min(520, w-48), 360)
        rect.center = (w//2, h//2)
        self.card(rect)
        x, y = rect.x+32, rect.y+24
        width = rect.width-64
        self.text("Sokoban", rect.centerx, y, 32, "#855321", True, center=True)
        if self.page == "menu":
            self.text("Chọn chế độ chơi", rect.centerx, y+54, 17, MUTED, center=True)
            self.button("single", (x, y+104, width, 60), "1 tác nhân", primary=True)
            self.button("dual", (x, y+188, width, 60), "2 tác nhân")
            self.text("Phím 1 / 2 để chọn · Esc để thoát", rect.centerx, y+280, 14, MUTED, center=True)
        else:
            self.text("2 tác nhân · Số lượt n", rect.centerx, y+54, 18, bold=True, center=True)
            field = pg.Rect(x, y+94, width, 50)
            pg.draw.rect(self.canvas, "#f7ead0", field)
            pg.draw.rect(self.canvas, "#846345", field, 2)
            self.text(self.round_input+"|", field.x+16, field.y+10, 22, bold=True)
            self.text(self.setup_error or "Nhập n > 0, rồi bấm Bắt đầu hoặc Enter.", x, y+158, 14,
                      "#a4402c" if self.setup_error else MUTED)
            self.button("start", (x, y+202, width, 48), "Bắt đầu", primary=True)
            self.button("menu", (x, y+268, width, 40), "Quay lại")

    def present(self):
        self.screen.blit(self.draw(), (0, 0))
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
            app.open_menu()
            app.run(args.frames)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Không thể mở bàn chơi: {exc}\n")
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
