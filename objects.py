
from __future__ import annotations

from tkinter import Event

from boardgame import Piece, Tile, BGEvent
from systems import Color, CONFIG


BLACK_STONE_IMAGE = CONFIG["BLACK_STONE_IMAGE_PATH"]
WHITE_STONE_IMAGE = CONFIG["WHITE_STONE_IMAGE_PATH"]
PUTABLE_TILE_IMAGE = CONFIG["PUTABLE_TILE_IMAGE_PATH"]



class Stone(Piece):

    def __init__(self, color: Color):
        if color == Color.BLACK:
            stone_img = BLACK_STONE_IMAGE
        else:
            stone_img = WHITE_STONE_IMAGE
        super().__init__(stone_img)
        self.color = color
    
    @staticmethod
    def create(color: Color) -> Stone:
        return Stone(color)


class PutableSpaceTile(Tile):

    def __init__(self):
        super().__init__(
            PUTABLE_TILE_IMAGE,
            left_clicked_func=self.execute_put_stone,
        )
    
    def execute_put_stone(self, event: BGEvent):
        manager = event.board.master
        stone = Stone(manager.turn_player.color)
        manager.put_stone(stone, event.coordinate)
