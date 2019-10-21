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
    '''A rectangular gui element that can be clicked on
        Args:
            x (int) - x position relitive to parent
            y (int) - y position relitive to parent
            width (int) - width of clickable area
            height (int) - height of clickable area
            drawable (batch, lable, ...) - any type that can be drawn with the draw() method with no parameters
            onClick (float : optional) - callback function if image is clicked on
    '''
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
            if not self._onClick is None and self._x <= x <= self._x + self._width and self._y <= y <= self._y + self._height:
                self.pressed()
                return self
        return None
    
    def pressed(self):
        self._onClick()

    def release(self):
        pass

class GuiRectangle(GuiPressable):
    '''A rectangular gui element that can drawn and clicked on. Will shade when pressed
        Args:
            x (int) - x position relitive to parent
            y (int) - y position relitive to parent
            width (int) - width of clickable area
            height (int) - height of clickable area
            drawable (batch, lable, ...) - any type that can be drawn with the draw() method with no parameters
            color ((int, int, int, int) : optional) - color to draw rectangle, defaults to white
            onClick (float : optional) - callback function if image is clicked on
    '''
    def __init__(self, x, y, width, height, color=(255,255,255,255), onClick=None):
        batch = pyglet.graphics.Batch()
        self._vertList = batch.add(6, gl.GL_TRIANGLES, None,
            ('v2f', (0, 0, width, 0, 0, height, 0, height, width, 0, width, height)),
            ('c4B', (color * 6))
        )
        super().__init__(x, y, width, height, batch, onClick)

    def pressed(self):
        self._onClick()
        #Set the color for each vertex to .8 its current value without effecting transparency
        self._vertList.colors = [*[int(x * .8) for x in self._color[:3]], self._color[3]] * 6

    def release(self):
        self._vertList.colors = self._color * 6

class GuiImage(GuiPressable):
    '''Draw an image that may be clickable to the screen
        Args:
            x (int) - x position relitive to parent
            y (int) - y position relitive to parent
            img (str, pyglet.image) - either img path or pyglet image object
            xScale (float : optional) - scale the width of the image
            yScale (float : optional) - scale the height of the image
            rotation (float : optional) - rotation of image
            imgX (int : optional) - x position of subimage
            imgY (int : optional) - y position of subimage
            imgHeight (int : optional) - height of subimage, defaults to maximum size
            imgWidth (int : optional) - width of subimage, defaults to maximum size
            onClick (function() : optional) - callback function if image is clicked on
    '''
    def __init__(self, x, y, img, xScale=1, yScale=1, rotation=0, imgX=None, imgY=None, imgHeight=None, imgWidth=None, onClick=None):
        if type(img) == str:
            img = pyglet.image.load(img)
        if not imgX is None and not imgY is None:
            if imgWidth is None:
                imgWidth = img.width - imgX
            if imgHeight is None:
                imgHeight = img.height - imgY
            img = img.get_region(imgX, imgY, imgHeight, imgWidth)
        sprite = pyglet.sprite.Sprite(img=img)
        sprite.update(rotation=rotation, scale_x=xScale, scale_y=yScale)
        super().__init__(x, y, sprite.width, sprite.height, sprite, onClick)

class GuiStaticBatch(GuiElement):
    '''Static area of GUI with multiple triangle based shapes. Will all be rendered in a single batch for efficiently
    Args:
        x (int) - x position relitive to parent
        y (int) - y position relitive to parent
        vertexs ((float)) - A SINGLE truple or list of pairs of vertexes to be drawn in 2D triangles. 
            Triangle verticies must be given in counter clockwise order.
            ex: (0, 0, 5, 0, 0, 10, 0, 10, 5, 0, 5, 10) - Creates a rectangle
        colors ((int)) - A SINGLE truple or list of colors that map one to one to each vertex.
            Or a single color to be assinged to all vertices.
            Colors are defined by four bytes(0-255) in the order Red, Green, Blue, Alpha.
            ex: 
                (255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255) - For a single red triangle
                (0, 255, 0, 255) - Sets all vertices to green
    '''
    def __init__(self, x, y, vertexs, colors):
        if len(colors) == 4 and len(colors) != len(vertexs):
            colors = colors * len(vertexs)
        batch = pyglet.graphics.Batch()
        self._vertList = batch.add(len(vertexs), gl.GL_TRIANGLES, None,
            ('v2f', vertexs),
            ('c4B', colors)
        )
        super().__init__(x, y, batch)
