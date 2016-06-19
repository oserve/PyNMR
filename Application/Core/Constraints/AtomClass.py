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

from .. import MolecularViewerInterface as MVI


class AtomSet(object):
    """Base Class contains residu number
        and the atom type of the atom
    """

    def __init__(self, structureName, resi_number, resi_type, segid):
        """Initialisation sets the residu number
            and the atom type
        """
        self.structure = structureName
        self.number = resi_number
        self.atType = resi_type
        self.segid = segid

    def __str__(self):
        return "Set of atoms " + self.atType + " on residue " + str(self.number) + " on segment / chain " + self.segid

    def __eq__(self, otherAtomSet):
        return isinstance(otherAtomSet, self.__class__) and (self.__dict__ == otherAtomSet.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def coord(self):
        return MVI.get_coordinates(self)