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
from sys import stderr
import re

from BaseConstraintParser import BaseConstraintParser

class CYANAParser(BaseConstraintParser):
    """
    """
    AtTypeReg = re.compile(r'[CHON][A-Z]*')

    def prepareFile(self):
        """
        """
        self.inFileTab = self.text

    def parseConstraints(self):
        """
        """
        for aConstraintLine in self.inFileTab:
            if len(aConstraintLine) > 1 and aConstraintLine.find('#') == 0:
                stderr.write(aConstraintLine + " skipped. Commented out.\n")
                parsed = None
            cons_tab = aConstraintLine.split()
            try:
                parsed = {"residues":
                    [{'resid': int(cons_tab[0]),
                     'name': CYANAParser.AtTypeReg.match(
                        self.convertTypeDyana(cons_tab[2])).group()},
                    {'resid': int(cons_tab[3]),
                     'name': CYANAParser.AtTypeReg.match(
                        self.convertTypeDyana(cons_tab[5])).group()}]}
                parsed["values"] = ([str(1.8 + (float(cons_tab[6]) - 1.8)/2), '1.8', cons_tab[6]])
                parsed["definition"] = aConstraintLine
            except:
                stderr.write("Unknown error while loading constraint " + ":\n" +
                             aConstraintLine + "\n")
                parsed = None
            yield parsed

    @staticmethod
    def convertTypeDyana(atType):
        """
        Adapt xeasy nomenclature Q to pymol *
        """
        if 'Q' in atType:
            newType = atType.replace('Q', 'H', 1) + ('*')
            # Q is replaced by H and a star at the end of the atom type
            # avoid QQ (QQD-> HD*)
            return newType.replace('Q', '')
        else:
            return atType