
from __future__ import annotations

from tkinter import Misc

from boardgame import Piece, Tile, BGEvent, Board
from systems import Color, CONFIG

OTHELLO_BOARD_SIZE = (8, 8)

BLACK_STONE_IMAGE = CONFIG["BLACK_STONE_IMAGE_PATH"]
WHITE_STONE_IMAGE = CONFIG["WHITE_STONE_IMAGE_PATH"]
PUTABLE_TILE_IMAGE = CONFIG["PUTABLE_TILE_IMAGE_PATH"]

BOARD_BACKGROUND_IMAGE_PATH = CONFIG["BOARD_BACKGROUND_IMAGE_PATH"]
FRAME_IMAGE_PATH = CONFIG["FRAME_IMAGE_PATH"]
GRID_IMAGE_PATH = CONFIG["GRID_IMAGE_PATH"]



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
        manager = event.board.master.manager
        stone = Stone(manager.turn_player.color)
        manager.put_stone(stone, event.coordinate)

class OthelloBoard(Board):

    def __init__(
            self, 
            master: Misc, 
            board_display_size: tuple[int, int], 
            grid_width: int,
        ):
        super().__init__(
            master, 
            OTHELLO_BOARD_SIZE, 
            BOARD_BACKGROUND_IMAGE_PATH,
            board_display_size,
            GRID_IMAGE_PATH,
            FRAME_IMAGE_PATH,
            grid_width,
            )
        self.init_board()
    
    def init_board(self):
        """石を初期配置するメソッド"""
        self.take_all_pieces()
        self.put(Stone.create(Color.WHITE), (OTHELLO_BOARD_SIZE[0] // 2 - 1, OTHELLO_BOARD_SIZE[1] // 2 - 1))
        self.put(Stone.create(Color.BLACK), (OTHELLO_BOARD_SIZE[0] // 2, OTHELLO_BOARD_SIZE[1] // 2 - 1))
        self.put(Stone.create(Color.BLACK), (OTHELLO_BOARD_SIZE[0] // 2 - 1, OTHELLO_BOARD_SIZE[1] // 2))
        self.put(Stone.create(Color.WHITE), (OTHELLO_BOARD_SIZE[0] // 2, OTHELLO_BOARD_SIZE[1] // 2))
