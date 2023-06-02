from lib.typing import Board
import numpy as np
from typing import (
    TextIO
)


def sudoku_read(reader: TextIO, n: int = 9) -> Board:
    board = []
    for _ in range(n):
        board.append(list(map(int, reader.readline().split(' '))))
    return np.array(board)


def sudoku_write(writer: TextIO, state: Board, end: str = ''):
    for i in range(9):
        for j in range(9):
            writer.write(str(state[i][j]))
            if j != 8:
                writer.write(' ')
        if i != 8:
            writer.write('\n')

    if end:
        writer.write(end)
