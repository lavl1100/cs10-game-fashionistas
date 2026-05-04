import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Mouse Follow Sprite")

        self.player = None
        self.player_list = None

        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):
        # Create sprite
        self.player = arcade.Sprite("assets/my_sprite.png", scale=0.3)
        self.player.center_x = 400
        self.player.center_y = 300

        # Put sprite in a SpriteList (required for drawing)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_update(self, delta_time):
        # Smooth follow toward mouse
        self.player.center_x += (self.mouse_x - self.player.center_x) * 0.1
        self.player.center_y += (self.mouse_y - self.player.center_y) * 0.1

    def on_draw(self):
        self.clear()
        self.player_list.draw()


# Run the game
game = Game()
game.setup()
arcade.run()
