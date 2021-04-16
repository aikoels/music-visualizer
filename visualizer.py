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
CIRCLE = 'circle'
BAR = 'bar'
AUDIO_FILE_EXTENSION = ".wav"
FLOOR = 300  # Offset of Y coordinate for shapes

# Color Codes
WHITE = (255, 255, 255)
RED = (255, 80, 80)
SAND = (255, 178, 102)
RUST = (183, 65, 14)
BLUE = (80, 80, 255)
GREEN = (80, 255, 80)
PURPLE = (125, 80, 255)

# Available Color Palettes
default_palette = {BG: WHITE, FG: RED}
desert_palette = {BG: SAND, FG: RUST}
blue_white_palette = {BG: WHITE, FG: BLUE}
purple_white_palette = {BG: SAND, FG: PURPLE}

# TODO: Add Color Gradient Based on Frequencies (Closer to White @ High Frequencies)

# Selected Color Palette
color = default_palette
# Select shapes
shape = CIRCLE

# Factor to change color by for color effects
color_change = {RED: .7, GREEN: .9, BLUE: 2}
color_change_frequency = hop_length
color_change_db = -12  # A amplitude > than this value causes a color change

# Help Menu
help = '''
    Welcome to the MUST4611 Music Visualizer!
    Here are the controls:
    Enter - Skip Song
    S - Rotate between available shapes
    Number Keys - Change Color Palette (BG/FG)
        1 - Default (Red/White)
        2 - Desert (Rust/Sand)
        3 - Blue/White
        4 - Purple/White
    To change the color shifting values:
    Arrow Keys - Control the Color Shifting Parameters
        Up - Increase Color Change Frequency Bin by 100
        Down - Decrease Color Change Frequency Bin by 100
        Right - Increase Color Change Amplitude by 6db
        Left - Decrease Color Change Amplitude by 6db
    [ - Decrease red factor change by .1
    ] - Increase red factor change by .1
    ; - Decrease green factor change by .1
    ' - Increase green factor change by .1
    . - Decrease blue factor change by .1
    / - Increase blue factor change by .1
    C - Print the current color shifting values
'''

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
        #
        # Draw shapes (either bars or jumping circles)
        if shape == CIRCLE:
            pygame.draw.circle(screen, color[FG], (self.x, self.y + self.max_height - self.height), self.width)
        else:
            pygame.draw.rect(screen, color[FG],
                             (self.x, self.y + self.max_height - self.height, self.width, self.height))


def visualize_song(song_name):
    # Define Global Vars
    global sr, force_quit, color, color_change_frequency, color_change_db, shape

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

    # Save last color for color switching
    last_foreground = color[FG]

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
                # Basic Functions
                if event.key == pygame.K_RETURN:  # Enter - Skip This Song
                    playing = False
                if event.key == pygame.K_h:  # H - Print Help
                    print(help)
                # Shape Control
                if event.key == pygame.K_s:  # S - Change Shape
                    if shape == CIRCLE:
                        shape = BAR
                    else:
                        shape = CIRCLE
                # Color Variation Paramater Control
                if event.key == pygame.K_UP:  # Up Arrow - Increase Color Change Frequency
                    color_change_frequency += hop_length
                elif event.key == pygame.K_DOWN:  # Down Arrow - Decrease Color Change Frequency
                    color_change_frequency -= hop_length
                color_change_frequency = clamp(min(frequencies), max(frequencies), color_change_frequency)
                if event.key == pygame.K_LEFT:  # Left Arrow - Decrease Color Change Amplitude
                    color_change_db -= 6
                elif event.key == pygame.K_RIGHT:  # Right Arrow - Increase Color Change Amplitude
                    color_change_db += 6
                color_change_db = clamp(-60, 0, color_change_db)
                if event.key == pygame.K_c:  # C - Output Color Info
                    print("Current Frequency: %i\nCurrent DB Cutoff: %i\nCurrent Change Values: Red: %.1f, Green: %.1f, "
                          "Blue %.1f\n" % (color_change_frequency, color_change_db, color_change[RED], color_change[GREEN],
                                       color_change[BLUE]))
                # Color Variation Amount Control
                if event.key == pygame.K_LEFTBRACKET:  # [ - Increase Red Change Factor
                    color_change[RED] -= .1
                elif event.key == pygame.K_RIGHTBRACKET:  # ] - Decrease Red Change Factor
                    color_change[RED] += .1
                if event.key == pygame.K_SEMICOLON:  # ; - Decrease Green Change Factor
                    color_change[GREEN] -= .1
                elif event.key == pygame.K_QUOTE:  # ' - Increase Green Change Factor
                    color_change[GREEN] += .1
                if event.key == pygame.K_PERIOD:  # . - Decrease Blue Change Factor
                    color_change[BLUE] -= .1
                elif event.key == pygame.K_SLASH:  # / - Increase Blue Change Factor
                    color_change[BLUE] += .1
                # Color Palette Control
                if event.key == pygame.K_1:  # 1 - Default Color Palette
                    color = default_palette
                elif event.key == pygame.K_2:  # 2 - Desert Color Palette
                    color = desert_palette
                elif event.key == pygame.K_3:  # 3 - Blue White Palette
                    color = blue_white_palette
                elif event.key == pygame.K_4:  # 4 - Purple White Palette
                    color = purple_white_palette
                last_foreground = color[FG]
            if event.type == pygame.QUIT:  # Closing Window Quits This & Future Songs
                playing = False
                force_quit = True

        # Fill the background
        screen.fill(color[BG])

        # Check if color change is happening in this image
        for b in bars:
            db = get_decibel(pygame.mixer.music.get_pos() / 1000.0, b.freq)
            # Update color based on frequency and amplitude
            if b.freq == color_change_frequency and db > color_change_db:
                # Get current color values and change them by the color_change amount
                red = int(list(color[FG])[0] * color_change[RED])
                green = int(list(color[FG])[1] * color_change[GREEN])
                blue = int(list(color[FG])[2] * color_change[BLUE])
                # Make sure the values are between 0 and 255
                red = clamp(0, 255, red)
                green = clamp(0, 255, green)
                blue = clamp(0, 255, blue)
                # Change the FG color to the new values
                color[FG] = (red, green, blue)
                break

        # Draw bars with correct colors
        for b in bars:
            new_dB = get_decibel(pygame.mixer.music.get_pos() / 1000.0, b.freq)
            b.update(deltaTime, new_dB)
            b.render(screen)

        # Update the display
        pygame.display.flip()

        # Fix the color in case it changed
        color[FG] = last_foreground

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

    print("Welcome to MUST4611 Visualizer!\nPress H for Help\n")
    # Loop Through Input Directory and Visualize Files
    for filename in os.listdir(INPUT_DIRECTORY):
        if filename.endswith(AUDIO_FILE_EXTENSION):
            visualize_song(filename)
            if force_quit:  # Quit Early if Window is Closed
                break
        else:
            continue

    pygame.quit()
