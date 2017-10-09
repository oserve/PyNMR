from Application.Core.ConstraintParsers.CNSParser import CNSParser, constraintAmbiguity, constraintValues, residuesLooksLike
import pytest

@pytest.fixture()
def loadConstraintFile():
    with open("Tests/test_cns.mr", 'r') as file_in:
        fileText = file_in.read().upper()
    return fileText    

def test_prepareFile(loadConstraintFile):
    aParser = CNSParser(loadConstraintFile)
    aParser.prepareFile()
    parsedConstraints = [constraint for constraint in aParser.validConstraints]
    assert len(parsedConstraints) == 4

def test_parseConstraints(loadConstraintFile):
    aParser = CNSParser(loadConstraintFile)
    parsedConstraints = [constraint for constraint in aParser]
    assert len(parsedConstraints) == 4

def test_residuesLooksLike():
    residues = [{'name': 'HD12', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HD11', 'resid': '8', 'segid': 'TFB1'},]
    assert residuesLooksLike(*residues) == True

def test_notresiduesLooksLike():
    residues = [{'name': 'HD12', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HG11', 'resid': '8', 'segid': 'TFB1'}]
    assert residuesLooksLike(*residues) == False

def test_constraintAmbiguity():
    residues = [{'name': 'HD12', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HG11', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HD11', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HG11', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HD13', 'resid': '8', 'segid': 'TFB1'}, {'name': 'HG11', 'resid': '8', 'segid': 'TFB1'}]
    expectedResult = [{'name': "HD1*", 'resid':'8', 'segid':'TFB1'}, {'name': "HG11", 'resid':'8', 'segid':'TFB1'}]
    results = constraintAmbiguity(residues)
    assert expectedResult == results

def test_constraintValues(loadConstraintFile):
    aParser = CNSParser(loadConstraintFile)
    aParser.prepareFile()
    parsedConstraints = [constraint for constraint in aParser.validConstraints]
    assert constraintValues(parsedConstraints[0]) == (6.00, 1.20, 0.50)