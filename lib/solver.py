import numpy as np
import abc
from dataclasses import dataclass
import copy
import io
import time
import random
from typing import (
    Tuple,
    List,
    Union,
)

from lib.parser import sudoku_write
from lib.typing import Board, Strategy
from lib.sukoku import CSPSudoku, AC3Sudoku
from lib.errors import ImpossibleSudokuError
import sys


class Screen():
    def __init__(self):
        self.buffer = io.StringIO('')

    def render(self, board: Board):
        self.buffer.write('\033c')
        sudoku_write(self.buffer, board)
        self.buffer.seek(0, io.SEEK_SET)
        sys.stdout.write(self.buffer.read())


@dataclass
class Statistics:
    expanded_nodes: int = 0
    n_backing_track: int = 0


class Solver(abc.ABC):
    @abc.abstractmethod
    def solve(self) -> Tuple[Board, Statistics]:
        raise NotImplementedError


class HillClimbingSolver(Solver):
    def __init__(self, board: Board, display: bool = False) -> None:
        self.board = board
        self.cells = []
        self.display = display

        if self.display:
            self.screen = Screen()

        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[i][j] == 0:
                    self.cells.append((i, j))
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
        return conflicts // 2

    def _solve(self) -> int:

        min_conflict = self.heuristic(self.board)

        for (i, j) in self.cells:
            new_n, new_min_conflict = 0, min_conflict
            for n in range(1, 10):
                temp_n = self.board[i][j]
                self.board[i][j] = n
                h = self.heuristic(self.board)
                self.board[i][j] = temp_n

                if h < new_min_conflict:
                    new_min_conflict = h
                    new_n = n

            # Add stochastic
            if (new_min_conflict < min_conflict) or (random.random() < .15):
                self.board[i][j] = new_n
                min_conflict = new_min_conflict

        return min_conflict

    def solve(self) -> Board:
        min_conflict = -1
        while (min_conflict != 0):
            min_conflict = self._solve()
        return self.board


class CSPSolver:
    def __init__(self, board: Board, display: bool = False):
        self.root = CSPSudoku(board)
        self.queue: List[CSPSudoku] = []
        self.statistics: Statistics = Statistics()
        self.display = display

        if self.display:
            self.screen = Screen()

    def solve(self) -> Union[Board, None]:
        """
        Solve using BT-FC-MRV
        """

        self.queue.append(self.root)

        while (len(self.queue) != 0):
            node = self.queue[-1]

            if self.display:
                self.screen.render(node.board)
                time.sleep(0.1)

            if not len(node.domains):
                return node.board

            domain = node.find_mrv()
            row, col = domain.index
            n = domain.possible_values.pop()
            new_board = copy.deepcopy(node.board)
            new_board[row][col] = n
            try:
                new_node = CSPSudoku(new_board)
                if not domain.possible_values:  # If the domain only has the previous value
                    self.queue.pop()
                self.queue.append(new_node)
                self.statistics.expanded_nodes += 1
            except ImpossibleSudokuError:
                self.queue.pop()
                self.statistics.n_backing_track += 1

        return None


class AC3Solver:
    def __init__(self, board: Board, display: bool = False):
        self.related_cells = dict()
        self.calculate_relations()

        self.analyser = SudokuAnalyser(board, self.related_cells)

    def solve(self):
        if not self.analyser.sudoku.is_valid():
            return None

        return self.analyser.solve()

    def calculate_relations(self):
        for r in range(0, 9):
            for c in range(0, 9):
                coords = (c, r)
                self.related_cells[coords] = self.get_related_cells(coords)

    @staticmethod
    def get_related_cells(coords):
        related = list()

        for i in range(0, 9):
            related.append((i, coords[1]))
            related.append((coords[0], i))

        square_x = int((coords[0]) / 3) * 3
        square_y = int((coords[1]) / 3) * 3

        for x in range(0, 3):
            for y in range(0, 3):
                related.append((square_x + x, square_y + y))

        related_set = set(related)
        related_set.remove(coords)

        return related_set


class SudokuAnalyser:
    def __init__(self, sudoku, related_cells, possible_values=None):
        self.related_cells = related_cells

        self.sudoku = AC3Sudoku(sudoku, related_cells, possible_values)
        self.is_valid = True

        if possible_values == None:
            self.ac3_all()
            self.is_valid = self.sudoku.is_valid()

    def ac3_all(self):
        sudoku = self.sudoku
        queue = self.sudoku.get_unfinished_possible_values()

        while len(queue) > 0:
            element = queue.pop()
            element_values = self.sudoku.possible_values[element]

            r_all = sudoku.related_cells[element]

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

    def apply_value(self, coord, value):
        new_possible_values = dict()
        for k, v in self.sudoku.possible_values.items():
            new_possible_values[k] = v.copy()

        new_solver = SudokuAnalyser(
            self.sudoku.board,
            self.related_cells,
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

    def solve(self):
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

        # return solved and self.sudoku.is_finished() and self.is_valid


def sudoku_solver(board: Board, strategy: Strategy = 'AC-3', display: bool = False):
    if strategy == "MIN_CONFLICT":
        solver = HillClimbingSolver(board, display=display)
    elif strategy == "FC":
        solver = CSPSolver(board, display=display)
    elif strategy == "AC-3":
        solver = AC3Solver(board, display=display)

    return solver.solve()
