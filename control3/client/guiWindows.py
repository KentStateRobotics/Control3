#!/usr/bin/env python
'''
gui Windows
KentStateRobotics Jared Butcher 7/31/2019
'''
import pyglet
from pyglet.gl import gl
import client.guiElements as guiElements

class ControlWindow(pyglet.window.Window):
    """Menu windows should inheret this
    Valid events can be found https://pyglet.readthedocs.io/en/stable/modules/window.html
    Some useful ones incude:
        on_close() - When window is closed
        on_resize(width, height)
        on_draw()
        on_activate() - Window in is focus and can receive input
        on_deactivate() - Window can no longer receive input
        on_key_press(symbol, modifiers)
        on_key_release(symbol, modifiers)
        on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        on_mouse_press(x, y, button, modifiers)
        on_mouse_release(x, y, button, modifiers)
        on_mouse_scroll(x, y, scroll_x, scroll_y)
        on_text(text)
        on_text_motion(motion)
    """
    def __init__(self):
        super().__init__(resizable=True)
        self.elements = []
        self.elementHeldDown = None

    def addElement(self, element):
        self.elements.append(element)

    def removeElement(self, element):
        self.elements.remove(element)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            for element in reversed(self.elements):
                elm = element.checkClick(x, y)
                if not elm is None:
                    self.elementHeldDown = elm
                    break

    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            if not self.elementHeldDown is None:
                self.elementHeldDown.release()
                self.elementHeldDown = None

    def on_draw(self):
        self.clear()
        for element in self.elements:
            element.draw()

class GuiTestMenu(ControlWindow):
    def __init__(self):
        super().__init__()
        rectangle = guiElements.GuiRectangle(100, 100, 200, 200, onClick=lambda: print("yo"))
        self.addElement(rectangle)
        rectangle.addChild(guiElements.GuiElement(20, 5, pyglet.text.Label(text="Cross: " + str(5), font_size=24)))
        self.addElement(guiElements.GuiImage(200, 200, "control3/debugScripts/testTexture.jpg", imgX=50, imgY=50, imgHeight=50, imgWidth=50, onClick=lambda: print("hi")))
        

