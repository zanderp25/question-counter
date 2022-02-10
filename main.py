import os, sys, locale
import qcount
from localize import localized

from tkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog

if sys.platform == "darwin":
    import PyTouchBar

# TODO: If a completed question is not in questions, add it (maybe prompt?)
# TODO: Filter duplicates
# TODO: make about page look nicer
# TODO: Parse input with spaces before and after dashes
# TODO: Add error handling

class Application(ttk.Frame):
    def __init__(self, master:Tk=None):
        super().__init__(master)
        self.master:Tk = master
        self.master.title("Question Counter")
        self.master.geometry("250x115")
        self.master.resizable(False, False)
        self.pack(fill="both", expand=True)
        self.master.protocol("WM_DELETE_WINDOW", self.on_quit)
        if sys.platform == "darwin":
            self.master.createcommand('tk::mac::Quit', self.on_quit)
        self.supported_languages = ["en", "es", "ja"]
        self.language = "en"
        if locale.getdefaultlocale()[0] is not None:
            if locale.getdefaultlocale()[0][:2] in self.supported_languages:
                self.language = locale.getdefaultlocale()[0][:2]
                print(f"Language set to {self.language}")
            else:
                print(f"Language {locale.getdefaultlocale()[0][:2]} not supported")
        else:
            print("Warning: Could not determine language.")
        self.question = None
        self.questions = []
        self.completed = []
        self.undo_history = []
        self.redo_history = []
        self.savefile = None
        self.saved = True
        # load settings from file
        self.create_menubar()
        self.create_widgets()
        if sys.platform == "darwin":
            self.create_touchbar()
        self.buttons = [
            self.next_button
        ]
        self.disable_buttons() # Disable buttons when no questions are loaded

    def on_quit(self) -> None:
        if not self.saved:
            e = messagebox.askyesnocancel(localized["quit"][self.language], localized["unsaved_changes_quit"][self.language])
            if e == True:
                self.save_file()
                self.master.destroy()
            elif e == False:
                self.master.destroy()
            else:
                pass
        else:
            self.master.destroy()

    def create_menubar(self) -> None:
        modifier = "Command" if sys.platform == "darwin" else "Control"
        self.menubar = Menu(self.master)

        if sys.platform == "darwin":
            self.appmenu = Menu(self.menubar, name='apple')
            self.menubar.add_cascade(menu=self.appmenu)
            self.appmenu.add_command(label=localized["about"][self.language], command=self.about)

        self.file = Menu(self.menubar, tearoff=0)  
        self.file.add_command(label=localized["new"][self.language], command=self.new_file, accelerator= modifier + "+N")
        self.master.bind(f"<{modifier}-n>", lambda a: self.new_file())
        self.file.add_command(label=localized["open"][self.language], command=self.open_file, accelerator= modifier + "+O")
        self.master.bind(f"<{modifier}-o>", lambda a: self.open_file())
        self.file.add_command(label=localized["save"][self.language], command=self.save_file, accelerator= modifier + "+S")
        self.master.bind(f"<{modifier}-s>", lambda a: self.save_file())
        self.file.add_command(label=localized["save_as"][self.language], command=self.save_as_file, accelerator= modifier + "+Shift+S")
        self.master.bind(f"<{modifier}-S>", lambda a: self.save_as_file())
        if sys.platform == "darwin":
            self.master.createcommand('tk::mac::ShowPreferences', self.preferences)
        else:
            self.file.add_separator()
            self.file.add_command(label=localized["preferences"][self.language], command=self.preferences, accelerator= modifier + "+,")
            self.master.bind(f"<{modifier}-comma>", lambda a: self.preferences())
            self.file.add_command(label=localized["quit"][self.language], command=self.on_quit, accelerator= modifier + "+Q")
            self.master.bind_all(f"<{modifier}-q>", lambda a: self.on_quit())
        self.menubar.add_cascade(label=localized["file"][self.language], menu=self.file)  

        self.edit = Menu(self.menubar, tearoff=0)  
        self.edit.add_command(label=localized["undo"][self.language], command=self.undo_action, accelerator= modifier + "+Z", state=DISABLED)
        self.master.bind(f"<{modifier}-z>", lambda a: self.undo_action())
        self.edit.add_command(label=localized["redo"][self.language], command=self.redo_action, accelerator= modifier + "+Y", state=DISABLED)
        self.master.bind(f"<{modifier}-y>", lambda a: self.redo_action())
        self.edit.add_separator()     
        self.edit.add_command(label=localized["cut"][self.language], accelerator= modifier + "+X")
        self.edit.add_command(label=localized["copy"][self.language], accelerator= modifier + "+C")
        self.edit.add_command(label=localized["paste"][self.language], accelerator= modifier + "+V")
        self.edit.add_command(label=localized["select_all"][self.language], accelerator= modifier + "+A")
        self.menubar.add_cascade(label=localized["edit"][self.language], menu=self.edit)  

        self.questions_menu = Menu(self.menubar, tearoff=0)
        self.questions_menu.add_command(label=localized["next_question"][self.language], command=self.next_on_click, accelerator= "Return" if sys.platform == "darwin" else "Enter")
        self.master.bind("<Return>", lambda a: self.next_on_click())
        self.questions_menu.add_separator()
        self.questions_menu.add_command(label=localized["add_question"][self.language], command=self.add_questions, accelerator= modifier + "+M")
        self.master.bind(f"<{modifier}-m>", lambda a: self.add_questions())
        self.questions_menu.add_command(label=localized["edit_questions"][self.language], command=self.edit_questions, accelerator= modifier + "+E")
        self.master.bind(f"<{modifier}-e>", lambda a: self.edit_questions())
        self.questions_menu.add_separator()
        self.questions_menu.add_command(label=localized["add_completed"][self.language], command=self.add_completed, accelerator= modifier + "+Shift+M")
        self.master.bind(f"<{modifier}-Shift-m>", lambda a: self.add_completed())
        self.questions_menu.add_command(label=localized["edit_completed"][self.language], command=self.edit_completed, accelerator= modifier + "+Shift+E")
        self.master.bind(f"<{modifier}-Shift-e>", lambda a: self.edit_completed())
        self.questions_menu.add_separator()
        self.questions_menu.add_command(label=localized["reset_completed"][self.language], command=self.reset_completed, accelerator= modifier + "+R")
        self.master.bind(f"<{modifier}-r>", lambda a: self.reset_completed())
        self.menubar.add_cascade(label=localized["questions"][self.language], menu=self.questions_menu)

        self.help = Menu(self.menubar, tearoff=0)
        if not sys.platform == "darwin":
            self.help.add_command(label=localized["about"][self.language], command=self.about)
        self.help.add_command(label=localized["get_help_online"][self.language], command=self.help_menu)
        self.menubar.add_cascade(label=localized["help"][self.language], menu=self.help) 

        self.master.config(menu=self.menubar)

    def create_touchbar(self):
        PyTouchBar.prepare_tk_windows(self.master)
        self.touchbar_items = []
        self.touchbar_next = PyTouchBar.TouchBarItems.Button(title = localized["next_question"][self.language], action = lambda a: self.next_on_click())
        self.touchbar_items += [self.touchbar_next]
        PyTouchBar.set_touchbar(self.touchbar_items)

    def create_widgets(self) -> None:
        self.question_frame1 = ttk.Frame(self)
        self.question_frame1.pack(fill="both", expand=True)

        self.question_label = ttk.Label(self.question_frame1, text=f"{localized['question'][self.language]}: 0")
        self.question_label.pack(side="left", padx=5, pady=2, fill="x", expand=True)
        self.total_label = ttk.Label(self.question_frame1, text=f"{localized['total'][self.language]}: 0")
        self.total_label.pack(side="right", padx=5, pady=2, fill="x", expand=True)

        self.question_frame2 = ttk.Frame(self)
        self.question_frame2.pack(fill="both", expand=True)

        self.remaining_label = ttk.Label(self.question_frame2, text=f"{localized['remaining'][self.language]}: 0")
        self.remaining_label.pack(side="left", padx=5, pady=2, fill="x", expand=True)
        self.completed_label = ttk.Label(self.question_frame2, text=f"{localized['completed'][self.language]}: 0")
        self.completed_label.pack(side="left", padx=5, pady=2, fill="x", expand=True)

        self.progress_var = IntVar()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=200, variable=self.progress_var)
        self.progress_bar.pack(padx=5, pady=0, fill="x", expand=True)

        self.button_frame1 = ttk.Frame(self)
        self.button_frame1.pack(fill="x", expand=True)

        self.next_button = ttk.Button(self.button_frame1, text=localized["next_question"][self.language], command=self.next_on_click)
        self.next_button.pack(side="left", padx=5, pady=(0,5), fill="x", expand=True)

    def disable_buttons(self):
        for button in self.buttons:
            button.config(state=DISABLED)
        self.menubar.entryconfig(localized["questions"][self.language], state=DISABLED)
        self.file.entryconfig(localized["save"][self.language], state=DISABLED)
        self.file.entryconfig(localized["save_as"][self.language], state=DISABLED)
    def enable_buttons(self):
        for button in self.buttons:
            button.config(state=NORMAL)
        self.menubar.entryconfig(localized["questions"][self.language], state=NORMAL)
        self.file.entryconfig(localized["save"][self.language], state=NORMAL)
        self.file.entryconfig(localized["save_as"][self.language], state=NORMAL)

    def next_on_click(self):
        self.add_undo()
        self.next_question()

    def next_question(self):
        if self.question is not None:
            if not self.question in self.completed and self.question != None:
                self.completed += [self.question]
        self.update_labels()

    def add_completed(self):
        add = simpledialog.askstring(localized["add_completed"][self.language], localized["add_completed_prompt"][self.language])
        if add is None: return
        add = [*qcount.parse_input(add)]
        for item in add:
            if not item in self.completed:
                self.completed += [item]
        self.update_labels()
        self.add_undo()
        self.master.focus_force()
    def reset_completed(self):
        if messagebox.askyesno(localized["reset_completed"][self.language],localized["reset_completed_prompt"][self.language]):
            self.completed = []
            self.add_undo()
            self.update_labels()
        self.master.focus_force()
    def add_questions(self):
        add = simpledialog.askstring(localized["add_question"][self.language],localized["add_question_prompt"][self.language])
        if add is None: return
        add = [*qcount.parse_input(add)]
        for item in add:
            if not item in self.questions:
                self.questions += [item]
        self.add_undo()
        self.update_labels()
        self.master.focus_force()
    def edit_questions(self):
        Editor(master=Toplevel(), root = self, completed=False)
    def edit_completed(self):
        Editor(master=Toplevel(), root = self, completed=True)

    def about(self):
        AboutScreen(master=Toplevel(), root = self)

    def preferences(self):
        Preferences(master=Toplevel(), root = self)

    def help_menu(self):
        link = f"https://question-counter.zanderp25.com/docs/{self.language}/"
        if sys.platform == "darwin":
            os.system(f'open "{link}"')
        elif sys.platform == "win32":
            os.system(f'start "" "{link}"')
        elif sys.platform == "linux":
            os.system(f'xdg-open "{link}"')
        else:
            messagebox.showerror("Error", "Unsupported platform detected.")
        self.master.focus_force()

    def new_file(self):
        questions = simpledialog.askstring(localized["new"][self.language], localized["new_prompt"][self.language])
        if questions:
            self.questions = qcount.parse_input(questions)
            self.completed = []
            self.savefile = "\U0001f539 Untitled"
            self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")
            self.saved = False
            self.clear_history()
            self.update_labels()
            self.enable_buttons()
    def open_file(self):
        self.savefile = filedialog.askopenfilename(
            initialdir = ".",
            title = localized["open"][self.language],
            filetypes = (
                (localized["json_filetype"][self.language],"*.json"),
                (localized["all_filetype"][self.language],"*.*"),
            ),
        )
        if not self.savefile: return
        self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")
        self.questions, self.completed = qcount.load(file = self.savefile)
        self.saved = True
        self.clear_history()
        self.next_question()
        self.enable_buttons()
        self.master.focus_force()
    def save_file(self):
        if self.savefile == "\U0001f539 Untitled":
            self.save_as_file()
        else:
            qcount.save(file = self.savefile, questions = self.questions, completed = self.completed)
        self.saved = True
    def save_as_file(self):
        self.savefile = filedialog.asksaveasfilename(
            title=localized["save_as"][self.language],
            initialdir=".", 
            filetypes=(("JSON Files","*.json"),("All Files","*.*")), 
            defaultextension=".json",
            initialfile="Untitled.json",
        )
        if not self.savefile: return
        qcount.save(file = self.savefile, questions = self.questions, completed = self.completed)
        self.master.title(os.path.split(self.savefile)[1] + " - Question Counter")
        self.saved = True
        self.master.focus_force()

    def update_labels(self):
        self.find_next()
        self.question_label.config(text=localized["question"][self.language]+ ": " + str(self.question))
        self.total_label.config(text=localized["total"][self.language] + ": " + str(len(self.questions)))
        self.remaining_label.config(text=localized["remaining"][self.language] + ": " + str(len(self.questions)-len(self.completed)))
        self.completed_label.config(text=localized["completed"][self.language] + ": " + str(len(self.completed)))
        try:
            self.progress_var.set(int(100*(len(self.completed)/len(self.questions))))
        except ZeroDivisionError:
            self.progress_var.set(0)

    def find_next(self):
        for question in self.questions:
            if question not in self.completed:
                self.question = question
                break
        else:
            self.question = None

    def undo_action(self):
        if len(self.undo_history) > 0:
            self.redo_history += [{"questions":list(self.questions), "completed":list(self.completed)}]
            self.edit.entryconfig(localized["redo"][self.language], state=NORMAL)
            action = self.undo_history[-1]
            self.completed = action["completed"]
            self.questions = action["questions"]
        self.undo_history = self.undo_history[:-1]
        if len(self.undo_history) == 0:
            self.edit.entryconfig(localized["undo"][self.language], state=DISABLED)
        self.update_labels()
    def redo_action(self):
        if len(self.redo_history) > 0:
            self.undo_history += [{"questions":list(self.questions), "completed":list(self.completed)}]
            self.edit.entryconfig(localized["undo"][self.language], state=NORMAL)
            action = self.redo_history[-1]
            self.completed = action["completed"]
            self.questions = action["questions"]
        self.redo_history = self.redo_history[:-1]
        if len(self.redo_history) == 0:
            self.edit.entryconfig(localized["redo"][self.language], state=DISABLED)
        self.update_labels()

    def add_undo(self):
        self.undo_history += [{"questions":list(self.questions), "completed":list(self.completed)}]
        self.redo_history = []
        self.edit.entryconfig(localized["undo"][self.language], state=NORMAL)
        self.edit.entryconfig(localized["redo"][self.language], state=DISABLED)
        self.saved = False

    def clear_history(self):
        self.undo_history = []
        self.redo_history = []
        self.edit.entryconfig(localized["undo"][self.language], state=DISABLED)
        self.edit.entryconfig(localized["redo"][self.language], state=DISABLED)

    def update_language(self, new_lang):
        for item in ["file", "edit", "questions", "help"]:
            self.menubar.entryconfig(localized[item][self.language], label=localized[item][new_lang])
        for item in ["new", "open", "save", "save_as"]:
            self.file.entryconfig(localized[item][self.language], label=localized[item][new_lang])
        for item in ["undo", "redo", "cut", "copy", "paste", "select_all"]:
            self.edit.entryconfig(localized[item][self.language], label=localized[item][new_lang])
        for item in ["next_question", "add_question", "edit_questions", "add_completed", "edit_completed", "reset_completed"]:
            self.questions_menu.entryconfig(localized[item][self.language], label=localized[item][new_lang])
        self.help.entryconfig(localized["get_help_online"][self.language], label=localized["get_help_online"][new_lang])
        if sys.platform == "darwin":
            self.appmenu.entryconfig(localized["about"][self.language], label=localized["about"][new_lang])
            self.touchbar_next.title = (localized["next_question"][new_lang])
        else:
            self.help.entryconfig(localized["about"][self.language], label=localized["about"][new_lang])
            self.file.entryconfig(localized["preferences"][self.language], label=localized["preferences"][new_lang])
            self.file.entryconfig(localized["quit"][self.language], label=localized["quit"][new_lang])
        self.next_button.config(text=localized["next_question"][new_lang])
        self.language = new_lang
        self.update_labels()
        self.master.focus_force()

