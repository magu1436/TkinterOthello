


from typing import Sequence, Callable
from tkinter import Frame, Misc, Canvas
import tkinter
from tkinter.ttk import Button
from PIL import ImageTk, Image

from boardgame import Coordinate
from systems import Color, CONFIG, OthelloPlayer
from text_object import AutoFontLabel
from objects import OthelloBoard
from display_items import SceneTransitionButton, Display


TURN_PLAYER_NAME_FONT_SIZE = 50
STONE_COUNT_FONT_SIZE: int = 50

REDO_BUTTON_TEXT = "待った！！"


class CounterDisplay(Frame):
    """石の枚数を表示するディスプレイのクラス"""

    def __init__(
            self,
            master: Misc,
            color: Color,
            size: Sequence[int],
    ):
        """コンストラクタ
        
        Args:
            master(Misc): このフレームのマスター
            color(Color): このディスプレイが表示する石の枚数の色
            size(Sequence[int]): このディスプレイのサイズ
        """
        size = Coordinate(size)
        super().__init__(master, width=size.x, height=size.y)
        if color == Color.BLACK:
            image_path = CONFIG["BLACK_STONE_IMAGE_PATH"]
        else:
            image_path = CONFIG["WHITE_STONE_IMAGE_PATH"]
        canvas_size = size // 2
        self.canvas = Canvas(self, width=canvas_size.x, height=canvas_size.y)
        self.stone_image = ImageTk.PhotoImage(Image.open(image_path))
        self.canvas.create_image(size[0]//2, size[1]//2, image=self.stone_image)
        self.label = AutoFontLabel(self, str(2), canvas_size.x)
        self.canvas.pack(side=tkinter.LEFT)
        self.label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    
    def update_counter(self, count: int):
        """表示枚数を更新するメソッド
        
        Args:
            count(int): 表示する枚数"""
        self.label.set_text(str(count))


class TurnPlayerDisplay(AutoFontLabel):

    def __init__(
            self,
            master: Misc,
            display_width: int,
            **kwargs
            ):
        super().__init__(
            master,
            display_width=display_width,
            **kwargs
        )
    
    def __create_display_label(self, turn_player_name: str):
        return f"{turn_player_name}のターン"
    
    def update_player_name(self, player_name: str):
        self.set_text(self.__create_display_label(player_name))


class ManagerDisplay(Frame):
    """ゲーム画面の右側に表示するディスプレイ
    
    ターンプレイヤーの表示や現在の石の数を表示する.
    試合の決着時、画面遷移のボタンや新しいゲームを始めるボタンを追加する."""
    
    def __init__(
            self,
            master: Misc,
            display_size: Sequence[int],
            redo_command: Callable[[], None],
            game_reset_func: Callable[[], None]
    ):
        super().__init__(
            master,
            width=display_size[0],
            height=display_size[1],
        )
        self.display_size = Coordinate(display_size)
        self.turn_player_display = TurnPlayerDisplay(self, display_size[0])
        self.black_stone_counter = CounterDisplay(self, Color.BLACK, self.display_size // 2)
        self.white_stone_counter = CounterDisplay(self, Color.WHITE, self.display_size // 2)
        self.redo_button = Button(self, text=REDO_BUTTON_TEXT, command=redo_command)

        self.game_reset_func: Callable = game_reset_func

        # 配置
        self.turn_player_display.grid(row=0, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        self.black_stone_counter.grid(row=1, column=0, sticky=tkinter.W+tkinter.E)
        self.white_stone_counter.grid(row=1, column=1, sticky=tkinter.W+tkinter.E)
        self.redo_button.grid(row=2, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)

    def update_display(
            self,
            player_name: str,
            black_stone_count: int,
            white_stone_count: int
    ):
        """ディスプレイの情報を更新するメソッド
        
        ターンプレイヤーの名前と石の数を同時に更新する
        
        Args:
            player_name(str): ターンプレイヤー名
            black_stone_amount(int): 黒の石の数
            white_stone_count(int): 白の石の数
        """
        self.turn_player_display.update_player_name(player_name)
        self.black_stone_counter.update_counter(black_stone_count)
        self.white_stone_counter.update_counter(white_stone_count)
    
    def indicate_victory_scene(self, winner: OthelloPlayer | None):
        """勝利者とホームボタン及びニューゲームボタンを表示させるメソッド
        
        Args:
            winner(OthelloPlayer | None): 勝者. 引き分けなら`None`をいれる."""
        if winner is None:
            text = "引き分け！"
        else:
            text = winner.name + "の勝利！"
        self.winner_label = AutoFontLabel(
            self,
            text,
        )
        self.winner_label.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.home_button = SceneTransitionButton(
            self,
            "ホーム画面へ",
            Display.HOME,
            self.reset_game
        )
        self.home_button.grid(row=4, column=0, sticky="ew")

        self.new_game_button = Button(
            self, text="新しいゲーム", command=self.reset_game
        )
        self.new_game_button.grid(row=4, column=1, sticky="ew")
    
    def reset_game(self):
        self.game_reset_func()
        self.winner_label.destroy()
        self.home_button.destroy()
        self.new_game_button.destroy()


class GameDisplay(Frame):

    def __init__(self, master: Misc, grid_width: int):
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

        # redo関数はOthelloManagerが持つが、redoボタンはManagerDisplayが持つという矛盾
        self.manager_display: ManagerDisplay = ManagerDisplay(
            self,
            self.display_size - (self.othello_board.x, 0),

        )