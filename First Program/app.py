from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import sin, cos, radians
import math
import random
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

# === Global Variables ===
camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 2000
rand_var = 423

player_pos = [0, 0, -30]  # x, y, z
player_angle = 0

player_life = 5
missed_bullets = 0
game_over = False
score = 0

cheat_mode = False
cheat_rotation_speed = 2  # degrees per frame
cheat_fire_cooldown = 10  # frames between shots
cheat_fire_timer = 0




def spawn_enemy_bullet(min_distance=150):
    while True:
        x = random.randint(-GRID_LENGTH // 2 + 50, GRID_LENGTH // 2 - 50)
        y = random.randint(-GRID_LENGTH // 2 + 50, GRID_LENGTH // 2 - 50)
        z = 10  # Ground level

        px, py, _ = player_pos
        distance = math.sqrt((x - px)**2 + (y - py)**2)

        if distance >= min_distance:
            return (x, y, z)



enemy_bullet_positions =[(450,450,10)] #[spawn_enemy_bullet() for _ in range(5)]


camera_angle_horizontal = 0.0
camera_height = 1000
follow_player = False

pulse_time = 0.0

bullets = []  # Each bullet = {'pos': [x, y, z], 'angle': deg}
bullet_speed = 5

BOUNDARY = GRID_LENGTH // 2 - 20  # Leave a margin from the walls





# === Drawing Functions ===
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_shapes():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glutSolidCube(60)
    glTranslatef(0, 0, 100)
    glColor3f(0, 1, 0)
    glutSolidCube(60)

    glColor3f(1, 1, 0)
    gluCylinder(gluNewQuadric(), 40, 5, 150, 10, 10)
    glTranslatef(100, 0, 0)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 40, 5, 150, 10, 10)

    glColor3f(0, 1, 1)
    glTranslatef(200, 0, 0)
    gluSphere(gluNewQuadric(), 80, 10, 10)
    glPopMatrix()


def draw_player():
    glPushMatrix()
    glTranslatef(*player_pos)

    if game_over:
        glRotatef(90, 1, 0, 0)  # Rotate around X-axis to lay the player down
        glTranslatef(0, 40, 0)
    else:
        glRotatef(-player_angle, 0, 0, 1)

    # Body
    glPushMatrix()
    glColor3f(0.0, 0.5, 0.0)
    glTranslatef(0, 0, 60)
    glScalef(0.6, 0.3, 1.0)
    glutSolidCube(40)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 95)
    gluSphere(gluNewQuadric(), 10, 20, 20)
    glPopMatrix()

    # Arms
    for dx in [-9, 9]:
        glPushMatrix()
        glColor3f(0.9, 0.7, 0.6)
        glTranslatef(dx, 0, 75)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 2.5, 20, 20, 20)
        glPopMatrix()

    # Gun
    glPushMatrix()
    glColor3f(0.75, 0.75, 0.75)
    glTranslatef(0, 0, 75)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 2.5, 40, 40, 20)
    glPopMatrix()

    # Legs
    for dx in [-5, 5]:
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(dx, 0, 20)
        gluCylinder(gluNewQuadric(), 2.5, 5, 25, 20, 20)
        glPopMatrix()

    glPopMatrix()

from OpenGL.GL import *

from OpenGL.GL import *

def draw_floor_with_boundaries():
    big_tile_size = 800
    small_tile_size = 200
    spacing = big_tile_size + 100  # add a little spacing between big tiles
    start = -spacing / 2

    # Draw 4 big lavender tiles (2x2)
    for i in range(2):
        for j in range(2):
            x = start + i * spacing
            y = start + j * spacing

            glColor3f(0.8, 0.6, 1.0)  # Lavender
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + big_tile_size, y, 0)
            glVertex3f(x + big_tile_size, y + big_tile_size, 0)
            glVertex3f(x, y + big_tile_size, 0)
            glEnd()



    def draw_wall(tx, ty, sx, sy):
    #     glPushMatrix()
    #     glTranslatef(tx, ty, wall_height / 2)
    #     glScalef(sx, sy, wall_height)
    #     glutSolidCube(1)
    #     glPopMatrix()

    # glColor3f(0, 0, 1)  # Top wall
    # draw_wall(0, half_size + wall_thickness / 2, grid_size * tile_size, wall_thickness)
    # glColor3f(0, 1, 0)  # Bottom wall
    # draw_wall(0, -half_size - wall_thickness / 2, grid_size * tile_size, wall_thickness)
    # glColor3f(0, 1, 1)  # Right wall
    # draw_wall(half_size + wall_thickness / 2, 0, wall_thickness, grid_size * tile_size)
    # glColor3f(1, 1, 1)  # Left wall
    # draw_wall(-half_size - wall_thickness / 2, 0, wall_thickness, grid_size * tile_size)
        pass


