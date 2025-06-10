from tkinter import Frame, Label, Listbox, Button
import tkinter as tk

from display_items import SceneTransitionButton, Display
from history import DBController

HOME_DISPLAY_BUTTON_TEXT = "ホームへ"
RESTORE_HISTORY_BUTTON_TEXT = "復元"
DELETE_HISTORY_BUTTON_TEXT = "削除"


class HistoryDisplay(Frame):
    """履歴一覧画面"""

    def __init__(self, master):
        super().__init__(name=Display.HISTORY.value)

        # home画面へ遷移するボタンの作成
        self.home_display_button = SceneTransitionButton(
            self,
            HOME_DISPLAY_BUTTON_TEXT,
            Display.HOME
        )

        # リストボックスの作成
        self.history_list = HistoryList(self)

        # restoreボタンとdeleteボタンの作成
        self.history_controll_frame = HistoryControllFrame(self)

        # ウィジェットの配置
        self.home_display_button.pack()
        self.history_list.pack()
        self.history_controll_frame.pack()


class HistoryList(Listbox):
    """履歴を表示するリストボックス"""

    selected = None
    
    def __init__(self, master):
        super().__init__(master)

        self.show_indexes()

    def show_indexes(self):
        """データベースからindexを取得し、listboxに表示するメソッド
        """
        # indexの取得
        all_index = DBController.get_all_indexes()

        # listboxにindexを表示
        for index in all_index:
            self.insert(0, index)


class HistoryControllFrame(Frame):
    """restoreボタンとdeleteボタンをもつFrame"""

    def __init__(self, master):
        super().__init__(master)

        restore_button = Button(self, text=RESTORE_HISTORY_BUTTON_TEXT)
        delete_button = Button(self, text=DELETE_HISTORY_BUTTON_TEXT)

        restore_button.pack(side=tk.LEFT)
        delete_button.pack(side=tk.RIGHT)