class Editor(ttk.Frame):
    def __init__(self, master:Toplevel, root:Application, completed:bool):
        super().__init__(master)
        self.master = master
        self.completed = completed
        self.root = root
        self.master.minsize(width=200, height=240)
        self.pack(fill="both", expand=True)
        self.values = StringVar()
        if not self.completed:
            val = self.root.questions
            self.master.title(localized["edit_questions"][self.root.language])
        else:
            val = self.root.completed
            self.master.title(localized["edit_completed"][self.root.language])
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
        self.button_frame.pack(side="top", padx=5, pady=5, fill="x", expand=False)
        self.add_button = ttk.Button(self.button_frame, text=localized["add"][self.root.language], command=self.add)
        self.add_button.pack(side="left", fill="x", expand=True)
        self.remove_button = ttk.Button(self.button_frame, text=localized["remove"][self.root.language], command=self.remove)
        self.remove_button.pack(side="left", fill="x", expand=True)
        self.button_frame2 = ttk.Frame(self)
        self.button_frame2.pack(side="top", padx=5, pady=5, fill="x", expand=False)
        self.cancel_button = ttk.Button(self.button_frame2, text=localized["cancel"][self.root.language], command=self.cancel)
        self.cancel_button.pack(side="left", fill="x", expand=True)
        self.ok_button = ttk.Button(self.button_frame2, text=localized["ok"][self.root.language], command=self.ok)
        self.ok_button.pack(side="left", fill="x", expand=True)

    def add(self):
        nlist = (list(eval(self.values.get())) if len(self.values.get()) > 0 else [])
        add = [*qcount.parse_input(simpledialog.askstring(localized["add_question"][self.root.language], localized[f"add_{'completed' if self.completed else 'question'}_prompt"][self.root.language]))]
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

