import copy
import threading
import io
import random
import sys
from typing import Union

import numpy as np

from lib.parser import sudoku_write
from lib.typing import Board, Strategy
from lib.sudoku import RELATED_CELLS, Sudoku


class Screen():
    def __init__(self):
        self.buffer = io.StringIO('')

    def render(self, board: Board):
        self.buffer.write('\033c')
        sudoku_write(self.buffer, board)
        self.buffer.seek(0, io.SEEK_SET)
        sys.stdout.write(self.buffer.read())


class HillClimbingSolver:
    def __init__(self, board: Board, display: bool = False, max_iter: int = 10_000) -> None:
        self.max_iter = max_iter
        self.n_iter = 0
        self.board = np.copy(board)
        self.sudoku = Sudoku(board)
        self.display = display

        if self.display:
            self.screen = Screen()

    def random_populate(self, sudoku):
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

        for j in range(len(board)):
            if col != j and board[row][col] == board[row][j]:
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

        while (not sudoku.is_finished()):
            queue = [(k, v) for k, v in sudoku.possible_values.items()]
            queue.sort(key=lambda item: len(item[1]))

            first_coords, first_numbers = queue[0]
            if len(first_numbers) == 1:
                if not sudoku.set_value(first_coords, next(iter(first_numbers))):
                    return False
                break

            self.random_populate(sudoku)
            min_conflict = self.heuristic(self.board)
            new_value = 0
            new_coords = first_coords

            for coords, numbers in queue:
                if len(numbers) != len(first_numbers):
                    break
                for n in numbers:
                    temp_n = self.board[coords[1]][coords[0]]
                    self.board[coords[1]][coords[0]] = n
                    h = self.heuristic(self.board)
                    self.board[coords[1]][coords[0]] = temp_n

                    if (h < min_conflict or min_conflict == -1) or (random.random() < 0.3):
                        min_conflict = h
                        new_value = n
                        new_coords = coords

            if not sudoku.set_value(new_coords, new_value):
                return False

        self.sudoku = sudoku
        return True

    def solve(self) -> Union[Board, None]:
        while (self.n_iter < self.max_iter):
            self.n_iter += 1
            if self._solve() and self.sudoku.is_finished() and self.sudoku.is_valid():
                return self.sudoku.board


class CSPSolver:
    def __init__(self, sudoku: Board, possible_values=None):
        self.sudoku = Sudoku(sudoku, possible_values)
        self.is_valid = True

    def apply_value(self, coord, value):
        new_possible_values = dict()
        for k, v in self.sudoku.possible_values.items():
            new_possible_values[k] = v.copy()

        new_solver = self.__class__(
            self.sudoku.board,
            new_possible_values
        )

        new_solver.is_valid = new_solver.sudoku.set_value(coord, value)

        return new_solver

    def search(self):
        queue = [(k, v) for k, v in self.sudoku.possible_values.items()]
        queue.sort(key=lambda item: len(item[1]))

        while len(queue) > 0:
            coords, poss = queue.pop(0)

            for value in poss:
                new_solver = self.apply_value(coords, value)

                if new_solver.solve() is not None:
                    self.sudoku = new_solver.sudoku
                    return True

            break

        return False

    def solve(self) -> Union[Board, None]:
        if not self.is_valid:
            return None

        if self.sudoku.is_finished() and self.is_valid:
            return self.sudoku.board

        if not self.is_valid:
            return None

        solved = self.search()
        if solved:
            return self.sudoku.board
        else:
            return None


class AC3Solver(CSPSolver):
    def __init__(self, sudoku, possible_values=None):
        super().__init__(sudoku, possible_values)
        if possible_values == None:
            self.ac3_all()
            self.is_valid = self.sudoku.is_valid()

    def ac3_all(self):
        sudoku = self.sudoku
        queue = self.sudoku.get_unfinished_possible_values()

        while len(queue) > 0:
            element = queue.pop()
            element_values = self.sudoku.possible_values[element]

            r_all = RELATED_CELLS[element]

            changed = False

            for related in r_all:
                if element not in sudoku.possible_values:
                    continue

                value = sudoku.board[related[1]][related[0]]

                if value in element_values:
                    sudoku.possible_values[element].remove(value)

                    if len(sudoku.possible_values[element]) == 1:
                        (last_val,) = sudoku.possible_values[element]
                        self.sudoku.board[element[1]][element[0]] = last_val
                        del self.sudoku.possible_values[element]
                        changed = True

            if changed:
                related_unfinished = sudoku.get_unfinished_cells(
                    r_all
                )
                for item in related_unfinished:
                    queue.add(item)


def sudoku_solver(board: Board, strategy: Strategy = 'AC-3', display: bool = False):
    if strategy == "MIN_CONFLICT":
        solver = HillClimbingSolver(board, display=display)
    elif strategy == "FC":
        solver = CSPSolver(board)
    elif strategy == "AC-3":
        solver = AC3Solver(board)

    return solver.solve()
