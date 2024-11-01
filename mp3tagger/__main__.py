import tkinter as tk
from classes.my_slider import *
from data.sections import *
from data.constants import *
from scripts.automate import *
from scripts.bpm import *
from scripts.builders import *
from dotenv import load_dotenv
from classes.mp3_tagger import MP3TaggerApp
load_dotenv()


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


def main():
    root = tk.Tk()
    app = MP3TaggerApp(root)


if __name__ == "__main__":
    main()
