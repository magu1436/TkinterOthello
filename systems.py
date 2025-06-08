from __future__ import annotations

from enum import Enum

from yaml import safe_load

from boardgame import Player


CONFIG_FILE_PATH = "config.yaml"
DATABASE_INFO_FILE_PATH = "database_info.yaml"

def load_config() -> dict:
    """config.yamlファイルを読み込み、コンフィグを読み込んで返す関数.
    
    returns:
        dict: config.yamlの内容を保持しているdict"""
    with open(CONFIG_FILE_PATH, "r") as file:
        config = safe_load(file)
    return config


def load_database_info() -> dict:
    """database_info.yamlファイルを読み込み、情報を読み込んで返す関数.
    
    returns:
        dict: database_info.yamlの内容を保持しているdict"""
    with open(DATABASE_INFO_FILE_PATH, "r") as file:
        database_info = safe_load(file)
    return database_info


class Color(Enum):

    BLACK = 0
    WHITE = 1


class OthelloPlayer(Player):

    def __init__(self, color: Color, name: str | None = None):
        super().__init__(name)
        self.color = color
        self.can_put: bool = True
