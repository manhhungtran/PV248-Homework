import numpy as np
import re
import struct as st
import sys
import wave as w
import math
import heapq

AMPLITUDE = 20

WTF = ['C', 'Cis', 'D', 'Es', 'E',
       'F', 'Fis', 'G', 'Gis', 'A', 'Bes', 'B']


def getPeak(window):
    amplitudes = np.abs(np.fft.rfft(window))
    limit = np.mean(amplitudes) * AMPLITUDE
    peaks = [amp if amp >= limit else 0 for amp in amplitudes]

    maxPeaks = []
    for i in range(3):
        maxPeak = heapq.nlargest(3, peaks)
        if maxPeak[i] == 0:
            break
        index = peaks.index(maxPeak[i])
        maxPeaks.append(index)
        try:
            peaks[index-1] = 0
        except IndexError:
            pass
        try:
            peaks[index+1] = 0
        except IndexError:
            pass

    return maxPeaks.sort()


def pitch(freq, a4):
    C0 = a4 * pow(2, -4.75)
    h = round(12 * math.log2(freq/C0))
    octave = h // 12
    n = h % 12

    return WTF[n] + str(octave)


def diff(freq):
    h = round(12 * math.log2(freq/C0))

    return round(1200 * math.log2(freq / pow(2, (h / 12)) * C0))


def diffToString(freq):
    dif = diff(freq)

    if int(dif) > 0:
        return " + {}".format(dif)
    elif int(dif) == 0:
        return ""
    else:
        return " - {}".format(str(dif)[1:])


def pitchToString(freq, a4):

    pitc = pitch(freq, a4)
    parser = re.search(r'(\w+)(-)?(\d+)', pitc, re.IGNORECASE)

    if (parser.group(3) != "0"):
        if (parser.group(2) is not None):
            res = "{},,{}".format(parser.group(
                1), ("," * int(parser.group(3))))

        elif int(parser.group(3)) < 3:
            res = "{}{}".format(parser.group(
                1), ("," * (2 - int(parser.group(3)))))

        else:
            res = "{}{}".format(parser.group(1)[:1].lower(
            ) + parser.group(1)[1:], ("’" * (int(parser.group(3)) - 3)))

    else:
        res = "{},,".format(parser.group(1))

    return res


def toString(freq, a4):
    return pitchToString(freq, a4) + diffToString(freq)


def getResult(amplitude):
    amplitude = round(amplitude, 2)
    if amplitude > 0.1:
        return amplitude, diffToString(amplitude), toString(amplitude), getPeak(amplitude)
    return None


def printResult(peaks, a4):
    start = 0
    end = 0
    pitches = []
    for time, peak in enumerate(peaks):
        if time > 0:
            if peak != peaks[time-1]:
                print("{:.1f}-{:.1f} {}".format(start, end, " ".join(pitches)))
                start = end
                pitches = map(lambda x: toString(x, a4), peak)
        else:
            pitches = map(lambda x: toString(x, a4), peak)
        end += 0.1

    print("{:.1f}-{:.1f} {}".format(start,
                                    end, " ".join(pitches)))


def main(a4, fileName):
    reader = w.open(fileName, 'rb')

    rate = reader.getframerate()
    sampWidth = reader.getsampwidth()
    channels = reader.getnchannels()

    reqLength = channels * rate * sampWidth

    minPeak = None
    maxPeak = None

    # print("frames", frames)
    # print("rate", rate)
    # print("sampWidth", sampWidth)
    # print("channels", channels)

    fmt = '%dh' % channels * rate

    window = []
    windowSize = rate / 10
    filteredData = []
    result = []

    # read data
    while reader.tell() < reader.getnframes():
        rawdata = reader.readframes(rate)
        if len(rawdata) != reqLength:
            continue

        structData = st.unpack(fmt, rawdata)

        for i in range(0, len(structData), 2):
            chunk = structData[i: i + 2]
            filteredData.append((chunk[0] + chunk[1]) / 2)

    # process data
    for value in filteredData:
        window.append(value)
        if len(window) != windowSize:
            continue

        result.append(getPeak(window))
        window = []

    # agregate data ???????????????
    result = filter(None, result)
    printResult(result, float(a4))
    reader.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
