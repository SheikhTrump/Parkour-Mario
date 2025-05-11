

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import time

width, height = 800, 600

class Player:
    def __init__(self):
        self.position = [0.0, 1.0, 0.0]
        self.angle = 0.0
        self.lives = 10
        self.kills = 0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.angle, 0.0, 1.0, 0.0)


        glColor3f(0.0, 0.5, 1.0)
        glPushMatrix()
        glScalef(0.5, 1.5, 0.5)
        glutSolidCube(1.0)
        glPopMatrix()


        glColor3f(1.0, 0.8, 0.6)
        glPushMatrix()
        glTranslatef(0.0, 1.0, 0.0)
        glutSolidSphere(0.3, 20, 20)
        glPopMatrix()


        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0.2, 0.5, 0.0)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glutSolidCylinder(0.05, 0.8, 10, 10)
        glPopMatrix()

        glPopMatrix()

class Enemy:
    def __init__(self, position, speed, size=0.8):
        self.position = position.copy()
        self.speed = speed
        self.size = size
        self.angle = 0

    def update(self, player_pos, cheat_mode_active=False):
        # Calculate direction to player
        dx = player_pos[0] - self.position[0]
        dz = player_pos[2] - self.position[2]
        dist = math.sqrt(dx*dx + dz*dz)


        if dist > 0.1:
            self.angle = math.degrees(math.atan2(dx, dz))
            self.position[0] += (dx/dist) * self.speed
            self.position[2] += (dz/dist) * self.speed

        if dist < 0.8 and not cheat_mode_active:
            return True
        return False

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(-self.angle, 0.0, 1.0, 0.0)

        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glScalef(0.4, 1.2, 0.4)
        glutSolidCube(1.0)
        glPopMatrix()


        glColor3f(0.8, 0.4, 0.4)
        glPushMatrix()
        glTranslatef(0.0, 0.9, 0.0)
        glutSolidSphere(0.25, 20, 20)
        glPopMatrix()


        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(0.15, 0.9, 0.2)
        glutSolidSphere(0.05, 10, 10)
        glTranslatef(-0.3, 0.0, 0.0)
        glutSolidSphere(0.05, 10, 10)
        glPopMatrix()

        glPopMatrix()

class Queen:
    def __init__(self, position):
        self.position = position.copy()
        self.size = 1.0
        self.saved = False
        self.angle = 0

    def check_collision(self, player_pos):
        if self.saved:
            return False

        dx = player_pos[0] - self.position[0]
        dz = player_pos[2] - self.position[2]
        dist = math.sqrt(dx*dx + dz*dz)

        if dist < 1.5:
            self.saved = True
            return True
        return False

    def draw(self):
        if not self.saved:
            glPushMatrix()
            glTranslatef(self.position[0], self.position[1], self.position[2])
            glRotatef(self.angle, 0.0, 1.0, 0.0)


            glColor3f(0.6, 0.0, 0.8)
            glPushMatrix()
            glScalef(0.6, 1.8, 0.6)
            glutSolidCube(1.0)
            glPopMatrix()


            glColor3f(1.0, 0.8, 0.6)
            glPushMatrix()
            glTranslatef(0.0, 1.3, 0.0)
            glutSolidSphere(0.3, 20, 20)
            glPopMatrix()


            glColor3f(1.0, 0.84, 0.0)
            glPushMatrix()
            glTranslatef(0, 1.6, 0)
            glRotatef(90, 1, 0, 0)
            glutSolidTorus(0.05, 0.3, 10, 10)


            for i in range(5):
                glPushMatrix()
                glRotatef(i * 72, 0, 0, 1)
                glTranslatef(0.3, 0, 0)
                glutSolidCone(0.05, 0.2, 10, 10)
                glPopMatrix()
            glPopMatrix()


            glColor3f(0.8, 0.0, 1.0)
            glPushMatrix()
            glTranslatef(0, 0.5, 0)
            glScalef(0.7, 0.2, 0.7)
            glutSolidTorus(0.1, 0.5, 10, 10)
            glPopMatrix()

            glPopMatrix()


            self.angle = (self.angle + 0.5) % 360

