"""Requirement 6: atomic two-agent rules, independent of any agent algorithm."""

import argparse
from dataclasses import dataclass

from .model import Board, Cell, DIRECTIONS, Level


@dataclass(frozen=True)
class CompetitiveState:
    players: tuple[Cell, Cell]
    boxes: frozenset[Cell]
    owners: tuple[tuple[Cell, int], ...]
    steps: int = 0


class CompetitiveBoard:
    """Both actions read one state; conflicts cancel symmetrically."""

    def __init__(self, level: Level, second_player: Cell, step_limit: int):
        board = Board(level)
        if type(step_limit) is not int or step_limit <= 0:
            raise ValueError("Số lượt n phải là số nguyên dương.")
        if not isinstance(second_player, (tuple, list)):
            raise ValueError("Tọa độ tác nhân 2 cần hai số nguyên x, y.")
        second_player = tuple(second_player)
        if (len(second_player) != 2 or any(type(v) is not int for v in second_player)
                or second_player not in board.floor or second_player in board.state.boxes
                or second_player == board.state.player):
            raise ValueError("Tác nhân 2 phải đứng trên ô sàn trống khác tác nhân 1.")
        self.level = level
        self.floor = frozenset(board.floor)
        self.goals = frozenset(board.goals)
        self.step_limit = step_limit
        self.state = CompetitiveState((board.state.player, second_player),
                                      board.state.boxes, ())

    @property
    def finished(self):
        return self.state.steps == self.step_limit

    @property
    def scores(self):
        return tuple(sum(owner == agent for _, owner in self.state.owners)
                     for agent in (0, 1))

    @property
    def winner(self):
        if not self.finished or self.scores[0] == self.scores[1]:
            return None
        return 0 if self.scores[0] > self.scores[1] else 1

    def step(self, actions: tuple[str, str]) -> bool:
        if (not isinstance(actions, (tuple, list)) or len(actions) != 2
                or any(not isinstance(action, str) or action not in DIRECTIONS for action in actions)):
            raise ValueError("Mỗi lượt cần hai hành động North/East/South/West.")
        if self.finished:
            return False
        old = self.state
        destinations = list(old.players)
        pushes = [None, None]
        for agent, action in enumerate(actions):
            dx, dy = DIRECTIONS[action]
            x, y = old.players[agent]
            dest = (x+dx, y+dy)
            if dest not in self.floor:
                continue
            if dest in old.boxes:
                beyond = (dest[0]+dx, dest[1]+dy)
                if beyond not in self.floor or beyond in old.boxes:
                    continue
                pushes[agent] = (dest, beyond)
            destinations[agent] = dest

        cancelled = set()
        while True:
            players = [old.players[i] if i in cancelled else destinations[i]
                       for i in (0, 1)]
            active = [None if i in cancelled else pushes[i] for i in (0, 1)]
            conflicts = set()
            if (players[0] == players[1]
                    or (players[0] == old.players[1] and players[1] == old.players[0])):
                conflicts.update((0, 1))
            if (all(active) and (active[0][0] == active[1][0]
                                or active[0][1] == active[1][1])):
                conflicts.update((0, 1))
            for agent, push in enumerate(active):
                if push and push[1] in players:
                    conflicts.add(agent)
                    conflicts.update(i for i in (0, 1) if players[i] == push[1])
            if conflicts <= cancelled:
                break
            cancelled.update(conflicts)

        boxes = set(old.boxes)
        owners = dict(old.owners)
        for agent, push in enumerate(active):
            if push:
                source, dest = push
                boxes.remove(source)
                boxes.add(dest)
                owners.pop(source, None)
                if dest in self.goals:
                    owners[dest] = agent
        self.state = CompetitiveState(tuple(players), frozenset(boxes),
                                      tuple(sorted(owners.items())), old.steps+1)
        return True


COMPETITION_LEVEL = Level("Kho đôi", (
    "%%%%%%%%%%%",
    "% A     D %",
    "% B       %",
    "%         %",
    "%     B   %",
    "% D       %",
    "%%%%%%%%%%%",
))


def main():
    parser = argparse.ArgumentParser(description="Thử luật mục 6 bằng hai hành động đồng thời.")
    parser.add_argument("--steps", type=int, help="Giới hạn n lượt; bỏ trống để nhập khi chạy.")
    parser.add_argument("--map", help="Bản đồ cũ với một A; tọa độ tác nhân 2 nhập riêng.")
    parser.add_argument("--second-player", type=int, nargs=2, default=(8, 5), metavar=("X", "Y"))
    args = parser.parse_args()
    try:
        n = args.steps if args.steps is not None else int(input("Số lượt n: "))
        game = CompetitiveBoard(Level.from_file(args.map) if args.map else COMPETITION_LEVEL,
                                tuple(args.second_player), n)
        while not game.finished:
            state = game.state
            print(f"\nLượt {state.steps}/{n} · Điểm {game.scores[0]}–{game.scores[1]}")
            for y, row in enumerate(game.level.rows):
                line = []
                for x, symbol in enumerate(row):
                    cell = (x, y)
                    line.append(str(state.players.index(cell)+1) if cell in state.players
                                else 'C' if cell in state.boxes and cell in game.goals
                                else 'B' if cell in state.boxes else 'D' if cell in game.goals
                                else '%' if symbol == '%' else ' ')
                print(''.join(line))
            actions = tuple(input("Hai hành động, ví dụ East North (q để thoát): ").split())
            if actions == ('q',):
                return
            try:
                game.step(actions)
            except ValueError as exc:
                print(exc)
        print(f"\nHết {n} lượt · Điểm {game.scores[0]}–{game.scores[1]} · "
              + ("Hòa" if game.winner is None else f"Tác nhân {game.winner+1} thắng"))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Không thể mở trận: {exc}\n")
    except (EOFError, KeyboardInterrupt):
        print("\nĐã dừng trận.")


if __name__ == "__main__":
    main()
