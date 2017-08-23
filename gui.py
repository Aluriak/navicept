"""Gui built on top of the navigator, requesting user choice through
a tkinter gui.

"""

from functools import partial
import tkinter as tk
from tkinter import font

import navigation
from context import Context
from navigation import find_concepts_interactively


DEFAULT_WM_TITLE = 'floating_navicept'
NO_COLOR = 'white'
COLOR_BG_TEXT = 'light grey'
COLOR_UNSET = 'pink'
COLOR_ERR = 'red'
COLOR_LOG = 'dark green'
COLOR_OK = 'light green'
COLOR_WAITING = '#fd6b14'


class Application(tk.Frame):
    """Allow user to explore the lattice of an input context.

    Use navigation.py to implement the solver under the hood.

    """

    def __init__(self, context:Context, master=None):
        master = master or tk.Tk()
        super().__init__(master)
        self.master.wm_title(DEFAULT_WM_TITLE)
        self.context = context
        self.reset_constraints()

    def create_widgets(self):
        # delete existing ones
        for child in self.winfo_children():
            child.destroy()
        buttons = {}
        for idx, dim in enumerate(self.context.sets):
            requireds, forbiddens = self.constraints[idx]
            user_requireds, user_forbiddens = self.user_constraints[idx]
            dim_buttons = tk.Frame(master=self)
            for elem in sorted(dim, reverse=True):
                button = tk.Button(dim_buttons, text=str(elem))
                # actions
                button.bind('<Button-1>', partial(self.choose_elem, dim_idx=idx, elem=elem, decision='in'))
                button.bind('<Button-2>', partial(self.choose_elem, dim_idx=idx, elem=elem, decision=''))
                button.bind('<Button-3>', partial(self.choose_elem, dim_idx=idx, elem=elem, decision='out'))
                # color
                required = elem in requireds
                forbidden = elem in forbiddens
                user_required = elem in user_requireds
                user_forbidden = elem in user_forbiddens
                if forbidden and required:
                    raise ValueError("Element {} is both required and forbidden. That's unexpected.".format(elem))
                if user_required:
                    button['background'] = 'green'
                elif required:
                    button['background'] = 'light green'
                elif user_forbidden:
                    button['background'] = 'red'
                elif forbidden:
                    button['background'] = 'pink'
                buttons[idx, elem] = button
                button.pack(side='right')
            dim_buttons.pack()
        self.buttons = buttons

        self.reset = tk.Button(self, text="", fg="blue",
                               command=self.reset_constraints)
        self.quit = tk.Button(self, text="", fg="red",
                              command=self.master.destroy)
        self.previous = tk.Button(self, text="", fg="green",
                                  command=self.restore_previous)
        self.current_error = tk.StringVar(self, value=' ' * 40)
        self.logline = tk.Label(self, textvariable=self.current_error)
        self.quit.pack(side="bottom")
        self.reset.pack(side="bottom")
        self.previous.pack(side="bottom")

        # logging for user
        error_font = font.Font(family='TkFixedFont', size=10, weight='bold')
        self.current_error = tk.StringVar(value=' ' * 40)
        self.lab_error = tk.Label(self, textvariable=self.current_error, fg=COLOR_ERR, font=error_font)
        self.lab_error.pack(side="bottom")

        self.pack()


    def err(self, msg:str):
        """Report given error message to user"""
        self.lab_error.configure(fg=COLOR_ERR)
        self.current_error.set(str(msg))
        self.update_idletasks()  # redraw (do not wait for the end of event handling)

    def log(self, msg:str):
        """Report given log message to user"""
        self.lab_error.configure(fg=COLOR_LOG)
        self.current_error.set(str(msg))
        self.update_idletasks()

    def info(self, msg:str):
        """Report given log message to user"""
        self.lab_error.configure(fg=COLOR_WAITING)
        self.current_error.set(str(msg))
        self.update_idletasks()


    def reset_constraints(self):
        """Forget all internal navigation. Called at the beginning to
        initialize a search, and each time user ask to reset.

        """
        self.coroutine = find_concepts_interactively(self.context)
        try:
            self.user_constraints, self.constraints = next(self.coroutine)
        except StopIteration as last:
            self.show_found_concept(last.value)
        else:
            self.create_widgets()


    def restore_previous(self):
        """Restore the previous state"""
        idx, elem, decision = self._last_user_input
        self.choose_elem(None, idx, elem, '')


    def choose_elem(self, event, dim_idx:set, elem:str, decision:str):
        """Callback when user have choosen an object to put in, out or unknow
        of the searched concept.

        """
        self._last_user_input = dim_idx, elem, decision
        # self.info('STARTING CONCEPT SEARCH…')
        assert decision in {'in', 'out', ''}
        try:
            self.user_constraints, self.constraints = self.coroutine.send(self._last_user_input)
            message = ''
        except StopIteration as last:
            self.user_constraints, self.constraints = last.value
            message = 'FOUND CONCEPT: ' + navigation.pretty_nconcept(self.constraints)
        self.create_widgets()
        self.info(message)


if __name__ == '__main__':
    context = Context(({'1', '2', '3'}, {'a', 'b', 'c'}),
                      {('1', 'a'), ('1', 'b'), ('2', 'b'), ('2', 'c')})
    context = Context(({'1', '2'}, {'3', '4'}, {'5', '6'}),
                      {('1', '3', '5'), ('2', '3', '5'), ('1', '3', '6'), ('1', '4', '6')})
    dimensions = ({'', '', ''}, {'', '', ''}, {'', '', ''})
    context = Context.with_random_relations(dimensions, density=0.6)

    win = Application(context)
    win.mainloop()
