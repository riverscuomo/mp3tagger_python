from dotenv import load_dotenv
load_dotenv()

import threading
from mp3tagger.scripts.builders import *
from mp3tagger.scripts.bpm import *
from mp3tagger.scripts.automate import *
from mp3tagger.data.constants import *
from mp3tagger.data.sections import *
from mp3tagger.widgets.tkSliderWidget import *
import os
import tkinter as tk
from tkinter import IntVar, ttk as ttk
from tkinter import Scrollbar, Canvas, WORD, IntVar, END
import subprocess

"""
pywinauto

pyWin32
comtypes
six
(optional) Pillow (to make screenshoots)

the default (win32) DOES NOT FIND THE ELEMENTS IN MP3TAG!
switch to backend="uia" like this:  app = Application(backend="uia")

you can look at mp3tag through inspect.exe

"""

NEUTRAL = 1
OFF = 0
ON = 2
sections_data.reverse()


def set_filter_string(value):

    # This is async so you may hear it after everything else
    # click()

    # Get user value from input
    my_filter = ""

    # print(IncludeBpm.get())

    if IncludeBpm.get() == 1:
        my_filter = get_bpm_filter(slider.getValues())

    for section in sections:

        my_filter = get_filter_From_section(my_filter, section, control_toggle_pressed=False)

    my_filter = clean_filter(my_filter)

    my_filter = my_filter.replace(" AND ", "\n")

    # Empty the Text boxes if they had text from the previous use and fill them again
    # Deletes the content of the Text box from start to END
    # textbox.delete("1.0", END)
    textbox.delete("1.0", "end-1c")  # Clear the current content
    # Fill in the text box with the value of gram variable
    textbox.insert(END, my_filter)


def set_filter_string_from_toggle(value, toggled_section_name=None):
    print("in")
    print(toggled_section_name)

    # This is async so you may hear it after everything else
    # click()

    # Get user value from input
    my_filter = ""

    # print(IncludeBpm.get())

    if IncludeBpm.get() == 1:
        my_filter = get_bpm_filter(slider.getValues())

    for section in sections:
        # print(section['label']['text'] )

        if section["label"]["text"] == toggled_section_name:
            my_filter = get_filter_From_section(
                my_filter, section, control_toggle_pressed=True
            )
            # print('control_toggle_pressed=True')

        else:
            my_filter = get_filter_From_section(
                my_filter, section, control_toggle_pressed=False
            )
            # print('control_toggle_pressed=False')

    my_filter = clean_filter(my_filter)

    my_filter = my_filter.replace(" AND ", "\n")

    # Empty the Text boxes if they had text from the previous use and fill them again
    # Deletes the content of the Text box from start to END
    # textbox.delete("1.0", END)
    textbox.delete("1.0", "end-1c")
    # Fill in the text box with the value of gram variable
    textbox.insert(END, my_filter)


def get_filter_From_section(my_filter, section, control_toggle_pressed):

    # pprint(section)

    label, positive_filters, negative_filters = get_filters(
        section, control_toggle_pressed
    )

    positive_filter = f"({label} MATCHES "
    negative_filter = f" (NOT {label} MATCHES "
    absent_amendment = f" OR {label} ABSENT) AND "
    no_blanks = section["no_blanks"].get()

    if no_blanks == 1:
        # print('got it')
        no_blanks = True
    else:
        no_blanks = False

    if positive_filters:
        positive_filter = positive_filter + "|".join(positive_filters)
        if no_blanks:
            positive_filter += ") AND "
        else:
            positive_filter += absent_amendment

        my_filter += positive_filter
    if negative_filters:
        negative_filter += "|".join(negative_filters)
        negative_filter += ") AND "
        my_filter = my_filter + negative_filter

    return my_filter


# THIS IS THE ONE
def get_filters(section, control_toggle_pressed):

    label = section["label"]["text"].strip()
    # print(f'get filters for {label}')
    positive_filters = []
    negative_filters = []

    control_toggle_value = section["scales"][0].get()
    # print(f'control_toggle_value: {control_toggle_value}')

    # if not control_toggle_value == NEUTRAL:

    if control_toggle_pressed:
        print("control_toggle_pressed so setting scale value to ", control_toggle_value)
        for scale in section["scales"]:
            scale.set(control_toggle_value)

    for scale in section["scales"]:
        # print(scale['label'])
        value = scale.get()

        if "*" in scale["label"].lower():
            # print('got it!')
            # print(value)
            # scale.set(0)
            continue

        if value == OFF:
            scale.configure(troughcolor="coral3")
            negative_filters.append(scale["label"].strip())
        if value == NEUTRAL:
            scale.configure(troughcolor=middle_color)
            continue
        if value == ON:
            scale.configure(troughcolor="green")
            positive_filters.append(scale["label"].strip())

    return label, positive_filters, negative_filters


