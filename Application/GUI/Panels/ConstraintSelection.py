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
import re
from sys import stderr
from ...Core.MolecularViewerInterfaces import MolecularViewerInterface as MVI
from appDefaults import defaultForParameter

regInput = re.compile(r'[^0-9+\-\,\s]')


class ConstraintSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        ttk.LabelFrame.__init__(self, master, text=u"Constraints Selection")
        self.consRangeFrame = RangeSelectionPanel(self)
        self.violationsFrame = ViolationSelectionPanel(self)
        self.structureManagement = StructureSelectionPanel(self)
        self.panelsList = (self.consRangeFrame, self.violationsFrame, self.structureManagement)
        self.widgetCreation()

    def widgetCreation(self):
        # Creation of range input
        self.consRangeFrame.grid(row=0, column=0)

        # Creation of Violations inputs
        self.violationsFrame.grid(row=0, column=1)

        # Creation of structure inputs
        self.structureManagement.grid(row=1, column=0, columnspan=2)

    def getInfo(self):
        infos = dict()
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos

    def setDefaults(self):
        self.violationsFrame.cutOff.set(defaultForParameter("cutOff"))
        self.structureManagement.comboPDB.values = MVI.getModelsNames(defaultForParameter('SatisfactionMarker'), defaultForParameter('UnSatisfactionMarker'))


class RangeSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Range Selection")

        self.RangesVars = dict()
        self.RangesCB = dict()
        self.RangesFunctions = dict()
        self.ranges = ('intra', 'sequential', 'medium', 'long')
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        for rowPosition, consRange in enumerate(self.ranges):
            self.RangesVars[consRange] = Tk.IntVar(self)
            self.RangesCB[consRange] = ttk.Checkbutton(self, text=': ' + consRange, command=self.tick, variable=self.RangesVars[consRange])
            self.RangesCB[consRange].grid(row=rowPosition, column=0, sticky=Tk.W)
        self.RangesVars["all"] = Tk.IntVar(self)
        self.RangesCB["all"] = ttk.Checkbutton(self, text=': all', command=self.tickAll, variable=self.RangesVars["all"])
        self.RangesCB["all"].grid(row=rowPosition + 1, column=0, sticky=Tk.W)
        self.RangesCB["all"].invoke()

    def tickAll(self):
        """
        """
        state_all = self.RangesVars["all"].get()
        for consRange in self.ranges:
            self.RangesVars[consRange].set(state_all)

    def tick(self):
        """
        """
        self.RangesVars["all"].set(1)
        if any(self.RangesVars[aRange].get() == 0 for aRange in self.ranges):
            self.RangesVars["all"].set(0)

    def getInfo(self):
        """
        """
        ranges = tuple(aRange for aRange in self.ranges if self.RangesVars[aRange].get() == 1)
        return {"residuesRange": ranges}


class ViolationSelectionPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"Constraint state :")

        self.ViolationsVars = dict()
        self.UnSatisfiedCB = dict()
        self.cutOff = Tk.DoubleVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        for rowPosition, violationType in enumerate(('unSatisfied', 'Satisfied')):
            self.ViolationsVars[violationType] = Tk.IntVar(self)
            self.UnSatisfiedCB[violationType] = ttk.Checkbutton(self, text=': ' + violationType, variable=self.ViolationsVars[violationType])
            self.UnSatisfiedCB[violationType].grid(row=rowPosition, column=0, sticky=Tk.W, columnspan=2)
            self.ViolationsVars[violationType].set(1)

        rowPosition += 1
        ttk.Label(self, text=u'Distance CutOff :').grid(row=rowPosition,
                                                        column=0, columnspan=2)

        rowPosition += 1
        self.spinBox_cutOff = Tk.Spinbox(self, textvariable=self.cutOff,
                                         from_=0.0, to=10.0, increment=0.1,
                                         format='%2.1f', width=6)
        self.spinBox_cutOff.grid(row=rowPosition, column=0)
        ttk.Label(self, text=u'\u212b').grid(row=rowPosition, column=1)

    def getInfo(self):
        """
        """
        violationStates = tuple(violationType for violationType in ('unSatisfied', 'Satisfied') if self.ViolationsVars[violationType].get() == 1)
        return {"cutOff": self.cutOff.get(), "violationState": violationStates}


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
                "ranges": interpret(self.residueRanges.get())}

    def updatePdbList(self, event):
        """
        """
        infos = self.mainApp.NMRInterface.getInfo()
        self.comboPDB['values'] = MVI.getModelsNames(infos['SatisfactionMarker'], infos['UnSatisfactionMarker'])

def interpret(residuesList):
    """
    """
    resList = set()
    if len(regInput.findall(residuesList)) == 0:
        for resi_range in residuesList.split("+"):
            aRange = resi_range.split("-")
            if 1 <= len(aRange) <= 2:
                resList.update(str(residueNumber) for residueNumber in xrange(int(aRange[0]), int(aRange[-1]) + 1))
            else:
                stderr.write("Residues set definition error : " + residuesList + "\n")

    return resList