"""Gui built on top of the navigator, requesting user choice through
a tkinter gui.

"""

from functools import partial
import tkinter as tk

import navigation
from context import Context
from navigation import find_concepts_interactively


DEFAULT_WM_TITLE = 'floating_navicept'


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
            dim_buttons = tk.Frame(master=self)
            for elem in sorted(dim, reverse=True):
                button = tk.Button(dim_buttons, text=str(elem))
                # actions
                button.bind('<Button-1>', partial(self.choose_elem, dim_idx=idx, elem=elem, decision='in'))
                button.bind('<Button-2>', partial(self.choose_elem, dim_idx=idx, elem=elem, decision=''))
                button.bind('<Button-3>', partial(self.choose_elem, dim_idx=idx, elem=elem, decision='out'))
                # color
                required = any(elem in cons.required for cons in self.constraints)
                forbidden = any(elem in cons.forbidden for cons in self.constraints)
                if forbidden and required:
                    raise ValueError("Element {} is both required and forbidden. That's unexpected.".format(elem))
                if required:
                    button['background'] = 'green'
                elif forbidden:
                    button['background'] = 'red'
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
        self.quit.pack(side="bottom")
        self.reset.pack(side="bottom")
        self.previous.pack(side="bottom")
        self.pack()


    def reset_constraints(self):
        """Forget all internal navigation. Called at the beginning to
        initialize a search, and each time user ask to reset.

        """
        print('STARTING CONCEPT SEARCH…')
        # self.coroutine = self.user_choice(find_concepts_interactively(self.context))
        self.coroutine = find_concepts_interactively(self.context)
        self.context, self.constraints = next(self.coroutine)
        self.create_widgets()


    def restore_previous(self):
        """Restore the previous state"""
        raise NotImplementedError


    def choose_elem(self, event, dim_idx:set, elem:str, decision:str):
        """Callback when user have choosen an object to put in, out or unknow
        of the searched concept.

        """
        assert decision in {'in', 'out', ''}
        constraint = self.constraints[dim_idx]
        try:
            self.context, self.constraints = self.coroutine.send((dim_idx, elem, decision))
        except StopIteration as last:
            self.show_found_concept(last.value)
        self.create_widgets()


    def show_found_concept(self, concept):
        """Callback when given concept have been selected by user"""
        print('FOUND CONCEPT:', navigation.pretty_nconcept(concept), end='\n\n')


if __name__ == '__main__':
    context = Context(({'1', '2', '3'}, {'a', 'b', 'c'}),
                      {('1', 'a'), ('1', 'b'), ('2', 'b'), ('2', 'c')})
    context = Context(({'1', '2'}, {'3', '4'}, {'5', '6'}),
                      {('1', '3', '5'), ('2', '3', '5'), ('1', '3', '6'), ('1', '4', '6')})
    dimensions = ({'', '', ''}, {'', '', ''}, {'', '', ''})
    context = Context.with_random_relations(dimensions, density=0.6)

    win = Application(context)
    win.mainloop()
