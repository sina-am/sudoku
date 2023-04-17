from typing import List


def parse_file(filepath: str) -> List[List[int]]:
    with open(filepath, 'r') as fd:
        n = int(fd.readline())
        sudoko = []
        for i in range(n):
            sudoko.append(list(map(int, fd.readline())))
        return sudoko
        
print(parse_file('input.txt'))
