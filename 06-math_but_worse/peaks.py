import numpy as np
import re
import struct as st
import sys
import wave as w

AMPLITUDE = 20


def main(fileName):
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

    while reader.tell() < reader.getnframes():
        rawdata = reader.readframes(rate)
        if len(rawdata) != reqLength:
            continue

        structData = st.unpack(fmt, rawdata)

        filteredData = []

        for i in range(0, len(structData), 2):
            chunk = structData[i: i + 2]
            filteredData.append((chunk[0] + chunk[1]) / 2)

        amplitudes = np.fft.rfft(filteredData)
        averageAmplitude = sum(map(np.abs, amplitudes)) / len(amplitudes)

        amplitudes = enumerate(amplitudes)

        filteredAmplitudes = filter(lambda amplitude: np.abs(
            amplitude[1]) >= (averageAmplitude * AMPLITUDE), amplitudes)

        filteredAmplitudes = map(lambda x: x[0], filteredAmplitudes)

        for freq in filteredAmplitudes:
            if minPeak is None or minPeak > freq:
                minPeak = freq
            if maxPeak is None or maxPeak < freq:
                maxPeak = freq
            # print(freq, np.abs(amplitude))

    if minPeak is None or maxPeak is None:
        print("no peaks")
    else:
        print("low = {}, high = {}".format(minPeak, maxPeak))

    reader.close()


if __name__ == '__main__':
    main(sys.argv[1])
