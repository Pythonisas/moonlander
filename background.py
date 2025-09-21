from random import randint

import pygame

from continent_polygons import continent_polygons
from globals import Settings


class Sky:
    """Starfield background."""

    def __init__(self, screen: pygame.surface.Surface, star_count: int = 200) -> None:
        """Initialize the starfield.

        Parameters
        ----------
        screen : pygame.Surface
            Target surface to draw on.
        star_count : int, optional
            Number of stars, by default 200.
        """
        width = Settings.WINDOW.width
        height = Settings.WINDOW.height - Settings.HORIZON
        self.rect = pygame.rect.Rect(0, 0, width, height)
        self.screen = screen
        self.stars = [
            {
                "pos": (randint(2, self.rect.right - 1), randint(2, self.rect.bottom - 1)),
                "size": randint(1, 3),
                "duration": randint(200, 600),  # blinking duration in frames
                "counter": 0,
                "color": randint(10, 255),
            }
            for _ in range(star_count)
        ]

    def update(self) -> None:
        """Update star animation (blinking and size changes)."""
        for star in self.stars:
            star["counter"] = (star["counter"] + 1) % (star["duration"] + 1)
            if star["counter"] == 0:
                star["color"] = (star["color"] + randint(0, 70)) % 256
                star["size"] = (star["size"] + 1) % 4

    def draw(self) -> None:
        """Draw the starfield onto the target surface."""
        pygame.draw.rect(self.screen, "black", self.rect)
        for star in self.stars:
            pygame.draw.circle(self.screen, (255, 255, star["color"]), star["pos"], star["size"])


class Moon:
    """Moon horizon with layered mountain ranges."""

    def __init__(self, screen: pygame.surface.Surface, layer_count: int = 5, peaks: int = 35):
        """Initialize the moon surface.

        Parameters
        ----------
        screen : pygame.Surface
            Target surface to draw on.
        layer_count : int, optional
            Number of mountain layers, by default 5.
        peaks : int, optional
            Base number of peaks per layer, by default 35.
        """
        self.screen = screen
        self.surface = pygame.surface.Surface(
            (Settings.WINDOW.width, Settings.HORIZON + layer_count * 30), pygame.SRCALPHA
        )
        self.rect = self.surface.get_rect()
        self.rect.left = Settings.WINDOW.left
        self.rect.bottom = Settings.WINDOW.bottom
        landing_area = pygame.rect.Rect(
            0,
            self.rect.height - Settings.HORIZON,
            Settings.WINDOW.width,
            Settings.HORIZON,
        )

        # Generate mountain layers
        layers = []
        for layer_index in range(layer_count):
            peak_count = randint(peaks // 2, peaks)
            dist = landing_area.width // peak_count
            color_value = 180 - layer_index * 20
            y = landing_area.top - 10 - randint(5, 10) * layer_index
            x = landing_area.left
            lof_peaks = [(x, landing_area.top)]
            for _ in range(peak_count):
                lof_peaks.append((x, y + randint(-5, 20)))
                x += dist
            lof_peaks.append((landing_area.right, y))
            lof_peaks.append((landing_area.right, landing_area.top))

            poly = []
            for index in range(len(lof_peaks) - 1):
                p1 = lof_peaks[index]
                p2 = lof_peaks[index + 1]
                p3 = (lof_peaks[index + 1][0], landing_area.top)
                p4 = (lof_peaks[index][0], landing_area.top)
                r = randint(-5, 5)
                c = [color_value + r] * 3
                poly.append({"points": (p1, p2, p3, p4), "color": c})
            layers.append(poly)

        # Draw landing area
        pygame.draw.rect(self.surface, (230, 230, 230), landing_area)

        # Draw mountain layers from back to front for depth effect
        for layer in reversed(layers):
            for poly in layer:
                pygame.draw.polygon(self.surface, poly["color"], poly["points"])

    def draw(self):
        """Blit the pre-rendered moon surface onto the screen."""
        self.screen.blit(self.surface, self.rect.topleft)


class Earth:
    """Draws a stylized Earth in the sky."""

    def __init__(self, screen: pygame.surface.Surface) -> None:
        """Initialize the Earth surface.

        Parameters
        ----------
        screen : pygame.Surface
            Target surface to draw on.
        """
        self.radius = 80
        diameter = 2 * self.radius
        self.surface = pygame.surface.Surface((diameter, diameter), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.left = Settings.WINDOW.right - 200
        self.rect.top = Settings.WINDOW.top + 50
        self.screen = screen

        # Atmospheric glow
        for a in range(20, 1, -1):
            pygame.draw.circle(
                self.surface,
                (135, 206, 250, 210 - a * 10),  # increasing transparency
                (self.radius, self.radius),
                self.radius - 20 + a,
            )

        # Main ocean
        pygame.draw.circle(
            self.surface,
            (30, 144, 255),
            (self.radius, self.radius),
            self.radius - 20,
        )

        # Continents
        for landmass in continent_polygons:
            poly = [(self.radius + (0.5 * x), self.radius + (0.5 * y)) for (x, y) in landmass]
            pygame.draw.polygon(self.surface, (181, 150, 116), poly)

    def draw(self) -> None:
        """Blit the pre-rendered Earth graphic onto the screen."""
        self.screen.blit(self.surface, self.rect.topleft)


class Question:
    """Simple text overlay asking for quit or restart."""

    def __init__(self, screen: pygame.surface.Surface) -> None:
        """Initialize the question overlay.

        Parameters
        ----------
        screen : pygame.Surface
            Target surface to draw on.
        """
        self.font = pygame.font.Font(None, 24)
        self.screen = screen
        self.surface = self.font.render("(Q)uit or (R)estart?", True, "red")
        self.rect = self.surface.get_rect()
        self.rect.centerx = Settings.WINDOW.centerx
        self.rect.bottom = Settings.WINDOW.bottom - 10

    def draw(self) -> None:
        """Blit the overlay text to the screen."""
        self.screen.blit(self.surface, self.rect.topleft)

