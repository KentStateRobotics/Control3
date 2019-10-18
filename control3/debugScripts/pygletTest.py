import pyglet
import pyglet.gl as gl
import numpy as np
import ctypes

window1 = pyglet.window.Window(resizable=True)
window2 = pyglet.window.Window()

img = pyglet.resource.image("testTexture.jpg")
img.anchor_x = img.width // 2
img.anchor_y = img.height // 2

win1MainBatch = pyglet.graphics.Batch()

kitakami = pyglet.sprite.Sprite(img=img, x = 400, y = 400, batch=win1MainBatch)

ranLable = pyglet.text.Label(text="AHHHH", font_size=70, x=10, y=200, batch=win1MainBatch)
verticies = np.array([
    (0,0,0,0,0),
    (0,0,1,0,1),
    (0,1,0,1,0),
    (0,1,1,1,1),
    (1,0,0,0,1),
    (1,0,1,1,1),
    (1,1,0,1,1),
    (1,1,1,0,1)
], dtype=np.float32)
vertBuffer = pyglet.graphics.vertexbuffer.create_buffer(len(verticies) * 5 * 4, target=gl.GL_ARRAY_BUFFER, usage=gl.GL_STATIC_DRAW)
vertBuffer.set_data(verticies.ctypes.data)

cube = np.array([
    (2,4,0),
    (4,1,0),
    (1,2,0),
    (4,2,6),
    (7,4,6),
    (2,7,6),
    (7,2,3),
    (1,7,3),
    (2,1,3),
    (4,7,5),
    (1,4,5),
    (7,1,5)
], dtype=np.uint16)
cubeBuffer = pyglet.graphics.vertexbuffer.create_buffer(len(cube) * 3 * 2, target=gl.GL_ELEMENT_ARRAY_BUFFER, usage=gl.GL_STATIC_DRAW)
cubeBuffer.set_data(cube.ctypes.data)
print(cube.ctypes.data)

counter = 0
crossLabel = pyglet.text.Label(text="Cross: " + str(counter), font_size=36, x=10, y=200)

def update(delta):
    kitakami.x += 10 * delta

pyglet.clock.schedule_interval(update, 1/120.0)

@window2.event
def on_draw():
    window2.clear()
    crossLabel.draw()

menuProgram = None
texture = None

@window1.event
def on_resize(width, height):
    global menuProgram, texture
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, width, 0, height, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, None)
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, ctypes.c_voidp(3 * 4))
    gl.glEnableVertexAttribArray(0)
    gl.glEnableVertexAttribArray(1)

    texture = pyglet.image.load("testTexture1.jpg").get_texture()

    vertShader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertShader, 1, ctypes.cast(ctypes.pointer((ctypes.c_char_p * 1)(*[open('../client/shaders/menu.vsh').read().encode('utf-8')])), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), None)
    gl.glCompileShader(vertShader)
    fragShader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragShader, 1, ctypes.cast(ctypes.pointer((ctypes.c_char_p * 1)(*[open('../client/shaders/menu.fsh').read().encode('utf-8')])), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), None)
    gl.glCompileShader(fragShader)
    menuProgram = gl.glCreateProgram()
    gl.glAttachShader(menuProgram, vertShader)
    gl.glAttachShader(menuProgram, fragShader)
    gl.glLinkProgram(menuProgram)
    gl.glDeleteShader(vertShader)
    gl.glDeleteShader(fragShader)



@window1.event
def on_draw():
    global counter, menuProgram, texture, vertBuffer, cubeBuffer
    window1.clear()
    #win1MainBatch.draw()
    gl.glUseProgram(menuProgram)
    vertBuffer.bind()
    cubeBuffer.bind()
    gl.glEnable(texture.target)
    gl.glBindTexture(texture.target, texture.id)
    MVP = gl.glGetUniformLocation(menuProgram, (ctypes.c_char_p)("MVP".encode('utf-8')))
    tint = gl.glGetUniformLocation(menuProgram, (ctypes.c_char_p)("tint".encode('utf-8')))
    cMat = (ctypes.c_float * 16)()
    gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, cMat)
    gl.glUniformMatrix4fv(MVP, 1, gl.GL_FALSE, cMat)
    gl.glUniform4fv(tint, 1, (ctypes.c_float * 4)(1,1,1,1))
    gl.glDrawElements(gl.GL_TRIANGLES, 12 * 3, gl.GL_UNSIGNED_SHORT, None)
    gl.glUseProgram(0)












    



@window1.event
def on_mouse_press(x, y, button, modifiers):
    global counter, crossLabel
    counter += 1
    crossLabel = pyglet.text.Label(text="Cross: " + str(counter), font_size=36, x=10, y=200)



if __name__ == "__main__":
    pyglet.app.run()