import mysql.connector
import json
from uuid import uuid4, UUID

from history import Scene, History
from objects import Stone
from systems import *

class MysqlController:
    """MySQLの基本操作を行うクラス"""

    def __init__(self):
        config = load_config()
        self.conn = mysql.connector.connect(
            host = config["sql_host"],
            user = config["sql_user"],
            password = config["sql_password"],
            database = config["sql_database"]
        )
        self.cursor = self.conn.cursor()

        # 履歴の一覧を保存するテーブル
        self.cursor.execute("""
             CREATE TABLE IF NOT EXISTS history_list(
                       uuid BINARY(16) PRIMARY KEY,
                       title DATE,
                       is_finished BOOLEAN
             )
        """)

        # ターンごとの盤面状態を保存するテーブル(history_listテーブルと関連付け)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scene_list(
                       id INT PRIMARY KEY AUTO_INCREMENT,
                       history_id BINARY(16),
                       board_status JSON,
                       turn_player CHAR(5),
                       FOREIGN KEY (history_id) REFERENCES history_list(uuid)
            )
        """)

    def convert_board_to_list(self, scene: Scene) -> list :
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
    
    def get_turn_player(self, scene: Scene) -> str:
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
    
    def convert_to_json(self, target:list) -> str:
         """リストをjson形式に変換するメソッド
         
        Args:
            target(list): json形式に変換したいリスト

        Returns:
            str: json形式で記述された文字列

         """
         return json.dumps(target)
    
    def convert_json_to_list(self, target:str) -> list:
        """json形式のデータをlistに変換するメソッド
        
        Args:
            target(str): listに変換したいjson形式のデータ

        Returns:
            list: 変換されたlist型のデータ
        """
        return json.loads(target)
    
    def convert_list_to_board(self, target_list:list) -> list:
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

    def convert_str_to_turnplayer(self, target_str:str) -> OthelloPlayer:
        """受け取ったstrをturn_playerとして返すメソッド
        """
        if target_str == "BLACK":
            return OthelloPlayer(Color.BLACK, "先手")
        
        elif target_str == "WHITE":
            return OthelloPlayer(Color.WHITE, "後手")
    
    def save(self, history: History) -> None:
        """履歴をデータベースへ保存するメソッド
        
        Args:
            history(History): データベースへ保存する履歴

        """
        # Historyオブジェクトからuuid,title,is_finishedを取得
        uuid_str = history.uuid
        title = history.title
        is_finished = history.is_finished

        # 取得したuuidをbytes型に変換
        uuid_bytes = UUID(uuid_str).bytes

        # history_listテーブルにデータを追加
        self.cursor.execute("""
            INSERT INTO history_list (uuid, title, is_finished) VALUES (%s, %s, %s)
        """, (uuid_bytes, title, is_finished))

         # HistoryオブジェクトからSceneオブジェクトを1つずつ取り出す
        for scene in history:

            # Sceneオブジェクトからturn_playerを文字列として取得
            turn_player = self.get_turn_player(scene)
            
            # Sceneオブジェクトから盤面状態をリストとして取得
            board_list = self.convert_board_to_list(scene)

            # 盤面状態のリストをjson形式に変換
            board_json = self.convert_to_json(board_list)

            # scene_listテーブルにデータを追加
            self.cursor.execute("""
                INSERT INTO scene_list (history_id, board_status, turn_player) VALUES (%s, %s, %s)
            """, (uuid_bytes, board_json, turn_player))

        # データベースの変更を確定
        self.conn.commit()

    def restore(self, uuid: str ) -> History:
        """データベースから履歴を復元するメソッド
        
        引数に復元したい履歴のUUIDを受け取り、それに対応したboardとturn_playerをscene_listテーブルから取得する。
        取得したboardとturn_playerを基にSceneオブジェクトを作成し、それをHistoryオブジェクトに追加、戻り値として返す。
        
        Args:
            uuid(str): 復元したい履歴に割り当てられているid

        Returns:
            History: 復元する履歴
        """
        # Historyオブジェクトの作成
        history = History()

        # 引数として受け取ったuuidをbytes型に変換
        uuid_bytes = UUID(uuid).bytes

        # uuidカラムの値がuuid_bytesと一致するデータを取得
        self.cursor.execute("""
            SELECT board_status, turn_player FROM scene_list WHERE history_id = %s
        """, (uuid_bytes,))

        rows: list[tuple] = self.cursor.fetchall()

        for board_json, turn_player_str in rows:

            # json形式で取得したboardのデータをlist形式に変換
            board_list = self.convert_json_to_list(board_json)

            # list形式に変換されたboardのデータをboardの形式に修正
            board = self.convert_list_to_board(board_list)

            # str型で取得したturn_playerのデータをOhelloPlayerオブジェクトに変換
            turn_player = self.convert_str_to_turnplayer(turn_player_str)

            # 変換,修正したboardとturn_playerを用いてSceneオブジェクトを作成し、Historyオブジェクトへ追加
            history.append(board, turn_player)

        return history

    def delete(self, uuid: str) -> None:
        """データベースから履歴を削除するメソッド
        
        引数に削除したい履歴のUUIDを受け取り、その履歴をデータベースから削除する
        
        Args:
            uuid(str): 復元したい履歴に割り当てられているid

        """
        # 引数として受け取ったuuidをbytes型に変換
        uuid_bytes = UUID(uuid).bytes

        # scene_listテーブルから、uuidカラムの値がuuid_bytesと一致するデータを削除
        self.cursor.execute("""
            DELETE FROM scene_list WHERE history_id = %s
        """, (uuid_bytes,))

        # history_listテーブルから、uuidカラムの値がuuid_bytesと一致するデータを削除
        self.cursor.execute("""
            DELETE FROM history_list WHERE uuid = %s
        """, (uuid_bytes,))

        self.conn.commit()