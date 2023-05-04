import time
from lib.parser import parse_file2
from lib.solver import SudokuSolver


def _benchmark(filepath: str, level: str):
    boards = parse_file2(filepath)
    avg_time = 0
    for board in boards:
        for i in range(10):
            t0 = time.perf_counter()
            if not SudokuSolver(board).solve("FC"):
                raise RuntimeError(f"unable to solve {board}")
            t1 = time.perf_counter()
            avg_time += t1 - t0

    t = avg_time/(10 * len(boards))
    print(f"Timeit for level {level}: {t}")


def benchmark():
    _benchmark('data/easy.txt', level="easy")
    _benchmark('data/intermediate.txt', level="intermediate")
    _benchmark('data/expert.txt', level="hard")


if __name__ == '__main__':
    benchmark()
