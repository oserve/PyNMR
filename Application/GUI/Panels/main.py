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

import ttk
from ConstraintSelection import ConstraintSelectionPanel
from FileSelection import FileSelectionPanel
from NOEDrawing import NOEDrawingPanel


class mainPanel(ttk.Frame):
    """
    """
    def __init__(self, master):
        """
        """
        ttk.Frame.__init__(self, master)
        self.fileSelection = FileSelectionPanel(self)
        self.constraintPanel = ConstraintSelectionPanel(self)
        self.NOEDrawing = NOEDrawingPanel(self)
        self.panelsList = [self.fileSelection, self.constraintPanel,
                           self.NOEDrawing]
        self.widgetCreation()

    def widgetCreation(self):
        """
        """
        self.fileSelection.grid(row=0, column=0)
        self.constraintPanel.grid(row=1, column=0)
        self.NOEDrawing.grid(row=2, column=0)

    def getInfo(self):
        """
        """
        infos = {}
        for panel in self.panelsList:
            infos.update(panel.getInfo())
        return infos
