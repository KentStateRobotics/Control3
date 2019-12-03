import pyglet
import client.guiWindows as guiWindows

def main():
    mainWindow = guiWindows.GuiDashboard()
    pyglet.app.run()

if __name__ == "__main__":
    main()