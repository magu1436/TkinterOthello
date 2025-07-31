
from tkinter import Frame, Misc

from boardgame import Coordinate

from display_items import SceneTransitionButton, Display
from objects import OthelloBoard
from game_manager import SpectatingManager, SpectatingManagerDisplay



class SpectatorDisplay(Frame):

    def __init__(self, master: Misc, grid_width: int):
        """コンストラクタ
        
        オセロボードと観戦マネージャー, サブディスプレイを生成して配置する.
        
        Args:
            master(Misc): マスター
            grid_width(int): ボードのグリッドの太さ"""
        master.update_idletasks()
        self.display_size: Coordinate = Coordinate(master.winfo_width(), master.winfo_height())
        super().__init__(
            master,
            width=self.display_size[0],
            height=self.display_size[1],
            name=Display.SPECTATOR,
        )

        self.othello_board = OthelloBoard(
            self,
            (self.display_size.y, self.display_size.y),
            grid_width
        )

        self.manager: SpectatingManager = SpectatingManager(self.othello_board)

        self.manager_display: SpectatingManagerDisplay = self.manager.create_manager_display(
            self,
            self.display_size - (self.othello_board.board_display_size.x, 0),
        )

        self.othello_board.pack(side="left")
        self.manager_display.pack(side="right")