from Application.Core.ConstraintParsers.BaseConstraintParser import BaseConstraintParser, Atoms

def test_findConstraintType():
    assert BaseConstraintParser.findConstraintType("ASSI") == "CNS"

def test_parseAtoms():
    parsingResult = ({"name":"tata", "resid":"7"}, {"name":"toto", "resi":"5", "segid":"B"})
    residues = [item for item in BaseConstraintParser.parseAtoms(parsingResult)]
    assert residues == [Atoms(**{"resi_number":7, "atoms":"tata", "segid":"A"}), Atoms(**{"resi_number":5, "atoms":"toto", "segid":"B"})]

def parseConstraints():
    for constraint in [{"residues": [{"resid": "7", "name": "H"}, {"resid": "5", "name": "HA", "segid": "B"}], "values" : (1.1, 2.2, 3.3), "definition" : "constraint1"}, {"residues": [{"resid": "4", "name": "H", "segid": "A"}, {"resid": "8", "name": "HA", "segid": "B"}], "values" : (4.4, 5.5, 6.6), "definition" : "constraint2"}]:
        yield constraint

def test_iterConstraints():
    aParser = BaseConstraintParser("")
    aParser.prepareFile = lambda: None
    aParser.parseConstraints = parseConstraints
    constraints = [constraint for constraint in aParser]
    assert len(constraints) == 2
