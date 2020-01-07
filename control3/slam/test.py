import pyrealsense2 as rs
import numpy as np
import cv2
import processing
import pyglet
import pyglet.gl as gl
import pyglet.window.mouse as mouse
import math

def displayImg():
    pipe = rs.pipeline()
    profile = pipe.start()
    try:
        while True:
            frames = pipe.wait_for_frames()
            rgb = frames.get_color_frame()
            depth = frames.get_depth_frame()
            array = np.asarray(rgb.get_data(), dtype=np.uint8)
            depthArray = np.asarray(depth.get_data(), dtype=np.uint16)
            print("pre ext")
            processing.depthToGray(depthArray)
            print("post ext")
            depthArray = depthArray.astype(np.uint8, copy=False)
            #array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
            #cv2.imshow("help", array)
            print(depthArray.shape)
            cv2.imshow("depth", depthArray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipe.stop()

#displayImg()

def main():
    window = pyglet.window.Window(resizable=True)
    #window.set_exclusive_mouse(True)
    colors = [255,255,255, 128,0,0, 0,0,128]
    color_gl_array = (gl.GLubyte * len(colors))(*colors)

    gl.glEnableClientState(gl.GL_COLOR_ARRAY )
    gl.glColorPointer(3, gl.GL_UNSIGNED_BYTE, 0, color_gl_array)
    

    vertices = [0, 0, 0,
            1, 0, 0,
            1, 1, 0]
    vertices_gl_array = (gl.GLfloat * len(vertices))(*vertices)

    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices_gl_array)

    indice = [0,1,2]
    indice_gl_array = (gl.GLubyte * len(indice))(*indice)
    
    temp = 0

    def update(delta):
        nonlocal temp
        temp += delta

    pyglet.clock.schedule_interval(update, 1/120.0)
    gl.glDisable(gl.GL_CULL_FACE)
    #gl.glEnable(gl.GL_LIGHTING)
    #gl.glEnable(gl.GL_LIGHT0)

    azimuth = 0
    inclination = 0
    camDistance = 10

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            nonlocal azimuth, inclination, camDistance
            gl.glMatrixMode(gl.GL_MODELVIEW)
            azimuth += dx * .005
            inclination = max(.001, min(math.pi - .001, azimuth + dy * .005))
            camPos = [0,0,0]
            camPos[0] = camDistance * math.sin(inclination) * math.cos(azimuth)
            camPos[1] = camDistance * math.cos(inclination)
            camPos[2] = camDistance * math.sin(inclination) * math.sin(azimuth)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.gluLookAt(camPos[0], camPos[1], camPos[2], 0, 0, 0, 0, 1, 0)

    @window.event
    def on_mouse_scroll(x, y, scrollX, scrollY):
        nonlocal camDistance
        camDistance += scrollY * .2
        on_mouse_drag(0,0,0,0,mouse.LEFT, None)

    @window.event
    def on_resize(width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(65, width / float(height), .1, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    @window.event
    def on_draw():
        nonlocal temp, color_gl_array
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glPushMatrix()
        gl.glTranslatef(0, 0, 10)
        lightPos = (gl.GLfloat * 4)()
        lightPos[3] = 1
        #gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightPos)
        gl.glPopMatrix()
        gl.glRotatef(temp * 60, 1, 0, 1)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(vertices) // 3)
        gl.glPopMatrix()
    pyglet.app.run()

main()