class Bullet:
    def __init__(self, position, angle):
        self.position = position.copy()
        self.angle = angle
        self.speed = 0.5

    def update(self, tile_center, max_dist):
        rad = math.radians(self.angle)
        self.position[0] += self.speed * math.sin(rad)
        self.position[2] += self.speed * math.cos(rad)


        if (abs(self.position[0] - tile_center[0]) > max_dist or
            abs(self.position[2] - tile_center[2]) > max_dist):
            return True
        return False

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])

        glColor3f(1.0, 1.0, 0.0)
        glutSolidSphere(0.1, 10, 10)

        glPopMatrix()

class Tile:
    def __init__(self, position, size, num_enemies, enemy_speed, is_final=False):
        self.position = position.copy()
        self.size = size
        self.num_enemies = num_enemies
        self.enemy_speed = enemy_speed
        self.is_final = is_final
        self.completed = False

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])


        half_size = self.size / 2

        glColor3f(0.7, 0.7, 0.7)
        glBegin(GL_QUADS)
        glVertex3f(-half_size, 0, -half_size)
        glVertex3f(half_size, 0, -half_size)
        glVertex3f(half_size, 0, half_size)
        glVertex3f(-half_size, 0, half_size)
        glEnd()


        glColor3f(0.4, 0.4, 0.4)
        edge_height = 0.2
        glBegin(GL_QUADS)

        glVertex3f(-half_size, 0, -half_size)
        glVertex3f(half_size, 0, -half_size)
        glVertex3f(half_size, -edge_height, -half_size)
        glVertex3f(-half_size, -edge_height, -half_size)

        glVertex3f(-half_size, 0, half_size)
        glVertex3f(half_size, 0, half_size)
        glVertex3f(half_size, -edge_height, half_size)
        glVertex3f(-half_size, -edge_height, half_size)

        glVertex3f(-half_size, 0, -half_size)
        glVertex3f(-half_size, 0, half_size)
        glVertex3f(-half_size, -edge_height, half_size)
        glVertex3f(-half_size, -edge_height, -half_size)

        glVertex3f(half_size, 0, -half_size)
        glVertex3f(half_size, 0, half_size)
        glVertex3f(half_size, -edge_height, half_size)
        glVertex3f(half_size, -edge_height, -half_size)
        glEnd()

        glPopMatrix()


class GameState:
    def __init__(self, difficulty=1):

        if difficulty == 1:
            self.base_enemies = 4
            self.enemy_speed = 0.01
            self.final_enemies = 8
        elif difficulty == 2:
            self.base_enemies = 6
            self.enemy_speed = 0.04
            self.final_enemies = 10
        else:
            self.base_enemies = 8
            self.enemy_speed = 0.1
            self.final_enemies = 12


        self.player = Player()


        self.bullets = []
        self.enemies = []
        self.tiles = []


        self.camera_mode = 0
        self.camera_distance = 5.0
        self.camera_height = 3.0


        self.game_over = False
        self.game_won = False
        self.round_finished = False
        self.show_final_round_message = False
        self.showing_difficulty_menu = True
        self.paused = False


        self.queen = None
        self.current_tile = 0
        self.create_tiles()


        self.cheat_mode_available = False
        self.cheat_mode_active = False
        self.cheat_mode_end_time = 0
        self.cheat_kills_needed = 10
        self.cheat_duration = 5

    def activate_cheat_mode(self):
        if self.cheat_mode_available and not self.cheat_mode_active:
            self.cheat_mode_active = True
            self.cheat_mode_end_time = time.time() + self.cheat_duration
            self.cheat_mode_available = False

    def create_tiles(self):

        num_tiles = random.randint(6, 8)
        tile_spacing = 45.0

        for i in range(num_tiles):

            if i < num_tiles - 1:
                tile = Tile(
                    position=[i * tile_spacing, 0, 0],
                    size=30.0,
                    num_enemies=random.randint(self.base_enemies - 1, self.base_enemies),
                    enemy_speed=self.enemy_speed
                )

            else:
                tile = Tile(
                    position=[i * tile_spacing, 0, 0],
                    size=60.0,
                    num_enemies=self.final_enemies,
                    enemy_speed=self.enemy_speed * 3,
                    is_final=True
                )
            self.tiles.append(tile)


        self.spawn_enemies()


        if self.tiles:
            final_tile = self.tiles[-1]
            self.queen = Queen([
                final_tile.position[0],
                1.0,
                final_tile.position[2]
            ])

    def spawn_enemies(self):
        tile = self.tiles[self.current_tile]
        self.enemies = []

        for _ in range(tile.num_enemies):

            x = tile.position[0] + random.uniform(-tile.size/2, tile.size/2)
            z = tile.position[2] + random.uniform(-tile.size/2, tile.size/2)
            self.enemies.append(Enemy(
                position=[x, 1.0, z],
                speed=tile.enemy_speed
            ))

    def check_tile_completion(self):
        if len(self.enemies) == 0 and not self.tiles[self.current_tile].completed:
            self.tiles[self.current_tile].completed = True
            self.round_finished = True
            return True
        return False

    def move_to_next_tile(self):
        if self.current_tile < len(self.tiles) - 1:
            self.current_tile += 1

            self.player.position = [
                self.tiles[self.current_tile].position[0],
                1.0,
                self.tiles[self.current_tile].position[2]
            ]
            self.round_finished = False
            self.spawn_enemies()


            if self.current_tile == len(self.tiles) - 2:
                self.show_final_round_message = True
                glutTimerFunc(2000, lambda _: setattr(self, 'show_final_round_message', False), 0)

            return True
        else:
            self.game_won = True
            return False


