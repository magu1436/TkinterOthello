
from dataclasses import dataclass
from uuid import uuid4, UUID
from datetime import date
import mysql.connector
import json

from objects import Stone
from systems import *


INDEX_LIST_TABLE_NAME = "index_list"
SCENE_LIST_TABLE_NAME = "scene_list"


@dataclass
class Scene:
    """一場面を保持するデータクラス"""
    board: list[list[None | Stone]]
    turn_player: OthelloPlayer



class History(list):
    """履歴を表すクラス
    
    リストを継承したコレクションクラスであり, 保持する要素は全て `Scene` クラスの
    インスタンスである.

    Attribute:
        uuid(str): 
    """
    def __init__(self):
        super().__init__()

        self.uuid = str(uuid4())
        self.title = date.today().strftime("%Y-%m/%d")
        self.is_finished = False
    
    def append(self, board: list[list[None | Stone]], turn_player: OthelloPlayer) -> None:
        """履歴にシーンを追加するメソッド
        
        Args:
            board(list[list[None | Stone]]): ボード状況を保持する二次元リスト
            turn_player(OthelloPlayer): ターンプレイヤー"""
        super().append(Scene(board, turn_player))

class DBController:
    """データベースとやりとりするためのコントローラ"""

    conn = None
    cursor = None

    @classmethod
    def initialize(cls):
        
        if cls.conn is None:
            config = load_database_info()
            cls.conn = mysql.connector.connect(
                host = config["sql_host"],
                user = config["sql_user"],
                password = config["sql_password"],
                database = config["sql_database"]
            )
            cls.cursor = cls.conn.cursor()

            # 履歴の一覧を保存するテーブル
            cls.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {INDEX_LIST_TABLE_NAME}(
                        uuid BINARY(16) PRIMARY KEY,
                        title CHAR(10),
                        is_finished BOOLEAN
                )
            """)

            # ターンごとの盤面状態を保存するテーブル(history_listテーブルと関連付け)
            cls.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {SCENE_LIST_TABLE_NAME}(
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        history_id BINARY(16),
                        board_status JSON,
                        turn_player CHAR(5),
                        FOREIGN KEY (history_id) REFERENCES {INDEX_LIST_TABLE_NAME}(uuid)
                )
            """)

    @staticmethod
    def convert_board_to_list(scene: Scene) -> list :
        """Sceneオブジェクトからboardオブジェクトを取得し、listに変換するメソッド

        要素は、下記のように型変換を行う
        Stoneオブジェクト → str型 , None → None 
        
        Args:
            scene(Scene): 一場面を保持するデータクラス

        Returns:
            list: 盤面に配置されている石の色を文字列として保存した配列
        """
        
        # 盤面の状態を保存する配列
        board_data = []

        # Sceneオブジェクトからboardを取得
        board = scene.board

        # boardの要素を1つずつ取り出す
        for row in board:

            row_data = []

            for element in row:

                # 取り出した要素がStoneオブジェクトだった場合
                if isinstance(element, Stone):

                    # StoneオブジェクトからColorオブジェクトを文字列として取得
                    row_data.append(element.color.name)
                
                else:
                        row_data.append(None)
            
            board_data.append(row_data)

        return board_data
    
    @staticmethod
    def get_turn_player(scene: Scene) -> str:
        """Sceneオブジェクトからturn_playerを取得し、文字列として返すメソッド

        Args:
            scene(Scene): 一場面を保持するデータクラス

        Returns:
            str: BLACKとWHITE,どちらのターンか示す文字列

        """
        # Sceneオブジェクトからturn_playerを取得
        turn_player_data = scene.turn_player

        # turn_playerからColorオブジェクトを文字列として取得
        turn_player_str = turn_player_data.color.name

        return turn_player_str
    
    @staticmethod
    def convert_to_json(target:list) -> str:
         """リストをjson形式に変換するメソッド
         
        Args:
            target(list): json形式に変換したいリスト

        Returns:
            str: json形式で記述された文字列

         """
         return json.dumps(target)
    
    @staticmethod
    def convert_json_to_list(target:str) -> list:
        """json形式のデータをlistに変換するメソッド
        
        Args:
            target(str): listに変換したいjson形式のデータ

        Returns:
            list: 変換されたlist型のデータ
        """
        return json.loads(target)
    
    @staticmethod
    def convert_list_to_board(target_list:list) -> list:
        """受け取ったlistをboardに変換するメソッド
        
        listの各要素は、下記のように型変換を行う
        str型(BLACK or WHITE) → Stoneオブジェクト , None → None

        Args:
            target_list(list): 変換の対象となる二次元list

        Returns:
            scene(Scene): 一場面を保持するデータクラス

        """
        board = []

        for row in target_list:

            board_row = []

            for element in row:

                # 取り出した要素がstr型だった場合
                if isinstance(element, str):

                    if element == "BLACK":
                        stone = Stone.create(Color.BLACK)
                    
                    elif element == "WHITE":
                        stone = Stone.create(Color.WHITE)

                    board_row.append(stone)

                else:
                    board_row.append(None)

            board.append(board_row)

        return board

    @staticmethod
    def convert_str_to_turnplayer(target_str:str) -> OthelloPlayer:
        """受け取ったstrをturn_playerとして返すメソッド
        """
        if target_str == "BLACK":
            return OthelloPlayer(Color.BLACK, "先手")
        
        elif target_str == "WHITE":
            return OthelloPlayer(Color.WHITE, "後手")
    
    @classmethod
    def save(cls, history: History) -> None:
        """履歴をデータベースへ保存するメソッド
        
        Args:
            history(History): データベースへ保存する履歴

        """
        # データベースへの接続確認
        cls.initialize()

        # Historyオブジェクトからuuid,title,is_finishedを取得
        uuid_str = history.uuid
        title = history.title
        is_finished = history.is_finished

        # 取得したuuidをbytes型に変換
        uuid_bytes = UUID(uuid_str).bytes

        # history_listテーブルにデータを追加
        cls.cursor.execute(f"""
            INSERT INTO {INDEX_LIST_TABLE_NAME} (uuid, title, is_finished) VALUES (%s, %s, %s)
        """, (uuid_bytes, title, is_finished))

         # HistoryオブジェクトからSceneオブジェクトを1つずつ取り出す
        for scene in history:

            # Sceneオブジェクトからturn_playerを文字列として取得
            turn_player = cls.get_turn_player(scene)
            
            # Sceneオブジェクトから盤面状態をリストとして取得
            board_list = cls.convert_board_to_list(scene)

            # 盤面状態のリストをjson形式に変換
            board_json = cls.convert_to_json(board_list)

            # scene_listテーブルにデータを追加
            cls.cursor.execute(f"""
                INSERT INTO {SCENE_LIST_TABLE_NAME} (history_id, board_status, turn_player) VALUES (%s, %s, %s)
            """, (uuid_bytes, board_json, turn_player))

        # データベースの変更を確定
        cls.conn.commit()

    @classmethod
    def restore(cls, uuid: bytes) -> History:
        """データベースから履歴を復元するメソッド
        
        引数に復元したい履歴のUUIDを受け取り、それに対応したboardとturn_playerをscene_listテーブルから取得する。
        取得したboardとturn_playerを基にSceneオブジェクトを作成し、それをHistoryオブジェクトに追加、戻り値として返す。
        
        Args:
            uuid(str): 復元したい履歴に割り当てられているid

        Returns:
            History: 復元する履歴
        """
        # データベースへの接続確認
        cls.initialize()

        # Historyオブジェクトの作成
        history = History()

        # TODO: ここから下のコードが正しく動作しているか確認

        # scene_listテーブルから、uuidカラムの値がuuid_bytesと一致するデータを取得
        cls.cursor.execute(f"""
            SELECT board_status, turn_player FROM {SCENE_LIST_TABLE_NAME} WHERE history_id = %s
        """, (uuid,))

        rows: list[tuple] = cls.cursor.fetchall()

        for board_json, turn_player_str in rows:

            # json形式で取得したboardのデータをlist形式に変換
            board_list = cls.convert_json_to_list(board_json)

            # list形式に変換されたboardのデータをboardの形式に修正
            board = cls.convert_list_to_board(board_list)

            # str型で取得したturn_playerのデータをOhelloPlayerオブジェクトに変換
            turn_player = cls.convert_str_to_turnplayer(turn_player_str)

            # 変換,修正したboardとturn_playerを用いてSceneオブジェクトを作成し、Historyオブジェクトへ追加
            history.append(board, turn_player)

        return history

    @classmethod
    def delete(cls, uuid: bytes) -> None:
        """データベースから履歴を削除するメソッド
        
        引数に削除したい履歴のUUIDを受け取り、その履歴をデータベースから削除する
        
        Args:
            uuid(str): 削除したい履歴に割り当てられているid

        """
        # データベースへの接続確認
        cls.initialize()

        # scene_listテーブルから、uuidカラムの値がuuid_bytesと一致するデータを削除
        cls.cursor.execute(f"""
            DELETE FROM {SCENE_LIST_TABLE_NAME} WHERE history_id = %s
        """, (uuid,))

        # history_listテーブルから、uuidカラムの値がuuid_bytesと一致するデータを削除
        cls.cursor.execute(f"""
            DELETE FROM {INDEX_LIST_TABLE_NAME} WHERE uuid = %s
        """, (uuid,))

        # データベースの変更を確定
        cls.conn.commit()

    @classmethod
    def get_all_indexes(cls) -> list[tuple[bytes, str, bool]]:
        """データベースから履歴のインデックスを取得するメソッド

        Returns:
            list[taple]: history_viewで表示する全データのindex(uuid, title, is_finished)

        """
        # データベースへの接続確認
        cls.initialize()

        # history_listテーブルから、全データのindexを取得
        cls.cursor.execute(f"""
            SELECT uuid, title, is_finished FROM {INDEX_LIST_TABLE_NAME}
        """)

        # SELECT文の結果を取得
        row:list[tuple] = cls.cursor.fetchall()

        # 取得したデータを戻り値として返す
        return row