"""Run: python -m sokoban_ui.check_requirements (no solver required)."""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from copy import copy
from dataclasses import replace
from itertools import product
from pathlib import Path
from unittest.mock import patch

import pygame as pg

from .app import SokobanApp, WIDTH, HEIGHT, main as run_app
from .competition import CompetitiveBoard
from .model import Board, DIRECTIONS, LEVELS, Level
from .renderer import BoardRenderer


def check_menu(app):
    def click(key):
        app.draw()
        rect, enabled = app.buttons[key]
        assert enabled
        w, h = app.screen.get_size()
        scale = min(w/WIDTH, h/HEIGHT)
        pos = (round((w-WIDTH*scale)/2+rect.centerx*scale),
               round((h-HEIGHT*scale)/2+rect.centery*scale))
        app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=pos, button=1))

    def save(name):
        app.pressed_until = 0
        frame = app.draw()
        assert not any(key in DIRECTIONS or key.startswith(("p1_", "p2_")) for key in app.buttons)
        rectangles = [rect for rect, _ in app.buttons.values()]
        for index, rect in enumerate(rectangles):
            assert not any(rect.colliderect(other) for other in rectangles[index+1:])
        pg.image.save(frame, str(Path(__file__).with_name(name)))

    for size, suffix in (((1280, 860), ""), ((720, 900), "_narrow"),
                         ((1280, 500), "_short"), ((640, 430), "_small")):
        app.handle_event(pg.event.Event(pg.VIDEORESIZE, w=size[0], h=size[1]))
        app.open_menu()
        save(f"preview_menu{suffix}.png")
        click("single")
        assert app.page == "game" and app.competition is None
        click("menu")
        assert app.page == "menu"
        click("dual")
        assert app.page == "setup"
        app.round_input = "0"
        click("start")
        assert app.page == "setup" and app.setup_error
        app.round_input = ""
        app.handle_event(pg.event.Event(pg.TEXTINPUT, text="2xyz"))
        assert app.round_input == "2"
        app.setup_error = ""
        save(f"preview_setup{suffix}.png")
        click("start")
        assert app.page == "game" and app.competition.step_limit == 2
        initial = app.competition.state
        with patch("pygame.time.get_ticks", return_value=1000):
            app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_d))
            assert app.competition.state == initial and app.pending == ["East", None]
            app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
            assert app.competition.state.steps == 1
            first = app.competition.state
            app.act("p1_South")
            app.act("p2_North")
        with patch("pygame.time.get_ticks", return_value=1124):
            app.draw()
            assert app.competition.state == first
            click("help")
            for action in ("p1_East", "p2_West", "play", "menu", "reset", "undo"):
                app.act(action)
            assert app.show_help and app.page == "game" and app.competition.state == first
            save(f"preview_competition_help{suffix}.png")
            app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE))
        with patch("pygame.time.get_ticks", return_value=2000):
            app.draw()
            assert app.competition.state == first and app.competition_paused
            save(f"preview_competition{suffix}.png")
            click("play")
            app.draw()
            assert app.competition.finished and app.competition.state.steps == 2
            final = app.competition.state
            save(f"preview_competition_end{suffix}.png")
            app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_w))
            assert app.competition.state == final
            click("undo")
            assert app.competition.state == first and app.competition_paused
            click("redo")
            assert app.competition.state == final
            click("competition_restart")
            assert app.competition.state == initial and app.pending == [None, None]
            click("reset")
            assert app.competition.state == initial
            click("menu")
            click("dual")
            click("menu")
            app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_1))
            assert app.page == "game" and app.competition is None

    # Both simultaneous pushes interpolate independently in the same draw order.
    level = Level("Two pushes", ("%%%%%%%%%%%", "% ABD     %", "%         %", "%  BD     %", "%%%%%%%%%%%"))
    game = CompetitiveBoard(level, (2, 3), 1)
    renderer = BoardRenderer(Board(level))
    previous = game.state
    game.step(("East", "East"))
    drawn = []
    with patch.object(renderer, "_blit", side_effect=lambda surface, sprite, pos: drawn.append((sprite, pos))):
        renderer.render_competition(game.state, previous, .5, ("East", "East"))
        crates = [(sprite, pos) for sprite, pos in drawn if sprite in renderer.crates.values()]
        assert {pos for _, pos in crates} == {(32+3.875*72, 32+row*72-12) for row in (1, 3)}
        assert all(sprite is renderer.crates[False] for sprite, _ in crates)
        drawn.clear()
        renderer.render_competition(game.state, previous, 1, ("East", "East"))
        crates = {pos: sprite for sprite, pos in drawn if sprite in renderer.crates.values()}
        assert crates[(32+4*72, 32+72-12)] is renderer.crates[True]
        assert crates[(32+4*72, 32+3*72-12)] is renderer.crates[False]


