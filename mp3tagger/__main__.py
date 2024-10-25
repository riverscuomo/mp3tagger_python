from dotenv import load_dotenv
from mp3tagger.classes.mp3_tagger import MP3TaggerApp
load_dotenv()

from mp3tagger.scripts.builders import *
from mp3tagger.scripts.bpm import *
from mp3tagger.scripts.automate import *
from mp3tagger.data.constants import *
from mp3tagger.data.sections import *
from mp3tagger.classes.slider import *
import tkinter as tk
import logging

"""
pywinauto

pyWin32
comtypes
six
(optional) Pillow (to make screenshots)

the default (win32) DOES NOT FIND THE ELEMENTS IN MP3TAG!
switch to backend="uia" like this:  app = Application(backend="uia")

you can look at mp3tag through inspect.exe
"""

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mp3_tagger.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

def main():
    root = tk.Tk()
    app = MP3TaggerApp(root)

if __name__ == "__main__":
    main()

