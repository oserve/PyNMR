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
from collections import OrderedDict, Mapping, defaultdict


class atomTypeListController(Mapping):
    """
    """

    def __init__(self):
        """
        """
        Mapping.__init__(self)
        self.atomTypes = defaultdict(list)

    def __getitem__(self, key):
        """
        """
        return self.atomTypes[key]

    def __iter__(self):
        """
        """
        return sorted(self.atomTypes.keys()).__iter__()

    def __len__(self):
        """
        """
        return len(self.atomTypes)

    def clear(self):
        """
        """
        self.atomTypes.clear()

    def addAtom(self, atom):
        """
        """
        self.atomTypes[atom.atoms].append(atom)


class resiNumberListController(Mapping):
    """
    """

    def __init__(self):
        """
        """
        Mapping.__init__(self)
        self.resiNumbers = defaultdict(list)

    def __getitem__(self, key):
        """
        """
        return self.resiNumbers[key]

    def __iter__(self):
        """
        """
        return sorted(self.resiNumbers.keys(), key=lambda x: int(x.split('\\')[0])).__iter__()

    def __len__(self):
        """
        """
        return len(self.resiNumbers)

    def clear(self):
        """
        """
        self.resiNumbers.clear()

    def addAtom(self, atom):
        """
        """
        self.resiNumbers["{}\ ({})".format(atom.resi_number, atom.segid)].append(atom)