def main():
    app = SokobanApp()
    app._load_level(1)
    # Known external fixture, not an implementation of UCS or A*.
    actions = ("West", "North", "South", "East", "East", "North")
    initial = app.board.state
    app.draw()
    app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=app.buttons["A*"][0].center, button=1))
    assert app.algorithm == "A*"
    for invalid, cost in ((actions, 5), (("North",), 1), (("Bad",), 1), (([],), 1)):
        try:
            app.load_solution(invalid, cost)
            raise AssertionError("Invalid solution accepted")
        except ValueError:
            assert app.board.state == initial and app.replay is None

    with patch("pygame.time.get_ticks", return_value=1000):
        app.load_solution(actions, 6, "A*")
        assert app.replay.paused and app.replay.index == 0 and app.board.state == initial
        app.act("play")
    with patch("pygame.time.get_ticks", return_value=1124):
        app.draw()
        assert app.replay.index == 0
    with patch("pygame.time.get_ticks", return_value=1125):
        app.draw()
        assert app.replay.index == 1
        app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_SPACE))
        assert app.replay.paused
        app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_SPACE, repeat=True))
        assert app.replay.paused
    with patch("pygame.time.get_ticks", return_value=3000):
        app.draw()
        assert app.replay.index == 1
        app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_RIGHT))
        second = app.board.state
        assert (second.moves, second.pushes) == (2, 1)
        app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
        assert app.replay.index == 1 and app.board.state.moves == 1
        app.act("play")
        app.act("help")
        assert app.replay.paused
        before = app.board.state
        for action in ("play", "replay_next", "replay_prev", "UCS", "A*", "solve", "reset"):
            app.act(action)
            assert app.board.state == before and app.algorithm == "A*" and app.show_help
        app._advance_replay()
        assert app.board.state == before
        app.act("help")

    # Export the newly enabled controls at all supported layout sizes.
    for size in ((1280, 860), (720, 900), (1280, 500), (640, 430)):
        app.handle_event(pg.event.Event(pg.VIDEORESIZE, w=size[0], h=size[1]))
        scale = min(size[0]/WIDTH, size[1]/HEIGHT)
        rect = app.buttons["replay_next"][0]
        pos = (round((size[0]-WIDTH*scale)/2+rect.centerx*scale),
               round((size[1]-HEIGHT*scale)/2+rect.centery*scale))
        app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=pos, button=1))
        assert app.board.state == second
        app.act("replay_prev")
        app.previous = None
        app.pressed_until = 0
        pg.image.save(app.draw(), str(Path(__file__).with_name(
            "preview_replay.png" if size == (1280, 860) else
            "preview_replay_narrow.png" if size == (720, 900) else
            "preview_replay_small.png" if size == (640, 430) else "preview_replay_short.png")))

    app.act("play")
    for _ in range(5):
        app.animation_start = -1000
        app._advance_replay()
    assert app.replay.finished and app.replay.paused and app.board.won
    assert app.level_index == 1 and (app.board.state.moves, app.board.state.pushes) == (6, 2)
    app.act("replay_prev")
    assert not app.board.won and app.board.state == app.board.history[5]
    app.act("replay_next")
    assert app.board.won
    app.act("reset")
    assert app.replay is None and app.board.state == initial

    # An external solution can start after manual moves, without losing counters.
    app.animation_start = -1000
    app.act("West")
    manual_start = app.board.state
    app.load_solution(actions[1:], 5)
    app.act("replay_next")
    assert app.board.state == second
    app.act("replay_prev")
    assert app.board.state == manual_start
    app.act("reset")

    def supplied_solver(board, algorithm):
        assert algorithm == "UCS"
        board.move("West")  # A callback cannot mutate the live UI board.
        return actions, 6
    app.solver = supplied_solver
    app.act("UCS")
    app.act("solve")
    assert app.replay and app.board.state == initial
    app.act("replay_next")
    app.act("A*")
    assert app.replay is None and not app.board.can_redo
    app.act("next")
    assert app.level_index == 0 and app.replay is None
    check_menu(app)
    with patch("sys.argv", ["sokoban_ui", "--frames", "1"]), patch.object(SokobanApp, "run", autospec=True) as run:
        run_app()
        assert run.call_args.args[0].page == "menu" and run.call_args.args[1] == 1
    pg.quit()

    collision = Level("Collision", ("%%%%%%%%%", "%A   BD %", "%       %", "%%%%%%%%%"))
    for second_player, joint, expected in (
        ((3, 1), ("East", "West"), ((1, 1), (3, 1))),
        ((2, 1), ("East", "West"), ((1, 1), (2, 1))),
        ((2, 1), ("East", "East"), ((2, 1), (3, 1))),
    ):
        game = CompetitiveBoard(collision, second_player, 1)
        game.step(joint)
        assert game.state.players == expected and game.finished
        final = game.state
        assert not game.step(joint) and game.state == final

    same_box = Level("Same box", ("%%%%%%%", "%     %", "% AB  %", "%  D  %", "%%%%%%%"))
    game = CompetitiveBoard(same_box, (4, 2), 1)
    before = game.state
    game.step(("East", "West"))
    assert game.state.players == before.players and game.state.boxes == before.boxes
    shared_dest = Level("Shared destination", ("%%%%%%%", "% D D %", "%AB B %", "%%%%%%%"))
    game = CompetitiveBoard(shared_dest, (5, 2), 1)
    before = game.state
    game.step(("East", "West"))
    assert game.state.players == before.players and game.state.boxes == before.boxes

    two = Level("Two pushes", ("%%%%%%%%%%%", "% ABD     %", "%         %", "%  BD     %", "%%%%%%%%%%%"))
    game = CompetitiveBoard(two, (2, 3), 1)
    game.step(("East", "East"))
    assert game.scores == (1, 1) and game.winner is None and game.finished

    steal = Level("Steal", ("%%%%%%%%%%", "% A B D  %", "%        %", "%%%%%%%%%%"))
    game = CompetitiveBoard(steal, (8, 1), 9)
    turns = (("East", "East"), ("East", "East"), ("East", "West"),
             ("South", "West"), ("West", "South"), ("West", "West"),
             ("West", "West"), ("North", "North"), ("West", "East"))
    for index, joint in enumerate(turns, 1):
        game.step(joint)
        if index == 3:
            assert game.scores == (1, 0)
        elif index == 4:
            assert game.scores == (0, 0)
    assert game.finished and game.scores == (0, 1) and game.winner == 1

    # Explore three rounds and check collisions, ownership and agent symmetry.
    game = CompetitiveBoard(same_box, (4, 2), 3)
    states = [game.state]
    for _ in range(3):
        next_states = set()
        for state in states:
            for joint in product(DIRECTIONS, repeat=2):
                normal, swapped = copy(game), copy(game)
                normal.state = state
                swapped.state = replace(state, players=state.players[::-1],
                                        owners=tuple((cell, 1-owner) for cell, owner in state.owners))
                normal.step(joint)
                swapped.step(joint[::-1])
                result = normal.state
                assert len(set(result.players)) == 2
                assert set(result.players) <= normal.floor and not set(result.players) & result.boxes
                assert result.boxes <= normal.floor and len(result.boxes) == len(state.boxes)
                assert {cell for cell, _ in result.owners} <= result.boxes & normal.goals
                assert swapped.state.players == result.players[::-1]
                assert swapped.state.boxes == result.boxes and swapped.scores == normal.scores[::-1]
                next_states.add(result)
        states = next_states
    for invalid_n in (0, -1, True, 1.5):
        try:
            CompetitiveBoard(same_box, (4, 2), invalid_n)
            raise AssertionError("Invalid n accepted")
        except ValueError:
            pass
    print("Requirements 5/6 passed: menu, two-agent GUI, external replay, buttons/modal/resize, timing, atomic turns, collisions, stealing, n, symmetry.")


if __name__ == "__main__":
    main()
