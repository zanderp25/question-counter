from io import TextIOWrapper
import os, json, sys
from typing import Literal, Union
import qcount

from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog

# TODO: Disable save and save as when nothing is loaded
# TODO: Make an unsaved work quwstion prompt
# TODO: Finish Undo and Redo
#      - make function for updating undo/redo history and buttons
# TODO: Add a progress bar
# TODO: make about page look nicer
#      - maybe add html viewer or something
# TODO: implement preferences menu button on macOS
# TODO: Parse input with spaces before and after dashes
# TODO: Add error handling
# TODO: Add SSH / Password support

class Application(ttk.Frame):
    def __init__(self, master:Tk=None):
        super().__init__(master)
        self.master:Tk = master
        self.master.title("Question Counter")
        self.master.geometry("250x100")
        self.pack(fill="both", expand=True)
        self.question = None
        self.questions = []
        self.completed = []
        self.undo_history = []
        self.redo_history = []
        self.savefile = None
        self.create_menubar()
        self.create_widgets()
        self.buttons = [
            self.next_button
        ]
        self.disable_buttons() # Disable buttons when no questions are loaded

    def create_menubar(self):
        modifier = "Command" if sys.platform == "darwin" else "Control"
        self.menubar = Menu(self.master)

        self.file = Menu(self.menubar, tearoff=0)  
        self.file.add_command(label="New", command=self.new_file, accelerator= modifier + "+N")
        self.master.bind_all(f"<{modifier}-n>", lambda a: self.new_file())
        self.file.add_command(label="Open", command=self.open_file, accelerator= modifier + "+O")
        self.master.bind_all(f"<{modifier}-o>", lambda a: self.open_file())
        self.file.add_command(label="Save", command=self.save_file, accelerator= modifier + "+S")
        self.master.bind_all(f"<{modifier}-s>", lambda a: self.save_file())
        self.file.add_command(label="Save as", command=self.save_as_file, accelerator= modifier + "+Shift+S")
        self.master.bind_all(f"<{modifier}-S>", lambda a: self.save_as_file())
        self.file.add_separator()
        self.menubar.add_cascade(label="File", menu=self.file)  

        self.edit = Menu(self.menubar, tearoff=0)  
        self.edit.add_command(label="Undo", command=self.undo_action, accelerator= modifier + "+Z", state=DISABLED)
        self.master.bind_all(f"<{modifier}-z>", lambda a: self.undo_action())
        self.edit.add_command(label="Redo", command=self.redo_action, accelerator= modifier + "+Y", state=DISABLED)
        self.master.bind_all(f"<{modifier}-y>", lambda a: self.redo_action())
        self.edit.add_separator()     
        self.edit.add_command(label="Cut", accelerator= modifier + "+X")
        self.edit.add_command(label="Copy", accelerator= modifier + "+C")
        self.edit.add_command(label="Paste", accelerator= modifier + "+V")
        self.edit.add_command(label="Select All", accelerator= modifier + "+A")
        self.menubar.add_cascade(label="Edit", menu=self.edit)  

        self.questions_menu = Menu(self.menubar, tearoff=0)
        self.questions_menu.add_command(label="Next Question", command=self.next_on_click, accelerator= "Return" if sys.platform == "darwin" else "Enter")
        self.master.bind_all("<Return>", lambda a: self.next_on_click())
        self.questions_menu.add_separator()
        self.questions_menu.add_command(label="Add Questions", command=self.add_questions, accelerator= modifier + "+M")
        self.master.bind_all(f"<{modifier}-m>", lambda a: self.add_questions())
        self.questions_menu.add_command(label="Edit Questions", command=self.edit_questions, accelerator= modifier + "+E")
        self.master.bind_all(f"<{modifier}-e>", lambda a: self.edit_questions())
        self.questions_menu.add_separator()
        self.questions_menu.add_command(label="Add Completed", command=self.add_completed, accelerator= modifier + "+Shift+M")
        self.master.bind_all(f"<{modifier}-Shift-m>", lambda a: self.add_completed())
        self.questions_menu.add_command(label="Edit Completed", command=self.edit_completed, accelerator= modifier + "+Shift+E")
        self.master.bind_all(f"<{modifier}-Shift-e>", lambda a: self.edit_completed())
        self.questions_menu.add_separator()
        self.questions_menu.add_command(label="Reset Completed", command=self.reset_completed, accelerator= modifier + "+R")
        self.master.bind_all(f"<{modifier}-r>", lambda a: self.reset_completed())
        self.menubar.add_cascade(label="Questions", menu=self.questions_menu)

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

        self.next_button = ttk.Button(self.button_frame1, text="Next", command=self.next_on_click)
        self.next_button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

    def disable_buttons(self):
        for button in self.buttons:
            button.config(state=DISABLED)
        self.menubar.entryconfig("Questions", state=DISABLED)
    def enable_buttons(self):
        for button in self.buttons:
            button.config(state=NORMAL)
        self.menubar.entryconfig("Questions", state=NORMAL)

    def next_on_click(self):
        self.add_undo()
        self.next_question()

    def next_question(self):
        self.undo_history += [{"questions": self.questions, "completed": self.completed}]
        if self.question is not None:
            if not self.question in self.completed and self.question != None:
                self.completed += [self.question]
        self.update_labels()

    def add_completed(self):
        add = [*qcount.parse_input(simpledialog.askstring("Add Completed","Enter questions to add to completed: "))]
        for item in add:
            if not item in self.completed:
                self.completed += [item]
        self.update_labels()
        self.add_undo()
        self.master.focus_force()
    def reset_completed(self):
        if messagebox.askyesno("Reset Completed","Are you sure you want to reset completed?"):
            self.completed = []
            self.add_undo()
            self.update_labels()
        self.master.focus_force()
    def add_questions(self):
        add = [*qcount.parse_input(simpledialog.askstring("Add Questions","Enter questions to add to questions: "))]
        for item in add:
            if not item in self.questions:
                self.questions += [item]
        self.add_undo()
        self.update_labels()
        self.master.focus_force()
    def edit_questions(self):
        self.toplevel = Editor(master=Toplevel(), root = self, completed=False)
    def edit_completed(self):
        self.toplevel = Editor(master=Toplevel(), root = self, completed=True)

    def about(self):
        messagebox.showinfo("About", "This is a Question Counter")

    def new_file(self):
        questions = simpledialog.askstring("New File", "Enter the numbers of the questions:")
        if questions:
            self.questions = qcount.parse_input(questions)
            self.completed = []
            self.savefile = "\U0001f539 Untitled"
            self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")
            self.clear_history()
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
        self.clear_history()
        self.next_question()
        self.enable_buttons()
        self.master.focus_force()
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
        self.master.focus_force()

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
        else:
            self.question = None

    def undo_action(self):
        print(self.undo_history)
        if len(self.undo_history) > 0:
            self.redo_history += [{"questions":self.questions, "completed":self.completed}]
            self.edit.entryconfig("Redo", state=NORMAL)
            action = self.undo_history[-1]
            self.completed = action["completed"]
            self.questions = action["questions"]
        self.undo_history = self.undo_history[:-1]
        if len(self.undo_history) == 0:
            self.edit.entryconfig("Undo", state=DISABLED)
        self.update_labels()
    def redo_action(self):
        if len(self.redo_history) > 0:
            self.undo_history += [{"questions":self.questions, "completed":self.completed}]
            action = self.redo_history[-1]
            self.completed = action["completed"]
            self.questions = action["questions"]
        self.redo_history = self.redo_history[:-1]
        if len(self.redo_history) == 0:
            self.edit.entryconfig("Redo", state=DISABLED)
        self.update_labels()

    def add_undo(self):
        print(self.undo_history)
        self.undo_history += [{"questions":self.questions, "completed":self.completed}]
        print(self.undo_history)
        self.edit.entryconfig("Undo", state=NORMAL)
        self.redo_history = []
        self.edit.entryconfig("Redo", state=DISABLED)

    def clear_history(self):
        self.undo_history = []
        self.redo_history = []
        self.edit.entryconfig("Undo", state=DISABLED)
        self.edit.entryconfig("Redo", state=DISABLED)

