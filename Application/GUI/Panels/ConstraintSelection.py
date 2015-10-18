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
 


class ConstraintSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text=u"Constraints Selection")
        self.consRangeFrame = RangeSelectionPanel(self)
        self.violationsFrame = ViolationSelectionPanel(self)
        self.structureManagement = StructureSelectionPanel(self)
        self.panelsList = [self.consRangeFrame, self.violationsFrame, self.structureManagement]
        self.widgetCreation()

    def widgetCreation(self):
        # Creation of range input
        self.consRangeFrame.grid(row=0, column=0)

        # Creation of Violations inputs
        self.violationsFrame.grid(row=0, column=1)

        # Creation of structure inputs
        self.structureManagement.grid(row=1, column=0, columnspan=2)

    def getInfo(self):
        infos = {}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos


class RangeSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Range Selection")

        self.RangesVars = {}
        self.RangesCB = {}
        self.RangesFunctions = {}
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        rowPosition = 0
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            self.RangesVars[consRange] = Tk.IntVar(self)
            self.RangesCB[consRange] = ttk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
            self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
            rowPosition = rowPosition + 1
        self.RangesVars["all"] = Tk.IntVar(self)
        self.RangesCB["all"] = ttk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
        self.RangesCB["all"].grid(row=rowPosition, column=0, sticky=Tk.W)
        self.RangesCB["all"].invoke()

    def tickAll(self):
        """
        """
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            self.RangesVars[consRange].set(self.RangesVars["all"].get())

    def tick(self):
        """
        """
        self.RangesVars["all"].set(1)
        for aRange in ['intra', 'sequential', 'medium', 'long']:
            if self.RangesVars[aRange].get() == 0:
                self.RangesVars["all"].set(0)
                break

    def getInfo(self):
        """
        """
        ranges = []
        for consRange in ['intra', 'sequential', 'medium', 'long']:
            if self.RangesVars[consRange].get() == 1:
                ranges.append(consRange)
        return {"residuesRange": ranges}


class ViolationSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Constraint state :")

        self.ViolationsVars = {}
        self.UnSatisfiedCB = {}
        self.cutOff = Tk.DoubleVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        rowPosition = 0
        for violationType in ['unSatisfied', 'Satisfied']:
            self.ViolationsVars[violationType] = Tk.IntVar(self)
            self.UnSatisfiedCB[violationType] = ttk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
            self.UnSatisfiedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W, columnspan=2)
            self.ViolationsVars[violationType].set(1)
            rowPosition = rowPosition + 1

        ttk.Label(self, text=u'Distance CutOff :').grid(row=rowPosition + 1,
                                                        column=0, columnspan=2)

        self.spinBox_cutOff = Tk.Spinbox(self, textvariable=self.cutOff,
                                         from_=0.0, to=10.0, increment=0.1,
                                         format='%2.1f', width=6)
        self.spinBox_cutOff.grid(row=rowPosition + 2, column=0)
        ttk.Label(self, text=u'\u212b').grid(row=rowPosition + 2, column=1)

    def getInfo(self):
        """
        """
        violationState = []
        for violationType in ['unSatisfied', 'Satisfied']:
            if self.ViolationsVars[violationType].get() == 1:
                violationState.append(violationType)
        return {"cutOff": self.cutOff.get(), "violationState": violationState}


class StructureSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Structure")
        self.residueRanges = Tk.StringVar()
        self.structureList = Tk.StringVar()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u"Structure :").grid(row=0, column=0)
        self.comboPDB = ttk.Combobox(self, state='readonly',
                                     textvariable=self.structureList)
        self.comboPDB.grid(row=0, column=1)
        self.comboPDB.bind('<Enter>', self.updatePdbList)

        ttk.Label(self, text=u'Residues ranges :').grid(row=2, column=0, sticky=Tk.W)
        self.entry_res = ttk.Entry(self, textvariable=self.residueRanges)
        self.entry_res.grid(row=2, column=1)
        self.residueRanges.set('all')

    def getInfo(self):
        """
        """
        return {"structure": self.structureList.get(),
                "ranges": self.residueRanges.get()}

    def updatePdbList(self, event):
        """
        """
        self.comboPDB['values'] = self.mainApp.getModelsNames()
