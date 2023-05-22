from tests.benchmark import benchmark


def main():
    benchmark('data/input.txt', 'data/output.txt', 30, 1, 'AC-3')


if __name__ == '__main__':
    main()
