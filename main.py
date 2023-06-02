import sys
import time
import numpy as np
from lib.sudoku import calculate_relations
from tests.benchmark import benchmark
from lib.parser import sudoku_read, sudoku_write
from lib.solver import CSPSolver, HillClimbingSolver, sudoku_solver


def main():
    # with open('./data/input.txt', 'r') as fd:
    #     for i in range(10):
    #         sudoku_read(fd)
    #     solver = HillClimbingSolver(sudoku_read(fd))
    #     print(solver.solve())
    #     print(solver.n_iter)
    benchmark('data/input.txt', 'data/output.txt', 30, 5, 'FC')
    benchmark('data/input.txt', 'data/output.txt', 30, 5, 'AC-3')
    benchmark('data/input.txt', 'data/output.txt', 30, 1, 'MIN_CONFLICT')


if __name__ == '__main__':
    main()
