import numpy as np
import re
import struct as st
import sys
import wave as w
import math
import heapq

AMPLITUDE = 20

WTF = ['c', "cis", "d", "es", "e", "f", "fis", "g", "gis", "a", "bes", "b"]


def getPeak(window):
    amplitudes = np.abs(np.fft.rfft(window))
    limit = np.mean(amplitudes) * AMPLITUDE
    peaks = [ampl if ampl >= limit else 0 for ampl in amplitudes]

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

    maxPeaks.sort()
    return maxPeaks


def pitch(freq, a4):
    C0 = a4 * pow(2, -4.75)
    h = round(12 * math.log2(freq/C0))
    octave = h // 12
    index = h % 12

    return WTF[index] + str(octave)


def diff(freq, a4):
    C0 = a4 * pow(2, -4.75)
    h = round(12 * math.log2(freq/C0))
    hh = pow(2, (h / 12)) * C0
    res = round(1200 * math.log2(freq / hh))
    return res


def diffToString(freq, a4):
    dif = diff(freq, a4)

    if int(dif) > 0:
        return " + {}".format(dif)
    elif int(dif) == 0:
        return " + 0"
    else:
        return " - {}".format(str(dif)[1:])


def pitchToString(freq, a4):
    pitc = pitch(freq, a4)
    parser = re.search(r'([a-zA-Z]+)(-)?(\d+)', pitc, re.IGNORECASE)

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
    return pitchToString(freq, a4) + diffToString(freq, a4)


def printResult(peaks, a4):
    start = 0
    end = 0
    for time, peak in enumerate(peaks):
        if time > 0 and peak != peaks[time-1]:
            if pitches:
                print("{:.1f}-{:.1f} {}".format(start, end, " ".join(pitches)))

            start = end

        pitches = map(lambda x: toString(x, a4), peak)
        end += 0.1

    print("{:.1f}-{:.1f} {}".format(start,
                                    end, " ".join(pitches)))


def main(a4, fileName):
    reader = w.open(fileName, 'rb')

    rate = reader.getframerate()
    sampWidth = reader.getsampwidth()
    channels = reader.getnchannels()

    # reqLength = channels * rate * sampWidth

    minPeak = None
    maxPeak = None

    # print("frames", frames)
    # print("rate", rate)
    # print("sampWidth", sampWidth)
    # print("channels", channels)

    frames = reader.getnframes()
    fmt = "<{}h".format(frames * channels)

    window = []
    windowSize = rate * 0.1
    # filteredData = []
    result = list()

    # read data
    rawData = reader.readframes(frames)
    structData = st.unpack(fmt, rawData)

    # process data
    for value in structData:
        window.append(value)
        if len(window) != windowSize:
            continue

        jo = getPeak(window)
        result.append(jo)
        window = []

    # agregate data ???????????????
    printResult(result, float(a4))
    reader.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
