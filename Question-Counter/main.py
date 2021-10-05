import sys, os, qcount

if '-c' in sys.argv:
    i = input("Load file? (y/n) > ")
    if i.lower == 'y':
        i = input("File name (leave blank for 'save.json') > ")
        if i == '' and os.path.isfile('save.json'):
            data = qcount.load('save.json')
        elif os.path.isfile(i):
            data = qcount.load(i)
        else:
            raise FileNotFoundError("File not found")
    else:
        questions = qcount.parse_input(input("Input the questions that need to be completed. > "))
    qcount.main()
    sys.exit()

from tkinter import *
from tkinter import ttk, messagebox, filedialog

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Question Counter")
        self.master.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        self.master.iconbitmap('icon.ico')

        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill=BOTH, expand=True)
        