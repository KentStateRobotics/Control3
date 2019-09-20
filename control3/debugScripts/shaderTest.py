import pygame
import OpenGL.GL as gl
import OpenGL.GLU as glu
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
import numpy as np
import ctypes

verticies = np.array([
    (0,0,0),
    (0,0,1),
    (0,1,0),
    (0,1,1),
    (1,0,0),
    (1,0,1),
    (1,1,0),
    (1,1,1)
], dtype=np.float32)
vertBuffer = vbo.VBO(verticies)

triangles = np.array([
    (4,2,0),
    (1,4,0),
    (2,1,0),
    (2,4,6),
    (4,7,6),
    (7,2,6),
    (2,7,3),
    (7,1,3),
    (1,2,3),
    (7,4,5),
    (4,1,5),
    (1,7,5)
], dtype=np.int32)
triBuffer = vbo.VBO(triangles, target=gl.GL_ELEMENT_ARRAY_BUFFER)


def resize(width, height, options):
    pygame.display.set_mode((width, height), options)
    glu.gluPerspective(45, width / height, 0.1, 50.0)
    gl.glTranslatef(0.0, 0.0, -5)
    gl.glEnable(gl.GL_CULL_FACE);
    gl.glEnable(gl.GL_DEPTH_TEST)
    

def main():
    pygame.init()
    displayOptions = pygame.DOUBLEBUF|pygame.OPENGL|pygame.RESIZABLE|pygame.HWSURFACE

    #resize(800, 600, displayOptions)

    screen = pygame.display.set_mode ((800,600), pygame.OPENGL|pygame.DOUBLEBUF, 24)
    gl.glViewport (0, 0, 800, 600)
    gl.glClearColor (0.0, 0.5, 0.5, 1.0)
    gl.glEnableClientState (gl.GL_VERTEX_ARRAY)

    vertices = [ 0.0, 1.0, 0.0,  0.0, 0.0, 0.0,  1.0, 1.0, 0.0 ]
    vbo = gl.glGenBuffers (1)
    gl.glBindBuffer (gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData (gl.GL_ARRAY_BUFFER, len(vertices)*4, (ctypes.c_float*len(vertices))(*vertices), gl.GL_STATIC_DRAW)


    VERTEX_SHADER = shaders.compileShader("""
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }""", gl.GL_VERTEX_SHADER)


    FRAGMENT_SHADER = shaders.compileShader("""
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }""", gl.GL_FRAGMENT_SHADER)

    shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing")
                pygame.quit()
            elif event.type == pygame.VIDEORESIZE:
                print(event.size)
                #resize(event.w, event.h, displayOptions)
        '''
        #gl.glRotatef(1.5,1.5,1.5,1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glUseProgram(shader)
        try:
            stuff.bind()
            try:
                gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
                gl.glDrawArrays(gl.GL_TRIANGLES, 0, 9)
            finally:
                stuff.unbind()
                gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        finally:
            gl.glUseProgram( 0 )


        pygame.display.flip()
        pygame.time.wait(10)'''
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(shader)
        #gl.glBindBuffer (gl.GL_ARRAY_BUFFER, vbo)
        #gl.glVertexPointer (3, gl.GL_FLOAT, 0, None)
        #gl.glDrawArrays (gl.GL_TRIANGLES, 0, 3)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertBuffer)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, triBuffer)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 6, gl.GL_FLOAT, False, 0, None)
        gl.glDrawElements(gl.GL_TRIANGLES, 12, gl.GL_UNSIGNED_INT, None)
        gl.glUseProgram(0)

        pygame.display.flip()
        pygame.time.wait(10)

main()