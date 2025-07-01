

from tkinter import Frame, Misc, Canvas, Label
from tkinter.ttk import Button

from systems import CONFIG
from boardgame.imagetools import BoardGamePhotoImage
from display_items import SceneTransitionButton, Display
from history_display import HistoryDisplay


TITLE_LOGO_PADDING_RATIO_TO_DISPLAY = (.6, .2)
NEW_GAME_BUTTON_TEXT = "新しいゲーム！"
HISTORY_DISPLAY_BUTTON_TEXT = "履歴一覧"


class HomeDisplay(Frame):

    def __init__(self, master: Misc, game_display: Frame, history_display: HistoryDisplay):
        master.update_idletasks()
        display_size = (master.winfo_width(), master.winfo_height())
        super().__init__(master, width=display_size[0], height=display_size[1], name=Display.HOME.value)
        self.__title_logo_image = BoardGamePhotoImage(CONFIG["TITLE_LOGO_IMAGE_PATH"])
        self.__bg_image = BoardGamePhotoImage(CONFIG["HOME_BACKGROUND_IMAGE_PATH"])

        # バックグラウンドの配置
        self.__bg_image.resize(display_size)
        self.display_canvas = Canvas(self, width=display_size[0], height=display_size[1])
        self.display_canvas.create_image(
            0,
            0,
            image=self.__bg_image,
            anchor="nw"
        )
        self.display_canvas.place(x=0, y=0, anchor="nw")

        # タイトルロゴの配置
        title_logo_place = [
            length * ratio // 2 for length, ratio in zip(display_size, TITLE_LOGO_PADDING_RATIO_TO_DISPLAY)
        ]
        logo_ratio = (display_size[0] - 2 * title_logo_place[0]) / self.__title_logo_image.width()
        self.__title_logo_image.resize(
            [int(length * logo_ratio) for length in (self.__title_logo_image.width(), self.__title_logo_image.height())]
            )
        self.display_canvas.create_image(
            title_logo_place[0],
            title_logo_place[1],
            image=self.__title_logo_image,
            anchor="nw"
        )
        
        # 遷移ボタンの配置
        self.new_game_button = SceneTransitionButton(
            self, 
            NEW_GAME_BUTTON_TEXT,
            Display.GAME
        )
        self.history_display_button = SceneTransitionButton(
            self,
            HISTORY_DISPLAY_BUTTON_TEXT,
            Display.HISTORY,
            history_display.history_list.update
        )
        button_space_size = (
            self.__title_logo_image.width(),
            (display_size[1] - (title_logo_place[1] + self.__title_logo_image.height())) // 2
        )
        button_place = (
            display_size[0] // 2,
            title_logo_place[1] + self.__title_logo_image.height() + button_space_size[1] // 2
        )
        button_size = (
            button_space_size[0] * 2 // 3,
            button_space_size[1] * 2 // 3
        )
        self.new_game_button.place(
            x=button_place[0],
            y=button_place[1],
            width=button_size[0],
            height=button_size[1],
            anchor="center"
        )
        self.history_display_button.place(
            x=button_place[0],
            y=button_place[1] + button_space_size[1],
            width=button_size[0],
            height=button_size[1],
            anchor="center"
        )