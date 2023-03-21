from tkinter import BitmapImage


def get_bpm_filter(bpm_list):
    bpmLow = bpm_list[0]
    filter = f"((NOT BPM LESS {bpmLow}"

    bpmHi = bpm_list[1]
    filter = filter + f" AND NOT BPM GREATER {bpmHi})"


    # "SECONDARY BPM RANGE (DOUBLED OR HALVED)"
    if type(bpmLow) == int:
        # print(bpmLow)
        if bpmLow > 80:
            bpmLow2 = int(bpmLow / 2)
            bpmHi2 = int(bpmHi / 2)
        else:
            bpmLow2 = int(bpmLow * 2)
            bpmHi2 = int(bpmHi * 2)
        if bpmLow2:
            filter = filter + f" OR (NOT BPM LESS {bpmLow2} AND NOT BPM GREATER {bpmHi2})) AND "
    return filter