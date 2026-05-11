"""Fashionidísimitas home screen and window-style navigation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable, Optional

import arcade

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Fashionidísimitas"

UI_SCALE = SCREEN_WIDTH / 800

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
BACKGROUND_IMAGE = ASSETS_DIR / "home_background.png"

BUTTON_IMAGE_PATHS = {
    "settings": ASSETS_DIR / "settings_button.png",
    "social media": ASSETS_DIR / "social_media_button.png",
    "closet": ASSETS_DIR / "closet_button.png",
    "clothing store": ASSETS_DIR / "clothing_store_button.png",
    "activity center": ASSETS_DIR / "activity_center_button.png",
}

BUTTON_ACTIVE_IMAGE_PATHS = {
    "social media": ASSETS_DIR / "social_media_button_active.png",
}

def _scaled(value: float) -> float:
    return value * UI_SCALE


SIDE_BAR_X = _scaled(166)
SIDE_BAR_Y = _scaled(300)
SIDE_BAR_WIDTH = _scaled(282)
SIDE_BAR_HEIGHT = _scaled(410)

TOP_BAR_Y = SCREEN_HEIGHT - _scaled(34)

CONTENT_CARD_X = _scaled(585)
CONTENT_CARD_Y = _scaled(275)
CONTENT_CARD_WIDTH = _scaled(382)
CONTENT_CARD_HEIGHT = _scaled(316)

HOME_BUTTON_WIDTH = _scaled(60)
HOME_BUTTON_HEIGHT = _scaled(60)
HOME_BUTTON_LEFT = _scaled(40)
HOME_BUTTON_TOP = _scaled(452)
HOME_BUTTON_GAP = _scaled(12)
HOME_BUTTON_IMAGE_WIDTH = _scaled(42)
HOME_BUTTON_IMAGE_HEIGHT = _scaled(42)

PRESS_ANIMATION_TIME = 0.18
PRESS_SHRINK_SCALE = 0.86


def _current_time() -> float:
    """Return a monotonic timestamp for animation timing."""
    return time.perf_counter()


def _path_exists(path: Path) -> bool:
    return path.is_file()


def _make_sprite(
    image_path: Path,
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    fallback_color: arcade.Color,
) -> arcade.Sprite:
    """Load a sprite from disk when available, otherwise use a solid block."""
    if _path_exists(image_path):
        sprite = arcade.Sprite(str(image_path))
        sprite.center_x = center_x
        sprite.center_y = center_y
        sprite.width = width
        sprite.height = height
        return sprite

    sprite = arcade.SpriteSolidColor(int(width), int(height), fallback_color)
    sprite.center_x = center_x
    sprite.center_y = center_y
    return sprite


def _make_panel(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    fill_color: arcade.Color,
    alpha: int,
) -> arcade.Sprite:
    sprite = arcade.SpriteSolidColor(int(width), int(height), fill_color)
    sprite.center_x = center_x
    sprite.center_y = center_y
    sprite.alpha = alpha
    return sprite


class DrawableSprite:
    """Small wrapper that renders a single sprite through a SpriteList."""

    def __init__(self, sprite: arcade.Sprite) -> None:
        self._sprite = sprite
        self._sprite_list = arcade.SpriteList()
        self._sprite_list.append(sprite)

    def draw(self) -> None:
        self._sprite_list.draw()

    @property
    def sprite(self) -> arcade.Sprite:
        return self._sprite

    @property
    def center_x(self) -> float:
        return self._sprite.center_x

    @center_x.setter
    def center_x(self, value: float) -> None:
        self._sprite.center_x = value

    @property
    def center_y(self) -> float:
        return self._sprite.center_y

    @center_y.setter
    def center_y(self, value: float) -> None:
        self._sprite.center_y = value

    @property
    def width(self) -> float:
        return self._sprite.width

    @width.setter
    def width(self, value: float) -> None:
        self._sprite.width = value

    @property
    def height(self) -> float:
        return self._sprite.height

    @height.setter
    def height(self, value: float) -> None:
        self._sprite.height = value

    @property
    def scale(self) -> float:
        return self._sprite.scale

    @scale.setter
    def scale(self, value: float) -> None:
        self._sprite.scale = value

    @property
    def alpha(self) -> int:
        return self._sprite.alpha

    @alpha.setter
    def alpha(self, value: int) -> None:
        self._sprite.alpha = value

    def replace(self, sprite: arcade.Sprite) -> None:
        self._sprite = sprite
        self._sprite_list.clear()
        self._sprite_list.append(sprite)


@dataclass
class StatusBox:
    """Small HUD block for money, energy, or level."""

    label: str
    value: str
    center_x: float
    center_y: float
    width: float = _scaled(132)
    height: float = _scaled(42)
    fill_color: arcade.Color = arcade.color.DARK_SLATE_GRAY
    border_color: arcade.Color = arcade.color.WHITE
    accent_color: arcade.Color = arcade.color.DARK_SEA_GREEN

    def __post_init__(self) -> None:
        self.shadow = DrawableSprite(_make_panel(self.center_x + _scaled(3), self.center_y - _scaled(3), self.width, self.height, arcade.color.BLACK, 110))
        self.border = DrawableSprite(_make_panel(self.center_x, self.center_y, self.width + _scaled(4), self.height + _scaled(4), self.border_color, 255))
        self.panel = DrawableSprite(_make_panel(self.center_x, self.center_y, self.width, self.height, self.fill_color, 220))
        self.accent = DrawableSprite(_make_panel(self.center_x - self.width * 0.36, self.center_y, _scaled(4), self.height - _scaled(10), self.accent_color, 255))
        self.label_text = arcade.Text(
            self.label.upper(),
            self.center_x - self.width * 0.24,
            self.center_y + _scaled(9),
            arcade.color.LIGHT_GRAY,
            max(10, int(9 * UI_SCALE)),
            anchor_x="left",
            anchor_y="center",
        )
        self.value_text = arcade.Text(
            self.value,
            self.center_x - self.width * 0.24,
            self.center_y - _scaled(8),
            arcade.color.WHITE,
            max(15, int(15 * UI_SCALE)),
            anchor_x="left",
            anchor_y="center",
        )

    def draw(self) -> None:
        self.shadow.draw()
        self.border.draw()
        self.panel.draw()
        self.accent.draw()
        self.label_text.draw()
        self.value_text.draw()


class HomeButton:
    """A left-side navigation button with a press animation and two visual states."""

    def __init__(
        self,
        label: str,
        center_x: float,
        center_y: float,
        on_activate: Callable[[], None],
        active: bool = False,
    ) -> None:
        self.label = label
        self.center_x = center_x
        self.center_y = center_y
        self.on_activate = on_activate
        self.hit_width = HOME_BUTTON_WIDTH
        self.hit_height = HOME_BUTTON_HEIGHT
        self.press_started_at: Optional[float] = None
        self.pending_activation = False
        self.current_scale = 1.0
        self.normal_sprite = DrawableSprite(self._build_sprite(active=False))
        self.active_sprite = DrawableSprite(self._build_sprite(active=True))
        self.sprite = self.active_sprite if active else self.normal_sprite
        self.show_label = not _path_exists(BUTTON_IMAGE_PATHS[self.label])
        self.text = arcade.Text(
            label.title(),
            center_x,
            center_y,
            arcade.color.WHITE,
            max(12, int(12 * UI_SCALE)),
            anchor_x="center",
            anchor_y="center",
        )

    def _build_sprite(self, active: bool) -> arcade.Sprite:
        image_path = BUTTON_ACTIVE_IMAGE_PATHS.get(self.label) if active else BUTTON_IMAGE_PATHS[self.label]
        fallback_color = arcade.color.TAN if active else arcade.color.DARK_SLATE_BLUE
        sprite = _make_sprite(
            image_path if image_path is not None else BUTTON_IMAGE_PATHS[self.label],
            self.center_x,
            self.center_y,
            HOME_BUTTON_IMAGE_WIDTH,
            HOME_BUTTON_IMAGE_HEIGHT,
            fallback_color,
        )
        sprite.alpha = 230
        return sprite

    def set_active(self, is_active: bool) -> None:
        self.sprite = self.active_sprite if is_active else self.normal_sprite
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y
        self.sprite.scale = self.current_scale

    def hit_test(self, x: float, y: float) -> bool:
        return (
            abs(x - self.sprite.center_x) <= self.hit_width / 2
            and abs(y - self.sprite.center_y) <= self.hit_height / 2
        )

    def press(self, now: float) -> None:
        self.press_started_at = now
        self.pending_activation = True

    def update(self, dt: float, now: float) -> None:
        if self.press_started_at is None:
            self.current_scale += (1.0 - self.current_scale) * min(1.0, dt * 12)
        else:
            elapsed = now - self.press_started_at
            if elapsed < PRESS_ANIMATION_TIME / 2:
                self.current_scale = 1.0 - (1.0 - PRESS_SHRINK_SCALE) * (elapsed / (PRESS_ANIMATION_TIME / 2))
            elif elapsed < PRESS_ANIMATION_TIME:
                self.current_scale = PRESS_SHRINK_SCALE + (1.0 - PRESS_SHRINK_SCALE) * (
                    (elapsed - PRESS_ANIMATION_TIME / 2) / (PRESS_ANIMATION_TIME / 2)
                )
            else:
                self.current_scale = 1.0
                self.press_started_at = None
                if self.pending_activation:
                    self.pending_activation = False
                    self.on_activate()

        self.sprite.scale = self.current_scale

    def draw(self) -> None:
        self.sprite.draw()
        if self.show_label:
            self.text.font_size = max(11, int(15 * self.current_scale))
            self.text.draw()


class HomeView(arcade.View):
    """Main dashboard with button sprites and top status boxes."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.color.BLACK
        self.background_sprite = DrawableSprite(self._build_background_sprite())
        self.top_bar = DrawableSprite(_make_panel(SCREEN_WIDTH / 2, TOP_BAR_Y, SCREEN_WIDTH, _scaled(92), arcade.color.BLACK, 100))
        self.side_bar = DrawableSprite(_make_panel(SIDE_BAR_X, SIDE_BAR_Y, SIDE_BAR_WIDTH, SIDE_BAR_HEIGHT, arcade.color.DARK_SLATE_GRAY, 205))
        self.content_card = DrawableSprite(_make_panel(CONTENT_CARD_X, CONTENT_CARD_Y, CONTENT_CARD_WIDTH, CONTENT_CARD_HEIGHT, arcade.color.BLACK_OLIVE, 180))
        self.content_border = DrawableSprite(_make_panel(CONTENT_CARD_X, CONTENT_CARD_Y, CONTENT_CARD_WIDTH + 4, CONTENT_CARD_HEIGHT + 4, arcade.color.WHITE, 255))
        self.money_box = StatusBox("Money", "$120", _scaled(120), TOP_BAR_Y)
        self.energy_box = StatusBox("Energy", "85%", _scaled(320), TOP_BAR_Y)
        self.level_box = StatusBox("Level", "1", _scaled(520), TOP_BAR_Y, width=_scaled(108), accent_color=arcade.color.TAN)
        self.title_text = arcade.Text(
            "Fashionidísimitas",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - _scaled(165),
            arcade.color.WHITE,
            32,
            anchor_x="center",
            anchor_y="center",
        )
        self.subtitle_text = arcade.Text(
            "Choose a computer window to manage your influencer life.",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - _scaled(204),
            arcade.color.LIGHT_GRAY,
            15,
            anchor_x="center",
            anchor_y="center",
        )
        self.note_text = arcade.Text(
            "This MVP starts with empty screens so the team can build them later.",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - _scaled(241),
            arcade.color.LIGHT_GRAY,
            13,
            anchor_x="center",
            anchor_y="center",
        )
        self.buttons: list[HomeButton] = []
        self._pending_action: Optional[Callable[[], None]] = None
        self._build_buttons()

    def _build_background_sprite(self) -> arcade.Sprite:
        return _make_sprite(
            BACKGROUND_IMAGE,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            arcade.color.DARK_SLATE_GRAY,
        )

    def _build_buttons(self) -> None:
        labels = [
            "settings",
            "social media",
            "closet",
            "clothing store",
            "activity center",
        ]
        for index, label in enumerate(labels):
            center_y = HOME_BUTTON_TOP - index * (HOME_BUTTON_HEIGHT + HOME_BUTTON_GAP)
            button = HomeButton(label, HOME_BUTTON_LEFT + HOME_BUTTON_WIDTH / 2, center_y, self._make_open_action(label))
            self.buttons.append(button)

    def _make_open_action(self, label: str) -> Callable[[], None]:
        def open_window() -> None:
            def show_window() -> None:
                self.window.show_view(
                    ComputerWindowView(
                        title=label.title(),
                        home_view=self,
                        on_close=lambda: self._close_window(label),
                    )
                )

            self._pending_action = show_window

        return open_window

    def _set_button_active(self, label: str, is_active: bool) -> None:
        for button in self.buttons:
            if button.label == label:
                button.set_active(is_active)
                break

    def _close_window(self, label: str) -> None:
        if label == "social media":
            self._set_button_active(label, False)

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def on_draw(self) -> None:
        self.clear()
        self.background_sprite.draw()
        self.top_bar.draw()
        self.side_bar.draw()
        self.content_border.draw()
        self.content_card.draw()
        self.money_box.draw()
        self.energy_box.draw()
        self.level_box.draw()
        self.title_text.draw()
        self.subtitle_text.draw()
        self.note_text.draw()
        for button in self.buttons:
            button.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        now = _current_time()
        for nav_button in self.buttons:
            if nav_button.hit_test(x, y):
                if nav_button.label == "social media":
                    nav_button.set_active(True)
                nav_button.press(now)
                break

    def on_update(self, delta_time: float) -> None:
        now = _current_time()
        for nav_button in self.buttons:
            nav_button.update(delta_time, now)

        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            action()


