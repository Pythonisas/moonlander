"""Moonlander – Pygame demo project without bitmaps.

This module contains the game logic and rendering components for a
simplified *Moon Lander* game. It demonstrates how complete
sprites/user interfaces can be drawn using only Pygame primitives (lines,
circles, polygons) without relying on predefined bitmaps.

The implementation focuses on clarity and comprehensibility rather than
maximum efficiency or especially compact source code.

Classes
-------
MyEvents
    Custom Pygame events for landing/crash.
Settings
    Central constants and parameters.
Sky
    Starfield background.
Moon
    Foreground horizon/moon surface with mountain ranges.
Earth
    Rendered Earth in the sky (with polygon continents).
Lander
    Lunar lander module, physics and status display.
Question
    Simple overlay message after landing.
Game
    Game loop, event handling and scene setup.

Functions
---------
main()
    Starts the game.
"""

from time import time

import pygame

from background import Earth, Moon, Question, Sky
from globals import MyEvents, Settings
from mobs import Lander


class Game:
    """Main game class handling loop, events, updates, and drawing."""

    def __init__(self) -> None:
        """Initialize the game window and objects."""
        pygame.init()

        # Classic pygame "display" API for maximum compatibility
        self.screen = pygame.display.set_mode(Settings.WINDOW.size)
        pygame.display.set_caption("MyMoonlander")

        self.clock = pygame.time.Clock()
        self.landing = True

    def run(self) -> None:
        """Run the main game loop until exit."""
        self.restart()
        time_previous = time()
        while self.running:
            self.watch_for_events()
            self.update()
            if self.running:
                self.draw()
            self.clock.tick(Settings.FPS)

            # Update delta time dynamically
            time_current = time()
            Settings.DELTATIME = time_current - time_previous
            time_previous = time_current
        pygame.quit()

    def watch_for_events(self) -> None:
        """Handle Pygame events (quit, keys, land/crash events)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == MyEvents.LANDED:
                self.landing = False
                self.lander.update(mode="landed", velocity=event.volocity)
            elif event.type == MyEvents.CRASHED:
                self.landing = False
                self.lander.update(mode="crashed", velocity=event.volocity)
            elif event.type == pygame.KEYDOWN:
                if self.landing:
                    if event.key == pygame.K_SPACE:
                        self.lander.update(action="thrust")
                    elif event.key == pygame.K_h:
                        self.lander.update(action="toggle_ai")
                else:
                    if event.key == pygame.K_q:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.restart()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.lander.update(action="unthrust")

    def update(self) -> None:
        """Update scene objects and check landing state."""
        self.background.update()
        self.lander.update(action="move")
        self.check_landing()

    def draw(self) -> None:
        """Draw all game elements in order."""
        self.background.draw()
        self.moon.draw()
        self.earth.draw()
        self.lander.draw()
        if not self.landing:
            self.question.draw()
        pygame.display.flip()

    def restart(self) -> None:
        """Reset the game state for a new run."""
        self.landing = True
        self.background = Sky(self.screen)
        self.moon = Moon(self.screen)
        self.earth = Earth(self.screen)
        self.lander = Lander(self.screen)
        self.question = Question(self.screen)
        self.running = True

    def check_landing(self) -> None:
        """Check whether the lander has landed safely or crashed."""
        velocity = self.lander.get_velocity()
        if self.lander.is_landed():
            if velocity > Settings.SAFE_SPEED_LANDING:
                evt = pygame.event.Event(MyEvents.CRASHED, volocity=velocity)
                pygame.event.post(evt)
            else:
                evt = pygame.event.Event(MyEvents.LANDED, volocity=velocity)
                pygame.event.post(evt)


def main():
    """Entry point of the program."""
    Game().run()


if __name__ == "__main__":
    main()
