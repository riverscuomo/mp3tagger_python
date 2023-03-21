import tkinter as tk
from tkinter import ttk as ttk
import winsound
import threading
from data.constants import *
from data.sections import *


NEUTRAL = 1
OFF = 0
ON = 2


# Only called at initialization
def build_scale(window, label, param, value, toggle_command, command):

    # print('build_scale()')

    all = tk.StringVar()

    # Set initial troughcolor
    if value == ON:
        troughcolor = 'green'
    if value == NEUTRAL:
        troughcolor = middle_color
    if value == OFF:
        troughcolor = 'coral3'

    scale = tk.Scale(window, from_=0, to=2, orient='horizontal', showvalue=0,
                     label=f"  {param}  ", length=65, sliderlength=20, width=18,
                     repeatdelay=125, troughcolor=troughcolor, variable=all, bg=bg_color, fg=fg_color, bd=3, highlightthickness=0,
                     activebackground=activebackground_color, font=param_font)
    scale.set(value)

    if '*' in param:
        print(param)
        scale.configure(command=lambda value, toggled_section_name=label : toggle_command(value, toggled_section_name))
        # scale.configure(command=toggle_command)
        # print(scale)
        # print(scale['command'])
    
    else:
        scale.configure(command=command)

    
    # print(scale)

    return scale


def report_change(self, name, value):
        print("%s changed to %s" % (name, value))


# Only called at initialization
def build_section(window, section, row, column, toggle_command, command):

    # print('build_section()')

    scales = []
    
    # Toggle Control scale that will set all the scales in this section
    scale = build_scale(window, section['label'], '      *', section['group_control'], toggle_command=toggle_command, command=command)
    scale.grid(row=row, column=column, padx=10, pady=0)
    scales.append(scale)

    # The label for this section
    row = row + 1
    label = tk.Label(window, text=section['label'], bg=bg_color, fg=fg_color)
    label.config(font=(header_font, header_font_size))
    label.grid(row=row, column=column, padx=10)

    # NO BLANKS CHECKBOX
    row += 1
    variable = section['no_blanks']
    no_blanks_checkbox = tk.Checkbutton(window, variable=variable, bg=bg_color, fg=fg_color, selectcolor="#333333") # text='include blanks', 
    no_blanks_checkbox.grid(row=row, column=column)
    # no_blanks_checkbox.select()

    
    
    # # A separator
    
    # row = row + 1

    # style = ttk.Style()


    # style.configure("Separator.separator", background="black")
    
    
    # sep = ttk.Separator(window, style="Separator.separator")
    # sep.grid(row=row, column=column, sticky="NSEW")
    

    
    # print(s.layout('TSeparator')) # [('Separator.separator', {'sticky': 'nswe'})]
    # print(s.element_options('Separator.separator')) 
    
    # Build each scale in this section
    for s in section['scales']:
        row = row + 1
        scale = build_scale(window, section['label'], param=s[0], value=s[1], toggle_command=toggle_command, command=command)
        scale.grid(row=row, column=column, padx=10, pady=5)
        scales.append(scale)

    section = {
        'label': label,
        'scales': scales,
        'no_blanks': variable,
    }

    return section


def clean_filter(filter):
    filter = filter.strip()
    filter = filter.strip('AND')
    filter = filter.strip('OR')
    filter = filter.strip()
    return filter


