from Application.Core.Geom import centerOfMass, calcDistance

def test_centerOfMass():
    coordinates = [(1.2, 1.1, 1.43), (2.8, 2.32, 2.12)]
    center = centerOfMass(coordinates)
    assert center == (2.0, 1.71, 1.775)

def test_calcDistanceSum6():
    calcDistance.method = "sum6"
    coordinates = (((1.1, 2.2, 3.3), (4.4, 5.5, 6.6)), ((7.7, 8.8, 9.9), (10.1, 11.11, 12.12)))
    distance = calcDistance(*coordinates)
    assert distance == 5.660871785341385

def test_calcDistanceAve6():
    calcDistance.method = "ave6"
    coordinates = (((1.1, 2.2, 3.3), (4.4, 5.5, 6.6)), ((7.7, 8.8, 9.9), (10.1, 11.11, 12.12)))
    distance = calcDistance(*coordinates)
    assert distance == 7.132251523107583
