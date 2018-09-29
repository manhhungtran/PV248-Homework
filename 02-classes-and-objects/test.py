import scorelib
import sys


def test_load(fileName):
    prints = scorelib.load(fileName)
    for pr in prints:
        pr.format()


if __name__ == '__main__':
    test_load(sys.argv[0])
