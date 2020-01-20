#!/usr/bin/env python
'''
GUI Windows
KentStateRobotics Jared Butcher 11/1/2019

Spicific, seperate windows (ex: main window, camera view) will inheret from ControlWindow 
which inhertes from pyglet.window.Window.
The ControlWindow class is required for using the guiElements graphical elements.
Windows can override events beloning to the pyglet window.
'''
import pyglet
from pyglet.gl import gl
import client.guiElements as guiElements

class ControlWindow(pyglet.window.Window):
    """Menu windows should inheret this
    Add gui elements to the by using addElement.
    Events belonging to pyglet window can be overriden. 
    If mouse_press, mouse_release, and on_draw are overriden call the versions in this class as well.
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
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def addElement(self, element):
        self.elements.append(element)

    def removeElement(self, element):
        self.elements.remove(element)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            for element in reversed(self.elements):
                elm = element.checkClick((x, y), (x, y))
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
        try:
            for element in self.elements:
                element.draw(self.get_size())
        except Exception:
            import traceback
            traceback.print_exc()
            

class GuiTestMenu(ControlWindow):
    def __init__(self):
        super().__init__()
        rectangle = guiElements.GuiButton(200, 200, .2, .2, relativity=(False, False, True, True),onClick=lambda: print("yo"))
        self.addElement(guiElements.GuiButton(100, 100, .8, .8, relativity=(False, False, True, True), color=(128, 128, 128, 255)))
        self.addElement(guiElements.GuiButton(.8, .8, width=.1, onClickColor=(0,255,255,0), maintainAspectRatio=1, relativity=(True, True, True, True), onClick=lambda: print("help")))
        self.addElement(rectangle)

        rectangle.addElement(guiElements.GuiButton(.1, 20, .5, .5, color=(255,0,0,255), relativity=(True, False, True, True), border=(5,0,0,5), onClick=lambda: print("yoyo")))
        rectangle.addElement(guiElements.GuiButton(.8, 80, 100, 100, color=(0,255,0,255), relativity=(True, False, False, False), border=(5,5,5,5), onClick=lambda: print("ahh")))

        

        self.addElement(guiElements.GuiImage("control3/debugScripts/testTexture.jpg", 0, 0, width=.1, maintainAspectRatio=1, relativity=(False, False, True, False)))

