import numpy as np
import re
import struct as st
import sys
import wave as w
from math import log2, pow
import heapq

AMPLITUDE = 20

WTF = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Bes', 'B']


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
            peaks[index - 1] = 0
        except IndexError:
            pass
        try:
            peaks[index + 1] = 0
        except IndexError:
            pass

    maxPeaks.sort()
    return maxPeaks


def pitch(freq, a4):
    C0 = a4*pow(2, -4.75)
    h = round(12*log2(freq/C0))
    octavesDiff = (int(h) // 12) - 3
    n = int(h) % 12

    tones = n
    roughFreq = pow(2, (h / 12)) * C0
    tonesDiff = round(1200 * log2(freq / roughFreq))

    if tonesDiff >= 50:
        tones += 1
        tonesDiff = ((-1)*(100 - tonesDiff))

    if tones >= 12:
        tones -= 12
        octavesDiff += 1

    if octavesDiff < 0:
        result = WTF[tones] + (',' * (-1 * octavesDiff - 1))
    else:
        result = WTF[tones].lower() + ("'" * octavesDiff)

    return '{}{:+d}'.format(result, tonesDiff)


def printResult(peaks, a4):
    start = 0
    end = 0
    pitches = []
    for time, peak in enumerate(peaks):
        if time > 0 and peak != peaks[time-1]:
            print("{:.1f}-{:.1f} {}".format(start,
                                            end, " ".join(pitches)))

            start = end

        pitches = map(lambda x: pitch(x, a4), peak)
        end += 0.1

    print("{:.1f}-{:.1f} {}".format(start,
                                    end, " ".join(pitches)))


def main(a4, fileName):
    reader = w.open(fileName, 'rb')

    rate = reader.getframerate()
    # sampWidth = reader.getsampwidth()
    channels = reader.getnchannels()

    # reqLength = channels * rate * sampWidth

    # minPeak = None
    # maxPeak = None

    # print("frames", frames)
    # print("rate", rate)
    # print("sampWidth", sampWidth)
    # print("channels", channels)

    frames = reader.getnframes()
    fmt = "<{}h".format(frames * channels)

    # window = []
    windowSize = int(rate * 0.1)
    # filteredData = []
    result = list()

    # read data
    rawData = reader.readframes(frames)
    structData = st.unpack(fmt, rawData)

    # process data
    for value in range(0, len(structData) - rate + 1, windowSize):
        jo = getPeak(structData[value: (value + rate)])
        result.append(jo)
        # window = []

    # agregate data ???????????????
    printResult(result, float(a4))
    reader.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
