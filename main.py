import pygame
import cffi
import pymunk
# import ez_profile
# /// script
# dependencies = [
#  "pygame-ce",
#  "cffi",
#  "pymunk",
# ]
# ///

if __name__ == '__main__':
    import asyncio

    from src.engine.game import Game

    game = Game()
    asyncio.run(game.run())
