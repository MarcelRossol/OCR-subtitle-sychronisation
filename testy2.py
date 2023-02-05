from tkinter import *
from tkinter import filedialog

root = Tk()
root.geometry('300x100')
root.title('Create video subtitles')
file_paths = {}


def changeState():
    if (start_button['state'] == NORMAL):
        start_button['state'] = DISABLED
    else:
        start_button['state'] = NORMAL


def get_video_path():
    root.video_path = filedialog.askopenfilename(initialdir="C:/", title="Select video",
                                                 filetypes=((".mp4 files", "*.mp4"), ("all files", "*.*")))
    video_path = root.video_path
    file_paths['video_path'] = video_path
    print(file_paths)
    print(len(list(file_paths.keys())))
    if len(list(file_paths.keys())) == 2:
        start_button['state'] = NORMAL



def get_text_path():
    root.text_path = filedialog.askopenfilename(initialdir="C:/", title="Select video",
                                                filetypes=((".txt files", "*.txt"), ("all files", "*.*")))
    text_path = root.text_path
    file_paths['text_path'] = text_path
    print(file_paths)
    print(len(list(file_paths.keys())))
    if len(list(file_paths.keys())) == 2:
        start_button['state'] = NORMAL




start_button = Button(root, text="Start", state=DISABLED)
start_button.pack()

btn2 = Button(root, text="Enable/Disable Btn 1", command=changeState)
btn2.pack(side = RIGHT)

start_button['state'] = NORMAL



root.mainloop()

