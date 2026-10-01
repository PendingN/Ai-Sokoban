"""Run from 02_BaiTap_Lab: python -m sokoban_ui.check_presentation.

Checks UI events and exports real Pygame surfaces for visual review.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from pathlib import Path
import tempfile

import pygame as pg

from .app import SokobanApp, WIDTH, HEIGHT, PAPER
from .model import Level


def main():
    output = Path(__file__).parent
    app = SokobanApp()
    assert app.screen.get_size() == (1280, 860)

    # Fill the available space unless integer art pixels cost at most 5%.
    # 597/598 straddle the exact snap threshold for the 568-pixel scene.
    for height, expected in ((860, 704), (753, 568), (754, 598)):
        app.handle_event(pg.event.Event(pg.VIDEORESIZE, w=1280, h=height))
        assert app.board_rect.size == (expected, expected), (height, app.board_rect)
    app.handle_event(pg.event.Event(pg.VIDEORESIZE, w=1280, h=860))

    def screen_rect(rect):
        w, h = app.screen.get_size()
        scale = min(w/WIDTH, h/HEIGHT)
        return pg.Rect(round((w-WIDTH*scale)/2+rect.x*scale),
                       round((h-HEIGHT*scale)/2+rect.y*scale),
                       round(rect.width*scale), round(rect.height*scale))

    def click(key):
        app.draw()
        rect, enabled = app.buttons[key]
        assert enabled, key
        app.animation_start = -1000
        app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=screen_rect(rect).center, button=1))
        app.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1))

    def save(name):
        app.previous = None
        app.pressed_until = 0
        app.present()
        pg.image.save(app.screen, str(output/name))

    # Audit actual text bounds instead of only comparing nominal layout values.
    original_text = app.text
    def checked_text(*args, **kwargs):
        rect = original_text(*args, **kwargs)
        assert app.canvas.get_rect().contains(rect), (args[0], rect, app.canvas.get_size())
        return rect
    app.text = checked_text
    original_button = app.button
    def checked_button(key, rect, label="", *args, **kwargs):
        rect = pg.Rect(rect)
        if label:
            size = 14 if kwargs.get("small") else 18 if rect.height >= 52 else 16
            padding = 44 if kwargs.get("icon") else 16 if rect.width <= 64 else 24
            width, height = app.font(size, True).size(label)
            assert width <= rect.width-padding and height <= rect.height-8, (key, label, rect)
        original_button(key, rect, label, *args, **kwargs)
    app.button = checked_button

    # Every compact control has a visible, distinct glyph without new assets.
    canvas = app.canvas
    app.canvas = pg.Surface((48, 48))
    glyphs = set()
    for icon in ("undo", "redo", "reset", "menu", "help", "play", "pause", "step_back", "step_next", "search"):
        app.canvas.fill(PAPER)
        blank = pg.image.tobytes(app.canvas, "RGB")
        app._icon(icon, (24, 24), "#3c2c23")
        glyph = pg.image.tobytes(app.canvas, "RGB")
        assert glyph != blank and glyph not in glyphs, icon
        glyphs.add(glyph)
    app.canvas = canvas

    save("preview.png")
    app.handle_event(pg.event.Event(pg.MOUSEMOTION, pos=screen_rect(app.buttons["reset"][0]).center))
    hinted = pg.image.tobytes(app.draw(), "RGB")
    save("preview_tooltip.png")
    app.mouse = (-1, -1)
    assert hinted != pg.image.tobytes(app.draw(), "RGB")
    click("next")
    save("preview_level2.png")
    for direction in ("North", "East", "South", "West"):
        assert direction not in app.buttons
        before = app.board.state.moves
        app.animation_start = -1000
        app.handle_event(pg.event.Event(pg.KEYDOWN, key={"North": pg.K_UP, "East": pg.K_RIGHT,
                                                       "South": pg.K_DOWN, "West": pg.K_LEFT}[direction]))
        assert app.board.state.moves == before+1
    click("undo")
    click("redo")
    click("reset")
    assert app.board.state == app.board.initial

    # The pressed frame has a distinct face color and a lowered hard edge.
    app.draw()
    rect = screen_rect(app.buttons["reset"][0])
    released = pg.image.tobytes(app.canvas.subsurface(rect), "RGB")
    app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=rect.center, button=1))
    app.draw()
    assert released != pg.image.tobytes(app.canvas.subsurface(rect), "RGB")
    pg.image.save(app.canvas, str(output/"preview_pressed.png"))
    app.handle_event(pg.event.Event(pg.MOUSEBUTTONUP, button=1))

    # Fast repeated movement remains gated by the original 125 ms timing.
    app.animation_start = -1000
    app.act("North")
    state = app.board.state
    app.act("South")
    assert app.board.state == state
    app.act("reset")

    click("help")
    state, index = app.board.state, app.level_index
    for action in ("North", "East", "South", "West", "undo", "redo", "reset", "next", "prev", "victory_next"):
        app.act(action)
        assert app.show_help and app.board.state == state and app.level_index == index
    save("preview_help.png")
    # Clicking the level switch while the modal is open only dismisses it.
    click("next")
    assert not app.show_help and app.level_index == index and app.board.state == state

    def win():
        app._load_level(1)
        for direction in ("West", "North", "South", "East", "East", "North"):
            app.animation_start = -1000
            app.act(direction)
        assert app.board.won and app.level_index == 1
        assert (app.board.state.moves, app.board.state.pushes) == (6, 2)

    win()
    save("preview_victory.png")
    assert app.buttons["next"][0] != app.buttons["victory_next"][0]
    click("undo")
    assert not app.board.won
    click("redo")
    assert app.board.won
    click("next")
    assert app.level_index == 0
    win()
    click("victory_next")
    assert app.level_index == 0

    for size in ((720, 900), (960, 645), (999, 645), (1000, 645), (1280, 500), (1280, 1000), (640, 430)):
        app.handle_event(pg.event.Event(pg.VIDEORESIZE, w=size[0], h=size[1]))
        assert app.canvas.get_size() == size
        assert app.board_area.contains(app.board_rect)
        for rect, _ in app.buttons.values():
            assert app.canvas.get_rect().contains(screen_rect(rect))
        rectangles = [screen_rect(rect) for rect, _ in app.buttons.values()]
        for index, rect in enumerate(rectangles):
            assert not any(rect.colliderect(other) for other in rectangles[index+1:])
        click("next")
        assert app.level_index == 1
        click("prev")
        assert app.level_index == 0
        click("help")
        app.present()
        if size == (640, 430):
            save("preview_help_small.png")
        app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE))
        assert app.running and not app.show_help
        if size == (720, 900):
            save("preview_narrow.png")
        elif size == (1280, 500):
            save("preview_short.png")
        elif size == (640, 430):
            app.handle_event(pg.event.Event(pg.MOUSEMOTION, pos=screen_rect(app.buttons["help"][0]).center))
            save("preview_tooltip_small.png")
            app.mouse = (-1, -1)
        win()
        app.present()
        click("next")
        assert app.level_index == 0

    app.handle_event(pg.event.Event(pg.VIDEORESIZE, w=1280, h=860))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/"Kho dài.txt"
        path.write_text("%%%%%%%%%%%%\n% A B  D   %\n%          %\n%%%%%%%%%%%%\n", encoding="utf-8")
        app.levels = (Level.from_file(path),)
        app._load_level(0)
        save("preview_rectangular.png")
        app.levels = (Level("Kho cao", ("%%%%", "%AB%", "% D%", "%  %", "%  %", "%  %", "%%%%")),)
        app._load_level(0)
        save("preview_tall.png")

    # Asset export retains the old anchors, canvas sizes and hard alpha edges.
    for name, expected in app.renderer.ASSET_SIZES.items():
        sprite = app.renderer.assets[name]
        assert sprite.get_size() == expected
        assert {sprite.get_at((x, y)).a for y in range(sprite.get_height()) for x in range(sprite.get_width())} <= {0, 255}
        if name in ("box", "box_goal"):
            assert sprite.get_bounding_rect().bottom == 156
        elif name.startswith("player_"):
            assert sprite.get_bounding_rect().bottom == 162
    # Protect the retained generated shading from the old 12-color reduction.
    worker = app.renderer.assets["player_south"]
    assert len({tuple(worker.get_at((x, y))) for y in range(worker.get_height())
                for x in range(worker.get_width()) if worker.get_at((x, y)).a}) > 16

    # Refresh the art contact sheet alongside the actual gameplay previews.
    sheet = pg.Surface((960, 720))
    sheet.fill(PAPER)
    for index, (name, sprite) in enumerate(app.renderer.assets.items()):
        cell = pg.Rect(index % 4 * 240, index // 4 * 240, 240, 240)
        ratio = min(1, 216/sprite.get_width(), 188/sprite.get_height())
        size = (round(sprite.get_width()*ratio), round(sprite.get_height()*ratio))
        image = pg.transform.scale(sprite, size)
        sheet.blit(image, image.get_rect(center=(cell.centerx, cell.y+104)))
        label = app.font(16, True).render(name, True, "#3c2c23")
        sheet.blit(label, label.get_rect(midtop=(cell.centerx, cell.y+208)))
    pg.image.save(sheet, str(output/"preview_assets.png"))
    pg.quit()
    print("Presentation checks passed: scale, buttons, modal, victory, resize, rectangles, anchors; previews exported.")


if __name__ == "__main__":
    main()
