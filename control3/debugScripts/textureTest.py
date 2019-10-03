import pygame
import OpenGL.GL as gl
import OpenGL.GLU as glu
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
import numpy as np
import ctypes
import cv2


verticies = np.array([
    (0,0,0,0,0),
    (0,0,1,0,0),
    (0,1,0,0,0),
    (0,1,1,0,0),
    (1,0,0,0,0),
    (1,0,1,0,0),
    (1,1,0,0,0),
    (1,1,1,0,0)
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
], dtype=np.uint16)
triBuffer = vbo.VBO(triangles, target=gl.GL_ELEMENT_ARRAY_BUFFER)


def resize(width, height, options):
    pygame.display.set_mode((width, height), options)
    glu.gluPerspective(45, width / height, 0.1, 50.0)
    gl.glTranslatef(0.0, 0.0, -5)
    gl.glEnable(gl.GL_CULL_FACE)
    #gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glClearColor (0.0, 0.5, 0.5, 1.0)
    gl.glEnableClientState (gl.GL_VERTEX_ARRAY)
    
    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, len(verticies) * 4 * 5, verticies, gl.GL_STATIC_DRAW)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, None)
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, None)
    gl.glEnableVertexAttribArray(0)
    gl.glEnableVertexAttribArray(1)

    textureImg = pygame.font.Font(None, 50).render("Hello", True, (255, 0, 0), (0,255,0))
    #textureImg = pygame.image.load("testTexture1.jpg")
    print(textureImg.get_height())
    print(textureImg.get_width())
    textureData = pygame.image.tostring(textureImg, "RGB", 1)
    npImg = np.fromstring(textureData, dtype=np.uint8)
    npImg = np.reshape(npImg, (textureImg.get_height(), textureImg.get_width(), 3))
    cv2.imshow("hello", npImg)
    cv2.waitKey(0)
    textureBuffer = gl.glGenTextures(1)
    #gl.glActiveTexture(gl.GL_TEXTURE0)
    #gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, textureBuffer)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, 4, textureImg.get_width(), textureImg.get_height(), 
    0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, textureData)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)


    indiceVbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indiceVbo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(triangles) * 2 * 3, triangles, gl.GL_STATIC_DRAW)

    VERTEX_SHADER = shaders.compileShader("""
        #version 330 core
        layout(location=0) in vec3 inPosition;
        layout(location=1) in vec2 inUV;
        out vec2 UV;
        uniform mat4 MVP;
        void main() {
            gl_Position = MVP * vec4(inPosition, 1);
            UV = inUV;
        }""", gl.GL_VERTEX_SHADER)


    FRAGMENT_SHADER = shaders.compileShader("""
        #version 330 core
        in vec2 UV;
        out vec4 color;
        uniform sampler2D myTexture; 
        void main() {
            color = texture(myTexture, UV).rgba;
            //color = vec3(1,UV[0],UV[1]);
        }""", gl.GL_FRAGMENT_SHADER)


    return shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
    


def main():
    pygame.init()
    displayOptions = pygame.DOUBLEBUF|pygame.OPENGL|pygame.RESIZABLE|pygame.HWSURFACE

    shader = resize(800, 600, displayOptions)

    angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing")
                pygame.quit()
            elif event.type == pygame.VIDEORESIZE:
                print(event.size)
                shader = resize(event.w, event.h, displayOptions)
        gl.glClear (gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(shader)
        MVP = gl.glGetUniformLocation(shader, 'MVP')
        gl.glUniformMatrix4fv(MVP, 1, gl.GL_FALSE, gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX))

        gl.glDrawElements(gl.GL_TRIANGLES, 12 * 3, gl.GL_UNSIGNED_SHORT, None)

        gl.glPushMatrix()
        gl.glTranslatef(-1.5, 0, 0)
        angle += 1
        gl.glRotatef(angle, 1, 0, 0)
        gl.glUniformMatrix4fv(MVP, 1, gl.GL_FALSE, gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX))
        gl.glDrawElements(gl.GL_TRIANGLES, 12 * 3, gl.GL_UNSIGNED_SHORT, None)
        gl.glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

main()