def draw_enemy_bullet(position):
    x, y, z = position
    z = 50

    # Pulse scale factor using sine wave
    scale = 1.0 + 0.2 * math.sin(pulse_time)

    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)

    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 30, 35, 20)

    # glColor3f(0.0, 0.0, 0.0)
    # glTranslatef(0, 0, 30)
    # gluSphere(gluNewQuadric(), 15, 20, 20)

    glPopMatrix()



def move_enemy_bullet_towards_player():
    global enemy_bullet_positions
    speed = 0.04  # Adjustment    for how  fast enemies move

    updated_positions = []
    for ex, ey, ez in enemy_bullet_positions:
        px, py, _ = player_pos
        dx = px - ex
        dy = py - ey
        distance = math.hypot(dx, dy)

        if distance > 1e-2:  # Avoid division by zero
            dx /= distance
            dy /= distance
            ex += dx * speed
            ey += dy * speed

        updated_positions.append((ex, ey, ez))

    enemy_bullet_positions[:] = updated_positions


def rotate_gun_cheat_mode():
    global player_angle
    player_angle = (player_angle + cheat_rotation_speed) % 360

def will_bullet_hit(px, py, dir_x, dir_y, ex, ey, hit_radius=15):
    # Vector  from player to enemy_bullet
    vx = ex - px
    vy = ey - py

    # Project enemy_bullet vector onto bullet direction
    dot = vx * dir_x + vy * dir_y

    if dot < 0:
        return False  # enemy_bullet is behind

    # Closest point on the bullet path to the enemy_bullet
    closest_x = px + dot * dir_x
    closest_y = py + dot * dir_y

    # Distance from that closest point to the enemy_bullet
    dist_sq = (closest_x - ex) ** 2 + (closest_y - ey) ** 2

    return dist_sq <= hit_radius ** 2



def auto_aim_and_fire():
    px, py, pz = player_pos
    angle_rad = radians(player_angle)
    dir_x = math.sin(angle_rad)
    dir_y = math.cos(angle_rad)

    for ex, ey, ez in enemy_bullet_positions:
        if will_bullet_hit(px, py, dir_x, dir_y, ex, ey):
            fire_cheat_bullet()
            return True

    return False


def fire_cheat_bullet():
    bx, by, bz = player_pos[0], player_pos[1], player_pos[2] + 75
    bullets.append({'pos': [bx, by, bz], 'angle': player_angle})
    print(" Cheat bullet fired!")

def draw_bullet(bullet):
    x, y, z = bullet['pos']
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(0.3, 0.3, 0.3)
    glColor3f(0, 0, 0.0)
    glutSolidCube(20)
    glPopMatrix()
def reset_game():
    global player_pos, bullets, enemy_bullet_positions, player_life, missed_bullets, game_over, score
    player_pos = [0, 0, 0]
    bullets = []
    enemy_bullet_positions = [spawn_enemy_bullet() for _ in range(5)]
    player_life = 5
    missed_bullets = 0
    game_over = False
    score = 0

def check_collisions():
    global bullets, enemy_bullet_positions, player_life, game_over, score

    bullet_radius = 10
    enemy_bullet_radius = 20
    player_radius = 25

    new_bullets = []

    # Check kore bullet-enemy_bullet collision
    for bullet in bullets:
        bx, by, bz = bullet['pos']
        bullet_hit = False
        for i in range(len(enemy_bullet_positions)):
            ex, ey, ez = enemy_bullet_positions[i]
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - ez)**2)
            if dist < bullet_radius + enemy_bullet_radius + 20:
                # Bullet hit enemy_bullet
                bullet_hit = True
                enemy_bullet_positions[i] = spawn_enemy_bullet()
                score += 1
                print(" Hit! Score:", score)
                break
        if not bullet_hit:
            new_bullets.append(bullet)

    bullets = new_bullets

    # Check kore enemy_bullet-player collisions
    px, py, pz = player_pos
    for i in range(len(enemy_bullet_positions)):
        ex, ey, ez = enemy_bullet_positions[i]
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - ez)**2)
        if dist < player_radius + enemy_bullet_radius:
            player_life -= 1
            print(" Player hit! Life:", player_life)
            enemy_bullet_positions[i] = spawn_enemy_bullet()
            if player_life <= 0:
                print("💀 GAME OVER")
                game_over = True
