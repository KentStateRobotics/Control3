import pygame
from pygame.locals import *
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import numpy as np

verticies = (
    (0,0,0),
    (0,0,1),
    (0,1,0),
    (0,1,1),
    (1,0,0),
    (1,0,1),
    (1,1,0),
    (1,1,1)
)

triangles = (
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
)

def cube():
    GL.glBegin(GL.GL_TRIANGLES)
    for triangle in triangles:
        x = .33
        for vertex in triangle:
            GL.glColor3fv((x, verticies[triangle[2]][1], verticies[triangle[2]][2]))
            x = x + .33
            GL.glVertex3fv(verticies[vertex])

    GL.glEnd()

def resize(width, height):
    GL.glViewport(0, 0, width, height)
    print(width)
    print(height)
    GLU.gluPerspective(45, width / height, 0.1, 50.0)

    #GL.glMatrixMode(GL.GL_PROJECTION)
    #GL.glLoadIdentity()
    #GL.glOrtho(0, width, height, 0, .1, 50)

    GL.glTranslatef(0.0, 0.0, -5)

    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glLoadIdentity()
    

def main():
    pygame.init()
    displayOptions = pygame.DOUBLEBUF|pygame.OPENGL|pygame.RESIZABLE|pygame.HWSURFACE
    pygame.display.set_mode((800,600), displayOptions)

    #resize(800, 600)
    GLU.gluPerspective(45, 800 / 600, 0.1, 50.0)
    GL.glEnable(GL.GL_CULL_FACE);
    GL.glCullFace(GL.GL_FRONT)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glTranslatef(0.0, 0.0, -5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing")
                pygame.quit()
            elif event.type == pygame.VIDEORESIZE:
                #screen = pygame.display.set_mode(event.size, displayOptions)
                print(event.w)
                #GLU.gluPerspective(45, event.w / event.h, 0.1, 50.0)
                #resize(event.w, event.h)
    
        GL.glRotatef(1.5,1.5,1.5,1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        cube()
        pygame.display.flip()
        pygame.time.wait(10)

main()