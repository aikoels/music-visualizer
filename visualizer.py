import librosa
import numpy
import pygame
import os
import platform
import pathlib

'''
1. Window name = song name
2. Next song play in same window
2. Zerocrossing/BPM for color changes
Separate percussive and harmonic elements in a piece
'''

sr = None  # Resampling rate for songs, set to None to disable
x_axis = 'time'  # X Axis unit for graphs
y_axis = 'log'  # Y Axis unit for graphs, e.g. 'hz' or 'log'
window_size = 1024
hop_length = 512

# Program Defaults
FILE_DELIM = None
if platform.system() == 'Windows':
    FILE_DELIM = '\\'
else:
    FILE_DELIM = '/'
INPUT_DIRECTORY = str(pathlib.Path().absolute()) + FILE_DELIM + "input" + FILE_DELIM


def clamp(min_value, max_value, value):
    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value


class AudioBar:
    def __init__(self, x, y, freq, color, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        self.x, self.y, self.freq = x, y, freq

        self.color = color

        self.width, self.min_height, self.max_height = width, min_height, max_height

        self.height = min_height

        self.min_decibel, self.max_decibel = min_decibel, max_decibel

        self.__decibel_height_ratio = (self.max_height - self.min_height) / (self.max_decibel - self.min_decibel)

    def update(self, dt, decibel):
        desired_height = decibel * self.__decibel_height_ratio + self.max_height

        speed = (desired_height - self.height) / 0.1

        self.height += speed * dt

        self.height = clamp(self.min_height, self.max_height, self.height)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y + self.max_height - self.height, self.width, self.height))


def visualize_song(song_name):
    pygame.init()
    print("Loading Song: " + song_name)
    global sr
    x, sr = librosa.load(os.path.join(INPUT_DIRECTORY, song_name), sr=sr)

    # === Output Spectograms ===
    window = numpy.hanning(window_size)
    stft = librosa.core.spectrum.stft(x, n_fft=window_size, hop_length=hop_length, window=window)
    out = 2 * numpy.abs(stft) / numpy.sum(window)

    spectrogram = librosa.amplitude_to_db(out, ref=numpy.max)

    spectral_centroid = librosa.feature.spectral_centroid(x, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(x, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(x)
    bpm = librosa.beat.tempo(x, sr=sr)[0]

    frequencies = librosa.core.fft_frequencies(n_fft=window_size)

    # getting an array of time periodic
    times = librosa.core.frames_to_time(numpy.arange(spectrogram.shape[1]), sr=sr, hop_length=hop_length, n_fft=window_size)

    time_index_ratio = len(times) / times[len(times) - 1]

    frequencies_index_ratio = len(frequencies) / frequencies[len(frequencies) - 1]

    def get_decibel(target_time, freq):
        return spectrogram[int(freq * frequencies_index_ratio)][int(target_time * time_index_ratio)]

    infoObject = pygame.display.Info()

    screen_w = int(infoObject.current_w / 2.5)
    screen_h = int(infoObject.current_w / 2.5)

    # Set up the drawing window
    screen = pygame.display.set_mode([screen_w, screen_h])

    bars = []

    frequencies = numpy.arange(100, 8000, 100)

    r = len(frequencies)

    width = screen_w / r

    x = (screen_w - width * r) / 2

    for c in frequencies:
        bars.append(AudioBar(x, 300, c, (255, 0, 0), max_height=400, width=width))
        x += width

    t = pygame.time.get_ticks()
    getTicksLastFrame = t

    pygame.mixer.music.load(os.path.join(INPUT_DIRECTORY, song_name))
    pygame.mixer.music.play(0)

    # Run until the user asks to quit
    running = True
    while running:

        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with white
        screen.fill((255, 255, 255))

        for b in bars:
            b.update(deltaTime, get_decibel(pygame.mixer.music.get_pos() / 1000.0, b.freq))
            b.render(screen)

        # Flip the display
        pygame.display.flip()

    pygame.quit()


for filename in os.listdir(INPUT_DIRECTORY):
    if filename.endswith(".wav"):
        visualize_song(filename)
    else:
        continue
