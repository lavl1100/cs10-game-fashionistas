import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Thrift Rack Minigame"

STARTING_MONEY = 100


class ThriftItem:
    def __init__(self):
        textures = [
            "assets/shirt.png",
            "assets/dress.png",
            "assets/pants.png"
        ]

        texture_path = random.choice(textures)

        self.sprite = arcade.Sprite(texture_path, scale=0.5)
        self.sprite.center_x = SCREEN_WIDTH // 2
        self.sprite.center_y = SCREEN_HEIGHT // 2 + 50

        self.price = random.randint(5, 30)
        self.value = random.randint(0, 60)

        # Rarity tint
        if self.value > 45:
            self.sprite.color = arcade.color.GOLD
        elif self.value > 25:
            self.sprite.color = arcade.color.LIGHT_GRAY
        else:
            self.sprite.color = arcade.color.WHITE


class ThriftGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BEIGE)

        self.rack = []
        self.current_index = 0

        self.money = STARTING_MONEY
        self.score = 0

        self.message = ""

    def setup(self):
        self.rack.clear()
        self.current_index = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

        # Fill rack with items
        for _ in range(10):
            self.rack.append(ThriftItem())

    def get_current_item(self):
        if self.rack:
            return self.rack[self.current_index]
        return None

    def on_draw(self):
        self.clear()

        item = self.get_current_item()

        if item:
            item.sprite.draw()

            # Price
            arcade.draw_text(
                f"Price: ${item.price}",
                SCREEN_WIDTH // 2 - 60,
                150,
                arcade.color.BLACK,
                16
            )

        # UI
        arcade.draw_text(f"Money: ${self.money}", 20, 20, arcade.color.BLACK, 16)
        arcade.draw_text(f"Profit: {self.score}", 20, 50, arcade.color.BLACK, 16)

        arcade.draw_text("← → to browse | SPACE to buy", 200, 20, arcade.color.DARK_GRAY, 14)

        # Message feedback
        arcade.draw_text(self.message, 200, 80, arcade.color.RED, 16)

    def on_key_press(self, key, modifiers):
        if not self.rack:
            return

        # Browse rack
        if key == arcade.key.RIGHT:
            self.current_index = (self.current_index + 1) % len(self.rack)

        elif key == arcade.key.LEFT:
            self.current_index = (self.current_index - 1) % len(self.rack)

        # Buy item
        elif key == arcade.key.SPACE:
            item = self.get_current_item()

            if item.price > self.money:
                self.message = "Not enough money!"
                return

            # Purchase
            self.money -= item.price
            profit = item.value - item.price
            self.score += profit

            self.message = f"Bought! Profit: {profit}"

            # Remove item
            self.rack.pop(self.current_index)

            # Fix index
            if self.current_index >= len(self.rack):
                self.current_index = 0

            # Add new item to end (like new clothes on rack)
            self.rack.append(ThriftItem())


def main():
    game = ThriftGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
