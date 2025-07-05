


from tkinter import Frame, Misc, Canvas
import tkinter

from boardgame import Coordinate
from systems import Color, OthelloPlayer
from objects import OthelloBoard
from display_items import Display
from game_manager import GameManager, ManagerDisplay


class GameDisplay(Frame):
    """ゲームディスプレイ
    
    Attributes:
        display_size(Coordinate): 画面に表示される大きさ
        othello_board(OthelloBoard): オセロボード
        manager(GameManager): ゲームマネージャー
        manager_display(ManagerDisplay): サブディスプレイ"""

    def __init__(self, master: Misc, grid_width: int):
        """コンストラクタ

        オセロボードとゲームマネージャー、サブディスプレイも同時に生成して配置する.
        
        Args:
            master(Misc): マスター
            grid_width(int): ボードのグリッドの太さ
        """
        master.update_idletasks()
        self.display_size: Coordinate = Coordinate(master.winfo_width(), master.winfo_height())
        super().__init__(
            master,
            width=self.display_size[0],
            height=self.display_size[1],
            name=Display.GAME,
        )

        self.othello_board: OthelloBoard = OthelloBoard(
            self,
            (self.display_size.y, self.display_size.y),
            grid_width,
        )

        self.manager = GameManager(
            self.othello_board,
            (OthelloPlayer(Color.BLACK, "先手"), OthelloPlayer(Color.WHITE, "後手")),
        )

        self.manager_display: ManagerDisplay = self.manager.create_manager_display(
            self,
            self.display_size - self.othello_board.board_display_size,
        )
        self.manager.start_new_game()

        self.othello_board.pack(side=tkinter.LEFT)
        self.manager_display.pack(side=tkinter.LEFT)