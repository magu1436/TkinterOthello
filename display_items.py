
from typing import Callable
from enum import StrEnum
from tkinter import Misc, Frame
from tkinter.ttk import Button



class Display(StrEnum):
    HOME = "home"
    GAME = "game"
    HISTORY = "history"
    SPECTATOR = "spectator"


class SceneTransitionButton(Button):
    """画面遷移を行うボタン"""

    def __init__(self, master: Misc, text: str, trans_to: Display, another_command: Callable | None = None):
        """画面遷移を行うボタン
        
        Args:
            master(Mist): マスター
            text(str): ボタンの文字列
            trans_to(Display): 遷移先の画面
            another_command(Callable | None): 遷移以外に行う処理. default to None.
        """
        super().__init__(master, text=text, command=self.trans_display)
        self.trans_to: Display = trans_to
        self.another_command: Callable | None = another_command
    
    def trans_display(self):
        """クリックされたときの処理
        
        もとの画面を非表示にして、遷移先の画面を表示にし、シーン遷移を表現する.
        """
        for child in self.master.winfo_toplevel().winfo_children():
            if child.winfo_name() == self.trans_to:
                child.tkraise()
                break
        if self.another_command is not None:
            self.another_command()