import numpy as np
import scipy.spatial.transform as transform
import typing

class Component:

    componentNameMap = {}

    @staticmethod
    def createComponet(config: dict) -> 'KSRCore.control.Component':
        return Component.componentNameMap[config['type']](config)

    def __init__(self, config: dict, parent: 'KSRCore.control.model.Component' = None):
        self._config = config
        self.parent = parent
        self.defaultRot = transform.Rotation.from_euler('xyz', self._config['rot'], degrees=True)
        self.defaultPos = np.array(self._config['pos'])
        self.rot = self.defaultRot
        self.pos = self.defaultPos
        self.colisionModels = []
        self.limits = None
        if 'limits' in self._config:
            self.limits = (transform.Rotation.from_euler('xyz', self._config['limits'][0], degrees=True), transform.Rotation.from_euler('xyz', self._config['limits'][1], degrees=True))
        self.children = []
        if 'children' in self._config:
            for child in self._config['children']:
                self.children.append(Component.createComponet(child))

    @property
    def isRoot(self) -> bool:
        return self.parent is None

    @property
    def absRotation(self) -> 'scipy.spatial.transform.Rotation':
        if self.parent is None:
            return self.rot
        else:
            return self.rot * self.parent.absRotation

    @property
    def absPosition(self) -> 'numpy.array':
        if self.parent is None:
            return self.pos
        else:
            return np.add(self.rot.apply(self.pos), self.parent.absPosition)

    def setRotation(self, rotation):
        self.rot = rotation

    def setPosition(self, position: 'numpy.array'):
        self.pos = position

    def execute(self):
        pass

class BoundLinearRotationJoint(Component):
    def __init__(self, config: dict, parent: 'KSRCore.control.model.Componet' = None):
        super().__init__(config)
        if self.limits:
            self.limits[0] = transform.Rotation.from_euler('xyz', self.limits[0], degrees=True)
            self.limits[1] = transform.Rotation.from_euler('xyz', self.limits[1], degrees=True)
            self.slerp = transform.Slerp([0, 1], self.limits)
        else:
            raise RuntimeError("LinearRotationJoint requires limits")
           
    def rotate(self, ratio: float):
        self.rot = self.slerp([ratio])[0]

    def goto(self, ratio: float):
        self.rot = self.limits[0]
        self.rotate(ratio)
        

class ContinuousLinearRotationJoint(Component):
    def rotate(self, rotations: float):
        pass

    def setSpeed(self, speed: float):
        pass
        
class LinearTransformJoint(Component):
    def __init__(self, config: dict, parent: 'KSRCore.control.model.Componet' = None):
        super().__init__(config)
        if self.limits:
            range = np.subtract(self.limits[1], self.limits[0])
            self.maxDisplacement = np.linalg.norm(range, 2)
            self.unitTransfrom = range / self.maxDisplacement
        else:
            raise RuntimeError("LinearTrnasformJoint requires limits")

    def transform(self, distance: float):
        self.pos = np.add(self.unitTransfrom * distance, self.pos))
        for i in range(3):
            self.pos[i] = min(max(self.pos[i], self.limits[0][i]), self.limits[1][i])

    def goto(self, distance: float):
        self.pos = self.limits[0]
        self.transform(distance)

class BoundMotor(BoundLinearRotationJoint):
    def __init__(self, config: dict, parent: 'KSRCore.control.model.Componet' = None):
        super().__init__(config)

    def execute(self):
        pass


Component.componentNameMap = {
    'Component': Component,
    'LinearRotationJoint': LinearRotationJoint
    'LinearTransformJoint': LinearTransformJoint,
    'BoundMotor': BoundMotor
    }