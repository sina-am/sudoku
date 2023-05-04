from lib.solver import Board
from typing import (
    List
)


def parse_file(filepath: str) -> Board:
    board = []
    with open(filepath, 'r') as fd:
        n = int(fd.readline())
        for _ in range(n*n):
            board.append(list(map(int, fd.readline().split(' '))))
    return board


def parse_file2(filepath: str) -> List[Board]:
    boards = []
    with open(filepath, 'r') as fd:
        for i in range(10):
            fd.readline()
            board = []
            for _ in range(9):
                board.append(list(map(int, list(fd.readline()[:-1]))))
            boards.append(board)

    return boards
