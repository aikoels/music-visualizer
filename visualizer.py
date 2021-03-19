import librosa
import numpy
import pygame
import os
import platform
import pathlib

'''
2. Zerocrossing/BPM for color changes
Separate percussive and harmonic elements in a piece
'''

sr = None  # Resampling rate for songs, set to None to disable
x_axis = 'time'  # X Axis unit for graphs
y_axis = 'log'  # Y Axis unit for graphs, e.g. 'hz' or 'log'
window_size = 8096
hop_length = 100

# Constants for the program (mostly placeholders for reading)
BG = 'background'
BAR = 'bar'
BAR_FLOOR = 300
AUDIO_FILE_EXTENSION = ".wav"
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Selected Color Palette
color = {BG: WHITE, BAR: RED}

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


# TODO: Parameterize over required values to enable different "modes" (color, shape, size, etc)
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
    # Define Global Vars
    global sr, force_quit

    # Fill the background & set title
    screen.fill(color[BG])
    pygame.display.set_caption(song_name)

    # Load song using global sample rate
    x, sr = librosa.load(os.path.join(INPUT_DIRECTORY, song_name), sr=sr)

    # === Retrieve Features Used for Visualizer ===
    window = numpy.hanning(window_size)
    stft = librosa.core.spectrum.stft(x, n_fft=window_size, hop_length=hop_length, window=window)
    out = 2 * numpy.abs(stft) / numpy.sum(window)

    spectrogram = librosa.amplitude_to_db(out, ref=numpy.max)

    # TODO: Incorporate these into color/shape/size and create different "styles" or "modes"
    zero_crossing_rate = librosa.feature.zero_crossing_rate(x)
    bpm = librosa.beat.tempo(x, sr=sr)[0]

    frequencies = librosa.core.fft_frequencies(n_fft=window_size)

    # Get as an array over time
    times = librosa.core.frames_to_time(numpy.arange(spectrogram.shape[1]), sr=sr, hop_length=hop_length,
                                        n_fft=window_size)

    time_index_ratio = len(times) / times[len(times) - 1]

    frequencies_index_ratio = len(frequencies) / frequencies[len(frequencies) - 1]

    def get_decibel(target_time, freq):
        return spectrogram[int(freq * frequencies_index_ratio)][int(target_time * time_index_ratio)]

    bars = []

    frequencies = numpy.arange(hop_length, window_size, hop_length)
    r = len(frequencies)

    width = screen_w / r

    x = (screen_w - width * r) / 2

    # Create Frequency Bars
    for f in frequencies:
        bars.append(AudioBar(x, BAR_FLOOR, f, color[BAR], max_height=400, width=width))
        x += width

    # PyGame Clock Control
    t = pygame.time.get_ticks()
    getTicksLastFrame = t

    # Play Song
    pygame.mixer.music.load(os.path.join(INPUT_DIRECTORY, song_name))
    pygame.mixer.music.play(0)

    # Run until the user asks to quit
    playing = True
    while playing:

        # PyGame Clock Control
        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t

        # Check for Window Being Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                force_quit = True

        # Fill the background
        screen.fill(color[BG])

        # Draw Each Bar to Height Given by Change in dB
        for b in bars:
            b.update(deltaTime, get_decibel(pygame.mixer.music.get_pos() / 1000.0, b.freq))
            b.render(screen)

        # Update the display
        pygame.display.flip()

        # Stop When Song is Completed
        if not pygame.mixer.music.get_busy():
            playing = False


# Set Up PyFame Window
pygame.init()
infoObject = pygame.display.Info()
screen_w = int(infoObject.current_w / 2.5)
screen_h = int(infoObject.current_w / 2.5)
screen = pygame.display.set_mode([screen_w, screen_h])

# Force Quit Setting To Stop Early
force_quit = False

# Loop Through Input Directory and Visualize .wav Files
for filename in os.listdir(INPUT_DIRECTORY):
    if filename.endswith(AUDIO_FILE_EXTENSION):
        visualize_song(filename)
        if force_quit:
            break
    else:
        continue

pygame.quit()
