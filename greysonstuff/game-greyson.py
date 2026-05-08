"""
FASHIONISTA — Grow Your Platform
A fashion influencer simulation game built with Python + Arcade.

Install:  pip install arcade
Run:      python social_sim.py

Controls:
  Space       — Open compose menu
  1-5         — Quick-pick post type in compose menu
  ESC         — Close compose menu
  Scroll      — Scroll feed
  Click       — Compose button / post type buttons
"""

import math
import random
from dataclasses import dataclass
from typing import List
from enum import Enum

import arcade

# ── Window ────────────────────────────────────────────────────────────────────
W, H  = 1100, 720
TITLE = "FASHIONISTA — Grow Your Platform"

SB_W = 290
FX   = SB_W + 12
FW   = W - SB_W - 22

# ── Moodboard palette ─────────────────────────────────────────────────────────
BG        = (255, 247, 242)
PANEL     = (230,  60, 110)
PANEL_LO  = (210,  40,  90)
CARD_BG   = (255, 255, 255)
CARD_VIR  = (255, 252, 225)
HOT_PINK  = (230,  40, 105)
PINK_LITE = (255, 210, 230)
LAVENDER  = (185, 145, 255)
CORAL     = (255, 115,  85)
MINT      = (100, 205, 170)
GOLD      = (210, 160,   0)
GOLD_BRT  = (255, 215,  55)
BLUSH     = (255, 190, 215)
BLACK     = ( 18,  10,  22)
DARK_ROSE = (130,  20,  65)
WHITE     = (255, 255, 255)
CREAM     = (255, 247, 242)
ROSE_GRAY = (195, 165, 178)
ROSE_DIV  = (245, 195, 215)

_PT_COLORS = {
    "MEME":     (230,  40, 105),
    "VIDEO":    (160, 110, 255),
    "ARTICLE":  (255, 110,  80),
    "OOTD":     ( 80, 195, 158),
    "HOT TAKE": (210, 160,   0),
}


# ── Text cache ────────────────────────────────────────────────────────────────
# arcade 4.x: draw_text() rebuilds a pyglet Label every call (very slow).
# arcade.Text objects cache the layout; we create them once and update props.
# The TextBatch assigns keys by (scope, call-order-within-scope) so each
# draw site gets a stable slot without needing explicit string keys at call sites.

class _TextBatch:
    def __init__(self):
        self._cache:    dict[str, arcade.Text] = {}
        self._counters: dict[str, int]          = {}
        self._used:     set[str]                = set()

    def begin_frame(self):
        self._counters.clear()
        self._used.clear()

    def draw(self, scope: str, text, x, y, color,
             size=13, bold=False, ax="left", ay="top"):
        idx = self._counters.get(scope, 0)
        self._counters[scope] = idx + 1
        key  = f"{scope}/{idx}"
        text = str(text)
        color = color if len(color) == 4 else (*color, 255)
        self._used.add(key)

        if key not in self._cache:
            self._cache[key] = arcade.Text(
                text, x, y, color,
                font_size=size, bold=bold, anchor_x=ax, anchor_y=ay,
            )
        else:
            t = self._cache[key]
            if t.text  != text:  t.text  = text
            if t.x     != x:     t.x     = x
            if t.y     != y:     t.y     = y
            if t.color != color: t.color = color

        self._cache[key].draw()

    def end_frame(self):
        for k in set(self._cache) - self._used:
            del self._cache[k]


TB = _TextBatch()


def txt(scope, text, x, y, color, size=13, bold=False, ax="left", ay="top"):
    TB.draw(scope, text, x, y, color, size, bold, ax, ay)


# ── Drawing helpers ───────────────────────────────────────────────────────────

