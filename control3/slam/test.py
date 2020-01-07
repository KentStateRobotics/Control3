import pyrealsense2 as rs
import numpy as np
import cv2
import processing
import pyglet
import pyglet.gl as gl
import pyglet.window.mouse as mouse
import math
import cMap
import sys

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
    pipe = rs.pipeline()
    profile = pipe.start()
    sensors = profile.get_device().query_sensors()
    depthSensor = None
    for sensor in sensors:
        if sensor.is_depth_sensor():
            depthSensor = sensor
            break
    if depthSensor is None:
        print("failed to find sensor")
        return
    depthScale = depthSensor.as_depth_sensor().get_depth_scale()
    depthMap = cMap.construct(255, 20, 5)
    try:
        window = pyglet.window.Window(resizable=True)
        #window.set_exclusive_mouse(True)
        '''colors = [255,255,255, 128,0,0, 0,0,128]
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
        indice_gl_array = (gl.GLubyte * len(indice))(*indice)'''

        points = None
        verts = None
        gl.glDisable(gl.GL_CULL_FACE)

        azimuth = 0
        inclination = 0
        camDistance = 5

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
            nonlocal verts
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            #gl.glRotatef(temp * 60, 1, 0, 1)
            #gl.glDrawArrays(gl.GL_POINTS, 0, len(vertices) // 3)
            gl.glRotatef(math.pi / 2, 0, 1, 0)
            if not verts is None:
                gl.glDrawArrays(gl.GL_POINTS, 0, len(verts) // 3)

            gl.glPopMatrix()

        def update(delta):
            nonlocal points, depthScale, verts
            print("pre frames")
            frames = pipe.wait_for_frames()
            depth = frames.get_depth_frame()
            depthArray = np.asarray(depth.get_data(), dtype=np.uint16)
            cMap.applyDepthImage(depthMap, depthArray, depthScale, depthArray.shape[0], depthArray.shape[1], 1.5184, 1.0123, 0, .12, 0, 0, 0, 0)
            points = cMap.getPoints(depthMap)
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            print(len(points[1]))
            print(points[0])
            verts = np.frombuffer(points[1], dtype=np.float32)
            gl.glVertexPointer(3, gl.GL_FLOAT, 0, verts.ctypes.data)
            on_draw()
            
            
        
        pyglet.clock.schedule_interval(update, 1.0)
        #update(1)
        pyglet.app.run()
    finally:
        pipe.stop()
main()