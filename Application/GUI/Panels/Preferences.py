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
import tkColorChooser

from Panel import Panel


class SticksPreferencesPanel(Panel):
    """
    """
    def __init__(self, master):
        """
        """
        Panel.__init__(self, master, frameText="NOE Sticks Preferences")
        self.radius = Tk.DoubleVar(self)
        self.spinBox_Radius = Tk.Spinbox(self, textvariable=self.radius,
                                         from_=0.00, to=0.5, increment=0.01)
        self.satisfiedColorButton = ttk.Button(self, text="Choose color",
                                               command=self.setSatisfiedColor)
        self.tooFarButton = ttk.Button(self, text="Choose color",
                                       command=self.setTooFarColor)
        self.tooCloseButton = ttk.Button(self, text="Choose color",
                                         command=self.setTooCloseColor)
        self.violationID = Tk.StringVar(self)
        self.notViolationID = Tk.StringVar(self)
        self.violationIDEntry = ttk.Entry(self, textvariable=self.violationID)
        self.notViolationIDEntry = ttk.Entry(self, textvariable=self.notViolationID)
        self.colors = {}
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text='Stick radius (A):').grid(row=0, column=0)
        self.spinBox_Radius.grid(row=0, column=1)
        ttk.Label(self, text='Satisfied constraint').grid(row=1, column=0)
        self.satisfiedColorButton.grid(row=1, column=1)
        ttk.Label(self, text="Atoms too far").grid(row=2, column=0)
        self.tooFarButton.grid(row=2, column=1)
        ttk.Label(self, text="Atoms too close").grid(row=3, column=0)
        self.tooCloseButton.grid(row=3, column=1)
        ttk.Label(self, text='Violation Identification :').grid(row=4, column=0)
        self.violationIDEntry.grid(row=4, column=1)
        ttk.Label(self, text='Not violation Identification :').grid(row=5, column=0)
        self.notViolationIDEntry.grid(row=5, column=1)

    def getInfo(self):
        """
        """
        return {"radius": self.radius.get(), "colors": self.colors, "violationID": self.violationID, "notViolationID": self.notViolationID}

    def setSatisfiedColor(self):
        """
        """
        currentColor = self.float2intColor(self.colors["notViolated"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["notViolated"] = self.int2floatColor(result[0])

    def setTooFarColor(self):
        """
        """
        currentColor = self.float2intColor(self.colors["tooFar"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooFar"] = self.int2floatColor(result[0])

    def setTooCloseColor(self):
        """
        """
        currentColor = self.float2intColor(self.colors["tooClose"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooClose"] = self.int2floatColor(result[0])

    # This should be in an different file probably
    def float2intColor(self, color):
        """
        """
        return (int(color[0]*255), int(color[1]*255), int(color[2]*255))

    def int2floatColor(self, color):
        """
        """
        return [color[0]/255.0, color[1]/255.0, color[2]/255.0,
                color[0]/255.0, color[1]/255.0, color[2]/255.0]


class DensityPreferencesPanel(Panel):
    """
    """
    def __init__(self, master):
        """
        """
        Panel.__init__(self, master, frameText="NOE density Preferences")
        self.gradient = Tk.StringVar()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text='Gradient :').grid(row=0, column=0)
        self.gradientSelection = ttk.Combobox(self, state="readonly",
                                              textvariable=self.gradient)
        self.gradientSelection.grid(row=0, column=1)

    def getInfo(self):
        """
        """
        return {"gradient": self.gradient.get()}


class PreferencesPanel(Panel):
    """
    """
    def __init__(self, master):
        """
        """
        Panel.__init__(self, master, frameText="NOE Preferences")
        self.panelsList = []
        self.methodsList = [("Sum of r^6", "sum6"), ("Average of r^6", "ave6")]
        self.selectedMethod = Tk.StringVar()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text='NOE Distance calculation :\n(> 2 atoms)').grid(
            row=0, column=0, rowspan=2)
        position = 0
        for methodName, method in self.methodsList:
            ttk.Radiobutton(self, text=methodName, variable=self.selectedMethod,
                           value=method).grid(row=position, column=1)
            position = position + 1

        self.sticksPanel = SticksPreferencesPanel(self)
        self.sticksPanel.grid(row=position, column=0, columnspan=2)
        self.panelsList.append(self.sticksPanel)
        position = position + 1
        self.densityPanel = DensityPreferencesPanel(self)
        self.densityPanel.grid(row=position, column=0, columnspan=2)
        self.panelsList.append(self.densityPanel)

    def getInfo(self):
        """
        """
        infos = {"method": self.selectedMethod.get()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos
