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
        drawable (batch, lable, ...) - any type that can be drawn with the draw() method with no parameters
        x (int | float) - x location to draw relitive to parent, can be pixles or ratio
        y (int | float) - y location to draw relitive to parent, can be pixles or ratio
        width (int | float) - width of clickable area, can be pixles or ratio
        height (int | float) - height of clickable area, can be pixles or ratio
        maintainAspectRatio (float) - If and only if a single dimension argument is given, will automaticly scale the second one
        relativity ((bool, bool, bool, bool)) - Flags if (x, y, width, height) respectively are given in pixles or 0-1 scale relitive to the parent.
            False - absolute pixles
            True - relitive ratio
    """
    def __init__(self, drawable, x, y, width=None, height=None, maintainAspectRatio=None, relativity=(False, False, False, False)):
        if (width is None or height is None) and maintainAspectRatio is None:
            raise TypeError("width and height must be set is maintainAspectRatio is not")
        elif width is None and height is None:
            raise TypeError("width or height must be set is maintainAspectRatio is set")
        self._children = []
        self._hidden = False
        self._defaultPos = (x, y)
        self._pos = list(self._defaultPos)
        self._defaultSize = (width, height)
        self._size = list(self._defaultSize)
        self._maintainAspectRatio = maintainAspectRatio
        self._relativity = relativity
        self._drawable = drawable

    def addChild(self, element):
        self._children.append(element)

    def removeChild(self, element):
        self._children.remove(element)

    def hide(self, hide):
        self._hidden = hide

    def isHidden(self):
        return self._hidden

    def getCurrentPosition(self):
        return self._pos

    def getDefaultPosition(self):
        return self._defaultPos

    def setPosition(self, x, y):
        self._defaultPos = (x, y)

    def resize(self, width, height):
        self._defaultSize = (width, height)

    def calculateSize(self, parentSize):
        size = list(self._defaultSize)
        if (not size[0] is None) and self._relativity[2]:
            size[0] *= parentSize[0]
        if (not size[1] is None) and self._relativity[3]:
            size[1] *= parentSize[1]
        if self._maintainAspectRatio:
            if self._defaultSize[0] is None:
                size[0] = self._maintainAspectRatio * size[1]
            else:
                size[1] = self._maintainAspectRatio * size[0]
        scale = (size[0] / (1 if self._defaultSize[0] is None else self._defaultSize[0]),
            size[1] / (1 if self._defaultSize[1] is None else self._defaultSize[1]))
        return (int(size[0]), int(size[1])), scale

    def draw(self, parentSize):
        if not self._hidden:
            self._size, scale = self.calculateSize(parentSize)
            self._pos = list(self._defaultPos)
            if self._relativity[0]:
                self._pos[0] *= parentSize[0]
            if self._relativity[1]:
                self._pos[1] *= parentSize[1]
            gl.glPushMatrix()
            gl.glTranslatef(self._pos[0], self._pos[1], 0)
            gl.glPushMatrix()
            #print(parentSize)
            #print(self._pos)
            #print(self._size)
            print("ELM")
            print(self._defaultSize)
            print(self._size)
            print(scale)
            gl.glScalef(scale[0], scale[1], 1)
            self._drawable.draw()
            gl.glPopMatrix()
            for child in self._children:
                child.draw(self._size)
            gl.glPopMatrix()

    def checkClick(self, pos):
        if not self._hidden:
            for child in self._children:
                elm = child.checkClick((pos[0] + self._pos[0], pos[1] + self._pos[1]))
                if not elm is None:
                    return elm
        return None



class GuiPressable(GuiElement):
    '''A rectangular gui element that can be clicked on
        Args:
            drawable (batch, lable, ...) - any type that can be drawn with the draw() method with no parameters
            x (int | float) - x location to draw relitive to parent, can be pixles or ratio
            y (int | float) - y location to draw relitive to parent, can be pixles or ratio
            width (int | float) - width of clickable area, can be pixles or ratio
            height (int | float) - height of clickable area, can be pixles or ratio
            maintainAspectRatio (float) - If and only if a single dimension argument is given, will automaticly scale the second one
            relativity ((bool, bool, bool, bool)) - Flags if (x, y, width, height) respectively are given in pixles or 0-1 scale relitive to the parent.
                False - absolute pixles
                True - relitive ratio
            onClick (float : optional) - callback function if image is clicked on
    '''
    def __init__(self, drawable, x, y, width=None, height=None, maintainAspectRatio=None, relativity=(False, False, False, False), onClick=None):
        self._onClick = onClick
        super().__init__(drawable, x, y, width, height, maintainAspectRatio, relativity)

    def checkClick(self, pos):
        if not self._hidden:
            for child in reversed(self._children):
                elm = child.checkClick((pos[0] - self._pos[0], pos[1] - self._pos[1]))
                if not elm is None:
                    return elm
            if not self._onClick is None and self._pos[0] <= pos[0] <= self._pos[0] + self._size[0] and self._pos[1] <= pos[1] <= self._pos[1] + self._size[1]:
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
            drawable (batch, lable, ...) - any type that can be drawn with the draw() method with no parameters
            x (int | float) - x location to draw relitive to parent, can be pixles or ratio
            y (int | float) - y location to draw relitive to parent, can be pixles or ratio
            width (int | float) - width of clickable area, can be pixles or ratio
            height (int | float) - height of clickable area, can be pixles or ratio
            maintainAspectRatio (float) - If and only if a single dimension argument is given, will automaticly scale the second one
            relativity ((bool, bool, bool, bool)) - Flags if (x, y, width, height) respectively are given in pixles or 0-1 scale relitive to the parent.
                False - absolute pixles
                True - relitive ratio
            color ((int, int, int, int) : optional) - color to draw rectangle, defaults to white
            onClick (float : optional) - callback function if image is clicked on
    '''
    def __init__(self, x, y, width=None, height=None, maintainAspectRatio=None, relativity=(False, False, False, False), color=(255,255,255,255), onClick=None):
        batch = pyglet.graphics.Batch()
        self._color = color
        size = [width, height]
        if width is None:
            size[0] = 1
        elif height is None:
            size[1] = 1
        self._vertList = batch.add(6, gl.GL_TRIANGLES, None,
            ('v2f', (0, 0, size[0], 0, 0, size[1], 0, size[1], size[0], 0, size[0], size[1])),
            ('c4B', (color * 6))
        )
        super().__init__(batch, x, y, width, height, maintainAspectRatio, relativity, onClick)

    def pressed(self):
        self._onClick()
        #Set the color for each vertex to .8 its current value without effecting transparency
        self._vertList.colors = [*[int(x * .8) for x in self._color[:3]], self._color[3]] * 6

    def release(self):
        self._vertList.colors = self._color * 6



class GuiImage(GuiPressable):
    '''Draw an image that may be clickable to the screen
        Args:
            img (str, pyglet.image) - either img path or pyglet image object
            x (int | float) - x location to draw relitive to parent, can be pixles or ratio
            y (int | float) - y location to draw relitive to parent, can be pixles or ratio
            width (int | float) - width of clickable area, can be pixles or ratio
            height (int | float) - height of clickable area, can be pixles or ratio
            maintainAspectRatio (float) - If and only if a single dimension argument is given, will automaticly scale the second one
            relativity ((bool, bool, bool, bool)) - Flags if (x, y, width, height) respectively are given in pixles or 0-1 scale relitive to the parent.
                False - absolute pixles
                True - relitive ratio
            rotation (float : optional) - rotation of image
            imgX (int : optional) - x position of subimage
            imgY (int : optional) - y position of subimage
            imgHeight (int : optional) - height of subimage, defaults to maximum size
            imgWidth (int : optional) - width of subimage, defaults to maximum size
            onClick (function() : optional) - callback function if image is clicked on
    '''
    def __init__(self, img, x, y, width=None, height=None, maintainAspectRatio=None, relativity=(False, False, False, False), rotation=0, imgX=None, imgY=None, imgHeight=None, imgWidth=None, onClick=None):
        if type(img) == str:
            img = pyglet.image.load(img)
        if not imgX is None and not imgY is None:
            if imgWidth is None:
                imgWidth = img.width - imgX
            if imgHeight is None:
                imgHeight = img.height - imgY
            img = img.get_region(imgX, imgY, imgHeight, imgWidth)
        sprite = pyglet.sprite.Sprite(img=img)
        sprite.update(rotation=rotation)
        if maintainAspectRatio is None:
            if width is None:
                width = sprite.width
            if height is None:
                height = sprite.height
        super().__init__(sprite, x, y, width, height, maintainAspectRatio, relativity, onClick)

    def calculateSize(self, parentSize):
        size = list(self._defaultSize)
        if (not size[0] is None) and self._relativity[2]:
            size[0] *= parentSize[0]
        if (not size[1] is None) and self._relativity[3]:
            size[1] *= parentSize[1]
        if self._maintainAspectRatio:
            if self._defaultSize[0] is None:
                size[0] = self._maintainAspectRatio * size[1]
            else:
                size[1] = self._maintainAspectRatio * size[0]
        scale = (size[0] / self._drawable.width,
            size[1] / self._drawable.height)
        return (int(size[0]), int(size[1])), scale



        if self._maintainAspectRatio:
            if self._defaultSize[0] is None:
                size = [self._maintainAspectRatio * adjSize[1], adjSize[1]]
            else:
                size = [adjSize[0], self._maintainAspectRatio * adjSize[0]]
        else:
            size = [self._defaultSize[0] * (self._defaultSize[0] / self._drawable.width), self._defaultSize[1] * (self._defaultSize[1] / self._drawable.height)]
        if self._relativity[3]:
            size[1] *= parentSize[1]
        if self._relativity[2]:
            size[0] *= parentSize[0]
        return (int(size[0]), int(size[1]))

class GuiText(GuiElement):
    '''Draw text or HTML
        Args:
            label (pyglet.text.HTMLLabel | pyglet.text.Label) - a drawable object with a text attribute
            x (int | float) - x location to draw relitive to parent, can be pixles or ratio
            y (int | float) - y location to draw relitive to parent, can be pixles or ratio
            width (int | float) - width of clickable area, can be pixles or ratio
            height (int | float) - height of clickable area, can be pixles or ratio
            maintainAspectRatio (float) - If and only if a single dimension argument is given, will automaticly scale the second one
            relativity ((bool, bool, bool, bool)) - Flags if (x, y, width, height) respectively are given in pixles or 0-1 scale relitive to the parent.
                False - absolute pixles
                True - relitive ratio
    '''
    def __init__(self, label, x, y, width=None, height=None, maintainAspectRatio=None, relativity=(False, False, False, False)):
        if not type(label) in (pyglet.text.HTMLLabel, pyglet.text.Label):
            raise TypeError("Lable must be of type pyglet.text.HTMLLabel or pyglet.text.Label")
        if maintainAspectRatio is None:
            if width is None:
                width = 1
            if height is None:
                height = 1
        super().__init__(label, x, y, width, height, maintainAspectRatio, relativity)
    
    def editText(self, text):
        self._drawable.text = text



class GuiStaticBatch(GuiElement):
    '''Static area of GUI with multiple triangle based shapes. Will all be rendered in a single batch for efficiently.
    Use by fetching the batch from getBatch and creating elements within it
        Args:
            x (int | float) - x location to draw relitive to parent, can be pixles or ratio
            y (int | float) - y location to draw relitive to parent, can be pixles or ratio
            width (int | float) - width of clickable area, can be pixles or ratio
            height (int | float) - height of clickable area, can be pixles or ratio
            maintainAspectRatio (float) - If and only if a single dimension argument is given, will automaticly scale the second one
            relativity ((bool, bool, bool, bool)) - Flags if (x, y, width, height) respectively are given in pixles or 0-1 scale relitive to the parent.
                False - absolute pixles
                True - relitive ratio
    '''
    def __init__(self, x, y, width=None, height=None, maintainAspectRatio=None, relativity=(False, False, False, False)):
        self._batch = pyglet.graphics.Batch()
        super().__init__(self._batch, x, y, width, height, maintainAspectRatio, relativity)

    def addVertexList(self, x, y, vertexs, colors):
        """Add a vertex list to the batch
        Args:
            x (int) - x position relitive to batch
            y (int) - y position relitive to batch
            vertexs ((float)) - A SINGLE truple or list of pairs of vertexes to be drawn in 2D triangles. 
                Triangle verticies must be given in counter clockwise order.
                ex: (0, 0, 5, 0, 0, 10, 0, 10, 5, 0, 5, 10) - Creates a rectangle
            colors ((int)) - A SINGLE truple or list of colors that map one to one to each vertex.
                Or a single color to be assinged to all vertices.
                Colors are defined by four bytes(0-255) in the order Red, Green, Blue, Alpha.
                ex: 
                    (255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255) - For a single red triangle
                    (0, 255, 0, 255) - Sets all vertices to green
        """
        if len(colors) == 4 and len(colors) != len(vertexs):
            colors = colors * len(vertexs)
        self._vertList = self._batch.add(len(vertexs), gl.GL_TRIANGLES, None,
            ('v2f', vertexs),
            ('c4B', colors)
        )

    def getBatch(self):
        '''Returns this elements batch object to allow manual adding of pygle drawable objects
        Such as sprites, text, html, vertex lists, etc...
        '''
        return self._batch