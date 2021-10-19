from io import TextIOWrapper
import os, json, sys
import qcount

from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog

# TODO: Add error handling
# TODO: Finish Undo and Redo
# TODO: Add SSH / Password support
# TODO: Fix keyboard shortcuts
# TODO: Add Menu Bar item for Questions
# TODO: Add option to view all questions / completed questions

class Application(ttk.Frame):
    def __init__(self, master:Tk=None):
        super().__init__(master)
        self.master:Tk = master
        self.master.title("Question Counter")
        # self.master.geometry("400x400")
        self.pack(fill="both", expand=True)
        self.question = None
        self.questions = []
        self.completed = []
        self.undid = {"completed": [], "questions": []}
        self.redid = {"completed": [], "questions": []}
        self.savefile = None
        self.create_menubar()
        self.create_widgets()
        self.buttons = [
            self.next_button, 
            self.add_completed_button, 
            self.edit_completed_button, 
            self.add_questions_button, 
            self.edit_questions_button, 
            self.reset_completed_button
        ]
        self.disable_buttons() # Disable buttons when no questions are loaded

    def create_menubar(self):
        modifier = "Command" if sys.platform == "darwin" else "Control"
        self.menubar = Menu(self.master, background='#ff8000', foreground='black', activebackground='white', activeforeground='black') 

        self.file = Menu(self.menubar, tearoff=1, background='#ffcc99', foreground='black')  
        self.file.add_command(label="New", command=self.new_file, accelerator= modifier + "+N")
        self.file.add_command(label="Open", command=self.open_file, accelerator= modifier + "+O")  
        self.file.add_command(label="Save", command=self.save_file, accelerator= modifier + "+S")  
        self.file.add_command(label="Save as", command=self.save_as_file, accelerator= modifier + "+Shift+S")    
        self.file.add_separator()
        self.menubar.add_cascade(label="File", menu=self.file)  

        self.edit = Menu(self.menubar, tearoff=0)  
        self.edit.add_command(label="Undo", command=self.undo_action, accelerator= modifier + "+Z", state=DISABLED)  
        self.edit.add_command(label="Redo", command=self.redo_action, accelerator= modifier + "+Y", state=DISABLED)  
        self.edit.add_separator()     
        self.edit.add_command(label="Cut", accelerator= modifier + "+X")  
        self.edit.add_command(label="Copy", accelerator= modifier + "+C")  
        self.edit.add_command(label="Paste", accelerator= modifier + "+V")  
        self.edit.add_command(label="Select All", accelerator= modifier + "+A")  
        self.menubar.add_cascade(label="Edit", menu=self.edit)  

        self.help = Menu(self.menubar, tearoff=0)  
        self.help.add_command(label="About", command=self.about)  
        self.menubar.add_cascade(label="Help", menu=self.help) 

        self.master.config(menu=self.menubar)

    def create_widgets(self):
        self.question_frame1 = ttk.Frame(self)
        self.question_frame1.pack(fill="both", expand=True)

        self.question_label = ttk.Label(self.question_frame1, text="Question: 0")
        self.question_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.total_label = ttk.Label(self.question_frame1, text="Total: 0")
        self.total_label.pack(side="right", padx=5, pady=5, fill="x", expand=True)

        self.question_frame2 = ttk.Frame(self)
        self.question_frame2.pack(fill="both", expand=True)

        self.remaining_label = ttk.Label(self.question_frame2, text="Remaining: 0")
        self.remaining_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.completed_label = ttk.Label(self.question_frame2, text="Completed: 0")
        self.completed_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.button_frame1 = ttk.Frame(self)
        self.button_frame1.pack(fill="x", expand=True)

        self.next_button = ttk.Button(self.button_frame1, text="Next", command=self.next_question)
        self.next_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.button_frame2 = ttk.Frame(self)
        self.button_frame2.pack(fill="x", expand=True)

        self.add_completed_button = ttk.Button(self.button_frame2, text="Add Completed", command=self.add_completed)
        self.add_completed_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.edit_completed_button = ttk.Button(self.button_frame2, text="Edit Completed", command=self.edit_completed)
        self.edit_completed_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.button_frame3 = ttk.Frame(self)
        self.button_frame3.pack(fill="x", expand=True)

        self.add_questions_button = ttk.Button(self.button_frame3, text="Add Questions", command=self.add_questions)
        self.add_questions_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.edit_questions_button = ttk.Button(self.button_frame3, text="Edit Questions", command=self.edit_questions)
        self.edit_questions_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.button_frame4 = ttk.Frame(self)
        self.button_frame4.pack(fill="x", expand=True)

        self.reset_completed_button = ttk.Button(self.button_frame4, text="Reset Completed", command=self.reset_completed)
        self.reset_completed_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

    def disable_buttons(self):
        for button in self.buttons:
            button.config(state=DISABLED)
    def enable_buttons(self):
        for button in self.buttons:
            button.config(state=NORMAL)

    def next_question(self):
        if self.question is not None:
            self.completed += [self.question]
        self.find_next()
        self.update_labels()
    def add_completed(self):
        add = [*qcount.parse_input(simpledialog.askstring("Add Completed","Enter questions to add to completed: "))]
        for item in add:
            if not item in self.completed:
                self.completed += [item]
        self.update_labels()
    def edit_completed(self):
        ...
    def add_questions(self):
        ...
    def edit_questions(self):
        ...
    def reset_completed(self):
        ...

    def about(self):
        messagebox.showinfo("About", "This is a Question Counter")

    def new_file(self):
        self.savefile = "\U0001f539 Untitled"
        self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")
        questions = simpledialog.askstring("New File", "Enter the numbers of the questions:")
        if questions:
            self.questions = qcount.parse_input(questions)
        self.update_labels()
        self.enable_buttons()
    def open_file(self):
        self.savefile = filedialog.askopenfilename(
            initialdir = ".",
            title = "Open file",
            filetypes = (
                ("JSON Files","*.json"),
                ("All Files","*.*"),
            ),
        )
        if not self.savefile:
            return
        self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")
        self.questions, self.completed = qcount.load(file = self.savefile)
        self.find_next()
        self.enable_buttons()
    def save_file(self):
        if self.savefile == "\U0001f539 Untitled":
            self.save_as_file()
        else:
            qcount.save(file = self.savefile, questions = self.questions, completed = self.completed)
    def save_as_file(self):
        self.savefile = filedialog.asksaveasfilename(
            title="Save As",
            initialdir=".", 
            filetypes=(("JSON Files","*.json"),("All Files","*.*")), 
            defaultextension=".json",
            initialfile="Untitled.json",
        )
        qcount.save(file = self.savefile, questions = self.questions, completed = self.completed)
        self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")

    def update_labels(self):
        self.find_next()
        self.question_label.config(text="Question: " + str(self.question))
        self.total_label.config(text="Total: " + str(len(self.questions)))
        self.remaining_label.config(text="Remaining: " + str(len(self.questions)-len(self.completed)))
        self.completed_label.config(text="Completed: " + str(len(self.completed)))

    def find_next(self):
        for question in self.questions:
            if question not in self.completed:
                self.question = question
                break

    def undo_action(self):
        ...
    def redo_action(self):
        ...

root = Tk()
app = Application(master=root)
app.mainloop()