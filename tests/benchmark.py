import time
import numpy as np
from lib.parser import sudoku_read
from lib.solver import sudoku_solver
from lib.typing import Strategy


def benchmark(
    problem_file: str,
    solution_file: str,
    n_boards: int,
    n_run: int = 10,
    strategy: Strategy = "AC-3",
):
    i = 0
    with open(problem_file) as pfd:
        with open(solution_file) as sfd:
            avg_time = 0
            for _ in range(n_boards):
                solution_board = sudoku_read(sfd)
                board = sudoku_read(pfd)

                for __ in range(n_run):
                    t0 = time.perf_counter()
                    solved = sudoku_solver(board, strategy=strategy)
                    t1 = time.perf_counter()
                    if solved is None or not np.array_equal(solved, solution_board):
                        i += 1
                        print(f"unable to solve\n{board}")
                        print(f"got board\n", solved)
                        print(f"expected board\n", solution_board)
                        print(i)
                    avg_time += t1 - t0

            t = avg_time/(n_run * n_boards)
            print(f"Solved in: {t}s")
