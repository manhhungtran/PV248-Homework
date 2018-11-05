import sys
import numpy as np
import re
from collections import defaultdict

YOHO = "NEJKULIKALASLASLKJGHASKLGHASKJGHKASGHKAJSGH"


def parse(line):
    result = defaultdict(lambda: 0, dict())

    r = re.compile(r"(\+|\-)\s*(\d*)\s*(\w*)(.*)")

    while(line):
        res = r.match(line)
        value = int(res.group(2) or 1)
        if res.group(1) == "-":
            value = value * (-1)
        key = res.group(3)
        result[key or YOHO] += value
        line = res.group(4).strip()

    return result


def main(file):
    variables = list()
    variablesKeys = list()
    results = list()
    lines = list(filter(lambda x: not re.match(r'^\s*$', x),
                        open(file, 'r', encoding="utf-8")))

    for line in lines:
        if(not line.startswith("-")):
            line = "+" + line
        li = list(map(lambda x: x.strip(), line.split("=")))

        number = int(li[1])
        res = parse(li[0])

        for k in res.keys():
            if not k in variablesKeys and k != YOHO:
                variablesKeys.append(k)

        number -= int(res[YOHO])

        variableValues = list()
        for key in variablesKeys:
            variableValues.append(res[key] or 0)

        variables.append(variableValues)
        results.append(number)

    maxi = len(max(variables, key=len))
    variables = list(map(lambda x: fixValues(
        x, maxi), variables))

    # print("Variable keys", variablesKeys)
    # print("Variables", variables)
    # print("Results", results)

    augmentedMatrix = [row.copy() for row in variables]
    for index, number in enumerate(results):
        augmentedMatrix[index].append(number)

    variablesRank = np.linalg.matrix_rank(np.array(variables))
    augmentedMatrixRank = np.linalg.matrix_rank(np.array(augmentedMatrix))

    # print(augmentedMatrixRank, augmentedMatrix)
    # print(variablesRank, variables)

    if variablesRank == augmentedMatrixRank:
        try:
            solutions = np.linalg.solve(np.array(variables), np.array(results))
            solutionsString = []
            for var, sol in zip(list(variablesKeys), solutions):
                solutionsString.append('{} = {}' .format(var, sol))
            print('solution: {}'.format(", ".join(sorted(solutionsString))))
        except:
            solutionSpaceDimendion = len(variablesKeys) - variablesRank
            print('solution space dimension: {}'.format(solutionSpaceDimendion))
    else:
        print('no solution')


def fixValues(lis, length):
    if len(lis) != length:
        for _ in range(length - len(lis)):
            lis.append(0)
    return lis


if __name__ == '__main__':
    main(sys.argv[1])
    # main("C:\\Users\\ManhHungT\\Documents\\GitHub\\PV248-Homework\\05-math\\3")
