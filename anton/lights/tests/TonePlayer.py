import math
import numpy
import pyaudio

def play(frequency, length, rate=44100):
    '''play a tone of a desired frequency for a desired length of time
       this is written to minimize the perceived gap between tones when
       played sequentially'''

    #hidden function for generating a sine wave
    def sine(frequency, length, rate):
        length = int(length * rate)
        factor = (float(frequency) * (math.pi * 2) / rate)
        return numpy.sin(numpy.arange(length) * factor)

    chunks = [sine(frequency, length, rate)]
    chunk = numpy.concatenate(chunks) * 0.25
    fade = 200
    fade_in = numpy.arange(0., 1., 1/fade)
    fade_out = numpy.arange(1., 0., -1/fade)
    chunk[:fade] = numpy.multiply(chunk[:fade], fade_in)
    chunk[-fade:] = numpy.multiply(chunk[-fade:], fade_out)
    stream.write(chunk.astype(numpy.float32).tostring())

if __name__ == '__main__':
    print('You shouldn\'t be running this file by itself.')
    print('You have to import it at the top of your project file.')
else:
    #create the audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,channels=1, rate=44100, output=1)