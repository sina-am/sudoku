from dataclasses import dataclass
import copy
from typing import (
    Set,
    Tuple,
    List,
    Union,
    Literal
)


class ImpossibleNodeError(Exception):
    ...


Board = List[List[int]]
Strategy = Literal["FC"]


@dataclass
class Domain:
    index: Tuple[int, int]
    possible_values: Set[int]

    def __lt__(self, other):
        return len(self.possible_values) < len(other.possible_values)

    def __eq__(self, other):
        return len(self.possible_values) == len(other.possible_values)


class Node:
    state: Board
    domains: List[Domain]

    def __init__(self, state: Board):
        self.state = state
        self.find_domains()

    def find_domains(self):
        self.domains = []
        for i in range(len(self.state)):
            for j in range(len(self.state)):
                if self.state[i][j] == 0:
                    possible_values = self.find_domain(i, j)
                    if not len(possible_values):
                        raise ImpossibleNodeError("domain is empty")
                    self.domains.append(Domain(index=(i, j), possible_values=possible_values))

        self.domains.sort()

    def find_domain(self, row: int, col: int) -> Set[int]:
        domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        for i in range(len(self.state)):
            domain -= {self.state[i][col]}

        for j in range(len(self.state)):
            domain -= {self.state[row][j]}

        i_box = (row//3) * 3
        j_box = (col//3) * 3
        for i in range(i_box, i_box + 3):
            for j in range(j_box, j_box + 3):
                domain -= {self.state[i][j]}

        return domain


class SudokuSolver:
    def __init__(self, board: Board):
        self.root = Node(board)
        self.queue: List[Node] = []

    def _solve_with_fc(self) -> Union[Node, None]:
        self.queue.append(self.root)

        while (len(self.queue) != 0):
            node = self.queue[-1]
            if not len(node.domains):
                return node

            domain = node.domains[0]
            row, col = domain.index
            n = domain.possible_values.pop()
            new_state = copy.deepcopy(node.state)
            new_state[row][col] = n
            try:
                new_node = Node(new_state)
                if not domain.possible_values:
                    self.queue.pop()
                self.queue.append(new_node)
            except ImpossibleNodeError:
                self.queue.pop()

        return None

    def solve(self, strategy: Strategy) -> Union[Node, None]:
        match strategy:
            case "FC":
                return self._solve_with_fc()
