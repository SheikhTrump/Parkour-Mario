from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

point_x=15
point_y=100

def draw_points(x, y):
    glPointSize(5) #pixel size. by default 1 thake
    glBegin(GL_POINTS)
    glVertex2f(x,y) #jekhane show korbe pixel
    glEnd()


def iterate():
    glViewport(0, 0, 500, 500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
def animate():
    global point_x,point_y
    point_x+=2
    point_y-=.01
    if point_x> 500 or point_y>500:
        point_x=150
        point_y=150
    glutPostRedisplay()
def keyboard(key,x,y):
    if key==b"d":
        global point_x
        point_x+=1
        glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 0, 0.0) #konokichur color set (RGB)
    #call the draw methods here
    
    glPointSize(10)
    glBegin(GL_LINES)
    glVertex2f(point_x,point_y)
    glVertex2f(point_x+100,point_y+10)
    glVertex2f(point_x+200,point_y+20)
    glVertex2f(point_x+300,point_y+30)
    glVertex2f(point_x+400,point_y+40)
    glVertex2f(point_x+500,point_y+50)
    glVertex2f(point_x+600,point_y+60)
    glVertex2f(point_x+700,point_y+70)
    glVertex2f(point_x+800,point_y+80)
    glVertex2f(point_x+900,point_y+90)
    
   
    glEnd()


    glutSwapBuffers()



glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(500, 500) #window size
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"CSE 423 ") #window name
glutDisplayFunc(showScreen)
#glutIdleFunc(animate)
glutKeyboardFunc(keyboard)

glutMainLoop()