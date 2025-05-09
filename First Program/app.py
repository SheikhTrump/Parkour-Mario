from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random

# Window dimensions
width, height = 800, 600

# Game state
class GameState:
    def __init__(self):
        # Player properties
        self.player_pos = [0.0, 1.0, 0.0]  # x, y, z
        self.player_angle = 0.0
        self.player_lives = 10
        self.player_kills = 0
        self.is_jumping = False
        self.jump_height = 0
        self.jump_max_height = 2.0
        self.jump_speed = 0.1

        # Game objects
        self.bullets = []
        self.enemies = []

        # Camera
        self.camera_mode = 0  # 0 = TPP, 1 = FPP
        self.camera_distance = 5.0
        self.camera_height = 3.0

        # Tiles
        self.current_tile = 0
        self.tiles = []
        self.create_tiles()

        # Game status
        self.game_over = False
        self.game_won = False

        self.is_jumping = False
        self.jump_progress = 0
        self.jump_duration = 30  # frames for jump to complete
        self.jump_height = 2.0  # max height of jump
        self.jump_distance = 20.0  # forward distance of jump
        self.jump_start_pos = [0, 0, 0]  # starting position of jump

    def create_tiles(self):
        # Create 6-8 tiles with increasing difficulty
        num_tiles = random.randint(6, 8)
        tile_spacing = 45.0  # Increased spacing to match larger tiles

        for i in range(num_tiles):
            # Regular tiles (3x larger than before)
            if i < num_tiles - 1:
                tile = {
                    'position': [i * tile_spacing, 0, 0],  # x, y, z
                    'size': 30.0,  # Increased from 10.0 to 30.0 (3x)d
                    'num_enemies': random.randint(3, 4),
                    'enemy_speed': 0.01,
                    'completed': False
                }
            # Final tile (3x larger than before)
            else:
                tile = {
                    'position': [i * tile_spacing, 0, 0],
                    'size': 60.0,  # Increased from 20.0 to 60.0 (3x)
                    'num_enemies': 10,
                    'enemy_speed': 0.08,  # Faster enemies
                    'completed': False
                }
            self.tiles.append(tile)

        # Initialize first tile
        self.spawn_enemies()

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
            self.spawn_enemies()
            return True
        else:
            self.game_won = True
            return False

# Initialize game state
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

# Add this function to check if player is within current tile bounds
def is_player_in_tile():
    # If player is jumping, don't check bounds
    if game_state.is_jumping:
        return True

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

    # Draw game over or victory message
    if game_state.game_over:
        glColor3f(1.0, 0.0, 0.0)
        # Check if player fell off
        if not is_player_in_tile():
            text = "FELL OFF THE TILE! - Press R to restart"
        else:
            text = "GAME OVER - Press R to restart"
        glRasterPos2f(width/2 - len(text)*5, height/2)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    elif game_state.game_won:
        glColor3f(0.0, 1.0, 0.0)
        text = "VICTORY! - Press R to restart"
        glRasterPos2f(width/2 - len(text)*5, height/2)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Re-enable lighting and restore projection
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def update(value):
    if not game_state.game_over and not game_state.game_won:
        # Handle jumping
        if game_state.is_jumping:
            game_state.jump_progress += 1
            t = game_state.jump_progress / game_state.jump_duration

            # Vertical jump curve
            game_state.player_pos[1] = game_state.jump_start_pos[1] + math.sin(t * math.pi) * game_state.jump_height

            # Only move forward if not transitioning between tiles
            if not (len(game_state.enemies) == 0 and game_state.tiles[game_state.current_tile]['completed']):
                rad = math.radians(game_state.player_angle)
                game_state.player_pos[0] = game_state.jump_start_pos[0] + math.sin(rad) * game_state.jump_distance * t
                game_state.player_pos[2] = game_state.jump_start_pos[2] + math.cos(rad) * game_state.jump_distance * t

            # Jump completion
            if game_state.jump_progress >= game_state.jump_duration:
                game_state.is_jumping = False
                game_state.player_pos[1] = 1.0  # Reset to standing height

                # Check landing position for normal jumps
                if not (len(game_state.enemies) == 0 and game_state.tiles[game_state.current_tile]['completed']):
                    if not is_player_in_tile():
                        game_state.game_over = True
                # Handle tile transition
                elif game_state.move_to_next_tile():
                    pass  # Tile transition handled in move_to_next_tile()

            glutPostRedisplay()
            glutTimerFunc(16, update, 0)
            return

        # Check bounds only when grounded
        if not game_state.is_jumping and not is_player_in_tile():
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

            # Collision with player
            if dist < 0.8:
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
                    break

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

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

    # Draw HUD
    draw_hud()

    glutSwapBuffers()

def keyboard(key, x, y):
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
    elif key == b' ' and not game_state.is_jumping:  # Jump
        if len(game_state.enemies) == 0 and game_state.tiles[game_state.current_tile]['completed']:
            if game_state.current_tile < len(game_state.tiles) - 1:
                game_state.is_jumping = True
                game_state.jump_progress = 0
                game_state.jump_start_pos = game_state.player_pos.copy()
            else:
                game_state.game_won = True
        elif not game_state.is_jumping:  # Regular jump
            game_state.is_jumping = True
            game_state.jump_progress = 0
            game_state.jump_start_pos = game_state.player_pos.copy()
    elif key == b'c':  # Toggle camera mode
        game_state.camera_mode = 1 - game_state.camera_mode
    elif key == b'r':  # Restart game
        reset_game()

    glutPostRedisplay()

def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_state.game_over and not game_state.game_won:
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
    game_state = GameState()
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