class Editor(ttk.Frame):
    def __init__(self, master:Toplevel, root:Application, completed:bool):
        super().__init__(master)
        self.master = master
        self.completed = completed
        self.root = root
        self.pack(fill="both", expand=True)
        self.values = StringVar()
        if not self.completed:
            val = self.root.questions
            self.master.title("Edit Questions")
        else:
            val = self.root.completed
            self.master.title("Edit Completed")
        val.sort()
        self.values.set("\n".join([str(e) for e in val]))
        self.oldcount = self.root.questions if not self.completed else self.root.completed
        self.create_widgets()
        self.master.focus_force()
    
    def create_widgets(self):
        self.listframe = ttk.Frame(self)
        self.listframe.pack(side="top", fill="both", expand=True)
        self.list = Listbox(self.listframe, width=20, height=10, listvariable=self.values, selectmode=EXTENDED)
        self.list.pack(side="left", fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.listframe, orient="vertical", command=self.list.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.list.config(yscrollcommand=self.scrollbar.set)
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side="top", padx=5, pady=5, fill="x", expand=True)
        self.add_button = ttk.Button(self.button_frame, text="Add", command=self.add)
        self.add_button.pack(side="left", fill="x", expand=True)
        self.remove_button = ttk.Button(self.button_frame, text="Remove", command=self.remove)
        self.remove_button.pack(side="left", fill="x", expand=True)
        self.button_frame2 = ttk.Frame(self)
        self.button_frame2.pack(side="top", padx=5, pady=5, fill="x", expand=True)
        self.cancel_button = ttk.Button(self.button_frame2, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side="left", fill="x", expand=True)
        self.ok_button = ttk.Button(self.button_frame2, text="OK", command=self.ok)
        self.ok_button.pack(side="left", fill="x", expand=True)

    def add(self):
        nlist = (list(eval(self.values.get())) if len(self.values.get()) > 0 else [])
        add = [*qcount.parse_input(simpledialog.askstring("Add Questions","Enter questions to add to questions: "))]
        for item in add:
            if not item in nlist:
                nlist += [item]
        self.values.set("\n".join([str(e) for e in nlist]))
        self.list.yview_moveto(1)
        self.list.focus_force()
    def remove(self):
        if len(self.list.curselection()) == 0:
            return
        oldlist = eval(self.values.get())
        newlist = [item for item in oldlist if item not in [oldlist[i] for i in self.list.curselection()]]
        self.values.set("\n".join(newlist))
    def cancel(self):
        self.master.destroy()
    def ok(self):
        if not self.completed:
            self.root.questions = [int(e) for e in list(eval(self.values.get()))]
        else:
            self.root.completed = [int(e) for e in list(eval(self.values.get()))]
        self.root.update_labels()
        self.root.add_undo()
        self.root.master.focus_force()
        self.master.destroy()

app = Application(master=Tk())
app.mainloop()
