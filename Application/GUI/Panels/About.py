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
import Tkinter as Tk


class About(ttk.Frame):
    """
    """
    def __init__(self, master=None):
        """
        """
        ttk.Frame.__init__(self, master)
        self.aboutFrame = ttk.LabelFrame(self, text=u'About')
        self.aboutFrame.grid(row=1, column=0)
        ttk.Label(self.aboutFrame, justify=Tk.CENTER, text=u"This Pymol plugin" +
                  " has been written \nbecause I thought it would be useful to" +
                  "check \nmy NOEs during my postdocship. I hope it'll" +
                  " \nhelp you as well. Feel free to send \nany comments to " +
                  ": github.com/oserve/PyNMR\nThis plugin is free and may be " +
                  "copied as \nlong as you respect the copyright."
                  ).grid(row=0, column=0)
        self.helpFrame = ttk.LabelFrame(self, text=u'Quick Help')
        self.helpFrame.grid(row=0, column=0)
        ttk.Label(self.helpFrame, text=u'- First open a file or' +
                  'download one frome the PDB\n  using a structure PDB code\n' +
                  '- Then select which type of constraint you want\n' +
                  '- You can select residue numbers (X, Y, Z)\n  or a range ' +
                  '(X-Z) or both (default is all)\n - After that, select the' +
                  'structure you want\n to' +
                  ' display the constraints on.\n - Finally, click on the' +
                  ' display you want\n (sticks or colormap)'
                  ).grid(row=0, column=0)
