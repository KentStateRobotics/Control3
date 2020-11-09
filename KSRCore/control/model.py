import numpy as np

class Component:

    componentNameMap = {}

    @staticmethod
    def createComponet(config: dict):
        return Component.componentNameMap[config['type']](config)

    def __init__(self, config: dict, parent: 'KSRCore.control.model.Component' = None):
        self._config = config
        self.parent = parent
        self.defaultRot = np.array(self._config['rot'])
        self.defaultPos = np.array(self._config['pos'])
        self.rot = self.defaultRot
        self.pos = self.defaultPos
        self.children = []
        if 'children' in self._config:
            for child in self._config['children']:
                self.children.append(Component.createComponet(child))

    @property
    def isRoot(self):
        return self.parent is None

    @property
    def getAbsRotation(self):
        pass

    @property
    def getAbsPosition(self):
        pass


class Joint(Component):
    def __init__(self, config: dict, parent: 'KSRCore.control.model.Componet' = None):
        super().__init__(config, parent)
        self.minRot = None
        self.maxRot = None

    def rotate(self, rotation):
        pass

    def setRotation(self, rotation):
        pass
        
class Actuator(Component)
    def __init__(self, config: dict, parent: 'KSRCore.control.model.Componet' = None):
        super().__init__(config, parent)
        self.minPos = None
        self.maxPos = None

    def move(self, offset):
        pass

    def setPosition(self, position):
        pass


class Motor(Joint):
    def __init__(self, config: dict, parent: 'KSRCore.control.model.Componet' = None):
        super().__init__(config)


Component.componentNameMap = {
    'component': Component,
    'structure': Structure
    'joint': Joint,
    'motor': Motor
    }