class AboutScreen(ttk.Frame):
    def __init__(self, master:Toplevel, root:Application):
        super().__init__(master)
        self.master = master
        self.root = root
        self.master.geometry("400x200")
        self.master.title(localized["about"][self.root.language])
        self.pack(fill="both", expand=True)
        self.create_widgets()
    def create_widgets(self):
        self.label = ttk.Label(self, text=localized["about"][self.root.language])
        self.label.pack(side="top", fill="both", expand=True)
        self.label2 = ttk.Label(
            self, 
            text="This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.", 
            wraplength=400)
        self.label2.pack(side="top", fill="both", expand=True)
        self.button = ttk.Button(self, text=localized["ok"][self.root.language], command=self.ok)
        self.button.pack(side="bottom", fill="x", expand=True)
    def ok(self):
        self.master.destroy()
        self.root.master.focus_force()

class Preferences(ttk.Frame):
    def __init__(self, master:Toplevel, root:Application):
        super().__init__(master)
        self.master = master
        self.root = root
        self.master.geometry("400x200")
        self.pack(fill="both", expand=True)
        self.create_widgets()
    languages = {
        "en": "English",
        "es": "Español",
        "ja": "日本語",
    }
    def create_widgets(self):
        self.language_frame = ttk.Frame(self)
        self.language_frame.pack(side="top", fill="both", expand=True)
        self.language_label = ttk.Label(self.language_frame, text=f"{localized['language'][self.root.language]}:")
        self.language_label.pack(side="left", fill="x", expand=True)
        self.language_value = StringVar()
        self.language_value.set(self.root.language)
        self.language_menu = ttk.OptionMenu(self.language_frame, self.language_value, self.languages[self.root.language], *self.languages.values())
        self.language_menu.pack(side="left", fill="x", expand=True)
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side="bottom", padx=5, pady=5, fill="x", expand=False)
        self.cancel_button = ttk.Button(self.button_frame, text=localized["cancel"][self.root.language], command=self.cancel)
        self.cancel_button.pack(side="left", fill="x", expand=True)
        self.button = ttk.Button(self.button_frame, text=localized["save"][self.root.language], command=self.save)
        self.button.pack(side="left", fill="x", expand=True)
    def save(self):
        # save to file
        self.root.update_language(list(self.languages.keys())[list(self.languages.values()).index(self.language_value.get())])
        self.master.destroy()
        self.root.master.focus_force()
    def cancel(self):
        self.master.destroy()
        self.root.master.focus_force()

app = Application(master=Tk())
app.mainloop()
