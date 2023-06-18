from typing import (
    Dict, List, Tuple, Set
)
from lib.typing import Board, Domain


class Sudoku:
    board: Board
    possible_values: Domain

    def __init__(self, board: Board, possible_values=None):
        self.board = board
        if possible_values is None:
            self.possible_values = self.initial_possible_values()
        else:
            self.possible_values = possible_values

    def initial_possible_values(self) -> Domain:
        possibilities = dict()

        for y in range(0, 9):
            for x in range(0, 9):
                if self.board[y][x] == 0:
                    possibilities[(x, y)] = self.find_domain((x, y))

        return possibilities

    def find_domain(self, coords: Tuple[int, int]) -> Set[int]:
        domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        for i in range(len(self.board)):
            domain -= {self.board[i][coords[0]]}
            domain -= {self.board[coords[1]][i]}

        x_box = (coords[0]//3) * 3
        y_box = (coords[1]//3) * 3
        for y in range(y_box, y_box + 3):
            for x in range(x_box, x_box + 3):
                domain -= {self.board[y][x]}

        return domain

    def is_finished(self):
        return len(self.possible_values) == 0

    def is_valid(self):
        for _, values in self.possible_values.items():
            if len(values) == 0:
                return False
        return True

    def set_value(self, coords: Tuple[int, int], value: int) -> bool:
        if coords not in self.possible_values or value not in self.possible_values[coords]:
            return False

        self.board[coords[1]][coords[0]] = value
        del self.possible_values[coords]

        for related in RELATED_CELLS[coords]:
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


def calculate_relations() -> Dict[Tuple[int, int], Set[Tuple[int, int]]]:
    related_cells = dict()

    for y in range(0, 9):
        for x in range(0, 9):
            related_cells[(x, y)] = get_related_cells((x, y))

    return related_cells


def get_related_cells(coords) -> Set[Tuple[int, int]]:
    related = list()

    for i in range(0, 9):
        related.append((i, coords[1]))
        related.append((coords[0], i))

    x_box = (coords[0]//3) * 3
    y_box = (coords[1]//3) * 3

    for x in range(x_box, x_box + 3):
        for y in range(y_box, y_box + 3):
            related.append((x, y))

    related_set = set(related)
    related_set.remove(coords)

    return related_set


RELATED_CELLS = calculate_relations()
