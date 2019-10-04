import pyglet
import pyglet.gl as gl
import numpy as np

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
pyglet.graphics.vertexbuffer()

counter = 0
crossLabel = pyglet.text.Label(text="Cross: " + str(counter), font_size=36, x=10, y=200)

def update(delta):
    kitakami.x += 10 * delta


pyglet.clock.schedule_interval(update, 1/120.0)

@window2.event
def on_draw():
    window2.clear()
    crossLabel.draw()

@window1.event
def on_resize(width, height):
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, width, 0, height, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)



@window1.event
def on_draw():
    global counter
    window1.clear()
    win1MainBatch.draw()
    
    

@window1.event
def on_resize(width, height):
    pass

@window1.event
def on_mouse_press(x, y, button, modifiers):
    global counter, crossLabel
    counter += 1
    crossLabel = pyglet.text.Label(text="Cross: " + str(counter), font_size=36, x=10, y=200)

















if __name__ == "__main__":
    pyglet.app.run()