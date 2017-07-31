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
import appDefaults


class SticksPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        self.satisfactions = ("Satisfied", "tooFar", "tooClose")
        self.satisfactionColorButtons = dict()
        ttk.LabelFrame.__init__(self, master, text=u"NOE Sticks Preferences")
        self.radius = Tk.DoubleVar(self)
        self.spinBox_Radius = Tk.Spinbox(self, textvariable=self.radius,
                                         from_=0.00, to=0.5, increment=0.01,
                                         format='%1.2f', width=4)
        for satisfaction in self.satisfactions:
            self.satisfactionColorButtons[satisfaction] = ttk.Button(self,
                                                                     text=u"Choose color",
                                                                     command=lambda satisfaction=satisfaction: self.setColor(satisfaction))
        self.UnSatisfactionMarker = Tk.StringVar(self)
        self.SatisfactionMarker = Tk.StringVar(self)
        self.UnSatisfactionMarkerEntry = ttk.Entry(self, textvariable=self.UnSatisfactionMarker, width=6)
        self.SatisfactionMarkerEntry = ttk.Entry(self, textvariable=self.SatisfactionMarker, width=6)
        self.colors = dict()
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u'Stick radius (\u212b):').grid(row=0, column=0)
        self.spinBox_Radius.grid(row=0, column=1)
        ttk.Label(self, text=u'Satisfied constraint').grid(row=1, column=0)
        self.satisfactionColorButtons["Satisfied"].grid(row=1, column=1)
        ttk.Label(self, text=u"Atoms too far").grid(row=2, column=0)
        self.satisfactionColorButtons["tooFar"].grid(row=2, column=1)
        ttk.Label(self, text=u"Atoms too close").grid(row=3, column=0)
        self.satisfactionColorButtons["tooClose"].grid(row=3, column=1)
        ttk.Label(self, text=u'Unsatisfied Marker :').grid(row=4, column=0)
        self.UnSatisfactionMarkerEntry.grid(row=4, column=1)
        ttk.Label(self, text=u'Satisfied Marker :').grid(row=5, column=0)
        self.SatisfactionMarkerEntry.grid(row=5, column=1)

    def setDefaults(self):
        """
        """
        self.colors = appDefaults.defaultForParameter("colors")
        self.UnSatisfactionMarker.set(appDefaults.defaultForParameter("UnSatisfactionMarker"))
        self.SatisfactionMarker.set(appDefaults.defaultForParameter("SatisfactionMarker"))
        self.radius.set(appDefaults.defaultForParameter("radius"))

    def getInfo(self):
        """
        """
        return {"radius": self.radius.get(),
                "colors": self.colors,
                "UnSatisfactionMarker": self.UnSatisfactionMarker.get(),
                "SatisfactionMarker": self.SatisfactionMarker.get()}

    def setColor(self, satisfaction):
        """
        """
        currentColor = self.float2hex(self.colors[satisfaction])
        result = tkColorChooser.askcolor(currentColor)
        if result[0]:
            self.colors[satisfaction] = self.int2floatColor(result[0])

    @staticmethod
    def int2floatColor(color):
        """
        """
        return [color[0]/255.0, color[1]/255.0, color[2]/255.0,
                color[0]/255.0, color[1]/255.0, color[2]/255.0]

    @staticmethod
    def float2hex(color):
        """From stackoverflow
        """
        return '#%02x%02x%02x' % (int(color[0]*255), int(color[1]*255), int(color[2]*255))

class DensityPreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE density Preferences")
        self.gradient = Tk.StringVar()
        self.gradientSelection = ttk.Combobox(self, state="readonly",
                                              textvariable=self.gradient)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, text=u'Gradient :').grid(row=0, column=0)
        self.gradientSelection.grid(row=0, column=1)

    def getInfo(self):
        """
        """
        return {"gradient": self.gradient.get()}


class PreferencesPanel(ttk.LabelFrame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.LabelFrame.__init__(self, master, text=u"NOE Preferences")
        self.panelsList = list()
        self.methodsList = ((u"\u03a3 r-6", "sum6"), (u"(\u03a3 r-6)/n", "ave6"))
        self.selectedMethod = Tk.StringVar()
        self.sticksPanel = SticksPreferencesPanel(self)
        self.panelsList.append(self.sticksPanel)
        self.densityPanel = DensityPreferencesPanel(self)
        self.panelsList.append(self.densityPanel)
        self.savePrefButton = ttk.Button(self, text=u"Save preferences",
                                         command=self.savePrefs)
        self.resetButton = ttk.Button(self, text=u"Defaults",
                                      command=self.resetPrefs)
        self.rangeCutOff = Tk.IntVar(self)
        self.rangeCutOffEntry = Tk.Spinbox(self, textvariable=self.rangeCutOff,
                                           from_=1, to=20, increment=1, width=2)
        self.url = Tk.StringVar(self)
        self.urlTextField = ttk.Entry(self, textvariable=self.url)
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        ttk.Label(self, justify=Tk.CENTER, text=u'NOE Distance calculation :\n(> 2 atoms)').grid(
            row=0, column=0, rowspan=2)

        for position, (methodName, method) in enumerate(self.methodsList):
            ttk.Radiobutton(self, text=methodName, variable=self.selectedMethod,
                            value=method).grid(row=position, column=1)
        position += 1
        ttk.Label(self, text=u'Residue range cut-off :').grid(row=position, column=0)

        self.rangeCutOffEntry.grid(row=position, column=1)
        position += 1
        self.sticksPanel.grid(row=position, column=0, columnspan=2)
        position += 1
        self.densityPanel.grid(row=position, column=0, columnspan=2)
        position += 1
        ttk.Label(self, text=u'PDB.org URL for download').grid(row=position, column=0, columnspan=2)
        position += 1
        self.urlTextField.grid(row=position, column=0, columnspan=2)
        position += 1
        self.savePrefButton.grid(row=position, column=0)
        self.resetButton.grid(row=position, column=1)

    def savePrefs(self):
        """
        """
        appDefaults.registerDefaults(self.mainGUI.getInfo())
        appDefaults.saveDefaults()

    def resetPrefs(self):
        """
        """
        appDefaults.setToStandardDefaults()
        self.setDefaults()

    def setDefaults(self):
        """
        """
        self.densityPanel.gradient.set(appDefaults.defaultForParameter("gradient"))
        self.selectedMethod.set(appDefaults.defaultForParameter("method"))
        self.url.set(appDefaults.defaultForParameter("urlPDB"))
        self.rangeCutOff.set(appDefaults.defaultForParameter("rangeCutOff"))
        self.densityPanel.gradientSelection['values'] = appDefaults.defaultForParameter('gradientColorList')
        self.sticksPanel.setDefaults()

    def getInfo(self):
        """
        """
        infos = {"method": self.selectedMethod.get(),
                 "rangeCutOff": self.rangeCutOff.get(),
                 "urlPDB": self.url.get()}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos
