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

from Application.GUI.DataViewer.DependantColumnsTableView import DependantColumnsTableView as DCTView
from Application.GUI.DataViewer.NOEViewController import NOEViewController as NVController
from Application.GUI.delegates import DelegateProviderMixin, notify_delegates


class NOEDataViewer(Tk.Toplevel, DelegateProviderMixin):
    """
    """
    def __init__(self, dataController):
        Tk.Toplevel.__init__(self, class_='NOEDataViewer')
        self.title(dataController.name + " on " + dataController.structure)
        self.resizable(width=False, height=False)
        self.NOETableView = DCTView(masterView=self, NumberOfResiLists=2)
        self.NOEVController = NVController(dataController, self, self.NOETableView)
        self.NOETableView.dataSource = self.NOEVController
        self.constraintSelectionText = Tk.StringVar()
        self.labelConstraints = ttk.Label(self, textvariable=self.constraintSelectionText,
                                          justify=Tk.CENTER)
        self.NOEValues = dict()
        self.NOEValueLabels = dict()
        for valueType in ('constraint', 'min', 'plus', 'actual'):
            self.NOEValues[valueType] = Tk.DoubleVar()
            self.NOEValueLabels[valueType] = ttk.Label(self, textvariable=self.NOEValues[valueType], width=3)

        self.add_delegate(self.NOEVController)
        self.NOETableView.add_delegate(self.NOEVController)

        self.widgetCreation()
    
    @notify_delegates
    def widgetCreation(self):
        ttk.Label(self, text='Select NOE residue and / or atom to see their counterparts :').grid(row=1, column=0, columnspan=8)
        self.labelConstraints.grid(row=0, column=0, columnspan=8)
        ttk.Label(self, text='1st residue').grid(row=2, column=0, columnspan=4)
        ttk.Label(self, text='2nd residue').grid(row=2, column=4, columnspan=4)
        self.NOETableView.grid(row=3, column=0, columnspan=8)
        self.NOETableView.setColumnTitles(('Name', 'Atom', 'Name', 'Atom'))

        columnPosition = 0
        for key, aLabel in self.NOEValueLabels.iteritems():
            ttk.Label(self, text=key).grid(row=4, column=columnPosition, sticky=Tk.W)
            aLabel.grid(row=4, column=columnPosition + 1)
            aLabel.state(['disabled'])
            columnPosition += 2

    def setTitle(self, NumberOfConstraints, numberOfResiduesInvolved):
        """
        """
        self.constraintSelectionText.set(str(NumberOfConstraints) + " constraints used, involving " +
                                    str(numberOfResiduesInvolved) + " residues")

    def setLabelsState(self, state):
        """
        """
        if 'disabled' in state:
            for value in self.NOEValues.itervalues():
                value.set(0)
        for aLabel in self.NOEValueLabels.itervalues():
            aLabel.state(state)

    def setLabelValues(self, values, state):
        """
        """
        style = ttk.Style()
        style.configure("Red.TLabel", foreground="red")
        style.configure("Green.TLabel", foreground="green")

        for key, value in self.NOEValues.iteritems():
            value.set(round(float(values[key]), 1))

        if state == 'Satisfied':
            self.NOEValueLabels['constraint'].configure(style="Green.TLabel")
        if state == 'unSatisfied':
            self.NOEValueLabels['constraint'].configure(style="Red.TLabel")
