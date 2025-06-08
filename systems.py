from __future__ import annotations

from enum import Enum

from yaml import safe_load

from boardgame import Player


CONFIG_FILE_PATH = "config.yaml"


def load_config():
    """config.yamlファイルを読み込み、コンフィグを読み込む."""
    global CONFIG
    with open(CONFIG_FILE_PATH, "r") as file:
        CONFIG = safe_load(file)


CONFIG = {}
load_config()


class Color(Enum):

    BLACK = 0
    WHITE = 1


class OthelloPlayer(Player):

    def __init__(self, color: Color, name: str | None = None):
        super().__init__(name)
        self.color = color
        self.can_put: bool = True
