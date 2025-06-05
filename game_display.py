


from typing import Sequence, Callable
from tkinter import Frame, Misc, Canvas, Label, Button
import tkinter
from PIL import ImageTk, Image

from boardgame import Coordinate
from systems import Color, CONFIG
from text_object import AutoFontLabel


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
        self.label = Label(self, text=str(2), font=("", STONE_COUNT_FONT_SIZE))
        self.canvas.pack(side=tkinter.LEFT)
        self.label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    
    def update_counter(self, count: int):
        """表示枚数を更新するメソッド
        
        Args:
            count(int): 表示する枚数"""
        self.label["text"] = str(count)


class TurnPlayerDisplay(Label):

    def __init__(
            self,
            master: Misc,
            **kwargs
            ):
        super().__init__(
            master, 
            text=self.__create_display_label(""),
            font=("", TURN_PLAYER_NAME_FONT_SIZE),
            **kwargs
            )
    
    def __create_display_label(self, turn_player_name: str):
        return f"{turn_player_name}のターン"
    
    def update_player_name(self, player_name: str):
        self["text"] = self.__create_display_label(player_name)


class ManagerDisplay(Frame):
    
    def __init__(
            self,
            master: Misc,
            display_size: Sequence[int],
            redo_command: Callable[[], None],
    ):
        super().__init__(
            master,
            width=display_size[0],
            height=display_size[1],
        )
        self.display_size = Coordinate(display_size)
        self.turn_player_display = TurnPlayerDisplay(self)
        self.black_stone_counter = CounterDisplay(self, Color.BLACK, self.display_size // 2)
        self.white_stone_counter = CounterDisplay(self, Color.WHITE, self.display_size // 2)
        self.redo_button = Button(self, text=REDO_BUTTON_TEXT, command=redo_command)

        # 配置
        self.turn_player_display.grid(row=0, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        self.black_stone_counter.grid(row=1, column=0, sticky=tkinter.W+tkinter.E)
        self.white_stone_counter.grid(row=1, column=1, sticky=tkinter.W+tkinter.E)
        self.redo_button.grid(row=2, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)

        ##############################
        AutoFontLabel(self, "this is test text", display_width=self.display_size[0]).grid(row=3, column=0, columnspan=2)
        ################################

    def update_display(
            self,
            player_name: str,
            black_stone_count: int,
            white_stone_count: int
    ):
        self.turn_player_display.update_player_name(player_name)
        self.black_stone_counter.update_counter(black_stone_count)
        self.white_stone_counter.update_counter(white_stone_count)