# Copyright Notice
# ================
#
# The PyMOL Plugin source code in this file is copyrighted, but you can
# freely use and copy it as long as you don't change or remove any of
# the copyright notices.
#
# ----------------------------------------------------------------------
#               This PyMOL Plugin is Copyright (C) 2013 by
#                 olivier serve <olivier dot serve at gmail dot com>
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name(s) of the author(s) not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# THE AUTHOR(S) DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN
# NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------
import Tkinter as Tk
import ttk
from sys import stderr

from Application.GUI.Panels.ttkScrolledList import ScrolledList
from Application.GUI.delegates import DelegateProviderMixin, notify_delegates

class DependantColumnsTableView(ttk.Frame, DelegateProviderMixin):
    """
    """
    def __init__(self, masterView=None, NumberOfResiLists=1, dataSource = None):
        """
        """
        ttk.Frame.__init__(self, class_='DCTView', master=masterView)
        self.dataSource = dataSource
        self.TkVars = tuple(Tk.StringVar() for number in xrange(NumberOfResiLists * 2))
        self.listTitleLabels = tuple(ttk.Label(self) for number in xrange(NumberOfResiLists * 2))

        self.scrolledLists = list()
        for index, aVar in enumerate(self.TkVars):
            aList = ScrolledList(self, listvariable=aVar, width=10)
            if index % 2 == 0:
                aList.selectmode(Tk.EXTENDED)
            aList.bind('<<ListboxSelect>>', self.updateDisplay)
            self.scrolledLists.append(aList)

        self.selectedList = None
        self.selectedRows = None

    def grid(self, *args, **kwargs):
        """
        """
        super(DependantColumnsTableView, self).grid(*args, **kwargs)
        for index, aList in enumerate(self.scrolledLists):
            self.listTitleLabels[index].grid(row=0, column=index*2, columnspan=2)
            aList.grid(row=1, column=index*2, columnspan=2)
        try:
            self.TkVars[0].set(" ".join(self.dataSource.valuesForColumn(0)))
        except AttributeError:
            stderr.write(str(self) + " has no dataSource.\n")

    def clear(self):
        """
        """
        for aList in self.scrolledLists:
            aList.clear()
    
    def setColumnTitles(self, titleList):
        """
        """
        try:
            for index, title in enumerate(titleList):
                self.listTitleLabels[index].configure(text = title)

        except KeyError:
            stderr.write('There are more titles than lists avalaible.\n')

    @notify_delegates
    def changeSelection(self, evt):
        """
        """
        w = evt.widget
        listBoxes = [listBox.listbox for listBox in self.scrolledLists]
        self.selectedList = listBoxes.index(w)
        self.selectedRows = tuple(w.curselection() for w in self.scrolledLists)

    def updateDisplay(self, evt):
        """
        """
        self.changeSelection(evt)
        for listIndex in xrange(self.selectedList + 1, len(self.TkVars)):
            self.TkVars[listIndex].set('')
        try:
            for index in xrange(1, len(self.TkVars)):
                self.TkVars[index].set(" ".join(self.dataSource.valuesForColumn(index)))
        except AttributeError:
            stderr.write(str(self) + " has no dataSource.\n")
