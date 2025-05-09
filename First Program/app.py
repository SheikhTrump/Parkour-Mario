from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import time

# Window dimensions
width, height = 800, 600

# Game state
class GameState:
    def __init__(self, difficulty=1):  # Default to easy (1)
        # Set game parameters based on difficulty
        if difficulty == 1:  # Easy
            self.base_enemies = 4
            self.enemy_speed = 0.01
            self.final_enemies = 8
        elif difficulty == 2:  # Medium
            self.base_enemies = 6
            self.enemy_speed = 0.04
            self.final_enemies = 10
        else:  # Hard (3)
            self.base_enemies = 8
            self.enemy_speed = 0.1
            self.final_enemies = 12

        # Player properties
        self.player_pos = [0.0, 1.0, 0.0]  # x, y, z
        self.player_angle = 0.0
        self.player_lives = 10
        self.player_kills = 0

        # Game objects
        self.bullets = []
        self.enemies = []

        # Camera
        self.camera_mode = 0  # 0 = TPP, 1 = FPP
        self.camera_distance = 5.0
        self.camera_height = 3.0

        # Game status
        self.game_over = False
        self.game_won = False
        self.round_finished = False
        self.show_final_round_message = False
        self.showing_difficulty_menu = True  # Show menu at start

        # Queen - initialize FIRST
        self.queen = {
            'position': [0, 1.0, 0],
            'size': 1.0,
            'saved': False
        }

        # Tiles - initialize AFTER queen
        self.current_tile = 0
        self.tiles = []
        self.create_tiles()

        # Cheat mode variables
        self.cheat_mode_available = False
        self.cheat_mode_active = False
        self.cheat_mode_end_time = 0
        self.cheat_kills_needed = 10
        self.cheat_duration = 5  # seconds

    def activate_cheat_mode(self):
        if self.cheat_mode_available and not self.cheat_mode_active:
            self.cheat_mode_active = True
            self.cheat_mode_end_time = time.time() + self.cheat_duration
            self.cheat_mode_available = False

    def create_tiles(self):
        # Create 6-8 tiles with increasing difficulty
        num_tiles = random.randint(6, 8)
        tile_spacing = 45.0  # Increased spacing to match larger tiles

        for i in range(num_tiles):
            # Regular tiles (3x larger than before)
            if i < num_tiles - 1:
                tile = {
                    'position': [i * tile_spacing, 0, 0],  # x, y, z
                    'size': 30.0,  # Increased from 10.0 to 30.0 (3x)
                    'num_enemies': random.randint(self.base_enemies - 1, self.base_enemies),
                    'enemy_speed': self.enemy_speed,
                    'completed': False
                }
            # Final tile (3x larger than before)
            else:
                tile = {
                    'position': [i * tile_spacing, 0, 0],
                    'size': 60.0,  # Increased from 20.0 to 60.0 (3x)
                    'num_enemies': self.final_enemies,
                    'enemy_speed': self.enemy_speed * 3,  # Faster enemies
                    'completed': False
                }
            self.tiles.append(tile)

        # Initialize first tile
        self.spawn_enemies()
        # Position queen in center of final tile
        if self.tiles:  # If there are tiles
            final_tile = self.tiles[-1]
            self.queen['position'] = [
                final_tile['position'][0],
                1.0,
                final_tile['position'][2]
            ]

    def spawn_enemies(self):
        tile = self.tiles[self.current_tile]
        self.enemies = []

        for _ in range(tile['num_enemies']):
            # Spawn enemies within tile bounds
            x = tile['position'][0] + random.uniform(-tile['size']/2, tile['size']/2)
            z = tile['position'][2] + random.uniform(-tile['size']/2, tile['size']/2)
            self.enemies.append({
                'position': [x, 1.0, z],
                'speed': tile['enemy_speed'],
                'size': 0.8
            })

    def check_tile_completion(self):
        if len(self.enemies) == 0 and not self.tiles[self.current_tile]['completed']:
            self.tiles[self.current_tile]['completed'] = True
            self.round_finished = True
            return True
        return False

    def move_to_next_tile(self):
        if self.current_tile < len(self.tiles) - 1:
            self.current_tile += 1
            # Position player at center of new tile
            self.player_pos = [
                self.tiles[self.current_tile]['position'][0],
                1.0,  # Reset height
                self.tiles[self.current_tile]['position'][2]
            ]
            self.round_finished = False
            self.spawn_enemies()
            return True
        else:
            self.game_won = True
            return False

