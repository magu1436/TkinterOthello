
from dataclasses import dataclass
from uuid import UUID

from objects import Stone
from systems import OthelloPlayer


@dataclass
class Scene:
    """一場面を保持するデータクラス"""
    board: list[list[None | Stone]]
    turn_player: OthelloPlayer


class History(list):
    """履歴を表すクラス
    
    リストを継承したコレクションクラスであり, 保持する要素は全て `Scene` クラスの
    インスタンスである.
    """
    def __init__(self):
        super().__init__()
    
    def append(self, board: list[list[None | Stone]], turn_player: OthelloPlayer) -> None:
        """履歴にシーンを追加するメソッド
        
        Args:
            board(list[list[None | Stone]]): ボード状況を保持する二次元リスト
            turn_player(OthelloPlayer): ターンプレイヤー"""
        super().append(Scene(board, turn_player))


class DBController:
    """データベースとやりとりするためのコントローラ"""

    @staticmethod
    def save(history: History) -> None:
        """履歴をデータベースに保存するメソッド"""
        pass

    def get_all_indexes():
        """データベースから履歴のインデックスを取得するメソッド"""


    @staticmethod
    def restore(uuid: str | UUID) -> History:
        """データベースから履歴を復元するメソッド
        
        引数に復元したい履歴のUUIDを受け取り、それに対応した履歴を返す."""
        pass

    def delete(uuid):
        """データベースから履歴を削除するメソッド
        
        引数に削除したい履歴のUUIDを受け取り、その履歴をデータベースから削除する"""