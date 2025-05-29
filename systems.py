from __future__ import annotations

from enum import Enum

from yaml import safe_load

from boardgame import Player


CONFIG_FILE_PATH = "config.yaml"

def load_config() -> dict:
    """config.yamlファイルを読み込み、コンフィグを読み込んで返す関数.
    
    returns:
        dict: config.yamlの内容を保持しているdict"""
    with open(CONFIG_FILE_PATH, "r") as file:
        config = safe_load(file)
    return config


class Color(Enum):

    BLACK = 0
    WHITE = 1


class OthelloPlayer(Player):

    def __init__(self, color: Color, name: str | None = None):
        super().__init__(name)
        self.color = color
        self.can_put: bool = True