def lerp_c(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def rect(x, y, w, h, color):
    arcade.draw_lbwh_rectangle_filled(x, y, w, h, color)

def rect_out(x, y, w, h, color, lw=1):
    arcade.draw_lbwh_rectangle_outline(x, y, w, h, color, lw)

def hline(x1, x2, y, color=ROSE_DIV):
    arcade.draw_line(x1, y, x2, y, color, 1)


# ── Post Types ────────────────────────────────────────────────────────────────

class PT(Enum):
    MEME     = ("MEME",     "✦", _PT_COLORS["MEME"],     0.30, 0.18,  90, "Relatable & shareable — high viral shot")
    VIDEO    = ("VIDEO",    "v", _PT_COLORS["VIDEO"],    0.20, 0.25, 120, "High effort, great growth if it lands")
    ARTICLE  = ("ARTICLE",  "#", _PT_COLORS["ARTICLE"],  0.08, 0.12, 150, "Slow burn — lowest viral, longest lasting")
    OOTD     = ("OOTD",     "o", _PT_COLORS["OOTD"],     0.12, 0.20,  80, "Reliable likes, rarely breaks through")
    HOT_TAKE = ("HOT TAKE", "*", _PT_COLORS["HOT TAKE"], 0.45, 0.08,  60, "Chaos mode — highest viral, most polarising")

    def __init__(self, label, icon, color, viral_chance, base_growth, max_age, desc):
        self.label        = label
        self.icon         = icon
        self.color        = color
        self.viral_chance = viral_chance
        self.base_growth  = base_growth
        self.max_age      = max_age
        self.desc         = desc


TEMPLATES: dict = {
    PT.MEME: [
        "me: i don't need more clothes. also me: *adds to cart*",
        "the fit is giving EVERYTHING today",
        "not me crying over a sample sale",
        "slay or nay? no wrong answers",
        "outfit of the day: chaotic neutral",
        "found this gem thrifting and i'm OBSESSED",
        "no thoughts, head full of fashion week",
    ],
    PT.VIDEO: [
        "come thrifting with me! (haul inside)",
        "styling one piece 5 different ways",
        "my entire wardrobe, ranked honestly",
        "get ready with me: editorial era",
        "trying every Y2K trend so you don't have to",
        "honest review: that viral skirt everyone has",
    ],
    PT.ARTICLE: [
        "why quiet luxury is dominating right now",
        "the return of Y2K: a full deep dive",
        "buy less, choose better — my journey",
        "what your wardrobe says about you",
        "the real cost of fast fashion (thread)",
        "how to build a capsule wardrobe from scratch",
    ],
    PT.OOTD: [
        "OOTD: thrift flip era",
        "golden hour fits are UNDEFEATED",
        "new jacket, new chapter",
        "summer girl era commencing",
        "pressed flowers + coquette = my aesthetic",
        "she who dresses well, lives well",
    ],
    PT.HOT_TAKE: [
        "ugg boots are back and i'm not mad about it",
        "fast fashion is a crisis and we all know it",
        "skinny jeans are coming back. controversial.",
        "your aesthetic doesn't have to be consistent",
        "designer labels don't equal style. i said it.",
        "thrifting is an art form, not a personality",
    ],
}

MILESTONES = [
    (500,     "Micro-Creator",   "your journey starts here"),
    (1_000,   "Nano-Influencer", "four figures — keep going"),
    (5_000,   "Rising Star",     "brands are watching now"),
    (10_000,  "Content Queen",   "you've made it to 10K"),
    (50_000,  "Fashion Icon",    "the industry knows your name"),
    (100_000, "IT GIRL STATUS",  "hall of fame. legendary."),
]


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Post:
    ptype: PT
    text: str
    quality: float

    likes: int     = 0
    shares: int    = 0
    comments: int  = 0
    age: float     = 0.0
    is_viral: bool     = False
    viral_mult: float  = 1.0
    viral_flash: float = 0.0
    dead: bool = False

    @property
    def engagement(self):
        return self.likes + self.shares * 3 + self.comments * 2

    @property
    def follower_rate(self):
        return self.engagement * self.quality * self.viral_mult * 0.004

    def tick(self, dt: float):
        self.age += dt
        if self.age >= self.ptype.max_age:
            self.dead = True
            return
        decay = max(0.05, 1.0 - self.age / self.ptype.max_age)
        rate  = self.ptype.base_growth * self.quality * decay * self.viral_mult
        if random.random() < rate * dt:
            self.likes    += random.randint(1, 15)
            self.shares   += random.randint(0,  4)
            self.comments += random.randint(0,  5)
        if self.viral_flash > 0:
            self.viral_flash = max(0.0, self.viral_flash - dt)


@dataclass
class Notif:
    text: str
    timer: float
    color: tuple


# ── Main window ───────────────────────────────────────────────────────────────

class Fashionista(arcade.Window):

    CARD_H = 128

    def __init__(self):
        super().__init__(W, H, TITLE)
        arcade.set_background_color(BG)

        self.followers:     int   = 100
        self.day:           int   = 1
        self.day_timer:     float = 0.0
        self.day_len:       float = 60.0
        self.energy:        int   = 10
        self.max_energy:    int   = 10
        self.posts_made:    int   = 0
        self.viral_count:   int   = 0
        self.total_likes:   int   = 0
        self.milestone_idx: int   = 0
        self._fol_frac:     float = 0.0

        self.posts:      List[Post]  = []
        self.notifs:     List[Notif] = []
        self.post_types: List[PT]    = list(PT)

        self.scroll:    int  = 0
        self.composing: bool = False
        self.hover_idx: int  = -1

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _gain_followers(self, n: int):
        self.followers += n
        while self.milestone_idx < len(MILESTONES):
            threshold, title, sub = MILESTONES[self.milestone_idx]
            if self.followers < threshold:
                break
            self._notif(f"* {title} — {sub}", GOLD_BRT)
            self.milestone_idx += 1
            self.max_energy = min(20, self.max_energy + 2)

    def _notif(self, text, color=BLACK):
        self.notifs.append(Notif(text, 3.5, color))
        if len(self.notifs) > 6:
            self.notifs.pop(0)

    # ── Update ────────────────────────────────────────────────────────────────

    def on_update(self, dt):
        dt = min(dt, 0.1)

        self.day_timer += dt
        if self.day_timer >= self.day_len:
            self.day_timer -= self.day_len
            self.day       += 1
            self.energy     = self.max_energy
            self._notif(f"Day {self.day} — energy restored, darling.", HOT_PINK)

        total_rate = 0.0
        for p in self.posts:
            p.tick(dt)
            if p.dead:
                continue
            if not p.is_viral and random.random() < p.ptype.viral_chance * dt:
                p.is_viral    = True
                p.viral_mult  = random.uniform(3.0, 9.0)
                p.viral_flash = 2.5
                self.viral_count += 1
                self._notif(
                    f"* Your {p.ptype.label} went VIRAL! ({p.viral_mult:.1f}x)",
                    GOLD,
                )
            total_rate += p.follower_rate

        self._fol_frac += total_rate * dt
        if self._fol_frac >= 1.0:
            gained          = int(self._fol_frac)
            self._fol_frac -= gained
            self._gain_followers(gained)

        if not self.posts and random.random() < 0.0005:
            self.followers = max(0, self.followers - 1)

        self.posts = [p for p in self.posts if not p.dead]
        self.total_likes = sum(p.likes for p in self.posts)

        for n in self.notifs:
            n.timer -= dt
        self.notifs = [n for n in self.notifs if n.timer > 0]

    # ── Post creation ─────────────────────────────────────────────────────────

    def _create_post(self, ptype: PT):
        if self.energy <= 0:
            self._notif("No energy left — wait for tomorrow", CORAL)
            return

        skill   = min(0.8, math.log10(max(10, self.followers)) / 6.0)
        alpha   = 1.0 + skill * 3.0
        beta    = max(1.2, 4.0 - skill * 2.0)
        quality = max(0.05, min(1.0, random.betavariate(alpha, beta)))

        text = random.choice(TEMPLATES[ptype])

        post = Post(ptype=ptype, text=text, quality=quality)
        self.posts.insert(0, post)
        self.posts    = self.posts[:20]
        self.posts_made += 1
        self.energy     -= 1
        self.scroll      = 0

        if quality > 0.70:
            qlabel, qc = "serving looks", MINT
        elif quality > 0.40:
            qlabel, qc = "pretty decent", GOLD
        else:
            qlabel, qc = "a little weak", CORAL

        self._notif(f"Posted  |  {qlabel}  ({quality:.0%})", qc)
        self.composing = False

    # ── Drawing ───────────────────────────────────────────────────────────────

    def on_draw(self):
        TB.begin_frame()
        self.clear()
        self._draw_sidebar()
        self._draw_feed()
        self._draw_notifs()
        if self.composing:
            self._draw_compose()
        TB.end_frame()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _draw_sidebar(self):
        # Two-tone pink background
        rect(0, H // 2, SB_W, H // 2, PANEL)
        rect(0, 0,       SB_W, H // 2, PANEL_LO)
        arcade.draw_line(SB_W, 0, SB_W, H, DARK_ROSE, 1)

        S = "sb"   # scope — every txt() in this function shares this scope
        y = H - 22

        txt(S, "* FASHIONISTA *", SB_W // 2, y, WHITE, 16, bold=True, ax="center")
        y -= 28
        hline(20, SB_W - 20, y, (*WHITE, 50))
        y -= 24

        # Followers
        f    = self.followers
        fstr = (f"{f / 1_000_000:.1f}M" if f >= 1_000_000
                else f"{f / 1_000:.1f}K"  if f >= 1_000
                else str(f))
        txt(S, "FOLLOWERS", SB_W // 2, y, BLUSH, 9, ax="center")
        y -= 18
        txt(S, fstr, SB_W // 2, y, WHITE, 36, bold=True, ax="center")
        y -= 46

        # Day + progress bar
        season   = (self.day - 1) // 7 + 1
        day_in_s = (self.day - 1) % 7 + 1
        txt(S, f"Season {season}  |  Day {day_in_s}", SB_W // 2, y, BLUSH, 10, ax="center")
        y -= 16
        bw   = SB_W - 40
        prog = self.day_timer / self.day_len
        rect(20, y - 8, bw, 8, (*WHITE, 40))
        rect(20, y - 8, max(2, int(bw * prog)), 8, WHITE)
        y -= 28

        # Energy pips (circles, not text)
        hline(20, SB_W - 20, y, (*WHITE, 50))
        y -= 18
        txt(S, "ENERGY", SB_W // 2, y, BLUSH, 9, ax="center")
        y -= 20
        pip_w = (SB_W - 40) / max(1, self.max_energy)
        for i in range(self.max_energy):
            c = GOLD_BRT if i < self.energy else (*WHITE, 40)
            arcade.draw_circle_filled(20 + (i + 0.5) * pip_w, y - 4, 6, c)
        y -= 28

        # Stats
        hline(20, SB_W - 20, y, (*WHITE, 50))
        y -= 22
        for label, val in [
            ("Posts Made",   str(self.posts_made)),
            ("Gone Viral",   str(self.viral_count)),
            ("Active Posts", str(len(self.posts))),
            ("Total Likes",  f"{self.total_likes:,}"),
        ]:
            txt(S, label, 22,        y, BLUSH, 10)
            txt(S, val,   SB_W - 22, y, WHITE, 11, bold=True, ax="right")
            y -= 22

        # Compose button
        rect(18, 30, SB_W - 36, 46, WHITE)
        rect_out(18, 30, SB_W - 36, 46, BLUSH, 1)
        txt(S, "+ POST",              SB_W // 2, 68, HOT_PINK, 16, bold=True, ax="center")
        txt(S, "Space or click here", SB_W // 2, 16, BLUSH,     8,            ax="center")

    # ── Feed ──────────────────────────────────────────────────────────────────

    def _draw_feed(self):
        txt("feed", "* YOUR FEED", FX + 4, H - 18, ROSE_GRAY, 11, bold=True)
        hline(FX, W - 10, H - 30, ROSE_DIV)

        if not self.posts:
            txt("feed", "No posts yet.",                           FX + FW // 2, H // 2 + 20, ROSE_GRAY, 16, ax="center")
            txt("feed", "Press Space to publish your first post.", FX + FW // 2, H // 2 -  8, ROSE_GRAY, 12, ax="center")
            return

        y = H - 48 + self.scroll
        for slot, post in enumerate(self.posts):
            ch = self.CARD_H
            if y - ch > H + 5:
                y -= ch + 10
                continue
            if y < -10:
                break
            self._draw_card(post, FX + 2, y - ch, FW - 4, ch, slot)
            y -= ch + 10

    def _draw_card(self, post: Post, x, y, w, h, slot: int):
        scope = f"c{slot}"
        pc    = post.ptype.color

        # Background
        if post.viral_flash > 0:
            t  = (post.viral_flash % 0.5) / 0.5
            bg = lerp_c(CARD_BG, CARD_VIR, t)
        else:
            bg = CARD_VIR if post.is_viral else CARD_BG
        rect(x, y, w, h, bg)
        rect_out(x, y, w, h, lerp_c(pc, WHITE, 0.55), 1)

        # Top colour strip
        strip_h = 5
        rect(x, y + h - strip_h, w, strip_h, pc)

        # Post-type label
        txt(scope, f"{post.ptype.icon}  {post.ptype.label}",
            x + 14, y + h - strip_h - 10, pc, 11, bold=True)

        # Viral badge
        if post.is_viral:
            rect(x + w - 72, y + h - strip_h - 22, 66, 18, GOLD)
            txt(scope, "* VIRAL *",
                x + w - 39, y + h - strip_h - 20, BLACK, 9, bold=True, ax="center")
        else:
            # Consume the slot so card scope counter stays stable
            txt(scope, "", 0, 0, (*BLACK, 0), 1)

        # Quality bar
        rect(x + 14, y + h - strip_h - 26, w - 28, 3,
             lerp_c(CORAL, MINT, post.quality))

        # Post text
        short = post.text[:72] + ("..." if len(post.text) > 72 else "")
        txt(scope, short, x + 14, y + h - strip_h - 38, BLACK, 13)

        # Divider + engagement
        hline(x + 14, x + w - 14, y + 34, ROSE_DIV)
        for icon, val in [("<3", post.likes), ("RT", post.shares), ("//", post.comments)]:
            txt(scope, f"{icon} {val:,}", x + 16 + [0, 95, 190][["<3","RT","//"].index(icon)],
                y + 16, ROSE_GRAY, 11)

        # Lifetime bar
        remaining = max(0.0, 1.0 - post.age / post.ptype.max_age)
        rect(x, y, w, 4, ROSE_DIV)
        rect(x, y, int(w * remaining), 4, lerp_c(CORAL, pc, remaining))

    # ── Compose overlay ───────────────────────────────────────────────────────

    def _draw_compose(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, W, H, (*PINK_LITE, 160))

        mw, mh = 640, 450
        mx     = W // 2 - mw // 2
        my     = H // 2 - mh // 2

        rect(mx, my, mw, mh, WHITE)
        rect_out(mx, my, mw, mh, HOT_PINK, 2)
        rect(mx, my + mh - 56, mw, 56, HOT_PINK)

        txt("cmp", "* CHOOSE YOUR VIBE *",
            W // 2, my + mh - 16, WHITE, 19, bold=True, ax="center")
        txt("cmp", "click a button  or  press 1-5  |  ESC to cancel",
            W // 2, my + mh - 40, BLUSH, 10, ax="center")

        n       = len(self.post_types)
        btn_h   = 56
        gap     = 8
        total   = n * btn_h + (n - 1) * gap
        start_y = my + mh - 56 - 16 + total // 2 - total + btn_h

        for i, pt in enumerate(self.post_types):
            scope = f"cb{i}"
            bx = mx + 20
            by = start_y + (n - 1 - i) * (btn_h + gap)
            bw = mw - 40

            hover    = (self.hover_idx == i)
            bg       = lerp_c(WHITE, pt.color, 0.12) if hover else WHITE
            border_c = pt.color if hover else lerp_c(pt.color, WHITE, 0.5)

            rect(bx, by, bw, btn_h, bg)
            rect_out(bx, by, bw, btn_h, border_c, 2 if hover else 1)
            rect(bx, by, 36, btn_h, lerp_c(pt.color, WHITE, 0.3))

            txt(scope, str(i + 1),
                bx + 18, by + btn_h - 16, pt.color, 18, bold=True, ax="center")
            txt(scope, f"{pt.icon}  {pt.label}",
                bx + 50, by + btn_h - 16, BLACK, 14, bold=True)
            txt(scope,
                f"Viral: {pt.viral_chance:.0%}  |  Growth: {pt.base_growth:.0%}"
                f"  |  Lifetime: {pt.max_age}s  |  {pt.desc}",
                bx + 50, by + 10, ROSE_GRAY, 9)

    # ── Notifications ─────────────────────────────────────────────────────────

    def _draw_notifs(self):
        y = 80
        for i, n in enumerate(reversed(self.notifs[-5:])):
            alpha    = int(min(1.0, n.timer) * 255)
            bg_alpha = int(min(1.0, n.timer) * 180)
            tw       = len(n.text) * 7 + 24
            rect(W - tw - 14, y - 4, tw + 4, 22, (*PINK_LITE, bg_alpha))
            txt(f"ntf{i}", n.text, W - 16, y, (*n.color[:3], alpha), 12, ax="right")
            y += 26

    # ── Input ─────────────────────────────────────────────────────────────────

    def on_key_press(self, key, mod):
        if key == arcade.key.ESCAPE:
            self.composing = False
            return
        if key == arcade.key.SPACE and not self.composing:
            self.composing = True
            return
        if self.composing:
            mapping = {
                arcade.key.KEY_1: 0, arcade.key.KEY_2: 1, arcade.key.KEY_3: 2,
                arcade.key.KEY_4: 3, arcade.key.KEY_5: 4,
            }
            if key in mapping and mapping[key] < len(self.post_types):
                self._create_post(self.post_types[mapping[key]])
            return
        if key == arcade.key.UP:
            self.scroll = max(0, self.scroll - 100)
        elif key == arcade.key.DOWN:
            self.scroll = min(len(self.posts) * (self.CARD_H + 10), self.scroll + 100)

    def on_mouse_press(self, x, y, button, mod):
        if self.composing:
            idx = self._compose_hit(x, y)
            if idx >= 0:
                self._create_post(self.post_types[idx])
        else:
            if 18 <= x <= SB_W - 18 and 30 <= y <= 76:
                self.composing = True

    def on_mouse_motion(self, x, y, dx, dy):
        self.hover_idx = self._compose_hit(x, y) if self.composing else -1

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll = max(0, self.scroll - int(scroll_y * 35))

    def _compose_hit(self, x, y) -> int:
        mw, mh  = 640, 450
        mx      = W // 2 - mw // 2
        my      = H // 2 - mh // 2
        n       = len(self.post_types)
        btn_h, gap = 56, 8
        total   = n * btn_h + (n - 1) * gap
        start_y = my + mh - 56 - 16 + total // 2 - total + btn_h
        for i in range(n):
            bx = mx + 20
            by = start_y + (n - 1 - i) * (btn_h + gap)
            bw = mw - 40
            if bx <= x <= bx + bw and by <= y <= by + btn_h:
                return i
        return -1


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    game = Fashionista()
    arcade.run()
