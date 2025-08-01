from tkinter import Frame, Label, Listbox, Button
import tkinter as tk

from display_items import SceneTransitionButton, Display
from history import DBController, History, Scene
from objects import OthelloBoard, Stone
from game_display import GameDisplay
from game_manager import GameManager, ManagerDisplay
from systems import OthelloPlayer
from game_manager import SpectatingManager
from spectator_display import SpectatorDisplay

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
        HistoryList.uuid_list = []

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
    
    def restore_board_status(self):
        """Historyをもとにboardを復元するメソッド
        """
        # restore_selected_history()を使用してHistoryオブジェクトを取得
        history: History = self.restore_selected_history()

        # GameDisplayオブジェクトを取得
        game_display: GameDisplay = Display.get_display(Display.GAME)

        # GameDisplayオブジェクトからGameManagerオブジェクトを取得
        game_manager: GameManager = game_display.manager

        # GameDisplayオブジェクトからboardを取得
        othello_board: OthelloBoard = game_display.othello_board

        # GameDisplayオブジェクトからManagerDisplayオブジェクトを取得
        manager_display: ManagerDisplay = game_display.manager_display

        # historyから末尾のSceneオブジェクトを取得
        last_scene: Scene = history[-1]

        # last_sceneの1つ前のsceneからturn_playerを取得
        turn_player = history[-2].turn_player

        # GameManagerが持っているHistoryオブジェクトを,historyに変更
        game_manager.history = history

        # GameManagerがもっているturn_player属性をturn_playerに変更
        game_manager.turn_player = turn_player

        # 盤面へ石を再配置
        self.restore_put_stone(othello_board, last_scene)

        # タイルの再配置とサブディスプレイの更新
        game_manager.change_turn()

    def restore_put_stone(self, othello_board: OthelloBoard, last_scene: Scene):
        """受け取ったHistoryオブジェクトをもとに石の再配置を行うメソッド
        """
        # last_sceneからboardを取得
        board_status: list[list[Stone | None]] = last_scene.board

        # board_statusを1マスずつ参照し、othello_boardに駒を配置する
        i = 0
        for row in board_status:
            j = 0
            for stone in row:
                othello_board.put(stone, (j, i))
                j += 1
            i += 1
        
    
    def trans_display(self):
        history = self.restore_selected_history()
        is_finished = history.is_finished
        if is_finished:
            self.trans_to = Display.SPECTATOR
            spectator_display: SpectatorDisplay = Display.get_display(self.trans_to)
            spectating_manager: SpectatingManager = spectator_display.manager
            spectating_manager.create_game(history)
        else:
            self.trans_to = Display.GAME
            self.restore_board_status()
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

        # 削除するデータのuuidをuuid_listから削除
        del self.history_list.uuid_list[list_index]

        # データベース上から対象となる履歴を削除
        DBController.delete(uuid)

        # listboxの更新
        self.history_list.update()