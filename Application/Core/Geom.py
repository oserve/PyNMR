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
from math import sqrt, fsum
from itertools import product, izip
import errors

distance_method = None


def set_method(newMethod):
    """
    """
    global distance_method
    distance_method = newMethod


def centerOfMass(coords):
    """ Adapted from : Andreas Henschel 2006
    assumes equal weights for atoms (usually protons)
    """

    try:
        sumCoords = (sum(coord) for coord in zip(*coords))
        numCoords = len(coords)
        return tuple(coord/numCoords for coord in sumCoords)
    except ValueError:
        return (0, 0, 0)

# Methods for distance constraints


def calcDistance(coord_init, coord_final):
    """    Calculate distance according to :
    ((sum of all distances^-6)/number of distances)^-1/6
    or (sum of all distances^-6)^-1/6
    """
    result = None

    try:
        distance_list = (sqrt(fsum((coord[0] - coord[1]) ** 2 for coord in izip(AtomA, AtomB))) for (AtomA, AtomB) in product(coord_init, coord_final))
        number_of_distances = len(coord_init) * len(coord_final)
        sum6 = fsum(pow(distance, -6) for distance in distance_list)
        if distance_method == 'ave6':
            result = pow(sum6/number_of_distances, -1./6)
        elif distance_method == 'sum6':
            result = pow(sum6, -1./6)
    except (ValueError, TypeError):
        errors.add_error_message("Problem using coordinates : " +
                                 str(coord_init) + " " +
                                 str(coord_final) + "\n" +
                                 " and distances list : " +
                                 str(distance_list) + "\n")

    return result
