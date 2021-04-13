# Music Visualizer
Created for MUSC4611

Spring 2021

Quincy Els,
Theresa Pelosi,
Matthew Ferber,
Paul Rhee
 
### Installing the Visualizer
This program has only been tested on Windows, but it is expected to 
work on Mac or Unix.

Requirements:
- [Python 3.6.2+](https://www.python.org/downloads/)

After installing Python, ensure the following packages are 
installed: librosa, numpy, pygame, os, platform, pathlib.

You can do this with an IDE or using your command line 
or terminal:
```bash
python3 -m pip install librosa
python3 -m pip install numpy
python3 -m pip install pygame
python3 -m pip install os
python3 -m pip install platform
python3 -m pip install pathlib
```
Note: Some packages will be installed by default so the installation command
may fail, this is fine, run the other commands.

Convert all audio files to 16-bit .wav format and place them in the `input/` 
directory.

Execute the script: you can do this from an IDE (if you installed
the packages through one) or by command line or terminal. Simply
navigate to the directory containing the script and input 
folder, and run: `python3 visualizer.py` 

A PyGame window should appear with your visualizations.

### Using the Visualizer
Controls:
- You can quit at any time and skip the rest of the songs by closing the window.
- You can switch between color profiles using 1 (default) or 2 (desert) while
the visualizer runs.
- You can skip to the next song by pressing the `ENTER` key.
- The current song name will be displayed at the top of the window.
