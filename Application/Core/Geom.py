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
from math import sqrt


def centerOfMass(coords):
    """ Adapted from : Andreas Henschel 2006
    assumes equal weights for atoms (usually protons)
    """
    x, y, z = 0, 0, 0
    if len(coords) > 0:
        if len(coords) > 1:
            for coord in coords:
                x += coord[0]
                y += coord[1]
                z += coord[2]
            return (x/len(coords), y/len(coords), z/len(coords))
        else:
            return coords[0]
    else:
        return 0, 0, 0

# Methods for distance constraints


def calcDistance(coord_init, coord_final, method):
    """    Calculate distance according to :
    ((sum of all distances^-6)/number of distances)^-1/6
    or (sum of all distances^-6)^-1/6
    """
    result = 0.0

    if len(coord_init) > 0 and len(coord_final) > 0:
        distance_list = []
        for AtomA in coord_init:
            for AtomB in coord_final:
                distance_list.append(sqrt(pow((AtomA[0] - AtomB[0]), 2) +
                                          pow((AtomA[1] - AtomB[1]), 2) +
                                          pow((AtomA[2] - AtomB[2]), 2))
                                     )
        if len(distance_list) > 1:
            try:
                sum6 = sum(pow(distance, -6) for distance in distance_list)
                if method == 'ave6':
                    result = pow(sum6/len(distance_list), -1./6)
                elif method == 'sum6':
                    result = pow(sum6, -1./6)
            except:
                stderr.write("Problem with coordinates : "+ str(coord_init) +
                             " " + str(coord_final) + "\n" +
                             " with distances list" + str(distance_list) + "\n")
        else:
            result = distance_list[0]
    return result
