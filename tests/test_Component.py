import pytest
from unittest.mock import Mock
import numpy as np
import KSRCore.control.component as component
import tests
import json
import scipy.spatial.transform as transform

@pytest.fixture(scope='function')
def model():
    config = json.loads(open('./tests/testModel.json').read())
    return component.Component(config)

def test_component_root(model):
    assert model.name == 'modelRoot'
    assert model.absPosition.tolist() == [0, .2, 0]
    assert model.absRotation.as_euler('XYZ', True).tolist() == [0,0,0]

def test_component_find(model):
    assert model.find('modelRoot') == model
    assert model.find('hand').name == 'hand'
    assert model.find('wheel2').name == 'wheel2'
    assert model.find('notAPart') is None

def test_componet_abs_pos(model):
    pos = model.find('hand').absPosition.tolist()
    print(pos)
    assert pos[0] == 0
    assert pos[1] - (.2 + .4924) < .01
    assert pos[2] - .0868 + .1 < .01

def test_componet_abs_rot(model):
    print(model.find('hand').absRotation.as_euler('XYZ', True).tolist())
    assert model.find('hand').absRotation.as_euler('XYZ', True).tolist() == [80, 0, 0]