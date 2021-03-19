import librosa
import numpy
import pygame
import os
import platform
import pathlib

'''
Visualizer for MUSC4611
Capstone Group Project
'''

# Parameters for Audio Analysis
sr = None  # Re-Sampling rate for songs, set to None to disable
window_size = 8000
hop_length = 100

# Constants for Readability
BG = 'background'
FG = 'foreground'
AUDIO_FILE_EXTENSION = ".wav"
FLOOR = 300  # Offset of Y coordinate for shapes

# Color Codes
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SAND = (255, 178, 102)
RUST = (183, 65, 14)

# Available Color Palettes
default_palette = {BG: WHITE, FG: RED}
desert_palette = {BG: SAND, FG: RUST}

# Selected Color Palette
color = default_palette

# File Directory Defaults
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
    def __init__(self, x, y, freq, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        self.x, self.y, self.freq = x, y, freq

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
        pygame.draw.rect(screen, color[FG], (self.x, self.y + self.max_height - self.height, self.width, self.height))


def visualize_song(song_name):
    # Define Global Vars
    global sr, force_quit, color

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

    # TODO: Incorporate more features into color/shape/size and create different "styles" or "modes"
    frequencies = librosa.core.fft_frequencies(n_fft=window_size)

    # Get spectrogram as an array over time
    times = librosa.core.frames_to_time(numpy.arange(spectrogram.shape[1]), sr=sr, hop_length=hop_length,
                                        n_fft=window_size)

    time_index_ratio = len(times) / times[len(times) - 1]

    frequencies_index_ratio = len(frequencies) / frequencies[len(frequencies) - 1]

    # Get dB value of a given frequency at a given time from the spectrogram
    def get_decibel(target_time, freq):
        return spectrogram[int(freq * frequencies_index_ratio)][int(target_time * time_index_ratio)]

    # Get array containing values of each bin to draw a bar for
    frequencies = numpy.arange(hop_length, window_size, hop_length)
    r = len(frequencies)

    width = screen_w / r

    x = (screen_w - width * r) / 2

    # Create Frequency Bars
    bars = []
    for f in frequencies:
        bars.append(AudioBar(x, FLOOR, f, max_height=400, width=width))
        x += width

    # PyGame Clock Control
    t = pygame.time.get_ticks()
    getTicksLastFrame = t

    # Play Song
    pygame.mixer.music.load(os.path.join(INPUT_DIRECTORY, song_name))
    pygame.mixer.music.play(0)

    # Loop to Visualize & Get Input
    playing = True
    while playing:

        # PyGame Clock Control
        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t

        # Check for Input
        for event in pygame.event.get():
            # Key Press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Skip This Song
                    playing = False
                if event.key == pygame.K_1:  # 1 - Default Color Palette
                    color = default_palette
                if event.key == pygame.K_2:  # 2 - Desert Color Palette
                    color = desert_palette
            if event.type == pygame.QUIT:  # Closing Window Quits This & Future Songs
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


if __name__ == "__main__":
    # Set Up PyGame Window
    pygame.init()
    infoObject = pygame.display.Info()
    screen_w = int(infoObject.current_w / 2.5)
    screen_h = int(infoObject.current_w / 2.5)
    screen = pygame.display.set_mode([screen_w, screen_h])

    # Force Quit Setting To Stop Early
    force_quit = False

    # Loop Through Input Directory and Visualize Files
    for filename in os.listdir(INPUT_DIRECTORY):
        if filename.endswith(AUDIO_FILE_EXTENSION):
            visualize_song(filename)
            if force_quit:  # Quit Early if Window is Closed
                break
        else:
            continue

    pygame.quit()