game_state = GameState()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)


    light_position = [10.0, 10.0, 10.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)


    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

def reshape(w, h):
    global width, height
    width, height = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def is_player_in_tile():
    current_tile = game_state.tiles[game_state.current_tile]
    tile_center = current_tile.position
    half_size = current_tile.size / 2


    if (abs(game_state.player.position[0] - tile_center[0]) > half_size or
        abs(game_state.player.position[2] - tile_center[2]) > half_size):
        return False
    return True

def draw_difficulty_menu():

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)


    glColor3f(1.0, 1.0, 1.0)
    title = "CHOOSE DIFFICULTY"
    glRasterPos2f(width/2 - len(title)*9, height/2 - 100)
    for char in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))


    options = [
        "1 - Easy: 4 enemies per tile, slow speed",
        "2 - Medium: 6 enemies per tile, medium speed",
        "3 - Hard: 8 enemies per tile, fast speed"
    ]

    for i, option in enumerate(options):
        glColor3f(0.8, 0.8, 0.8)
        if i == 0:
            glColor3f(0.0, 1.0, 0.0)
        elif i == 1:
            glColor3f(1.0, 1.0, 0.0)
        elif i == 2:
            glColor3f(1.0, 0.0, 0.0)

        glRasterPos2f(width/2 - len(option)*9, height/2 + i*30)
        for char in option:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_crosshair():

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)


    glColor3f(1.0, 1.0, 1.0)
    crosshair_size = 15
    line_width = 2


    glLineWidth(line_width)
    glBegin(GL_LINES)
    glVertex2f(width/2 - crosshair_size, height/2)
    glVertex2f(width/2 + crosshair_size, height/2)
    glEnd()


    glBegin(GL_LINES)
    glVertex2f(width/2, height/2 - crosshair_size)
    glVertex2f(width/2, height/2 + crosshair_size)
    glEnd()


    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_hud():

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


    glDisable(GL_LIGHTING)


    glColor3f(1.0, 1.0, 1.0)
    text = f"Kills: {game_state.player.kills}"
    glRasterPos2f(20, 30)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    text = f"Lives: {game_state.player.lives}"
    glRasterPos2f(20, 60)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    text = f"Tile: {game_state.current_tile + 1}/{len(game_state.tiles)}"
    glRasterPos2f(20, 90)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    if game_state.current_tile == len(game_state.tiles) - 1:
        if game_state.queen.saved:
            status = "QUEEN SAVED!"
            color = (0.0, 1.0, 0.0)
        else:
            if len(game_state.enemies) > 0:
                status = "DEFEAT ALL ENEMIES TO SAVE QUEEN"
                color = (1.0, 0.0, 0.0)
            else:
                status = "SAVE THE QUEEN! (Walk to her)"
                color = (1.0, 1.0, 0.0)

        glColor3f(*color)
        text_width = len(status) * 9
        glRasterPos2f(width/2 - text_width/2, height - 30)
        for char in status:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    if (game_state.round_finished and not game_state.game_won and
        game_state.current_tile < len(game_state.tiles) - 1):
        glColor3f(0.0, 1.0, 0.0)
        message1 = "ROUND FINISHED!"
        message2 = "MOVE TO NEXT ROUND - PRESS SPACE"


        text_width1 = len(message1) * 18
        text_width2 = len(message2) * 18
        x_pos1 = width/2 - text_width1/2
        x_pos2 = width/2 - text_width2/2


        glRasterPos2f(x_pos1, height/2 - 30)
        for char in message1:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))


        glRasterPos2f(x_pos2, height/2 + 10)
        for char in message2:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))


    if game_state.show_final_round_message:
        glColor3f(1.0, 0.0, 0.0)
        message = "FINAL ROUND!"
        text_width = len(message) * 18
        x_pos = width/2 - text_width/2

        glRasterPos2f(x_pos, height/2 - 50)
        for char in message:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))


    if game_state.game_over:
        glColor3f(1.0, 0.0, 0.0)
        if not is_player_in_tile():
            text = "FELL OFF THE TILE! - Press R to restart"
        else:
            text = "GAME OVER - Press R to restart"
        glRasterPos2f(width/2 - len(text)*5, height/2)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    elif game_state.game_won:
        glColor3f(0.0, 1.0, 0.0)
        text = "VICTORY! YOU SAVED THE QUEEN! - Press R to restart"
        glRasterPos2f(width/2 - len(text)*5, height/2)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    if game_state.cheat_mode_active:
        glColor3f(0.0, 1.0, 1.0)
        status = f"CHEAT MODE ACTIVE! {max(0, int(game_state.cheat_mode_end_time - time.time()))}s"
        glRasterPos2f(width/2 - len(status)*4.5, 120)
        for char in status:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    elif game_state.cheat_mode_available:
        glColor3f(1.0, 1.0, 0.0)
        status = "CHEAT MODE AVAILABLE! (Press M)"
        glRasterPos2f(width/2 - len(status)*4.5, 120)
        for char in status:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    if game_state.paused:
        glColor3f(1.0, 1.0, 0.0)
        text = "GAME PAUSED - Press P to resume"
        glRasterPos2f(width/2 - len(text)*5, height/2 + 100)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def update(value):
    if not game_state.game_over and not game_state.game_won and not game_state.showing_difficulty_menu and not game_state.paused:
        #
        if game_state.cheat_mode_active and time.time() > game_state.cheat_mode_end_time:
            game_state.cheat_mode_active = False

        if not is_player_in_tile():
            game_state.game_over = True
            glutPostRedisplay()
            glutTimerFunc(16, update, 0)
            return


        current_tile = game_state.tiles[game_state.current_tile]
        max_dist = current_tile.size * 1.5

        for bullet in game_state.bullets[:]:
            if bullet.update(current_tile.position, max_dist):
                game_state.bullets.remove(bullet)


        for enemy in game_state.enemies[:]:
            if enemy.update(game_state.player.position, game_state.cheat_mode_active):
                game_state.player.lives -= 1
                game_state.enemies.remove(enemy)
                if game_state.player.lives <= 0:
                    game_state.game_over = True

        for bullet in game_state.bullets[:]:
            for enemy in game_state.enemies[:]:
                dx = bullet.position[0] - enemy.position[0]
                dy = bullet.position[1] - enemy.position[1]
                dz = bullet.position[2] - enemy.position[2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)

                if dist < enemy.size + 0.1:
                    game_state.bullets.remove(bullet)
                    game_state.enemies.remove(enemy)
                    game_state.player.kills += 1


                    if game_state.player.kills % game_state.cheat_kills_needed == 0:
                        game_state.cheat_mode_available = True
                    break


        game_state.check_tile_completion()

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


    if (game_state.current_tile == len(game_state.tiles) - 1 and
            len(game_state.enemies) == 0 and
            game_state.queen and not game_state.queen.saved and
            not game_state.showing_difficulty_menu and not game_state.paused):

        if game_state.queen.check_collision(game_state.player.position):
            game_state.game_won = True

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if game_state.showing_difficulty_menu:
        draw_difficulty_menu()
    else:

        if game_state.camera_mode == 0:
            rad = math.radians(game_state.player.angle)
            cam_x = game_state.player.position[0] - game_state.camera_distance * math.sin(rad)
            cam_z = game_state.player.position[2] - game_state.camera_distance * math.cos(rad)
            cam_y = game_state.player.position[1] + game_state.camera_height

            gluLookAt(
                cam_x, cam_y, cam_z,
                game_state.player.position[0], game_state.player.position[1], game_state.player.position[2],
                0, 1, 0
            )
        else:
            rad = math.radians(game_state.player.angle)
            eye_x = game_state.player.position[0] + 0.3 * math.sin(rad)
            eye_z = game_state.player.position[2] + 0.3 * math.cos(rad)
            eye_y = game_state.player.position[1] + 0.5

            look_x = game_state.player.position[0] + math.sin(rad)
            look_z = game_state.player.position[2] + math.cos(rad)
            look_y = game_state.player.position[1] + 0.5

            gluLookAt(
                eye_x, eye_y, eye_z,
                look_x, look_y, look_z,
                0, 1, 0
            )


        for tile in game_state.tiles:
            tile.draw()


        game_state.player.draw()
        for enemy in game_state.enemies:
            enemy.draw()
        for bullet in game_state.bullets:
            bullet.draw()

        if game_state.queen and game_state.current_tile == len(game_state.tiles) - 1 and not game_state.queen.saved:
            game_state.queen.draw()

        draw_hud()


        if (not game_state.game_over and not game_state.game_won and
            not game_state.round_finished and not game_state.show_final_round_message):
            draw_crosshair()

    glutSwapBuffers()