class ComputerWindowView(arcade.View):
    """An empty computer-style window for the game sections."""

    def __init__(self, title: str, home_view: HomeView, on_close: Callable[[], None]) -> None:
        super().__init__()
        self.title = title
        self.home_view = home_view
        self.on_close = on_close
        self.window_width = _scaled(560)
        self.window_height = _scaled(390)
        self.window_x = SCREEN_WIDTH / 2
        self.window_y = SCREEN_HEIGHT / 2 - _scaled(8)
        self.close_button_x = self.window_x + self.window_width / 2 - _scaled(24)
        self.close_button_y = self.window_y + self.window_height / 2 - _scaled(21)

    def on_show_view(self) -> None:
        arcade.set_background_color(arcade.color.BLACK)

    def _close(self) -> None:
        self.on_close()
        self.window.show_view(self.home_view)

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)
        margin = _scaled(19)
        title_bar_height = _scaled(50)
        close_size = _scaled(13)
        arcade.draw_lrbt_rectangle_filled(margin, SCREEN_WIDTH - margin, margin, SCREEN_HEIGHT - margin, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_filled(
            self.window_x - self.window_width / 2,
            self.window_x + self.window_width / 2,
            self.window_y - self.window_height / 2,
            self.window_y + self.window_height / 2,
            arcade.color.BEIGE,
        )
        arcade.draw_lrbt_rectangle_outline(
            self.window_x - self.window_width / 2,
            self.window_x + self.window_width / 2,
            self.window_y - self.window_height / 2,
            self.window_y + self.window_height / 2,
            arcade.color.WHITE,
            3,
        )
        arcade.draw_lrbt_rectangle_filled(
            self.window_x - self.window_width / 2,
            self.window_x + self.window_width / 2,
            self.window_y + self.window_height / 2 - title_bar_height,
            self.window_y + self.window_height / 2 - 6,
            arcade.color.BLACK_OLIVE,
        )
        arcade.draw_text(
            self.title,
            self.window_x - self.window_width / 2 + _scaled(18),
            self.window_y + self.window_height / 2 - _scaled(38),
            arcade.color.WHITE,
            max(18, int(18 * UI_SCALE)),
            anchor_y="center",
        )
        arcade.draw_lrbt_rectangle_filled(
            self.close_button_x - close_size,
            self.close_button_x + close_size,
            self.close_button_y - close_size,
            self.close_button_y + close_size,
            arcade.color.RED_ORANGE,
        )
        arcade.draw_text(
            "x",
            self.close_button_x,
            self.close_button_y - _scaled(1),
            arcade.color.WHITE,
            max(18, int(18 * UI_SCALE)),
            anchor_x="center",
            anchor_y="center",
        )

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if (
            abs(x - self.close_button_x) <= _scaled(13)
            and abs(y - self.close_button_y) <= _scaled(13)
        ):
            self._close()

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            self._close()


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(HomeView())
    arcade.run()


if __name__ == "__main__":
    main()
