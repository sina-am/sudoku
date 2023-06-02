import sys
import time
import os
import numpy as np
from lib.sudoku import calculate_relations
from tests.benchmark import benchmark
from lib.parser import sudoku_read, sudoku_write
from lib.solver import CSPSolver, HillClimbingSolver, sudoku_solver


def main():
    if len(sys.argv) == 2 and (sys.argv[1] == 'benchmark' or sys.argv[1] == '--benchmark'):
        print("Using FC:")
        benchmark('data/input.txt', 'data/output.txt', 30, 1, 'FC')
        print("Using AC-3:")
        benchmark('data/input.txt', 'data/output.txt', 30, 1, 'AC-3')
        print("Using HillClimbing:")
        benchmark('data/input.txt', 'data/output.txt', 30, 1, 'MIN_CONFLICT')

    elif len(sys.argv) >= 3 and (sys.argv[1] == 'solve' or sys.argv[1] == '--solve') and os.path.isfile(sys.argv[2]):
        strategy = 'FC'
        if len(sys.argv) == 5 and sys.argv[3] in ['--strategy', 'strategy']:
            strategy = sys.argv[4]

        with open(sys.argv[2], 'r') as fd:
            print(f"Solving using {strategy}")
            solved = sudoku_solver(sudoku_read(fd), strategy=strategy)  # type: ignore
            if solved is not None:
                sudoku_write(sys.stdout, solved, end='\n')


if __name__ == '__main__':
    main()
