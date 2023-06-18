import abc
import copy
import random
import time
import numpy as np
from typing import Union

from lib.typing import Board, Strategy
from lib.sudoku import RELATED_CELLS, Sudoku


class Solver(abc.ABC):
    @abc.abstractmethod
    def solve(self) -> Union[Board, None]:
        raise NotImplementedError


class HillClimbingSolver(Solver):
    def __init__(self, board: Board, max_iter: int = 100_000) -> None:
        self.max_iter = max_iter
        self.n_iter = 0
        self.board = np.copy(board)
        self.sudoku = Sudoku(board)
        self.epsilon = 0.3

    def random_populate(self, sudoku: Sudoku):
        for i in range(len(sudoku.board)):
            for j in range(len(sudoku.board)):
                if sudoku.board[i][j] == 0:
                    self.board[i][j] = random.randint(1, 9)

    @staticmethod
    def find_conflict(board: Board, row: int, col: int) -> int:
        conflicts = 0
        for i in range(len(board)):
            if row != i and board[row][col] == board[i][col]:
                conflicts += 1
            if col != i and board[row][col] == board[row][i]:
                conflicts += 1

        i_box = (row//3) * 3
        j_box = (col//3) * 3
        for i in range(i_box, i_box + 3):
            for j in range(j_box, j_box + 3):
                if (col != j and row != i) and board[row][col] == board[i][j]:
                    conflicts += 1

        return conflicts

    @staticmethod
    def heuristic(board: Board) -> int:
        conflicts = 0
        for i in range(len(board)):
            for j in range(len(board)):
                conflicts += HillClimbingSolver.find_conflict(board, i, j)
        return conflicts

    def _solve(self) -> bool:
        sudoku = copy.deepcopy(self.sudoku)

        while not sudoku.is_finished():
            queue = [(k, v) for k, v in sudoku.possible_values.items()]
            coords, values = min(queue, key=lambda item: len(item[1]))

            if len(values) == 1:
                if not sudoku.set_value(coords, next(iter(values))):  # type: ignore
                    return False
                continue

            self.random_populate(sudoku)
            min_conflict = float('inf')
            best_value = 0

            for value in values:
                temp_val = self.board[coords[1]][coords[0]]
                self.board[coords[1]][coords[0]] = value
                h = self.heuristic(self.board)
                self.board[coords[1]][coords[0]] = temp_val

                if (h < min_conflict) or (random.random() < self.epsilon):
                    min_conflict = h
                    best_value = value

            if not sudoku.set_value(coords, best_value):
                return False

        self.sudoku = sudoku
        return True

    def solve(self) -> Union[Board, None]:
        while (self.n_iter < self.max_iter):
            self.n_iter += 1
            if self._solve() and self.sudoku.is_finished() and self.sudoku.is_valid():
                return self.sudoku.board


class CSPSolver(Solver):
    def __init__(self, sudoku: Board, possible_values=None):
        self.sudoku = Sudoku(sudoku, possible_values)
        self.is_valid = True

    def apply_value(self, coord, value):
        new_possible_values = {k: v.copy() for k, v in self.sudoku.possible_values.items()}
        new_board = np.copy(self.sudoku.board)
        new_solver = self.__class__(
            new_board,
            new_possible_values,
        )

        new_solver.is_valid = new_solver.sudoku.set_value(coord, value)

        return new_solver

    def search(self):
        queue = [(k, v) for k, v in self.sudoku.possible_values.items()]
        coords, values = min(queue, key=lambda item: len(item[1]))

        for value in values:
            new_solver = self.apply_value(coords, value)

            if new_solver.solve() is not None:
                self.sudoku = new_solver.sudoku
                return True

        return False

    def solve(self) -> Union[Board, None]:
        if not self.is_valid:
            return None

        if self.sudoku.is_finished() and self.is_valid:
            return self.sudoku.board

        solved = self.search()
        if solved:
            return self.sudoku.board
        else:
            return None


class AC3Solver(CSPSolver):
    def __init__(self, sudoku, possible_values=None, *args, **kwargs):
        super().__init__(sudoku, possible_values, *args, **kwargs)
        if possible_values is None:
            self.check_arc_consistency()
            self.is_valid = self.sudoku.is_valid()

    def check_arc_consistency(self):
        queue = {k for k in self.sudoku.possible_values.keys()}

        while len(queue) != 0:
            cell = queue.pop()
            related_arcs = RELATED_CELLS[cell]
            for related in related_arcs:
                if related not in self.sudoku.possible_values:
                    continue

                related_values = self.sudoku.possible_values[related]
                inconsistent_values = set()
                for value in self.sudoku.possible_values[cell]:
                    if len(related_values - {value}) == 0:
                        inconsistent_values.add(value)

                self.sudoku.possible_values[cell] -= inconsistent_values


def sudoku_solver(board: Board, strategy: Strategy = 'AC-3'):
    if strategy == "MIN_CONFLICT":
        solver = HillClimbingSolver(board)
    elif strategy == "FC":
        solver = CSPSolver(board)
    elif strategy == "AC-3":
        solver = AC3Solver(board)

    return solver.solve()
