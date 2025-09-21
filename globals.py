import sys

import pygame


class MyEvents:
    """Custom Pygame events.

    Attributes
    ----------
    LANDED : int
        Event ID signaling a successful landing.
    CRASHED : int
        Event ID signaling a crash landing.
    """

    LANDED = pygame.USEREVENT + 1
    CRASHED = pygame.USEREVENT + 2


class Settings:
    """Global game settings and physical constants."""

    WINDOW = pygame.rect.Rect(0, 0, 600, 800)
    FPS = 60
    DELTATIME = 1.0 / FPS
    HORIZON = 50

    # Physical constants (Moon conditions)
    MOON_GRAVITY = 1.62  # m/s²
    EARTH_GRAVITY = 9.81  # m/s²
    PIXELS_PER_METER = 10  # Scale: 1m = 10px
    GRAVITY = MOON_GRAVITY * PIXELS_PER_METER  # = 16.2 px/s²
    THRUST = -2.1 * PIXELS_PER_METER  # = -21 px/s² (upward acceleration)
    SAFE_SPEED_LANDING = 2.5 * PIXELS_PER_METER  # Safe landing speed in px/s

    LEVEL = {
        "easy": sys.maxsize,
        "fair": 500,
        "hard": 450,
        "ai": 280,
    }

