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
import Pmw
import tkColorChooser

from Panel import Panel


class SticksPreferencesPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE Sticks Preferences")
        self.radius = Tk.DoubleVar(self)
        self.colors = {}
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text='Stick radius (A):').grid(row=0, column=0)
        self.spinBox_Radius = Tk.Spinbox(self, textvariable=self.radius, from_=0.00, to=0.5, increment=0.01)
        self.spinBox_Radius.grid(row=0, column=1)
        Tk.Label(self, text='Satisfied constraint').grid(row=1, column=0)
        self.satisfiedColorButton = Tk.Button(self, text="Choose color", command=self.setSatisfiedColor)
        self.satisfiedColorButton.grid(row=1, column=1)
        Tk.Label(self, text="Atoms too far").grid(row=2, column=0)
        self.tooFarButton = Tk.Button(self, text="Choose color", command=self.setTooFarColor)
        self.tooFarButton.grid(row=2, column=1)
        Tk.Label(self, text="Atoms too close").grid(row=3, column=0)
        self.tooCloseButton = Tk.Button(self, text="Choose color", command=self.setTooCloseColor)
        self.tooCloseButton.grid(row=3, column=1)

    def getInfo(self):
        return {"radius": self.radius.get(), "colors": self.colors}

    def setSatisfiedColor(self):
        currentColor = self.float2intColor(self.colors["notViolated"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["notViolated"] = self.int2floatColor(result[0])

    def setTooFarColor(self):
        currentColor = self.float2intColor(self.colors["tooFar"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooFar"]=self.int2floatColor(result[0])

    def setTooCloseColor(self):
        currentColor = self.float2intColor(self.colors["tooClose"])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors["tooClose"]=self.int2floatColor(result[0])

    #This should be in an different file probably
    def float2intColor(self, color):
        return (int(color[0]*255), int(color[1]*255), int(color[2]*255))

    def int2floatColor(self, color):
        return [color[0]/255.0, color[1]/255.0, color[2]/255.0, color[0]/255.0, color[1]/255.0, color[2]/255.0]


class DensityPreferencesPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE density Preferences")
        self.gradient = Tk.StringVar(self)
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text='Gradient :').grid(row=0, column=0)
        #x = Pmw.EntryField()  #Do not remove this line if combobox is the first Pmw combobox, Pmw bug
        self.gradientSelection = ttk.Combobox(self)
        self.gradientSelection.grid(row=0, column=1)

    def getInfo(self):
        return {"gradient": self.gradientSelection.component("entryfield").getvalue()}

class PreferencesPanel(Panel):
    def __init__(self, master):
        Panel.__init__(self, master, frameText="NOE Preferences")
        self.panelsList=[]
        self.widgetCreation()

    def widgetCreation(self):
        Tk.Label(self, text='NOE Distance calculation :\n(> 2 atoms)').grid(row=0, column=0)
        self.method = 0
        methodSelectionTypes = [("Sum of r^6", 1), ("Average of r^6",2)]
        position = 1
        for methodSelection, val in methodSelectionTypes:
            Tk.Radiobutton(self, text = methodSelection, variable = self.method, value = val).grid(row=position, column=1)
            position = position +1

        # self.methodSelection = Pmw.RadioSelect(self, buttontype='radiobutton', orient='vertical')
        # self.methodSelection.add("sum6", text="Sum of r^6")
        # self.methodSelection.add("average6", text="Average of r^6")
        # self.methodSelection.grid(row=0, column=1)

        self.sticksPanel = SticksPreferencesPanel(self)
        self.sticksPanel.grid(row=1, column=0, columnspan=2)
        self.panelsList.append(self.sticksPanel)

        self.densityPanel = DensityPreferencesPanel(self)
        self.densityPanel.grid(row=2, column=0, columnspan=2)
        self.panelsList.append(self.densityPanel)

    def getInfo(self):
        infos = {"method": self.methodSelection.getvalue()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos
