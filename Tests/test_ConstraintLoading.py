from Application.Core.ConstraintLoading import loadConstraintsFromFile
from Application.Core.ConstraintManager import imConstraintSetManager
import pytest

@pytest.fixture()
def testManager():
    return loadConstraintsFromFile("Tests/test_cns.mr", "test_cns")

def test_CMLoadConstraintsFromFile(testManager):
    assert type(testManager) == type(imConstraintSetManager(""))

def test_lenLoadConstraintsFromFile(testManager):
    assert len(testManager) == 4

def test_formatLoadConstraintsFromFile(testManager):
    assert testManager.format == "CNS"
