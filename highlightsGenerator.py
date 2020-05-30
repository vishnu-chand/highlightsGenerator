import numpy as np
from moviepy import editor as mpy


def getKeyFrames(ipeaks, peaks):
    # consider sequence which are 10% louder than the average
    # and return the frame index where sound is maxima
    # for each sequence return one maxima
    highlights = peaks > 1.1 * peaks.mean()
    keyFrames, maxima, imaxima = [], 0, 0
    for ipeak, peak, highlight in zip(ipeaks, peaks, highlights):
        if highlight:
            if peak > maxima:
                maxima, imaxima = peak, ipeak
        elif maxima:
            keyFrames.append(imaxima)
            maxima = 0  # reset maxima
    if maxima:
        keyFrames.append(imaxima)
    return keyFrames


def getEnergy(clip, start, stop, step):
    if stop <= 0:
        stop = clip.duration + stop
    start, stop, step = int(start), int(stop), int(step)
    result = np.empty([(stop - start) // step, 1], dtype='i4')
    for r, i in zip(result, range(start, stop, step)):
        i = clip.subclip(i, i + step).to_soundarray(fps=5000)  # due to low memory under sampled
        i = 1 * np.sqrt((i ** 2).sum())
        r[:] = i
    return result.ravel()


def getHighlights(vpath, vid, start=0, stop=-25, delta=3):
    clip = mpy.AudioFileClip(vpath)
    energy = getEnergy(clip, start, stop, delta)
    edges = np.zeros(energy.shape, dtype=bool)
    d1 = energy[:-1] <= energy[1:]
    d2 = energy[1:-1] >= energy[2:]
    edges[1:-1] = d1[:-1] & d2
    ienergy = np.arange(energy.size)
    ipeaks, peaks = ienergy[edges], energy[edges]
    keyFrames = getKeyFrames(ipeaks, peaks)
    clips = []
    for ix, keyFrame in enumerate(keyFrames, 1):
        start, stop = delta * (keyFrame - 1), delta * (keyFrame + 2.5)
        start, stop = max(0, start), min(stop, clip.duration)
        clips.append([f"Highlight {ix}", vid, int(start), int(stop)])
    return clips


if __name__ == '__main__':
    filename = '/home/hippo/hardrock/deleteMe/test3/static/EgWqoWG5V80.mp3'
    clips = highlights = getHighlights(filename, 'EgWqoWG5V80')
    for clip in clips:
        print(clip)
