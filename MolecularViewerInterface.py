#MolecularViewerInterface.py
#
#
try:
    from pymol import cmd as PymolCmd
    from pymol.cgo import CYLINDER

    def select(selectionName, selection):
        if selectionName == "":
            return PymolCmd.select(selection)
        else:
            return PymolCmd.select(selectionName, selection)

    def get_model(model):
        return PymolCmd.get_model(model)

    def alterBFactors(pdb,bFactor):
        PymolCmd.alter(pdb,"b="+ str(bFactor))

    def spectrum(color_gradient,pdb):
        PymolCmd.spectrum("b",color_gradient,pdb)
    
    def zoom(selection):
        PymolCmd.zoom(selection)

    def drawConstraint(points, color, aRadius, ID):
            """used to draw a NOE constraint between two sets of atoms
                    using cgo from Pymol
            """
            cons =[CYLINDER]+list(points[0])+list(points[1])+[aRadius]+color
            PymolCmd.load_cgo(cons, ID)

    def delete(selectionName):
        PymolCmd.delete(selectionName)

except ImportError:
    def select(selectionName, selection):
        return []

    def get_model(model):
        return []

    def alterBFactors(pdb,bFactor):
        pass

    def spectrum(color_gradient,pdb):
        pass

    def drawConstraint(points, color, aRadius, ID):
        pass
    
    def zoom(selection):
        pass
    
    def delete(selectionName):
        pass

def zeroBFactors(pdb):
        alterBFactors(pdb, 0)

def setBfactor(selection, bFactor):
        alterBFactors(selection, bFactor)

def paintDensity(color_gradient, pdb):
        spectrum(color_gradient, pdb)