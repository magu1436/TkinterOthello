import mysql.connector

from history import Scene, History
from objects import Stone
from systems import Color

class MysqlController:
    """MySQLの基本操作を行うクラス"""

    def __init__(self):
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "hirokisql",
            database = "othello"
        )
        cursor = conn.cursor()

    def analyze_color(self, scene: Scene) -> list :
            """Sceneオブジェクトからboardオブジェクトを取得し、文字列として保存するメソッド"""
            
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