#!/usr/bin/env python
'''
gui Elements
KentStateRobotics Jared Butcher 10/18/2019
'''
import pyglet
from pyglet.gl import gl

class GuiElement:
    """Base class for gui elements. Given x and y will be added to any offset the drawable
    already has and to all children.

    Args:
        x (int) - x location to draw, will be used in addtion to any offset within the drawable
        y (int) - y location to draw, will be used in addtion to any offset within the drawable
        drawable (batch, lable, ...) - any type that can be drawn with the draw() method with no parameters
    """
    def __init__(self, x, y, drawable):
        self._children = []
        self._hidden = False
        self._x = x
        self._y = y
        self._drawable = drawable

    def addChild(self, element):
        self._children.append(element)

    def removeChild(self, element):
        self._children.remove(element)

    def hide(self, hide):
        self._hidden = hide

    def isHidden(self):
        return self._hidden

    def getPosition(self):
        return self._x, self._y

    def setPosition(self, x, y):
        self._x = x
        self._y = y

    def draw(self):
        if not self._hidden:
            gl.glPushMatrix()
            gl.glTranslatef(self._x, self._y, 0)
            self._drawable.draw()
            for child in self._children:
                child.draw()
            gl.glPopMatrix()

    def checkClick(self, x, y):
        if not self._hidden:
            for child in self._children:
                elm = child.checkClick(x + self._x, y + self._y)
                if not elm is None:
                    return elm
        return None

class GuiPressable(GuiElement):
    def __init__(self, x, y, width, height, drawable, onClick=None):
        self._width = width
        self._height = height
        self._onClick = onClick
        super().__init__(x, y, drawable)

    def checkClick(self, x, y):
        if not self._hidden:
            for child in self._children:
                elm = child.checkClick(x + self._x, y + self._y)
                if not elm is None:
                    return elm
            print("1")
            if not self._onClick is None and self._x <= x <= self._x + self._width and self._y <= y <= self._y + self._height:
                print("2")
                self.pressed()
                print("3")
                return self
        return None
    
    def pressed(self):
        print("parent")
        self._onClick()

    def release(self):
        pass

class GuiRectangle(GuiPressable):
    def __init__(self, x, y, width, height, color=(255,255,255,255), onClick=None):
        batch = pyglet.graphics.Batch()
        self._vertList = batch.add(6, gl.GL_TRIANGLES, None,
            ('v2f', (0, 0, width, 0, 0, height, 0, height, width, 0, width, height)),
            ('c4B', (color * 6))
        )
        super().__init__(x, y, width, height, batch, onClick)

    def pressed(self):
        print("child")
        self._onClick()
        print("4")
        #Set the color for each vertex to .8 its current value without effecting transparency
        self._vertList.colors = [*[int(x * .8) for x in self._color[:3]], self._color[3]] * 6
        print("5")

    def release(self):
        print("release")
        self._vertList.colors = self._color * 6

class GuiImage(GuiRectangle):
    pass

class GuiStaticBatch(GuiElement):
    pass
