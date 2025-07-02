from tkinter import Frame, Label, Listbox, Button
import tkinter as tk

from display_items import SceneTransitionButton, Display
from history import DBController, History

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
            Display.HOME,
        )

        # リストボックスの作成
        self.history_list = HistoryList(self)

        # restoreボタンとdeleteボタンの作成
        self.history_controll_frame = HistoryControllFrame(self, self.history_list)

        # ウィジェットの配置
        self.home_display_button.pack()
        self.history_list.pack()
        self.history_controll_frame.pack()


class HistoryList(Listbox):
    """履歴を表示するリストボックス"""

    selected = None
    uuid_list = []
    
    def __init__(self, master):
        super().__init__(master, width=50, height=30, justify=tk.CENTER)

        # listbox内にindexを表示
        self.show_indexes()

    def show_indexes(self):
        """データベースからindexを取得し、listboxに表示するメソッド
        """
        # indexデータの取得
        all_index = DBController.get_all_indexes()

        # indexデータからtitleとis_finishedを抜き出す
        for uuid, title, is_finished in all_index:

            # uuidはuuid_listに保存
            self.uuid_list.append(uuid)

            # is_finishedが1のとき、"済"と表示する
            if is_finished:
                is_finished_str = "済"
            # is_finishedが0のとき、"未"と表示する
            else:
                is_finished_str = "未"

            # listboxに表示する文字列を作成
            index_str = f"{title} {is_finished_str}"

            # 文字列の追加
            self.insert(tk.END, index_str)     

    def get_listbox_index(self) -> int:
        """listboxで選択中のデータのindexを取得するメソッド
        """
        return self.curselection()[0]

    def update(self):
        """listboxの表示を更新するメソッド
        """
        # listboxに表示されている全項目の削除
        self.delete(0, tk.END)

        # listboxにindexを再表示
        self.show_indexes()

class HistoryControllFrame(Frame):
    """restoreボタンとdeleteボタンをもつFrame"""

    def __init__(self, master, history_list: HistoryList):
        self.history_list = history_list
        super().__init__(master)

        restore_button = RestoreButton(self, self.history_list)
        delete_button = DeleteButton(self, self.history_list)

        restore_button.pack(side=tk.LEFT)
        delete_button.pack(side=tk.RIGHT)


class RestoreButton(SceneTransitionButton):
    """restoreボタン"""

    def __init__(self, master, history_list: HistoryList):
        self.history_list = history_list
        super().__init__(master, RESTORE_HISTORY_BUTTON_TEXT, Display.SPECTATOR)
        self["command"] = self.trans_display

    def restore_selected_history(self) -> History:
        """履歴の復元を行うメソッド
        
        DBcontroller.restore()でデータベースから履歴を取得し、復元を行う
        """

        # indexを元に削除するデータのuuidを取得
        uuid = self.history_list.uuid_list[self.history_list.get_listbox_index()]

        # データベース上から対象となる履歴を取得
        return DBController.restore(uuid)
    
    def trans_display(self):
        is_finished = self.restore_selected_history().is_finished
        if is_finished:
            self.trans_to = Display.SPECTATOR
        else:
            self.trans_to = Display.GAME
        super().trans_display()


class DeleteButton(Button):
    """deleteボタン"""

    def __init__(self, master, history_list: HistoryList):
        self.history_list = history_list
        super().__init__(master, text=DELETE_HISTORY_BUTTON_TEXT, command=self.delete_history)

    def delete_history(self):
        """履歴の削除を行うメソッド
        
        DBcontroller.delete()でデータベースから履歴の削除を行う
        """
        # listboxで選択されているデータのindexを取得
        list_index = self.history_list.get_listbox_index()

        # indexを元に削除するデータのuuidを取得
        uuid = self.history_list.uuid_list[list_index]

        # データベース上から対象となる履歴を削除
        DBController.delete(uuid)

        # listboxの更新
        self.history_list.update()