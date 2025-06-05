import mysql.connector
import json

from history import Scene, History
from objects import Stone
from systems import Color, load_config

class MysqlController:
    """MySQLの基本操作を行うクラス"""

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = load_config()["sql_host"],
            user = load_config()["sql_user"],
            password = load_config()["sql_password"],
            database = load_config()["sql_database"]
        )
        self.cursor = self.conn.cursor()

        # 履歴の一覧を保存するテーブル
        self.cursor.execute("""
             CREATE TABLE IF NOT EXISTS history_list(
                       uuid BINARY(16) PRIMARY KEY,
                       title DATE,
                       is_finished BOOREAN
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

    def get_board(self, scene: Scene) -> list :
        """Sceneオブジェクトからboardオブジェクトを取得し、文字列として保存するメソッド
        
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
    
    def save(self, history: History):
        
        # Historyオブジェクトからuuidとtitleを取得
        uuid_str = history.uuid
        title = history.title

        # 取得したuuidをbytes型に変換
        uuid_bytes = uuid_str.encode("utf-8")

        # history_listテーブルにデータを追加
        self.cursor.execute("""
            INSERT INTO history_list (uuid, title) VALUES (%s, %s)
        """, (uuid_bytes, title))

         # HistoryオブジェクトからSceneオブジェクトを1つずつ取り出す
        for scene in history:

            # Sceneオブジェクトからturn_playerを文字列として取得
            turn_player = self.get_turn_player(scene)
            
            # Sceneオブジェクトから盤面状態をリストとして取得
            board_list = self.get_board(scene)

            # 盤面状態のリストをjson形式に変換
            board_json = self.convert_to_json(board_list)

            # scene_listテーブルにデータを追加
            self.cursor.execute("""
                INSERT INTO scene_list (history_id, board_status, turn_player) VALUES (%s, %s, %s)
            """, (uuid_bytes, board_json, turn_player))

        # データベースの変更を確定
        self.conn.commit()