# === Input Handlers ===
def keyboardListener(key, x, y):
    global fovY, player_pos, player_angle
    move_step = 10
    rotate_step = 5

    if key == b'r' and game_over:
        reset_game()
        return

    # Ignores movement if game is over
    if game_over:
        return

    move_step = 10
    rotate_step = 5

    if key == b'z':
        fovY = max(10, fovY - 5)

    elif key == b'x':
        fovY = min(170, fovY + 5)
    elif key == b'w':
        new_x = player_pos[0] + move_step * sin(radians(player_angle))
        new_y = player_pos[1] + move_step * cos(radians(player_angle))
        if abs(new_x) < BOUNDARY and abs(new_y) < BOUNDARY:
            player_pos[0] = new_x
            player_pos[1] = new_y
    elif key == b's':
        new_x = player_pos[0] - move_step * sin(radians(player_angle))
        new_y = player_pos[1] - move_step * cos(radians(player_angle))
        if abs(new_x) < BOUNDARY and abs(new_y) < BOUNDARY:
            player_pos[0] = new_x
            player_pos[1] = new_y
    elif key == b'a':
        player_angle -= rotate_step
    elif key == b'd':
        player_angle += rotate_step
    elif key == b'c':
        global cheat_mode
        cheat_mode = not cheat_mode
        print(" Cheat mode:", "ON" if cheat_mode else "OFF")

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global camera_angle_horizontal, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle_horizontal -= 0.05
    elif key == GLUT_KEY_RIGHT:
        camera_angle_horizontal += 0.05
    elif key == GLUT_KEY_UP:
        camera_height += 10
    elif key == GLUT_KEY_DOWN:
        camera_height -= 10
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global follow_player

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Fire bullet
        bx, by, bz = player_pos[0], player_pos[1], player_pos[2] +75 # gun height
        bullets.append({'pos': [bx, by, bz], 'angle': player_angle})

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow_player = not follow_player

    glutPostRedisplay()



# === Camera Setup ===
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    look()


def look():
    if follow_player:
        px, py, pz = player_pos
        angle_rad = radians(player_angle)

        # Camera position closer and at player's eye height
        eye_x = px + 15* sin(angle_rad)
        eye_y = py + 15 * cos(angle_rad)
        eye_z = pz + 85  # adjust to eye level (was 100)

        center_x = px + 100 * sin(angle_rad)
        center_y = py + 100 * cos(angle_rad)
        center_z = pz + 75  # slightly above the ground

    else:
        radius = 800
        eye_x = radius * sin(camera_angle_horizontal)
        eye_y = radius * cos(camera_angle_horizontal)
        eye_z = camera_height
        center_x = 0
        center_y = 0
        center_z = 0

    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)


# === Main Render Loop ===
def idle():
    global pulse_time, game_over, cheat_fire_timer

    if game_over:
        return

    pulse_time += 0.05
    move_enemy_bullet_towards_player()

    if cheat_mode:
        rotate_gun_cheat_mode()
        cheat_fire_timer += 1
        if cheat_fire_timer >= cheat_fire_cooldown:
            if auto_aim_and_fire():
                cheat_fire_timer = 0

    update_bullets()
    check_collisions()

    if player_life <= 0 or missed_bullets >= 10:
        print(" Game Over!")
        game_over = True

    glutPostRedisplay()


def update_bullets():
    global bullets, missed_bullets
    for bullet in bullets:
        angle_rad = math.radians(bullet['angle'])
        bullet['pos'][0] += bullet_speed * math.sin(angle_rad)
        bullet['pos'][1] += bullet_speed * math.cos(angle_rad)

    new_bullets = []
    for b in bullets:
        if abs(b['pos'][0]) < GRID_LENGTH and abs(b['pos'][1]) < GRID_LENGTH:
            new_bullets.append(b)
        else:
            missed_bullets += 1
            print(" Bullet missed! Missed bullets:", missed_bullets)
    bullets[:] = new_bullets


def update_enemies():
    global enemy_bullet_positions
    speed = 2  # or whatever feels right
    new_positions = []

    for ex, ey, ez in enemy_bullet_positions:
        px, py, _ = player_pos
        dx = px - ex
        dy = py - ey
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            new_positions.append((ex, ey, ez))
            continue

        dx /= dist
        dy /= dist

        new_x = ex + dx * speed
        new_y = ey + dy * speed

        # Clamp to boundary
        if abs(new_x) > BOUNDARY:
            new_x = BOUNDARY * (1 if new_x > 0 else -1)
        if abs(new_y) > BOUNDARY:
            new_y = BOUNDARY * (1 if new_y > 0 else -1)

        new_positions.append((new_x, new_y, ez))

    enemy_bullet_positions = new_positions


def showScreen():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_text(10, 770, f"score: {score}  Life: {player_life}  Missed Bullets: {missed_bullets}")
    draw_text(10, 740, f"")


    draw_floor_with_boundaries()
    #draw_shapes()
    draw_player()

    for enemy_bullet in enemy_bullet_positions:
        draw_enemy_bullet(enemy_bullet)
    for bullet in bullets:
        draw_bullet(bullet)


    glutSwapBuffers()


# === Initialization ===
def init():
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)


# === Entry Point ===
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(1000, 800)
glutCreateWindow(b"Bullet Frenzy - 3D Shooter")
init()
glutDisplayFunc(showScreen)
glutIdleFunc(idle)
glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutMainLoop()