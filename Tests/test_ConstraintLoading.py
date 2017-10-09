from Application.Core.ConstraintLoading import loadConstraintsFromFile
from Application.Core.ConstraintManager import imConstraintSetManager

def test_loadConstraintsFromFile():
    testManager = loadConstraintsFromFile("Tests/test_cns.mr", "test_cns")
    expectedManager = imConstraintSetManager("test_cns")