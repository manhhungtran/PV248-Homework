import numpy
import re
import struct as st
import sys
import wave as w
from math import log2, pow
import heapq
import csv
import json
import math
import datetime


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

        Exception("No such datetie")


class Student:
    def __init__(self):
        self.mean = None
        self.median = None
        self.total = None
        self.passed = None
        self.regSlope = None
        self.name = None
        self.datesData = list()

    def serialize(self):
        result = dict()
        result["passed"] = self.passed
        result["median"] = self.median
        result["mean"] = self.mean
        result["total"] = self.total
        result["regression slope"] = self.regSlope

        startDateTime = datetime.datetime.strptime(
            '2018-9-17', '%Y-%m-%d').date().toordinal()

        if self.regSlope != 0:
            result['date 16'] = datetime.date.fromordinal(
                math.floor((16.0 / self.regSlope) + startDateTime)).__str__()
            result['date 20'] = datetime.date.fromordinal(
                math.floor((20.0 / self.regSlope) + startDateTime)).__str__()

        return result


def parseColumns(date):
    match = re.match(r"(\d{4}-\d{2}-\d{2})/(\d{2})", date)
    if match:
        result = DateData()
        result.number = match.group(2)
        result.date = datetime.datetime.strptime(
            match.group(1), '%Y-%m-%d').date()

        return result
    else:
        Exception("Date is in invalid format!")


def parseStudent(fileName, ide):
    student = Student()

    with open(fileName, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        for line in reader:
            for column, data in line.items():
                if column == "student":
                    if data != id:
                        student.name = data
                        continue
                else:
                    datedata = parseColumns(column)
                    datedata.score = float(data)
                    student.datesData.append(datedata)

            if student.name == ide:
                return student
        Exception("User not found!")


def parseAverage(fileName):
    student = Student()

    with open(fileName, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for line in reader:
            for column, data in line.items():
                if column == "student":
                    continue
                else:
                    datedata = parseColumns(column)
                    datedata.score = float(data)
                    student.datesData.append(datedata)

    student.name = "average"
    return student


def flatten(lista):
    res = list()
    for sublist in lista:
        for item in sublist:
            res.append(item)

    return res


def main(fileName, ide):
    if ide == "average":
        student = parseAverage(fileName)
    else:
        student = parseStudent(fileName, ide)
    # print(json.dumps(students[0].serialize(), indent=4, ensure_ascii=False))

    data = student.datesData
    rawScore = []
    rawData = {}
    rawScoreDate = {}
    scoreDate = []

    for datesData in data:
        if datesData.number not in rawData:
            rawData[datesData.number] = 0

        rawData[datesData.number] += float(datesData.score)

        if datesData.date.toordinal() not in rawScoreDate:
            rawScoreDate[datesData.date.toordinal()] = 0

        rawScoreDate[datesData.date.toordinal()] += float(datesData.score)

    for key, value in rawData.items():
        rawScore.append(value)

    for key, value in rawScoreDate.items():
        scoreDate.append((key, value))

    dates = []
    score = []
    for key, value in sorted(scoreDate, key=lambda k: k[0]):
        dates.append(key)
        score.append(value)

    for index in range(1, len(score)):
        score[index] = score[index - 1] + score[index]

    dates = numpy.array([date - datetime.datetime.strptime('2018-9-17',
                                                           '%Y-%m-%d').date().toordinal() for date in dates])

    # print(dates, score)
    student.regSlope = numpy.linalg.lstsq(
        [[date] for date in dates], score, rcond=-1)[0][0]

    student.passed = numpy.count_nonzero(numpy.array(rawScore))
    student.median = numpy.median(numpy.array(rawScore))
    student.mean = numpy.mean(numpy.array(rawScore))
    student.total = sum(rawScore)  # not sure

    print(json.dumps(student.serialize(), indent=4))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
