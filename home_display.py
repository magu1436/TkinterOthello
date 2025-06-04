

from tkinter import Frame, Misc, Canvas, Label
from tkinter.ttk import Button

from systems import CONFIG
from boardgame.imagetools import BoardGamePhotoImage


TITLE_LOGO_PADDING_RATIO_TO_DISPLAY = (.6, .2)


class HomeDisplay(Frame):

    def __init__(self, master: Misc, game_display: Frame, history_display: Frame):
        master.update_idletasks()
        display_size = (master.winfo_width(), master.winfo_height())
        super().__init__(master, width=display_size[0], height=display_size[1])
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
        


class SceneTransitionButton(Button):

    def __init__(self, master: Misc, text: str, width: int, trans_from: Frame, trans_to: Frame):
        super().__init__(master, text=text, width=width, command=self.trans_display)
        self.trans_from: Frame = trans_from
        self.trans_to: Frame = trans_to
    
    def trans_display(self):
        """クリックされたときの処理
        
        もとの画面を非表示にして、遷移先の画面を表示にし、シーン遷移を表現する.
        
        TODO:
            処理の実装"""
        pass