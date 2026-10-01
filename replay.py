"""Validate an external solution and replay complete board snapshots."""

from .model import Board, DIRECTIONS


class Replay:
    def __init__(self, board: Board, actions, total_cost: int):
        actions = tuple(actions)
        if type(total_cost) is not int or total_cost != len(actions):
            raise ValueError("Chi phí phải bằng số hành động (mỗi bước có chi phí 1).")
        checked = Board(board.level)
        checked.initial = board.state
        checked.history = [board.state]
        for index, action in enumerate(actions, 1):
            if not isinstance(action, str) or action not in DIRECTIONS or not checked.move(action):
                raise ValueError(f"Hành động {index} không hợp lệ: {action!r}.")
        if not checked.won:
            raise ValueError("Danh sách hành động chưa đưa tất cả thùng đến đích.")
        self.board = board
        self.actions = actions
        self.total_cost = total_cost
        self.paused = True
        # Only install history after every action and the final state pass.
        board.history = checked.history
        board.cursor = 0

    @property
    def index(self):
        return self.board.cursor

    @property
    def finished(self):
        return self.index == len(self.actions)
