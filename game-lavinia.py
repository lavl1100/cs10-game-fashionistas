import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Keyboard Movement Example"

MOVEMENT_SPEED = 8   # ⬅️ faster (was 5)


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BLACK)

        self.sprite_list = None
        self.player = None

    def setup(self):
        self.sprite_list = arcade.SpriteList()

        self.player = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_blue.png",
            scale=0.3   # ⬅️ smaller (was 0.5)
        )
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

        self.sprite_list.append(self.player)

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time):
        self.player.center_x += self.player.change_x
        self.player.center_y += self.player.change_y

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.change_y = MOVEMENT_SPEED
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP, arcade.key.S, arcade.key.DOWN):
            self.player.change_y = 0
        elif key in (arcade.key.A, arcade.key.LEFT, arcade.key.D, arcade.key.RIGHT):
            self.player.change_x = 0


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
