import typing
import scipy.spatial.transform as transform

class CollisionObject:
    def collides(self, object) -> bool:
        raise NotImplementedError("Not implemented")

class Cube(CollisionObject):
    def __init__(self, size: typing.Tuple[float, float, float], origin : typing.Tuple[float, float, float], roation: typing.Tuple[float, float, float]):
        self.orgin = origin 
        self.size = size
        self.rot = transform.Rotation.from_euler('xyz', rotation, degrees=True)

class Point(CollisionObject):
    def __init__(self, origin : typing.Tuple[float, float, float]):
        self.origin = origin 

class Plane(CollisionObject):
    def __init__(self, size: typing.Tuple[float, float], origin : typing.Tuple[float, float, float], roation: typing.Tuple[float, float, float]):
        self.origin = origin 
        self.size = size
        self.rot = transform.Rotation.from_euler('xyz', rotation, degrees=True)

class Sphere(CollisionObject):
    def __init__(self, size: float, origin : typing.Tuple[float, float, float]):
        self.orgin = origin 
        self.size = size

class Cylinder(CollisionObject):
    def __init__(self, size: typing.Tuple[float, float], origin : typing.Tuple[float, float, float], roation: typing.Tuple[float, float, float]):
        self.orgin = origin 
        self.size = size
        self.rot = transform.Rotation.from_euler('xyz', rotation, degrees=True)