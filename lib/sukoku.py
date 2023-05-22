from lib.errors import ImpossibleSudokuError
import numpy as np
from dataclasses import dataclass
from typing import (
    Dict, Tuple, Set, List
)
from lib.typing import Board


@dataclass
class Domain:
    index: Tuple[int, int]
    possible_values: Set[int]

    def __lt__(self, other):
        return len(self.possible_values) < len(other.possible_values)

    def __eq__(self, other):
        return len(self.possible_values) == len(other.possible_values)


class CSPSudoku:
    board: Board
    domains: List[Domain]

    def __init__(self, board: Board):
        self.board = np.copy(board)
        self.find_domains()

    def find_mrv(self) -> Domain:
        return min(self.domains)

    def find_domains(self):
        self.domains = []

        for i in range(len(self.board)):
            for j in range(len(self.board)):
                if self.board[i][j] == 0:
                    possible_values = self.find_domain(i, j)
                    if not len(possible_values):
                        raise ImpossibleSudokuError("domain is empty")

                    self.domains.append(Domain(index=(i, j), possible_values=possible_values))

    def find_domain(self, row: int, col: int) -> Set[int]:
        domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        for i in range(len(self.board)):
            domain -= {self.board[i][col]}

        for j in range(len(self.board)):
            domain -= {self.board[row][j]}

        i_box = (row//3) * 3
        j_box = (col//3) * 3
        for i in range(i_box, i_box + 3):
            for j in range(j_box, j_box + 3):
                domain -= {self.board[i][j]}

        return domain


class AC3Sudoku:
    board: Board
    possible_values: Dict[Tuple[int, int], Set[int]]

    def __init__(self, board: Board, related_cells, possible_values=None):
        self.board = np.copy(board)
        self.related_cells = related_cells

        if possible_values is None:
            self.possible_values = self.initial_possible_values()
        else:
            self.possible_values = possible_values

    # initial possible values without any pruning
    def initial_possible_values(self) -> Dict[Tuple[int, int], Set[int]]:
        possibilities = dict()

        for i in range(0, 9):
            for j in range(0, 9):
                if self.board[i][j] == 0:
                    possibilities[(j, i)] = set(range(1, 10))

        return possibilities

    def is_finished(self):
        return len(self.possible_values) == 0

    def is_valid(self):
        for _, values in self.possible_values.items():
            if len(values) == 0:
                return False
        return True

    # set a value in a coordinate, cascading all updates for forward checking
    def set_value(self, coords, value):
        if coords not in self.possible_values or value not in self.possible_values[coords]:
            return False

        self.board[coords[1]][coords[0]] = value
        del self.possible_values[coords]

        # update all related cells
        for related in self.related_cells[coords]:
            if related not in self.possible_values:
                if self.board[related[1]][related[0]] == value:
                    return False

                continue

            related_values = self.possible_values[related]

            related_values.discard(value)

            if len(related_values) == 0:
                return False

            if len(related_values) == 1:
                (last_value,) = related_values
                if not self.set_value(related, last_value):
                    return False

        return True

    def get_unfinished_possible_values(self):
        return set(k for k, v in self.possible_values.items())

    def get_unfinished_cells(self, coord_set):
        return [coord for coord in coord_set if coord in self.possible_values]


def calculate_relations():
    related_cells = dict()

    for r in range(0, 9):
        for c in range(0, 9):
            coords = (c, r)
            related_cells[coords] = get_related_cells(coords)

    return related_cells


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
