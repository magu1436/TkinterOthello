
from __future__ import annotations

from enum import Enum
from tkinter import Misc, Frame
import tkinter
from copy import copy
from typing import Sequence

from boardgame import Board, Tile, Coordinate
from objects import Stone, PutableSpaceTile
from systems import Color, OthelloPlayer, CONFIG
from history import History
from game_display import ManagerDisplay
from home_display import HomeDisplay
from display_items import Display


BLACK_STONE_IMAGE_PATH = CONFIG["BLACK_STONE_IMAGE_PATH"]
WHITE_STONE_IMAGE_PATH = CONFIG["WHITE_STONE_IMAGE_PATH"]
BOARD_BACKGROUND_IMAGE_PATH = CONFIG["BOARD_BACKGROUND_IMAGE_PATH"]
FRAME_IMAGE_PATH = CONFIG["FRAME_IMAGE_PATH"]
GRID_IMAGE_PATH = CONFIG["GRID_IMAGE_PATH"]
PUTABLE_TILE_IMAGE = ["PUTABLE_TILE_IMAGE_PATH"]
ICON_IMAGE_PATH = CONFIG["ICON_IMAGE_PATH"]

OTHELLO_BOARD_SIZE = (8, 8)


class OthelloException(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class ColorError(OthelloException):
    def __str__(self):
        return "Some issue happened about the stone color."

class HeadcountOfPlayerError:
    """参加プレイヤーが二人でないときに生じる"""
    def __str__(self):
        return "Headcount in games must be two."

class NotJoiningPlayerError:
    """ゲームに参加していないプレイヤーが指定されたときに生じる
    
    Args:
        player(OthelloPlayer): 未参加のプレイヤー"""
    def __str__(self):
        player = self.args[0]
        return f"{player.name} don't join the game."

class InvalidStonePlacementError(Exception):
    """石を置けない場所に置こうとしたときに投げられる例外
    
    Args:
        stone(Stone): 置こうとした石"""
    def __str__(self):
        stone: Stone = self.args[0]
        return f"Invalid stone placed at {stone.coordinate}: color {stone.color}"



class Direction(Enum):

    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    UPPER_RIGHT = (1, -1)
    UPPER_LEFT = (-1, -1)
    LOWER_RIGHT = (1, 1)
    LOWER_LEFT = (-1, 1)



class OthelloBoard(Board):

    def __init__(
            self, 
            master: Misc, 
            board_display_size: tuple[int, int], 
            grid_width: int,
        ):
        super().__init__(
            master, 
            OTHELLO_BOARD_SIZE, 
            BOARD_BACKGROUND_IMAGE_PATH,
            board_display_size,
            GRID_IMAGE_PATH,
            FRAME_IMAGE_PATH,
            grid_width,
            )
        self.init_board()
    
    def init_board(self):
        """石を初期配置するメソッド"""
        self.take_all_pieces()
        self.put(Stone.create(Color.WHITE), (self.board_size[0] // 2 - 1, self.board_size[1] // 2 - 1))
        self.put(Stone.create(Color.BLACK), (self.board_size[0] // 2, self.board_size[1] // 2 - 1))
        self.put(Stone.create(Color.BLACK), (self.board_size[0] // 2 - 1, self.board_size[1] // 2))
        self.put(Stone.create(Color.WHITE), (self.board_size[0] // 2, self.board_size[1] // 2))


class OthelloGameManager(Frame):
    """オセロのアプリケーションの全てのオブジェクトを管理し、ターン進行を担うマネージャークラス"""

    def __init__(
            self, 
            master: Misc,
            display_size: Coordinate | tuple[int, int],
            grid_width: int,
            participants: Sequence[OthelloPlayer],
            **kwargs):
        
        if len(participants) != 2:
            raise HeadcountOfPlayerError()

        self.players: list[OthelloPlayer, OthelloPlayer] = list(participants)
        self.whole_display_size: Coordinate = Coordinate(display_size)

        super().__init__(
            master, 
            width=self.whole_display_size.x, 
            height=self.whole_display_size.y, 
            name=Display.GAME.value,
            **kwargs
        )
        self.othello_board: OthelloBoard = OthelloBoard(
            self,
            (self.whole_display_size.y, self.whole_display_size.y),
            grid_width,
        )

        self.manager_display: ManagerDisplay = ManagerDisplay(
            self, 
            self.whole_display_size - (self.othello_board.board_display_size.x, 0),
            self.redo,
            self.start_new_game
            )
        
        self.othello_board.pack(side=tkinter.LEFT)
        self.manager_display.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        
        self.start_new_game()
    
    def start_new_game(self):
        """盤面を初期化して、新しいゲームを始めるためのメソッド"""
        for player in self.players:
            if player.color == Color.BLACK:
                self.turn_player: OthelloPlayer = player
                break

        for player in self.players:
            player.can_put = True

        self.othello_board.init_board()
        self.set_putable_tiles(self.turn_player.color)
        
        self.history: History = History()
        self.history.append(self.othello_board.board, self.turn_player)
        self.manager_display.update_display(
            self.turn_player.name,
            self.count_stone_amount(Color.BLACK),
            self.count_stone_amount(Color.WHITE)
        )
    
    def flip(self, stone: Stone):
        """石をひっくり返すメソッド
        
        Raises:
            ColorError: 自身の色が `Color` 以外だった場合に生じる"""
        match stone.color:
            case Color.BLACK:
                self.othello_board.put(Stone(Color.WHITE), stone.coordinate)
            case Color.WHITE:
                self.othello_board.put(Stone(Color.BLACK), stone.coordinate)
            case _:
                raise ColorError()
    
    def can_flip_along_direction(
            self, 
            color: Color, 
            coordinate: Coordinate | Sequence[int, int],
            direction: Direction
            ) -> bool:
        """引数に受け取った方向について、ひっくり返すことができるかどうか判別して返す.

        引数に受け取った座標に、引数に受け取った色の石を置いたときにひっくり返すことができるかどうか判別する.
        
        Args:
            color(Color): 置いたときにひっくり返すことができるか考える色
            coordinate(Coordinate | Sequense[int]): 置きたい石の座標.
            direction(Direction): 探索する方向"""
        cursor = copy(Coordinate(coordinate))
        if self.othello_board.get(cursor) is not None:
            return False
        cursor += direction.value
        exists_opponent_stone = False
        while self.othello_board.is_in_board(cursor):
            stone: Stone | None = self.othello_board.get(cursor)
            if stone is None:
                break
            if stone.color != color:
                exists_opponent_stone = True
            if stone.color == color:
                return exists_opponent_stone
            cursor += direction.value
        return False
    
    def can_put_stone(self, color: Color, coordinate: Sequence[int, int]) -> bool:
        """ある座標に石を置くことができるかどうか判別するためのメソッド.
        
        Args:
            color(Color): 置きたい石の色
            coordinate(Sequence[int]): 石を置きたい座標
        
        Returns:
            bool: 置くことができるかどうか"""
        if self.othello_board.get(coordinate) is not None:
            return False
        for direction in Direction:
            if self.can_flip_along_direction(color, coordinate, direction):
                return True
        return False

    def get_flipable_direction(self, color: Color, coordinate: Coordinate | tuple[int, int]) -> list[Direction]:
        """引数に受け取った座標に石を置いたとき、ひっくり返すことができる方向を返すメソッド
        
        Args:
            color(Color): 置く石
            coordinate(Coordinate | Sequence[int]): 石を置く座標
        
        Returns:
            list[Direction]: 置いたときにひっくり返すことができる方向のリスト"""
        flipable_directions = []
        for direction in Direction:
            if self.can_flip_along_direction(color, coordinate, direction):
                flipable_directions.append(direction)
        return flipable_directions
    
    def put_stone(self, put_stone: Stone, coordinate: Coordinate | tuple[int, int]) -> None:
        """石を置くメソッド
        
        このメソッドは石を置くことができることを前提として設計されている.
        万一置くことができないにもかかわらずこのメソッドが呼ばれたとき、例外を投げる.

        履歴の保存はこのメソッド内で行われる.
        
        Args:
            put_stone(Stone): 石
            coordinate(Coordinate | Sequence[int]): 座標
        
        Raises:
            InvalidStoneOlacementError: 石を置いてもひっくり返すことができないにもかかわらず、置こうとしたときに生じる."""

        # 置くことが可能か判定し、フリップを行う方向のリストを取得する
        flip_directions = self.get_flipable_direction(put_stone.color, coordinate)
        if (self.othello_board.get(coordinate) is not None) or (len(flip_directions) == 0):
            raise InvalidStonePlacementError(put_stone)
        
        # 置く前に履歴の保存
        self.history.append(self.othello_board.board, self.turn_player)
        
        self.othello_board.put(put_stone, coordinate)
        for direction in flip_directions:
            cursor = Coordinate(coordinate) + direction.value
            while self.othello_board.is_in_board(cursor):
                target_stone: Stone | None = self.othello_board.get(cursor)
                if put_stone.color == target_stone.color:
                    break
                self.flip(target_stone)
                cursor += direction.value

        # 次のプレイヤーへ
        self.change_turn()
    
    def change_turn(self):
        """ターンプレイヤー変更時の処理を行うメソッド"""

        # 新しいターンプレイヤーの設定
        for p in self.players:
            if p != self.turn_player:
                new_turn_player = p
        self.turn_player = new_turn_player

        # ManagerDisplayの更新
        self.manager_display.update_display(
            self.turn_player.name,
            self.count_stone_amount(Color.BLACK),
            self.count_stone_amount(Color.WHITE),
        )

        # 置けることを示すタイルのセット
        self.othello_board.reset_tiles()
        putable_tiles_list = self.set_putable_tiles(self.turn_player.color)

        # ふたりとも置くところがない場合、試合終了
        if not any([player.can_put for player in self.players]):
            self.end()
            return
        
        if len(putable_tiles_list) == 0:
            self.turn_player.can_put = False
            self.change_turn()
        else:
            self.turn_player.can_put = True
    
    def set_putable_tiles(self, color: Color) -> list[Tile]:
        """置けるところを示すためのタイルを設置するメソッド"""
        put_tiles = []
        for x in range(self.othello_board.board_size.x):
            for y in range(self.othello_board.board_size.y):
                if self.can_put_stone(color, (x, y)):
                    tile = PutableSpaceTile()
                    self.othello_board.set_tile(
                        tile,
                        (x, y)
                    )
                    put_tiles.append(tile)
        return put_tiles
    
    def count_stone_amount(self, color: Color | None = None) -> int:
        """盤上の石の数を数えるためのメソッド
        
        `color` に値を指定したとき、その色の石のみを数える.
        なにも指定されていないとき、全ての石の数を数える.
        
        Args:
            color(Color, optional): 数えたい石の色. default to None.
        
        Returns:
            int: 盤上の指定の色の石の数"""
        stones = self.othello_board.get_all_pieces()
        if color is None:
            return len(stones)
        return len([stone for stone in stones if stone.color == color])
    
    def end(self):
        """勝敗が決まったあとに呼び出される処理"""
        black_stone_amount = self.count_stone_amount(Color.BLACK)
        white_stone_amount = self.count_stone_amount(Color.WHITE)
        if black_stone_amount > white_stone_amount:
            winner_color = Color.BLACK
        else:
            winner_color = Color.WHITE
        winner = self.players[0] if self.players[0].color == winner_color else self.players[1]
        self.manager_display.indicate_victory_scene(winner)
    
    def redo(self):
        """一手戻る処理を行うメソッド."""
        if len(self.history) <= 1:
            return
        history: History = self.history.pop()
        board = history.board
        self.othello_board.take_all_pieces()
        for x in range(self.othello_board.board_size.x):
            for y in range(self.othello_board.board_size.y):
                self.othello_board.put(board[y][x], (x, y))
        self.change_turn()



def main():

    root = tkinter.Tk()
    root.state("zoomed")
    root.title("othello game")
    root.iconbitmap(default=ICON_IMAGE_PATH)
    root.update_idletasks()

    p1 = OthelloPlayer(Color.BLACK, "先手")
    p2 = OthelloPlayer(Color.WHITE, "後手")

    root_size = (root.winfo_width(), root.winfo_height())
    manager = OthelloGameManager(
        root,
        root_size,
        5,
        [p1, p2],
    )
    manager.grid(row=0, column=0, sticky="nsew")

    home_display = HomeDisplay(root)
    home_display.grid(row=0, column=0, sticky="nsew")

    home_display.tkraise()

    root.mainloop()

if __name__ == "__main__":
    main()