from typing import Any

import pygame

from globals import Settings


class Lander:
    """Lunar lander module with drawing, physics and status display."""

    def __init__(self, screen: pygame.surface.Surface) -> None:
        """Initialize the lander.

        Parameters
        ----------
        screen : pygame.Surface
            Reference to the main game display surface.
        """
        self.screen = screen
        self.surface = pygame.surface.Surface((90, 81), pygame.SRCALPHA)
        self.surface_thrusting = pygame.surface.Surface((90, 81), pygame.SRCALPHA)

        # pygame-ce has Surface.get_frect(); classic pygame typically has get_rect().
        # Use get_rect() for broad compatibility.
        self.rect = self.surface.get_rect()

        self.rect.centerx = Settings.WINDOW.centerx  # horizontal start position
        self.rect.top = self.rect.height  # vertical start position

        self.create_lander()               # draw the base lander
        self.create_lander_thrusting()     # draw the flame variant

        self.mode = "landing"              # "landing", "landed", "crashed"
        self.thrusting = False             # whether thrust is active
        self.velocity = 0                  # vertical velocity
        self.fuel_initial = Settings.LEVEL["fair"]  # initial fuel
        self.fuel = self.fuel_initial      # current fuel
        self.fuel_consumption = 20         # fuel consumption per second
        self.ai = False                    # autopilot flag

    def create_lander(self) -> None:
        """Draw the base lander graphic (without flame)."""
        cx = self.rect.width // 2
        cy = self.rect.height // 2
        s = self.rect.width // 2
        sur = self.surface

        # Antenna
        pygame.draw.line(sur, (220, 220, 220), (cx, cy - s // 2), (cx, cy - s // 1.2), 2)
        pygame.draw.circle(sur, (255, 255, 255), (cx, cy - s // 1.2), 3)

        # Crew module
        pygame.draw.polygon(
            sur,
            (160, 160, 160),
            [
                (cx - s // 4, cy - s // 2),
                (cx - s // 6, cy - s // 3),
                (cx + s // 6, cy - s // 3),
                (cx + s // 4, cy - s // 2),
            ],
        )

        # Connectors
        conn_color = (160, 160, 160)
        pygame.draw.line(sur, conn_color, (cx - s // 3, cy), (cx - s // 6, cy - s // 3), 2)
        pygame.draw.line(sur, conn_color, (cx, cy), (cx, cy - s // 3), 2)
        pygame.draw.line(sur, conn_color, (cx + s // 3, cy), (cx + s // 6, cy - s // 3), 2)

        # Main capsule
        pygame.draw.polygon(
            sur,
            (200, 200, 200),
            [
                (cx - s // 3, cy),
                (cx - s // 2, cy + s // 2),
                (cx + s // 2, cy + s // 2),
                (cx + s // 3, cy),
            ],
        )

        # Windows
        r = 5
        window_color = (50, 50, 50)
        pygame.draw.circle(sur, window_color, (cx, cy + (s // 4)), r)
        pygame.draw.circle(sur, window_color, (cx - (s // 4), cy + (s // 4)), r)
        pygame.draw.circle(sur, window_color, (cx + (s // 4), cy + (s // 4)), r)

        # Landing legs
        leg_color = (100, 100, 100)
        pygame.draw.line(sur, leg_color, (cx - s // 2, cy + s // 2), (cx - s, cy + s), 3)
        pygame.draw.line(sur, leg_color, (cx + s // 2, cy + s // 2), (cx + s, cy + s), 3)
        pygame.draw.line(sur, leg_color, (cx - s // 4, cy + s // 2), (cx - s // 3, cy + s), 3)
        pygame.draw.line(sur, leg_color, (cx + s // 4, cy + s // 2), (cx + s // 3, cy + s), 3)

        # Feet
        feet_color = (150, 150, 150)
        pygame.draw.circle(sur, feet_color, (cx - s + (r + 2), cy + s - (r + 2)), r - 1)
        pygame.draw.circle(sur, feet_color, (cx + s - (r + 2), cy + s - (r + 2)), r - 1)
        pygame.draw.circle(sur, feet_color, (cx - s // 3 + (r - 4), cy + s - (r + 2)), r - 1)
        pygame.draw.circle(sur, feet_color, (cx + s // 3 - (r - 4), cy + s - (r + 2)), r - 1)

    def create_lander_thrusting(self) -> None:
        """Create the variant of the lander with a thrust flame."""
        cx = self.rect.width // 2
        cy = self.rect.height // 2
        s = self.rect.width // 2
        sur = self.surface

        # Copy base lander
        self.surface_thrusting.blit(sur, (0, 0))

        # Flame polygon
        pygame.draw.polygon(
            self.surface_thrusting,
            (255, 140, 0),
            [
                (cx - 5, cy + s // 2),
                (cx + 5, cy + s // 2),
                (cx, cy + s // 2 + 20),
            ],
        )

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update the lander state depending on actions and mode.

        Supported kwargs
        ----------------
        action : str
            "thrust", "unthrust", "toggle_ai", or "move".
        mode : str
            "landing", "landed", or "crashed".
        """
        if "action" in kwargs:
            if kwargs["action"] == "thrust":
                self.thrust(True)
            elif kwargs["action"] == "unthrust":
                self.thrust(False)
            elif kwargs["action"] == "toggle_ai":
                self.ai = not self.ai   # Toggle autopilot
                if not self.ai:
                    self.thrust(False)
            elif kwargs["action"] == "move":
                if self.mode == "landing":
                    if self.ai:  # autopilot active
                        self.controler()
                    self.move()

        if "mode" in kwargs:
            self.mode = kwargs["mode"]
            if self.mode in ("landed", "crashed"):
                self.thrust(False)

    def controler(self):
        """Autopilot logic for safe deceleration before landing."""
        if self.mode in ("landed", "crashed"):
            # Landing already finished
            self.thrust(False)
            return

        # Net acceleration (gravity + thrust)
        acc = -1 * (Settings.THRUST + Settings.GRAVITY)
        v_save = Settings.SAFE_SPEED_LANDING * 0.5  # safety buffer
        if self.velocity <= v_save:
            # Already slow enough
            self.thrust(False)
            return

        # Compute required braking distance
        brake_distance = self.velocity ** 2 / (2 * acc)
        ground_distance = (Settings.WINDOW.height - 50) - self.rect.bottom

        # Enable thrust if braking distance exceeds remaining height
        self.thrust(ground_distance <= brake_distance)

    def thrust(self, thrusting: bool) -> None:
        """Toggle thrust, consuming fuel if available."""
        self.thrusting = thrusting and self.fuel > 0

    def draw(self) -> None:
        """Draw the lander and its HUD."""
        if self.thrusting:
            self.screen.blit(self.surface_thrusting, self.rect.topleft)
        else:
            self.screen.blit(self.surface, self.rect.topleft)
        self.draw_status()

    def draw_status(self) -> None:
        """Draw a simple status HUD onto the main display surface."""
        # Compute height above ground
        h = -1 * (self.rect.bottom - (Settings.WINDOW.bottom - Settings.HORIZON))

        font = pygame.font.SysFont("Consolas", 14, bold=True)

        # Background panel
        panel_rect = pygame.rect.Rect(5, 5, 300, 80)
        panel_color = "darkgrey" if self.ai else "black"
        pygame.draw.rect(self.screen, panel_color, panel_rect)
        pygame.draw.rect(self.screen, "grey", panel_rect, 1)

        labels = "Max speed (m/s):\nSpeed (m/s):\nHeight (m):"
        values = (
            f"{Settings.SAFE_SPEED_LANDING/Settings.PIXELS_PER_METER:>7.2f}\n"
            f"{self.velocity/Settings.PIXELS_PER_METER:>7.2f}\n"
            f"{h/Settings.PIXELS_PER_METER:>7.2f}"
        )

        text_labels = font.render(labels, True, "white")
        text_values = font.render(values, True, "white")

        self.screen.blit(text_labels, (10, 10))
        self.screen.blit(text_values, (235, 10))

        # Mode
        if self.mode == "landed":
            mode_color = "green"
        elif self.mode == "crashed":
            mode_color = "red"
        else:
            mode_color = "white"
        text_mode = font.render(f"Status: {self.mode}", True, mode_color)
        self.screen.blit(text_mode, (10, 65))

        # Fuel bar
        bar_bg = pygame.rect.Rect(5, 90, 300, 12)
        pygame.draw.rect(self.screen, "grey", bar_bg)
        ratio = 0
        if self.fuel_initial:
            ratio = int(bar_bg.width * self.fuel / self.fuel_initial)
        pygame.draw.rect(self.screen, "green", (bar_bg.left, bar_bg.top, ratio, bar_bg.height))
        if self.thrusting:
            pygame.draw.rect(
                self.screen,
                (255, 140, 0),
                (bar_bg.left, bar_bg.top, ratio, bar_bg.height),
                1,
            )

    def move(self) -> None:
        """Integrate lander motion for one frame."""
        if self.thrusting and self.fuel > 0:
            self.velocity += Settings.THRUST * Settings.DELTATIME
            self.fuel -= self.fuel_consumption * Settings.DELTATIME
            if self.fuel < 0:
                self.thrusting = False
                self.fuel = 0

        # Gravity
        self.velocity += Settings.GRAVITY * Settings.DELTATIME
        self.rect.top += self.velocity * Settings.DELTATIME

        # Clamp to ground
        if self.rect.bottom >= Settings.WINDOW.bottom - Settings.HORIZON:
            self.rect.bottom = Settings.WINDOW.bottom - Settings.HORIZON

    def get_velocity(self) -> float:
        """Return the current vertical velocity."""
        return self.velocity

    def is_landed(self) -> bool:
        """Check whether the lander has reached the ground."""
        return self.rect.bottom >= Settings.WINDOW.bottom - Settings.HORIZON