# Initialize game state with default difficulty (will be changed by menu)
game_state = GameState()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    # Set up light
    light_position = [10.0, 10.0, 10.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Set material properties
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
    tile_center = current_tile['position']
    half_size = current_tile['size'] / 2

    # Check x and z coordinates (y is height, we don't care about that)
    if (abs(game_state.player_pos[0] - tile_center[0]) > half_size or
        abs(game_state.player_pos[2] - tile_center[2]) > half_size):
        return False
    return True

def draw_tile(tile):
    glPushMatrix()
    glTranslatef(tile['position'][0], tile['position'][1], tile['position'][2])

    # Draw floor
    size = tile['size']
    half_size = size / 2

    glColor3f(0.7, 0.7, 0.7)  # Gray color for tiles
    glBegin(GL_QUADS)
    glVertex3f(-half_size, 0, -half_size)
    glVertex3f(half_size, 0, -half_size)
    glVertex3f(half_size, 0, half_size)
    glVertex3f(-half_size, 0, half_size)
    glEnd()

    # Draw edges
    glColor3f(0.4, 0.4, 0.4)
    edge_height = 0.2
    glBegin(GL_QUADS)
    # Front edge
    glVertex3f(-half_size, 0, -half_size)
    glVertex3f(half_size, 0, -half_size)
    glVertex3f(half_size, -edge_height, -half_size)
    glVertex3f(-half_size, -edge_height, -half_size)
    # Back edge
    glVertex3f(-half_size, 0, half_size)
    glVertex3f(half_size, 0, half_size)
    glVertex3f(half_size, -edge_height, half_size)
    glVertex3f(-half_size, -edge_height, half_size)
    # Left edge
    glVertex3f(-half_size, 0, -half_size)
    glVertex3f(-half_size, 0, half_size)
    glVertex3f(-half_size, -edge_height, half_size)
    glVertex3f(-half_size, -edge_height, -half_size)
    # Right edge
    glVertex3f(half_size, 0, -half_size)
    glVertex3f(half_size, 0, half_size)
    glVertex3f(half_size, -edge_height, half_size)
    glVertex3f(half_size, -edge_height, -half_size)
    glEnd()

    glPopMatrix()

def draw_queen():
    glPushMatrix()
    glTranslatef(game_state.queen['position'][0],
             game_state.queen['position'][1],
             game_state.queen['position'][2])

    # Queen body (purple)
    glColor3f(0.6, 0.0, 0.8)
    glutSolidSphere(game_state.queen['size'], 20, 20)

    # Crown (gold)
    glColor3f(1.0, 0.84, 0.0)
    glPushMatrix()
    glTranslatef(0, game_state.queen['size'] + 0.2, 0)
    glutSolidCone(0.5, 0.5, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_player():
    glPushMatrix()
    glTranslatef(game_state.player_pos[0], game_state.player_pos[1], game_state.player_pos[2])
    glRotatef(game_state.player_angle, 0.0, 1.0, 0.0)

    # Body
    glColor3f(0.0, 0.5, 1.0)  # Blue color
    glPushMatrix()
    glScalef(0.5, 1.5, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # Head
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glutSolidSphere(0.3, 20, 20)
    glPopMatrix()

    # Gun
    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    glPushMatrix()
    glTranslatef(0.2, 0.5, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glutSolidCylinder(0.05, 0.8, 10, 10)
    glPopMatrix()

    glPopMatrix()

def draw_enemies():
    for enemy in game_state.enemies:
        glPushMatrix()
        glTranslatef(enemy['position'][0], enemy['position'][1], enemy['position'][2])

        # Enemy body
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glutSolidSphere(enemy['size'], 20, 20)

        glPopMatrix()

def draw_bullets():
    for bullet in game_state.bullets:
        glPushMatrix()
        glTranslatef(bullet['position'][0], bullet['position'][1], bullet['position'][2])

        glColor3f(1.0, 1.0, 0.0)  # Yellow color
        glutSolidSphere(0.1, 10, 10)

        glPopMatrix()

def draw_difficulty_menu():
    # Switch to 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable lighting for menu
    glDisable(GL_LIGHTING)

    # Draw title
    glColor3f(1.0, 1.0, 1.0)
    title = "CHOOSE DIFFICULTY"
    glRasterPos2f(width/2 - len(title)*9, height/2 - 100)
    for char in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    # Draw options
    options = [
        "1 - Easy: 4 enemies per tile, slow speed",
        "2 - Medium: 6 enemies per tile, medium speed",
        "3 - Hard: 8 enemies per tile, fast speed"
    ]

    for i, option in enumerate(options):
        glColor3f(0.8, 0.8, 0.8)
        if i == 0:
            glColor3f(0.0, 1.0, 0.0)  # Green for easy
        elif i == 1:
            glColor3f(1.0, 1.0, 0.0)  # Yellow for medium
        elif i == 2:
            glColor3f(1.0, 0.0, 0.0)  # Red for hard

        glRasterPos2f(width/2 - len(option)*9, height/2 + i*30)
        for char in option:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Re-enable lighting and restore projection
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_hud():
    # Switch to 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable lighting for HUD
    glDisable(GL_LIGHTING)

    # Draw kill counter
    glColor3f(1.0, 1.0, 1.0)
    text = f"Kills: {game_state.player_kills}"
    glRasterPos2f(20, 30)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Draw lives
    text = f"Lives: {game_state.player_lives}"
    glRasterPos2f(20, 60)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Draw current tile
    text = f"Tile: {game_state.current_tile + 1}/{len(game_state.tiles)}"
    glRasterPos2f(20, 90)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Draw queen status in final tile
    if game_state.current_tile == len(game_state.tiles) - 1:
        if game_state.queen['saved']:
            status = "QUEEN SAVED!"
            color = (0.0, 1.0, 0.0)  # Green
        else:
            if len(game_state.enemies) > 0:
                status = "DEFEAT ALL ENEMIES TO SAVE QUEEN"
                color = (1.0, 0.0, 0.0)  # Red
            else:
                status = "SAVE THE QUEEN! (Walk to her)"
                color = (1.0, 1.0, 0.0)  # Yellow

        glColor3f(*color)
        text_width = len(status) * 9
        glRasterPos2f(width/2 - text_width/2, height - 30)
        for char in status:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Draw round finished message (only if not in final tile)
    if (game_state.round_finished and not game_state.game_won and
        game_state.current_tile < len(game_state.tiles) - 1):
        glColor3f(0.0, 1.0, 0.0)  # Green color
        message1 = "ROUND FINISHED!"
        message2 = "MOVE TO NEXT ROUND - PRESS SPACE"

        # Calculate positions to center the text
        text_width1 = len(message1) * 18  # Approximate width
        text_width2 = len(message2) * 18
        x_pos1 = width/2 - text_width1/2
        x_pos2 = width/2 - text_width2/2

        # Draw first line (bigger)
        glRasterPos2f(x_pos1, height/2 - 30)
        for char in message1:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

        # Draw second line
        glRasterPos2f(x_pos2, height/2 + 10)
        for char in message2:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    # Draw final round message
    if game_state.show_final_round_message:
        glColor3f(1.0, 0.0, 0.0)  # Red color
        message = "FINAL ROUND!"
        text_width = len(message) * 18  # Approximate width
        x_pos = width/2 - text_width/2

        glRasterPos2f(x_pos, height/2 - 50)
        for char in message:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    # Draw game over or victory message
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

    # Draw cheat mode status
    if game_state.cheat_mode_active:
        glColor3f(0.0, 1.0, 1.0)  # Cyan color
        status = f"CHEAT MODE ACTIVE! {max(0, int(game_state.cheat_mode_end_time - time.time()))}s"
        glRasterPos2f(width/2 - len(status)*4.5, 120)
        for char in status:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    elif game_state.cheat_mode_available:
        glColor3f(1.0, 1.0, 0.0)  # Yellow color
        status = "CHEAT MODE AVAILABLE! (Press M)"
        glRasterPos2f(width/2 - len(status)*4.5, 120)
        for char in status:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Re-enable lighting and restore projection
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def update(value):
    if not game_state.game_over and not game_state.game_won and not game_state.showing_difficulty_menu:
        # Handle cheat mode expiration
        if game_state.cheat_mode_active and time.time() > game_state.cheat_mode_end_time:
            game_state.cheat_mode_active = False

        # Check bounds
        if not is_player_in_tile():
            game_state.game_over = True
            glutPostRedisplay()
            glutTimerFunc(16, update, 0)
            return

        # Update bullets
        bullet_speed = 0.5
        for bullet in game_state.bullets[:]:
            rad = math.radians(bullet['angle'])
            bullet['position'][0] += bullet_speed * math.sin(rad)
            bullet['position'][2] += bullet_speed * math.cos(rad)

            # Remove out-of-bounds bullets
            current_tile = game_state.tiles[game_state.current_tile]
            tile_center = current_tile['position']
            max_dist = current_tile['size'] * 1.5
            if (abs(bullet['position'][0] - tile_center[0]) > max_dist) or abs(bullet['position'][2] - tile_center[2]) > max_dist:
                game_state.bullets.remove(bullet)

        # Update enemies
        for enemy in game_state.enemies[:]:
            # Movement
            dx = game_state.player_pos[0] - enemy['position'][0]
            dz = game_state.player_pos[2] - enemy['position'][2]
            dist = math.sqrt(dx*dx + dz*dz)

            if dist > 0.1:
                enemy['position'][0] += (dx/dist) * enemy['speed']
                enemy['position'][2] += (dz/dist) * enemy['speed']

            # Collision with player (skip if cheat mode is active)
            if dist < 0.8:
                if not game_state.cheat_mode_active:
                    game_state.player_lives -= 1
                game_state.enemies.remove(enemy)
                if game_state.player_lives <= 0:
                    game_state.game_over = True

        # Bullet-enemy collisions
        for bullet in game_state.bullets[:]:
            for enemy in game_state.enemies[:]:
                dx = bullet['position'][0] - enemy['position'][0]
                dy = bullet['position'][1] - enemy['position'][1]
                dz = bullet['position'][2] - enemy['position'][2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)

                if dist < enemy['size'] + 0.1:
                    game_state.bullets.remove(bullet)
                    game_state.enemies.remove(enemy)
                    game_state.player_kills += 1

                    # Check for cheat mode availability
                    if game_state.player_kills % game_state.cheat_kills_needed == 0:
                        game_state.cheat_mode_available = True
                    break

        # Check if current tile is completed
        game_state.check_tile_completion()

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

    # Check queen collision (only in final tile with no enemies)
    if (game_state.current_tile == len(game_state.tiles) - 1 and
            len(game_state.enemies) == 0 and
            not game_state.queen['saved'] and
            not game_state.showing_difficulty_menu):

            # Calculate distance to queen
            dx = game_state.player_pos[0] - game_state.queen['position'][0]
            dz = game_state.player_pos[2] - game_state.queen['position'][2]
            dist = math.sqrt(dx*dx + dz*dz)

            # If player touches queen after defeating all enemies
            if dist < 1.5:  # Collision distance
                game_state.queen['saved'] = True
                game_state.game_won = True

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if game_state.showing_difficulty_menu:
        draw_difficulty_menu()
    else:
        # Set up camera based on current mode
        if game_state.camera_mode == 0:  # Third-person
            rad = math.radians(game_state.player_angle)
            cam_x = game_state.player_pos[0] - game_state.camera_distance * math.sin(rad)
            cam_z = game_state.player_pos[2] - game_state.camera_distance * math.cos(rad)
            cam_y = game_state.player_pos[1] + game_state.camera_height

            gluLookAt(
                cam_x, cam_y, cam_z,
                game_state.player_pos[0], game_state.player_pos[1], game_state.player_pos[2],
                0, 1, 0
            )
        else:  # First-person
            rad = math.radians(game_state.player_angle)
            eye_x = game_state.player_pos[0] + 0.3 * math.sin(rad)
            eye_z = game_state.player_pos[2] + 0.3 * math.cos(rad)
            eye_y = game_state.player_pos[1] + 0.5  # Eye level

            look_x = game_state.player_pos[0] + math.sin(rad)
            look_z = game_state.player_pos[2] + math.cos(rad)
            look_y = game_state.player_pos[1] + 0.5

            gluLookAt(
                eye_x, eye_y, eye_z,
                look_x, look_y, look_z,
                0, 1, 0
            )

        # Draw all tiles
        for tile in game_state.tiles:
            draw_tile(tile)

        # Draw game objects
        draw_player()
        draw_enemies()
        draw_bullets()

        if game_state.current_tile == len(game_state.tiles) - 1 and not game_state.queen['saved']:
            draw_queen()
        # Draw HUD
        draw_hud()

    glutSwapBuffers()

def keyboard(key, x, y):
    global game_state

    # Handle difficulty selection
    if game_state.showing_difficulty_menu:
        if key == b'1':
            game_state = GameState(difficulty=1)  # Easy
            game_state.showing_difficulty_menu = False
        elif key == b'2':
            game_state = GameState(difficulty=2)  # Medium
            game_state.showing_difficulty_menu = False
        elif key == b'3':
            game_state = GameState(difficulty=3)  # Hard
            game_state.showing_difficulty_menu = False
        glutPostRedisplay()
        return

    move_speed = 0.2
    rotate_speed = 5.0

    if key == b'w':  # Move forward
        rad = math.radians(game_state.player_angle)
        game_state.player_pos[0] += move_speed * math.sin(rad)
        game_state.player_pos[2] += move_speed * math.cos(rad)
    elif key == b's':  # Move backward
        rad = math.radians(game_state.player_angle)
        game_state.player_pos[0] -= move_speed * math.sin(rad)
        game_state.player_pos[2] -= move_speed * math.cos(rad)
    elif key == b'a':  # Rotate left
        game_state.player_angle += rotate_speed
    elif key == b'd':  # Rotate right
        game_state.player_angle -= rotate_speed
    elif key == b' ':  # Teleport to next tile when current tile is completed
        if game_state.round_finished:
            if game_state.current_tile < len(game_state.tiles) - 1:
                game_state.move_to_next_tile()
            else:
                game_state.game_won = True
    elif key == b'c':  # Toggle camera mode
        game_state.camera_mode = 1 - game_state.camera_mode
    elif key == b'r':  # Restart game
        reset_game()
    elif key == b'm' or key == b'M':  # Activate cheat mode
        game_state.activate_cheat_mode()

    glutPostRedisplay()

def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_state.game_over and not game_state.game_won and not game_state.round_finished and not game_state.showing_difficulty_menu:
            # Fire a bullet
            bullet = {
                'position': [
                    game_state.player_pos[0],
                    game_state.player_pos[1] + 0.5,
                    game_state.player_pos[2]
                ],
                'angle': game_state.player_angle
            }
            game_state.bullets.append(bullet)

    glutPostRedisplay()

def reset_game():
    global game_state
    game_state.showing_difficulty_menu = True
    glutPostRedisplay()

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