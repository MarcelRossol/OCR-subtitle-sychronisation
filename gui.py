from tkinter import *
from tkinter import filedialog

root = Tk()
root.title('Create video subtitles')
file_paths = {}


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


video_path_button = Button(root, text="Select video", command=get_video_path)
text_path_button = Button(root, text="Select text", command=get_text_path)
start_button = Button(root, text="Start", state=DISABLED)

video_path_button.pack()
text_path_button.pack()
start_button.pack()


root.mainloop()


