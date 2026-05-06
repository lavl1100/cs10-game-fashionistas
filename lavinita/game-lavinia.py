import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Thrift Rack (Animated)"

STARTING_MONEY = 100
RACK_SIZE = 10
SPACING = 140  # distance between clothes


class ThriftItem:
    def __init__(self):
        textures = [
            "assets/shirt.png",
            "assets/dress.png",
            "assets/pants.png"
        ]

        texture_path = random.choice(textures)

        self.sprite = arcade.Sprite(texture_path, scale=0.4)

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
        self.sprite_list = arcade.SpriteList()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

    def setup(self):
        self.rack.clear()
        self.sprite_list = arcade.SpriteList()

        self.current_index = 0
        self.target_offset = 0
        self.current_offset = 0

        self.money = STARTING_MONEY
        self.score = 0
        self.message = ""

        for _ in range(RACK_SIZE):
            item = ThriftItem()
            self.rack.append(item)
            self.sprite_list.append(item.sprite)

        self.update_positions()

    def update_positions(self):
        center_x = SCREEN_WIDTH // 2

        for i, item in enumerate(self.rack):
            x = center_x + (i * SPACING) - self.current_offset
            item.sprite.center_x = x
            item.sprite.center_y = SCREEN_HEIGHT // 2 + 50

            # Scale center item bigger
            if i == self.current_index:
                item.sprite.scale = 0.5
            else:
                item.sprite.scale = 0.35

    def on_draw(self):
        self.clear()

        # Draw rack bar
        arcade.draw_line(100, SCREEN_HEIGHT // 2 + 120,
                         700, SCREEN_HEIGHT // 2 + 120,
                         arcade.color.DARK_BROWN, 4)

        # Draw all clothes
        self.sprite_list.draw()

        # Draw price for center item
        if self.rack:
            item = self.rack[self.current_index]

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

        arcade.draw_text(self.message, 200, 80, arcade.color.RED, 16)

    def on_update(self, delta_time):
        # Smooth scrolling animation
        speed = 10

        if abs(self.current_offset - self.target_offset) > 1:
            self.current_offset += (self.target_offset - self.current_offset) / speed

        self.update_positions()

    def on_key_press(self, key, modifiers):
        if not self.rack:
            return

        # Move right
        if key == arcade.key.RIGHT:
            self.current_index = (self.current_index + 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        # Move left
        elif key == arcade.key.LEFT:
            self.current_index = (self.current_index - 1) % len(self.rack)
            self.target_offset = self.current_index * SPACING

        # Buy item
        elif key == arcade.key.SPACE:
            item = self.rack[self.current_index]

            if item.price > self.money:
                self.message = "Not enough money!"
                return

            # Purchase
            self.money -= item.price
            profit = item.value - item.price
            self.score += profit

            self.message = f"Profit: {profit}"

            # Remove item
            self.sprite_list.remove(item.sprite)
            self.rack.pop(self.current_index)

            # Add new item at end
            new_item = ThriftItem()
            self.rack.append(new_item)
            self.sprite_list.append(new_item.sprite)

            # Fix index
            if self.current_index >= len(self.rack):
                self.current_index = 0

            self.target_offset = self.current_index * SPACING


def main():
    game = ThriftGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
