"""scrolledlist.py: A Tkinter widget combining a Listbox with Scrollbar(s).

  For details, see:
    http://www.nmt.edu/tcc/help/lang/python/examples/scrolledlist/
"""

# ================================================================
# Imports
# ----------------------------------------------------------------

import Tkinter as Tk
import ttk

# ================================================================
# Manifest constants
# ----------------------------------------------------------------

DEFAULT_WIDTH = "20"
DEFAULT_HEIGHT = "10"


class ScrolledList(ttk.Frame):
    """A compound widget containing a listbox and up to two scrollbars.

      State/invariants:
        .listbox:      [ The Listbox widget ]
        .vScrollbar:
           [ if self has a vertical scrollbar ->
               that scrollbar
             else -> None ]
        .hScrollbar:
           [ if self has a vertical scrollbar ->
               that scrollbar
             else -> None ]
        .callback:     [ as passed to constructor ]
        .vscroll:      [ as passed to constructor ]
        .hscroll:      [ as passed to constructor ]
    """

    def __init__(self, master=None, width=DEFAULT_WIDTH,
                 height=DEFAULT_HEIGHT, vscroll=1, hscroll=0, callback=None,
                 listvariable=None, selectmode=Tk.BROWSE):
        """Constructor for ScrolledList.
        """
        # -- 1 --
        # [ self  :=  a new Frame widget child of master ]
        ttk.Frame.__init__(self, master)
        # -- 2 --
        self.width = width
        self.height = height
        self.vscroll = vscroll
        self.hscroll = hscroll
        self.callback = callback
        # -- 3 --
        # [ self  :=  self with all widgets created and registered ]
        self.__createWidgets(listvariable, selectmode)

    def __createWidgets(self, alistvariable, aselectmode):
        """Lay out internal widgets.
        """
        # -- 1 --
        # [ if self.vscroll ->
        #     self  :=  self with a vertical Scrollbar widget added
        #     self.vScrollbar  :=  that widget ]
        #   else -> I ]
        if self.vscroll:
            self.vScrollbar = ttk.Scrollbar(self, orient=Tk.VERTICAL)
            self.vScrollbar.grid(row=0, column=1, sticky=Tk.N+Tk.S)
        # -- 2 --
        # [ if self.hscroll ->
        #     self  :=  self with a horizontal Scrollbar widget added
        #     self.hScrollbar  :=  that widget
        #   else -> I ]
        if self.hscroll:
            self.hScrollbar = ttk.Scrollbar(self, orient=Tk.HORIZONTAL)
            self.hScrollbar.grid(row=1, column=0, sticky=Tk.E+Tk.W)
        # -- 3 --
        # [ self  :=  self with a Listbox widget added
        #   self.listbox  :=  that widget ]
        self.listbox = Tk.Listbox(self, relief=Tk.SUNKEN,
                                  width=self.width, height=self.height,
                                  borderwidth=2, listvariable=alistvariable,
                                  selectmode=aselectmode)
        self.listbox.grid(row=0, column=0)
        self.listbox.configure(exportselection=False)
        # -- 4 --
        # [ if self.vscroll ->
        #     self.listbox  :=  self.listbox linked so that
        #         self.vScrollbar can reposition it ]
        #     self.vScrollbar  :=  self.vScrollbar linked so that
        #         self.listbox can reposition it
        #   else -> I ]
        if self.vscroll:
            self.listbox["yscrollcommand"] = self.vScrollbar.set
            self.vScrollbar["command"] = self.listbox.yview

        # -- 5 --
        # [ if self.hscroll ->
        #     self.listbox  :=  self.listbox linked so that
        #         self.hScrollbar can reposition it ]
        #     self.hScrollbar  :=  self.hScrollbar linked so that
        #         self.listbox can reposition it
        #   else -> I ]
        if self.hscroll:
            self.listbox["xscrollcommand"] = self.hScrollbar.set
            self.hScrollbar["command"] = self.listbox.xview
        # -- 6 --
        # [ self.listbox  :=  self.listbox with an event handler
        #       for button-1 clicks that causes self.callback
        #       to be called if there is one ]
        self.listbox.bind("<Button-1>", self.__clickHandler)

    def __clickHandler(self, event):
        """Called when the user clicks on a line in the listbox.
        """
        # -- 1 --
        if not self.callback:
            return
        # -- 2 --
        # [ call self.callback(c) where c is the line index
        #   corresponding to event.y ]
        lineNo = self.listbox.nearest(event.y)
        self.callback(lineNo)
        # -- 3 --
        self.listbox.focus_set()

    def count(self):
        """Return the number of lines in use in the listbox.
        """
        return self.listbox.size()

    def __getitem__(self, k):
        """Get the (k)th line from the listbox.
        """

        # -- 1 --
        if 0 <= k < self.count():
            return self.listbox.get(k)
        else:
            raise IndexError("ScrolledList[%d] out of range." % k)

    def get(self, index):
        """
        """
        return self.listbox.get(index)

    def append(self, text):
        """Append a line to the listbox.
        """
        self.listbox.insert(Tk.END, text)

    def insert(self, linex, text):
        """Insert a line between two existing lines.
        """

        # -- 1 --
        if 0 <= linex < self.count():
            where = linex
        else:
            where = Tk.END

        # -- 2 --
        self.listbox.insert(where, text)

    def delete(self, linex):
        """Delete a line from the listbox.
        """
        if 0 <= linex < self.count():
            self.listbox.delete(linex)

    def clear(self):
        """Remove all lines.
        """
        self.listbox.delete(0, Tk.END)

    def curselection(self):
        """
        """
        return self.listbox.curselection()

    def bind(self, sequence=None, func=None, add=None):
        """
        """
        self.listbox.bind(sequence, func, add)

    def selection_set(self, first, last=None):
        """
        """
        return self.listbox.selection_set(first, last)

    def selection_clear(self, first, last=None):
        """
        """
        self.listbox.selection_clear(first, last)

    def size(self):
        """
        """
        return self.listbox.size()

    def event_generate(self, event):
        """
        """
        self.listbox.event_generate(event)

    def selectmode(self, newMode):
        """
        """
        self.listbox.configure(selectmode=newMode)

    @property
    def exportselection(self):
        """Utility method to set constraint name
        """
        return self.listbox.exportselection

    @exportselection.setter
    def exportselection(self, exportSetting):
        """Utility method to set constraint name
        """
        self.listbox.exportselection = exportSetting
