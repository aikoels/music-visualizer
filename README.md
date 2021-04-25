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
- Python Libraries: librosa, numpy, pygame, os, platform, pathlib.

To install the python libraries using your command line 
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

### Using the Visualizer
Convert all audio files to .wav format (16-bit) and place them in the `input/` 
directory.

Execute the script:  you can do this by navigating to the directory containing the script and 
input directory in a terminal or command prompt and running `python3 visualizer.py` 

A PyGame window should appear with your visualizations, 
you can change the window size by editing the `screen_width` and 
`screen_height` variables in the `visualizer.py` script. 

Controls:
- You can quit at any time and skip the rest of the songs by closing the window.
- Press H for controls
- The current song name will be displayed at the top of the window.
