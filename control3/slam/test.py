import pyrealsense2 as rs
import numpy as np
import cv2
import processing

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

displayImg()

''''
def main():
    pygame.init()
    displayOptions = pygame.DOUBLEBUF|pygame.OPENGL|pygame.RESIZABLE|pygame.HWSURFACE

    resize(800, 600, displayOptions)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing")
                pygame.quit()
            elif event.type == pygame.VIDEORESIZE:
                print(event.size)
                resize(event.w, event.h, displayOptions)
    
        GL.glRotatef(1.5,1.5,1.5,1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        cube()
        pygame.display.flip()
        pygame.time.wait(10)
'''