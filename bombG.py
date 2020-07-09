import pyglet
from pyglet.window import mouse
from pyglet.gl import gl
from pyglet import resource
from pyglet import sprite
from pyglet import clock
from random import randint
from time import sleep

resource.path = ['./resources/']
resource.reindex()
pyglet.options['debug_gl'] = False

SCREENW = 800
SCREENH = 600
FULLSCREEN = False
window = pyglet.window.Window(SCREENW, SCREENH, caption="Bomb Your Opponents",
                              fullscreen=FULLSCREEN)

default_cur = window.get_system_mouse_cursor(window.CURSOR_DEFAULT)
choose_cur = window.get_system_mouse_cursor(window.CURSOR_HAND)
denial_cur = window.get_system_mouse_cursor(window.CURSOR_NO)


def center_image(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


# Load images
game_BG = resource.image('background.png')
platform = resource.image('platform2.png')
ship1 = resource.image('ship1.png')
ship2 = resource.image('ship2.png')
stats_box = resource.image('statsBox.png')
bomb = resource.image('bomb.png')
trophy = resource.image('trophy.png')
main_BG = resource.image('mainBG.png')
game_logo = resource.image('logo.png')
start_unselected = resource.image('startUnselected.png')
start_selected = resource.image('startSelected.png')
center_image(bomb)
center_image(game_logo)
center_image(start_unselected)
center_image(start_selected)

# Allow transparency
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

# Animations (to be implemented)
explosion_frames = [
    resource.image('explosion1.png'),
    resource.image('explosion2.png'),
    resource.image('explosion3.png'),
    resource.image('explosion4.png')
]

for img in explosion_frames:
    img.anchor_x = img.width / 2
    img.anchor_y = img.height / 2


class Player():
    def __init__(self, name, hp, status, pId):
        self.name = name
        self.hp = hp
        self.status = status
        self.pId = pId


class Engine():
    def __init__(self, currentScreen):
        self.mouse_x = 0
        self.mouse_y = 0
        self.currentScreen = currentScreen
        self.paused = True

    def on_click(self, x, y, button):
        self.currentScreen.on_click(x, y, button)

    def mouseXY(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def draw(self):
        self.currentScreen.draw()

    def update(self, dt):
        window.set_mouse_cursor(default_cur)  # Always update the cursor to be default
        self.currentScreen.update(dt)
    
    def setCurrentScreen(self, currentScreen):
        self.currentScreen = currentScreen


class Screen():
    def __init__(self):
        self.paused = True

    def draw(self):
        pass

    def on_click(self, x, y, button):
        pass

    def update(self, dt):
        pass


class MainMenu(Screen):

    logo = sprite.Sprite(game_logo, x=SCREENW//2, y=480)
    bg = sprite.Sprite(main_BG, x=0, y=0)
    selected = sprite.Sprite(start_selected, x=400, y=200)
    unselected = sprite.Sprite(start_unselected, x=selected.x, y=selected.y)

    def __init__(self):
        self.mouse_overButton = False
        self.p1 = Player("Red", 100, "alive", ship1)
        self.p2 = Player("Blue", 100, "alive", ship2)

        # Texts
        self.copyrights = pyglet.text.Label("Made by webguy88 in 2020",
                                            x=655, y=15, anchor_x='center',
                                            anchor_y='center', font_size=16,
                                            color=(0, 0, 0, 255),
                                            bold=True)

        self.version = pyglet.text.Label("v 1.0",
                                         x=768, y=40, anchor_x='center',
                                         anchor_y='center', font_size=16,
                                         color=(0, 0, 0, 255),
                                         bold=True)

        # Regions
        self.start = Region(250, 150, 300, 100)

    def draw(self):
        self.bg.draw()
        self.logo.draw()
        self.copyrights.draw()
        self.version.draw()

        if self.mouse_overButton:
            self.selected.draw()
        else:
            self.unselected.draw()

    def on_click(self, x, y, button):
        if self.start.contain(x, y):
            engine.setCurrentScreen(game)

    def update(self, dt):
        if self.start.contain(engine.mouse_x, engine.mouse_y):
            self.mouse_overButton = True
            window.set_mouse_cursor(choose_cur)
        else:
            self.mouse_overButton = False


class Game(Screen):

    # Turning preloaded images into sprite
    bg = sprite.Sprite(game_BG, x=0, y=0)
    player1 = sprite.Sprite(ship1, x=83, y=130)
    player2 = sprite.Sprite(ship2, x=593, y=250)
    explosion_animation = pyglet.image.Animation.from_image_sequence(explosion_frames, duration=0.1, loop=True)

    def __init__(self):
        # Firing system
        self.fired = False
        self.who_firedBomb = 0
        self.bomb_x = -10
        self.bomb_y = -10
        self.explosion_x = -10
        self.explosion_y = -10

        # Rest of instances
        self.explosion = sprite.Sprite(self.explosion_animation, x=self.explosion_x, y=self.explosion_y)
        self.bombSpr = sprite.Sprite(bomb, x=self.bomb_x, y=self.bomb_y)
        self.p1 = main_menu.p1
        self.p2 = main_menu.p2
        self.turn = 2
        self.mouse_overPlayer = 0
        self.player_hit = 0
        self.p1_hitbox = Region(self.player1.x, self.player1.y, 139, 71)
        self.p2_hitbox = Region(self.player2.x, self.player2.y, 139, 71)
        self.bomb_hitbox = Region(self.bombSpr.x, self.bombSpr.y, 48, 55)

        # Text

        self.p1name = pyglet.text.Label(f"Name: {self.p1.name}",
                                        x=(self.player1.x + 53), y=(self.player1.y - 42),
                                        anchor_x='center', anchor_y='center',
                                        font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p2name = pyglet.text.Label(f"Name: {self.p2.name}",
                                        x=(self.player2.x + 53), y=(self.player2.y - 42),
                                        anchor_x='center', anchor_y='center',
                                        font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p1HP = pyglet.text.Label(f"HP: {self.p1.hp}", 
                                      x=(self.player1.x + 37), y=(self.player1.y - 69),
                                      anchor_x='center', anchor_y='center',
                                      font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p2HP = pyglet.text.Label(f"HP: {self.p2.hp}",
                                      x=(self.player2.x + 37), y=(self.player2.y - 69),
                                      anchor_x='center', anchor_y='center',
                                      font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p1_status = pyglet.text.Label(f"Status: {self.p1.status}",
                                           x=(self.player1.x + 60), y=(self.player1.y - 95),
                                           anchor_x='center', anchor_y='center',
                                           font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p2_status = pyglet.text.Label(f"Status: {self.p2.status}",
                                           x=(self.player2.x + 60), y=(self.player2.y - 95),
                                           anchor_x='center', anchor_y='center',
                                           font_size=16, bold=True, color=(0, 0, 0, 255))

        # Turn texts
        self.turn_text = None

        self.turn1 = pyglet.text.Label(f"It's {self.p1.name}'s turn!",
                                       x=SCREENW/2, y=570,
                                       anchor_x='center', anchor_y='center',
                                       font_size=28, bold=True, color=(255, 255, 255, 255))

        self.turn2 = pyglet.text.Label(f"It's {self.p2.name}'s turn!",
                                       x=SCREENW/2, y=570,
                                       anchor_x='center', anchor_y='center',
                                       font_size=28, bold=True, color=(255, 255, 255, 255))

        # Choosing system
        self.choose = randint(0, 1)

        # Debugging goes here
        ...

    def select_player(self):
        if self.choose == 0:
            if self.p1.status == "alive":
                self.turn = 1

            elif self.p1.hp <= 0:
                self.turn = -1
        
        elif self.choose == 1:
            if self.p2.status == "alive":
                self.turn = 2

            elif self.p2.hp <= 0:
                self.turn = -1

    # Reset all data
    def restart(self):
        self.p1.name = "Red"
        self.p2.name = "Blue"
        self.p1.hp = 100
        self.p2.hp = 100
        self.p1.status = "alive"
        self.p2.status = "alive"
        self.player_hit = 0
        self.fired = False
        self.who_firedBomb = 0

    # Drawing stuff
    def draw(self):
        self.bg.draw()
        platform.blit(70, 100)  # In this case we use 1 image to draw multiple
        platform.blit(580, 220)
        self.player1.draw()
        self.player2.draw()

        # Stats
        if self.mouse_overPlayer == 1:
            stats_box.blit((self.player1.x - 30), (self.player1.y - 120))
            self.p1name.draw()
            self.p1HP.draw()
            self.p1_status.draw()

        if self.mouse_overPlayer == 2:
            stats_box.blit((self.player2.x - 30), (self.player2.y - 120))
            self.p2name.draw()
            self.p2HP.draw()
            self.p2_status.draw()

        if self.turn == 1 and not self.fired:
            self.turn_text = self.turn1
            self.bombSpr.x = (self.player1.x + 75)
            self.bombSpr.y = (self.player1.y + 40)

        elif self.turn == 2 and not self.fired:
            self.turn_text = self.turn2
            self.bombSpr.x = (self.player2.x + 75)
            self.bombSpr.y = (self.player2.y + 40)
        
        elif self.turn == 0:
            self.player_hit = 0
            self.bombSpr.x = -10
            self.bombSpr.y = -10

        self.turn_text.draw()

        # Bomb stuff
        if self.fired:
            self.bombSpr.draw()

        if self.player_hit == 1:
            self.explosion.x = (self.player1.x + 75)
            self.explosion.y = (self.player1.y + 40)
            draw_explosion(1)
        
        elif self.player_hit == 2:
            self.explosion.x = (self.player2.x + 75)
            self.explosion.y = (self.player2.y + 40)
            draw_explosion(1)

        # Debugging goes here
        ...

    def on_click(self, x, y, button):

        # Can only click whenever it's the player's turn and
        # they are not under the explosion animation

        # Player 1
        if self.p2_hitbox.contain(x, y) and self.turn == 1 \
           and self.player_hit == 0:
            self.fired = True
            self.who_firedBomb = 1

        # Player 2
        if self.p1_hitbox.contain(x, y) and self.turn == 2 \
           and self.player_hit == 0:
            self.fired = True
            self.who_firedBomb = 2

    def update(self, dt):
        self.mouse_overPlayer = 0

        # Choose player 1
        if self.p1_hitbox.contain(engine.mouse_x, engine.mouse_y):
            window.set_mouse_cursor(choose_cur)
            self.mouse_overPlayer = 1
            self.bomb_x = self.player1.x
            self.bomb_y = self.player1.y
        
        # Choose player 2
        elif self.p2_hitbox.contain(engine.mouse_x, engine.mouse_y):
            window.set_mouse_cursor(choose_cur)
            self.mouse_overPlayer = 2
            self.bomb_x = self.player2.x
            self.bomb_y = self.player2.y

        # Player 1 fired bomb
        if self.fired and self.who_firedBomb == 1:
            self.bombSpr.x += 10
            self.bombSpr.y += 2.5
            self.bombSpr.rotation += 10

        # Player 2 fired bomb
        if self.fired and self.who_firedBomb == 2:
            self.bombSpr.x -= 10
            self.bombSpr.y -= 2.5
            self.bombSpr.rotation -= 10

        # Bomb hits player 1
        if self.p1_hitbox.contain(self.bombSpr.x, self.bombSpr.y) \
           and self.turn == 2:
            print("Impact")
            print(self.turn, self.choose)
            self.player_hit = 1
            self.fired = False
            clock.schedule_once(stop_explosion, 1)

            # Remove HP and give next turn
            if self.player_hit == 1:
                self.p1.hp -= randint(5, 20)
                #self.player_hit = 0
                self.choose = randint(0, 1)
                self.select_player()
            

        # Bomb hits player 2
        if self.p2_hitbox.contain(self.bombSpr.x, self.bombSpr.y) \
           and self.turn == 1:
            print("Impact")
            print(self.turn, self.choose)
            self.player_hit = 2
            self.fired = False
            clock.schedule_once(stop_explosion, 1)
            
            # Remove HP and give next turn
            if self.player_hit == 2:
                print(self.p2.hp)
                self.p2.hp -= randint(5, 20)
                #self.player_hit = 0
                self.choose = randint(0, 1)
                self.select_player()

        self.set_stats_text()

    def set_stats_text(self):
        self.p1HP = pyglet.text.Label(f"HP: {self.p1.hp}", 
                                      x=(self.player1.x + 37), y=(self.player1.y - 69),
                                      anchor_x='center', anchor_y='center',
                                      font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p2HP = pyglet.text.Label(f"HP: {self.p2.hp}",
                                      x=(self.player2.x + 37), y=(self.player2.y - 69),
                                      anchor_x='center', anchor_y='center',
                                      font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p1_status = pyglet.text.Label(f"Status: {self.p1.status}",
                                           x=(self.player1.x + 60), y=(self.player1.y - 95),
                                           anchor_x='center', anchor_y='center',
                                           font_size=16, bold=True, color=(0, 0, 0, 255))

        self.p2_status = pyglet.text.Label(f"Status: {self.p2.status}",
                                           x=(self.player2.x + 60), y=(self.player2.y - 95),
                                           anchor_x='center', anchor_y='center',
                                           font_size=16, bold=True, color=(0, 0, 0, 255))

        # Check HP and status
        if self.p1.hp <= 0:
            self.p1.status = "dead"
            engine.setCurrentScreen(WinnerScreen(self.p2.name))

        elif self.p2.hp <= 0:
            self.p2.status = "dead"
            engine.setCurrentScreen(WinnerScreen(self.p1.name))


class WinnerScreen(Screen):

    prize = sprite.Sprite(trophy, x=0, y=0)

    def __init__(self, winner):
        self.winner = winner
        self.leave = Region(0, 0, SCREENW, SCREENH)

        self.winner_text = pyglet.text.Label(f"Congratulations, {self.winner}! You have won!",
                                             x=400, y=300, anchor_x='center', anchor_y='center',
                                             font_size=24, bold=True)

    def draw(self):
        self.winner_text.draw()
        self.prize.opacity = 50
        self.prize.draw()

    def on_click(self, x, y, button):
        if self.leave.contain(x, y):
            engine.setCurrentScreen(main_menu)
            game.restart()


    def update(self, dt):
        pass


# Gives life to the region
class Rect:

    def __init__(self, x, y, w, h):
        self.set(x, y, w, h)

    def draw(self):
        pyglet.graphics.draw(4, gl.GL_QUADS, self._quad)

    def set(self, x=None, y=None, w=None, h=None):
        self._x = self._x if x is None else x
        self._y = self._y if y is None else y
        self._w = self._w if w is None else w
        self._h = self._h if h is None else h
        self._quad = ('v2f', (self._x, self._y,
                              self._x + self._w, self._y,
                              self._x + self._w, self._y + self._h,
                              self._x, self._y + self._h))

    def __repr__(self):
        return f"Rect(x={self._x}, y={self._y}, w={self._w}, h={self._h})"


# Allows clicks in certain areas
class Region(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contain(self, x, y):
        inside_x = False
        inside_y = False

        if x >= self.x and x <= (self.x + self.width):
            inside_x = True

        if y >= self.y and y <= (self.y + self.height):
            inside_y = True

        if inside_x and inside_y:
            return True
        else:
            return False

    def draw(self):
        r = Rect(self.x, self.y, self.width, self.height)
        r.draw()



# Class instances
main_menu = MainMenu()
game = Game()
engine = Engine(main_menu)


# Window events
@window.event
def on_draw():
    window.clear()
    engine.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button & mouse.LEFT:
        engine.on_click(x, y, button)


@window.event
def on_mouse_motion(x, y, dx, dy):
    engine.mouseXY(x, y, dx, dy)
    pass


@window.event
def update(dt):
    engine.update(dt)
    pass


@window.event
def stop_explosion(dt):
    print(game.player_hit)
    game.player_hit = 0
    pass


@window.event
def draw_explosion(dt):
    game.explosion.draw()


clock.schedule_interval(update, 1/30)
clock.schedule_once(draw_explosion, 1)

pyglet.app.run()