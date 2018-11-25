import numpy
import re
import struct as st
import sys
import csv
import json
import math


class DateData:
    def __init__(self):
        self.number = None
        self.date = None
        self.score = 0

    def toString(self):
        return "date {}".format(self.number)

    def toString2(self):
        return "{};{};{}".format(self.date, self.number, self.score)

    def serialize(self):
        return self.date

    def getDeadline(self):
        if self.number and self.number:
            return "{}/{}".format(self.date, self.number)

        Exception("No such datetime")


class Result:
    def __init__(self):
        self.passed = 0
        self.first = 0.0
        self.last = 0.0
        self.median = 0.0
        self.mean = 0.0

    def serialize(self):
        result = dict()
        result["passed"] = self.passed
        result["first"] = self.first
        result["last"] = self.last
        result["median"] = self.median
        result["mean"] = self.mean

        return result


def parseColumns(date):
    match = re.match(r"(\d{4}-\d{2}-\d{2})/(\d{2})", date)
    if match:
        result = DateData()
        result.number = match.group(2)
        result.date = match.group(1)

        return result
    else:
        Exception("Date is in invalid format!")


def parse(fileName):
    result = list()
    with open(fileName, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for line in reader:
            for column, data in line.items():
                if column == "student":
                    continue
                else:
                    datedata = parseColumns(column)
                    datedata.score = float(data)
                    result.append(datedata)

    return result


def main(fileName, mode):
    data = parse(fileName)

    rawData = {}

    for datesData in data:
        if mode == "exercises":
            if datesData.number not in rawData:
                rawData[datesData.number] = float(datesData.score)
            else:
                rawData[datesData.number] += float(datesData.score)
        elif mode == "dates":
            if datesData.date not in rawData:
                rawData[datesData.date] = float(datesData.score)
            else:
                rawData[datesData.date] += float(datesData.score)
        elif mode == "deadlines":
            if datesData.getDeadline() not in rawData:
                rawData[datesData.getDeadline()] = float(datesData.score)
            else:
                rawData[datesData.getDeadline()] += float(datesData.score)
        else:
            Exception("Invalid mode.")

    results = {}

    for key, values in rawData.items():
        student = Result()
        student.passed = numpy.count_nonzero(numpy.array(values))
        student.median = numpy.median(numpy.array(values))
        student.mean = numpy.mean(numpy.array(values))
        student.first = numpy.percentile(numpy.array(values), 25)
        student.last = numpy.percentile(numpy.array(values), 75)

        results[key] = student.serialize()
        # print(len(values))
    print(json.dumps(results, indent=4))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