def keyboard(key, x, y):
    global game_state


    if game_state.showing_difficulty_menu:
        if key == b'1':
            game_state = GameState(difficulty=1)
            game_state.showing_difficulty_menu = False
        elif key == b'2':
            game_state = GameState(difficulty=2)
            game_state.showing_difficulty_menu = False
        elif key == b'3':
            game_state = GameState(difficulty=3)
            game_state.showing_difficulty_menu = False
        glutPostRedisplay()
        return


    if key == b'p' or key == b'P':
        game_state.paused = not game_state.paused
        glutPostRedisplay()
        return

    if game_state.paused:
        return

    move_speed = 0.2
    rotate_speed = 5.0

    if key == b'w':
        rad = math.radians(game_state.player.angle)
        game_state.player.position[0] += move_speed * math.sin(rad)
        game_state.player.position[2] += move_speed * math.cos(rad)
    elif key == b's':
        rad = math.radians(game_state.player.angle)
        game_state.player.position[0] -= move_speed * math.sin(rad)
        game_state.player.position[2] -= move_speed * math.cos(rad)
    elif key == b'a':
        game_state.player.angle += rotate_speed
    elif key == b'd':
        game_state.player.angle -= rotate_speed
    elif key == b' ':
        if game_state.round_finished:
            if game_state.current_tile < len(game_state.tiles) - 1:
                game_state.move_to_next_tile()
            else:
                game_state.game_won = True
    elif key == b'c':
        game_state.camera_mode = 1 - game_state.camera_mode
    elif key == b'r':
        reset_game()
    elif key == b'm' or key == b'M':
        game_state.activate_cheat_mode()

    glutPostRedisplay()

def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if (not game_state.game_over and not game_state.game_won and
            not game_state.round_finished and not game_state.showing_difficulty_menu and
            not game_state.paused):

            bullet = Bullet(
                position=[
                    game_state.player.position[0],
                    game_state.player.position[1] + 0.5,
                    game_state.player.position[2]
                ],
                angle=game_state.player.angle
            )
            game_state.bullets.append(bullet)

    glutPostRedisplay()

def reset_game():
    global game_state
    game_state.showing_difficulty_menu = True
    glutPostRedisplay()

import sys
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Tile Shooter Game")

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutTimerFunc(16, update, 0)

    init()
    glutMainLoop()

if __name__ == "__main__":
    main()