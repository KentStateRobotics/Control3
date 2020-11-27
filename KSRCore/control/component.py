'''
Module `componet` describes the structure and function of a robot model. Given a robot model as described below, 
keeps track of the state and facilitates control of drive devices.

.. include:: ./modelDoc.md
'''

import numpy as np
import scipy.spatial.transform as transform
import typing
import time

UPDATE_THREASHOLD_DURATION = 0.05

CommandRunners = []
ComponentNameMap = {}

class Setpoint:
    '''A struct containing 
    a target `setpoint`, 
    the last measured value `value`, 
    the relitive last time the current value was updated `updateTime`
    '''
    def __init__(self):
        self.updateTime = None
        self.value = None
        self.setpoint = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.updateTime = time.perf_counter()
        self.__value = value

class Component:
    '''Base class for all parts of a model
    '''

    def __init__(self, config: dict, parent: typing.Optional['KSRCore.control.model.Component'] = None):
        '''Pass the models entire config dictionary and will recursievely generate model
        '''
        self.config = config
        self.name = config['name']
        self.parent = parent
        self.defaultRotation = transform.Rotation.from_euler('XYZ', config['rotation'], degrees=True)
        self.defaultPosition = np.array(config['position'])
        self._rotation = self.defaultRotation
        self._position = self.defaultPosition
        self.visualModels = []
        self.colisionModels = []
        self.children = []
        if 'children' in self.config:
            for child in self.config['children']:
                self.children.append(ComponentNameMap[config['type']](child, self))

    @property
    def isRoot(self) -> bool:
        '''Is this the root object of the model
        '''
        return self.parent is None

    @property
    def absRotation(self) -> 'scipy.spatial.transform.Rotation':
        '''Gets rotation relitive to the root
        '''
        if self.parent is None:
            return self._rotation
        else:
            return self._rotation * self.parent.absRotation

    @property
    def absPosition(self) -> 'numpy.array':
        '''Gets position relitive to the root
        '''
        if self.parent is None:
            return self._position
        else:
            return np.add(self.parent._rotation.apply(self._position), self.parent.absPosition)

    @property
    def rotation(self):
        '''Gets rotation relitive to the root
        '''
        return self._rotation

    @property
    def position(self):
        '''Gets postion relitive to parent
        '''
        return self._position

    def find(self, name: str) -> typing.Union['KSRCore.control.model.Component', None]:
        '''Searches children and self for component with matching name, if it is not found, returns None
        '''
        if self.name == name:
            return self
        else:
            for child in self.children:
                com = child.find(name)
                if com:
                    return com
        return None


class Joint(Component):
    '''A component that can be driven, either rotationaly or positionaly.
        Children components will also be affected by this movement.
        `speed` is the speed of traversial or rotation, either in degrees per second or meters per second
        `distance` is the position of either traversial or rotation, either in degrees or meters 
    '''
    def __init__(self, config: dict, parent: typing.Optional['KSRCore.control.model.Component'] = None):
        super().__init__(config, parent)
        self.axis = transform.Rotation.from_euler('XYZ', config['axis'], degrees=True)
        self.limits = {}
        if 'limits' in config:
            self.limits['min'] = config['limits'].get('min', None)
            self.limits['max'] = config['limits'].get('max', None)
            self.limits['speed'] = config['limits'].get('speed', None)
        self._speed = Setpoint()
        self._distance = Setpoint()
        self._updateTime = time.perf_counter()

    @property
    def speedSetpoint(self) -> float:
        return self._speed.setpoint

    @speedSetpoint.setter
    def speedSetpoint(self, speedSetpoint: float):
        if 'speed' in self.limits:
            self._speed.setpoint = max(-1 * self.limits['speed'], min(self.limits['speed'], speedSetpoint))
        else:
            self._speed.setpoint = speedSetpoint

    @property
    def realSpeed(self) -> float:
        return self._speed.value

    def speedFeedback(self, speed: float):
        '''Hook called by feedback device to update how fast the joint is actually moving
        '''
        self._speed.value = speed

    @property
    def distanceSetpoint(self) -> float:
        return self._distance.setpoint

    @distanceSetpoint.setter
    def distanceSetpoint(self, distanceSetpoint: float):
        if 'min' in self.limits:
            self._distance.setpoint = max(self.limits['min'], min(self.limits['max'], distanceSetpoint))
        else:
            self._distance.setpoint = distanceSetpoint

    @property
    def realDistance(self) -> float:
        return self._distance.value

    def distanceFeedback(self, distance: float):
        '''Hook called by feedback device to update the joints actual position
        '''
        self._distance.value = distance
    
    @property
    def position(self):
        self.callUpdate()
        return self._position

    @property
    def rotation(self):
        self.callUpdate()
        return self._rotation

    def callUpdate(self):
        '''Calls the update function only at the the maximum rate specified in `UPDATE_THREASHOLD_DURATION` to minimize unless calls and reduce rounding errors
        '''
        curr = time.perf_counter()
        deltaTime = curr - self._updateTime
        if deltaTime > UPDATE_THREASHOLD_DURATION:
            self._updateTime = curr
            self.update(deltaTime)

    def update(self, deltaTime: float):
        '''Override in child class
            Calculate the new position and rotation based on the last measured values and setpoints
        '''
        pass
        
    def sendCommands(self):
        '''Override in child class
            Called on a regular interval to send commands to the devices
            Sends a command to every moving device this is controling because
            all downstream devices will try to stop movement if no commands are received after a timeout
        '''
        pass

ComponentNameMap = {
    'Component': Component,
    'Joint': Joint
    }