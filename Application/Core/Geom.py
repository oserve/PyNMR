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
from math import sqrt, pow
from MolecularViewerInterface import get_model

def centerOfMass(selection):
    ## Author: Andreas Henschel 2006
    ## assumes equal weights
    model = get_model(selection)
    if len(model.atom)>0:
        x,y,z=0,0,0
        for a in model.atom:
            x+= a.coord[0]
            y+= a.coord[1]
            z+= a.coord[2]
        return (x/len(model.atom), y/len(model.atom), z/len(model.atom))
    else:
        stderr.write("selection is empty :"+ str(selection)+"\n")
        return 0,0,0            

#Methods for distance constraints
def calcDistance(selection_init,selection_final,method):
    """
    Choose which method to calculate distances
    """
    if method=='ave6':
        return(averageDistance_6(selection_init,selection_final))
    elif method=='sum6':
        return(sumDistance_6(selection_init,selection_final))
    else:
        stderr.write("This method of calculation is not defined : "+str(method)+"\n")

def averageDistance_6(selection_init,selection_final):
    """
    Calculate distance according to : ((sum of all distances^6)/number of distances)^6
    """
    model_init = get_model(selection_init)
    model_final= get_model(selection_final)
    if len(model_init.atom)>0 and len(model_final.atom)>0:
            distance_list=[]
            for a in model_init.atom:
                for b in model_final.atom:
                    distance_list.append(sqrt(pow((a.coord[0]-b.coord[0]),2)+pow((a.coord[1]-b.coord[1]),2)+pow((a.coord[2]-b.coord[2]),2)))
            sum6=0
            for distance in distance_list:
                try:
                    sum6=sum6+pow(distance,-6)
                except:
                    stderr.write("Problem with selection : "+selection_init+" "+selection_final + "\n" + "distance is : "+str(distance)+" A")
            return pow(sum6/len(distance_list),-1./6)
    else:
        stderr.write("selection is empty : "+selection_init+" "+selection_final+"\n")
        return 0.0

def sumDistance_6(selection_init,selection_final):
    """
    Calculate distance according to : (sum of all distances^6)^-1/6
    """
    model_init = get_model(selection_init)
    model_final= get_model(selection_final)

    if len(model_init.atom)>0 and len(model_final.atom)>0:
            distance_list=[]
            for a in model_init.atom:
                for b in model_final.atom:
                    distance_list.append(sqrt(pow((a.coord[0]-b.coord[0]),2)+pow((a.coord[1]-b.coord[1]),2)+pow((a.coord[2]-b.coord[2]),2)))
            sum6=0
            for distance in distance_list:
                try:
                    sum6=sum6+pow(distance,-6)
                except:
                    stderr.write("Problem with selection : "+selection_init+" "+selection_final + "\n" + "distance is : "+str(distance)+" A")
            result=pow(sum6,-1./6)
            return result

    else:
        stderr.write("selection is empty : "+selection_init+" "+selection_final+"\n")
        return 0.0