def copy_to_mp3tag():  # sourcery skip: use-fstring-for-concatenation

    my_filter = textbox.get("1.0", "end-1c")
    my_filter = my_filter.replace("\n", " AND ")

    if HoldAbsent.get() == 1:
        my_filter = my_filter + " AND HOLD ABSENT"
    if DeselectAbsent.get() == 1:
        my_filter = my_filter + " AND DESELECT ABSENT"
    threading.Thread(target=automate, args=(my_filter,)).start()

# Update the window's scrolling region on a configure event of the frame
def onFrameConfigure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Create an empty Tkinter window
def set_up_window():
    window = tk.Tk()
    window.title("MP3 Tagger")
    window.configure(bg=bg_color, highlightcolor=fg_color)

    # This line maximizes the window. To use this on Windows:
    window.state('zoomed')
    return window


def create_frame(onFrameConfigure, window):
    # Create the canvas and the horizontal scrollbar
    canvas = Canvas(window, bg=bg_color, highlightthickness=0)  # Set background color here and remove highlight
    h_scrollbar = Scrollbar(window, orient='horizontal', command=canvas.xview)
    canvas.configure(xscrollcommand=h_scrollbar.set)

    # Create the frame to hold the widgets within the canvas, setting the bg_color
    frame = tk.Frame(canvas, bg=bg_color)  # Set background color here

    # Add the canvas and scrollbar to the window
    canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Add the frame to the canvas
    canvas.create_window((0, 0), window=frame, anchor='nw')

    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    return frame

window = set_up_window()
frame = create_frame(onFrameConfigure, window)

row = 0
column = 0
sections = []

# At runtime, do an initial build of each section.
# This includes the toggle control, the label, the no_blanks checkbox,
# a separator, and then a 3 position scale for each param in the section.
for x in sections_data:

    # Add a tkinter Intvar() to hold the no_blanks value for each section
    x["no_blanks"] = IntVar(name="NoBlanks" + x["label"])

    section = build_section(
        frame,
        x,
        row=row,
        column=column,
        toggle_command=set_filter_string_from_toggle,
        command=set_filter_string,
    )
    sections.append(section)
    column += 1

# BPM Label
column += 1
bpm_label = tk.Label(frame, text="BPM Range", bg=bg_color, fg=fg_color)
bpm_label.grid(row=row, column=column)


# BPM slider
row += 1
# NOTE: This is a custom widget in the widgets folder
slider = Slider(
    frame,
    width=600,
    height=50,
    min_val=55,
    max_val=140,
    init_lis=[80, 100],
    show_value=True,
)
# slider.configure(bg=bg_color)
slider.grid(row=row, column=column)

# BPM CHECKBOX
row += 1
IncludeBpm = IntVar()
bpm_checkbox = tk.Checkbutton(
    frame,
    text="include BPM",
    variable=IncludeBpm,
    bg=bg_color,
    fg=fg_color,
    selectcolor="#333333",
)
bpm_checkbox.grid(row=row, column=column)
bpm_checkbox.select()

# HOLD CHECKBOX
row += 1
HoldAbsent = IntVar()
hold_checkbox = tk.Checkbutton(
    frame,
    text="exclude files on hold",
    variable=HoldAbsent,
    bg=bg_color,
    fg=fg_color,
    selectcolor="#333333",
)
hold_checkbox.grid(row=row, column=column)
hold_checkbox.select()

# DESELECT ABSENT
row += 1
DeselectAbsent = IntVar()
hold_checkbox = tk.Checkbutton(
    frame,
    text="exclude deselect",
    variable=DeselectAbsent,
    bg=bg_color,
    fg=fg_color,
    selectcolor="#333333",
)
hold_checkbox.grid(row=row, column=column)
hold_checkbox.select()

# The Filter button
row += 2
b1 = tk.Button(frame, text="FILTER", command=copy_to_mp3tag, bg=bg_color, fg=fg_color)
b1.grid(row=row, column=column)

# THE FILTER TEXTBOX
textbox = tk.Text(
    frame, wrap=WORD, padx=10, bg=bg_color, fg=fg_color, font=filter_font
)
row += 1
textbox.grid(
    row=row,
    column=column,
    rowspan=5,
    pady=17,
)
textbox.delete("1.0", END)



mp3tag_path = os.environ.get("MP3TAG_PATH")
# At runtime, open mp3tag
subprocess.Popen(
    [mp3tag_path]
)  # https://stackoverflow.com/questions/37238645/how-to-open-external-programs-in-python # ARGH I FORGOT TO PUT THE PROGRAM NAME AGAIN, THE .EXE!!!

# This makes sure to keep the main window open
window.mainloop()

