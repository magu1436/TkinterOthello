
from __future__ import annotations

from tkinter import Event

from boardgame import Piece, Tile
from systems import Color, load_config


BLACK_STONE_IMAGE = load_config()["BLACK_STONE_IMAGE_PATH"]
WHITE_STONE_IMAGE = load_config()["WHITE_STONE_IMAGE_PATH"]
PUTABLE_TILE_IMAGE = load_config()["PUTABLE_TILE_IMAGE_PATH"]



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
    
    def execute_put_stone(self, othello_board , event: Event):
        manager = othello_board.master
        stone = Stone(manager.turn_player.color)
        coor = othello_board.get_board_coor_from_tkcoor_in_board((event.x, event.y))
        manager.put_stone(stone, coor)
