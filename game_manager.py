from __future__ import annotations

from enum import Enum
from copy import copy
from typing import Callable
import tkinter
from tkinter import Frame, Misc, Canvas
from tkinter.ttk import Button
import time

from boardgame import Coordinate, BoardGamePhotoImage

from objects import OthelloBoard, Stone, PutableSpaceTile
from history import History, Scene, DBController
from systems import OthelloPlayer, Color, CONFIG
from errors import TkinterOthelloException
from text_object import AutoFontLabel
from display_items import SceneTransitionButton, Display


REDO_BUTTON_TEXT = "待った！！"
SAVE_BUTTON_TEXT = "途中保存"
SM_UNDO_BUTTON_TEXT = "一手戻す"
SM_REDO_BUTTON_TEXT = "一手進める"
SM_HOME_BUTTON_TEXT = "ホームへ戻る"

TIME_CUT_IN = 2
PASS_CUT_IN_IMAGE_RATIO_TO_DISPLAY: float = .6
PASS_CUT_IN_IMAGE_PATH = CONFIG["PASS_CUT_IN_PATH"]
CUT_IN_BG_IMAGE_PATH = CONFIG["PASS_CUT_IN_BG"]
TIME_RAITIO_STOPPING_CUT_IN_ON_CENTER = .5
FPS = 30

class InvalidStonePlacementError(TkinterOthelloException):
    """石を置けない場所に置こうとしたときに投げられる例外
    
    Args:
        stone(Stone): 置こうとした石"""
    def __str__(self):
        stone: Stone = self.args[0]
        return f"Invalid stone placed at {stone.coordinate}: color {stone.color}"

class NotExistsManagerDisplayError(TkinterOthelloException):
    """create_manager_displayメソッドを呼ばれる前にmanager_displayを参照しようとしたときに生じる"""
    def __str__(self):
        return "No 'ManagerDisplay' objects is created. Use create_manager_display method firstly."



class Direction(Enum):

    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    UPPER_RIGHT = (1, -1)
    UPPER_LEFT = (-1, -1)
    LOWER_RIGHT = (1, 1)
    LOWER_LEFT = (-1, 1)


class GameManager:
    """ゲームの進行を管理するクラス
    
    Attributes:
        othello_board(OthelloBoard): オセロのボード
        players(tuple[OthelloPlayer]): オセロの参加者
        manager_display(ManagerDisplay): GameDisplayのサブディスプレイ(外部から変更不可)
        turn_player(OthelloPlayer): ターンプレイヤー
        history(History): 履歴"""
    
    def __init__(
            self, 
            othello_board: OthelloBoard, 
            participants: tuple[OthelloPlayer, OthelloPlayer],
        ):
        self.othello_board = othello_board
        self.players = participants
        self.__manager_display = None
    
    @property
    def manager_display(self) -> ManagerDisplay:
        if self.__manager_display is None:
            raise NotExistsManagerDisplayError()
        return self.__manager_display

    def create_manager_display(
            self,
            master: Misc,
            display_size: tuple[int, int] | Coordinate,
    ):
        manager_display = ManagerDisplay(
            master,
            display_size,
            self.redo,
            self.start_new_game,
            self
        )
        self.__manager_display = manager_display
        return self.__manager_display
    
    def start_new_game(self):
        """盤面を初期化して、新しいゲームを始めるためのメソッド"""
        for player in self.players:
            if player.color == Color.BLACK:
                self.turn_player: OthelloPlayer = player
                break

        for player in self.players:
            player.can_put = True

        self.othello_board.init_board()
        self.othello_board.reset_tiles()
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

        Args:
            stone(Stone): ひっくり返す石
        
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
            coordinate: Coordinate | tuple[int, int],
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
    
    def can_put_stone(self, color: Color, coordinate: tuple[int, int] | Coordinate) -> bool:
        """ある座標に石を置くことができるかどうか判別するためのメソッド.
        
        Args:
            color(Color): 置きたい石の色
            coordinate(tuple[int] | Coordinate): 石を置きたい座標
        
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
            if not all([all([stone for stone in row]) for row in self.othello_board.board]):
                self.pass_with_cut_in()
            self.turn_player.can_put = False
            self.change_turn()
        else:
            self.turn_player.can_put = True
    
    def pass_with_cut_in(self):
        """パスのカットイン演出を実行するメソッド"""
        display_size = self.othello_board.board_display_size + self.manager_display.display_size
        cut_in_image = BoardGamePhotoImage(PASS_CUT_IN_IMAGE_PATH)
        img_ratio = display_size.x * PASS_CUT_IN_IMAGE_RATIO_TO_DISPLAY / cut_in_image.width()
        cut_in_image.resize((int(cut_in_image.width() * img_ratio), (int(cut_in_image.height() * img_ratio))))
        cut_in_bg_image = BoardGamePhotoImage(
            CUT_IN_BG_IMAGE_PATH,
            (display_size.x, cut_in_image.height())
        )

        
        stoppping_time = TIME_CUT_IN * TIME_RAITIO_STOPPING_CUT_IN_ON_CENTER
        moving_time = (TIME_CUT_IN - stoppping_time) / 2

        canvas = Canvas(
            master=self.manager_display.winfo_toplevel(),
            width=display_size.x, 
            height=cut_in_image.height(), 
            bd=0,
            highlightthickness=0
        )
        canvas.create_image(
            cut_in_bg_image.width() // 2,
            cut_in_bg_image.height() // 2,
            image=cut_in_bg_image
        )
        cut_in = canvas.create_image(
            display_size.x,
            cut_in_image.height() // 2,
            image=cut_in_image
        )
        canvas.place(x=display_size.x//2, y=display_size.y//2, anchor="center")

        frame_amount = moving_time * FPS
        dt = moving_time / frame_amount
        dx = display_size.x // frame_amount

        # TODO: ここから実際に動かす処理を実装
        def move():
            for _ in range(int(frame_amount // 2)):
                canvas.move(cut_in, -dx, 0)
                canvas.master.update()
                time.sleep(dt)
        move()
        time.sleep(stoppping_time)
        move()
        canvas.destroy()


    
    def set_putable_tiles(self, color: Color) -> tuple[PutableSpaceTile]:
        """置けるところを示すためのタイルを設置するメソッド
        
        Args:
            color(Color): 置ける場所を探索する色
        
        returns:
            tuple[PutableSpaceTile]: 全ての置いたタイルを保持するタプル"""
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
        return tuple(put_tiles)
    
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
        self.history.is_finished = True
        self.save_progress()
    
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

    def save_progress(self):
        """ゲームの途中経過を保存するメソッド
        """
        # saveする前に最新の盤面状態をHistoryに追加
        self.history.append(self.othello_board.board, self.turn_player)

        # Historyをデータベースへ保存
        DBController.save(self.history)


class CounterDisplay(Frame):
    """石の枚数を表示するディスプレイのクラス"""

    def __init__(
            self,
            master: Misc,
            color: Color,
            display_width: int,
    ):
        """コンストラクタ
        
        Args:
            master(Misc): このフレームのマスター
            color(Color): このディスプレイが表示する石の枚数の色
            display_width(Sequence[int]): このディスプレイの幅
        """
        size = Coordinate(display_width, display_width // 2)
        super().__init__(master, width=size.x, height=size.y)
        if color == Color.BLACK:
            image_path = CONFIG["BLACK_STONE_IMAGE_PATH"]
        else:
            image_path = CONFIG["WHITE_STONE_IMAGE_PATH"]
        canvas_size = (size.x // 2, size.y)
        self.canvas = Canvas(self, width=canvas_size[0], height=canvas_size[1])
        self.stone_image = BoardGamePhotoImage(image_path, canvas_size)
        self.canvas.create_image(canvas_size[0]//2, canvas_size[1]//2, image=self.stone_image)
        self.label = AutoFontLabel(self, str(2), canvas_size[0])
        self.canvas.pack(side=tkinter.LEFT)
        self.label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    
    def update_counter(self, count: int):
        """表示枚数を更新するメソッド
        
        Args:
            count(int): 表示する枚数"""
        self.label.set_text(str(count))


class TurnPlayerDisplay(AutoFontLabel):

    def __init__(
            self,
            master: Misc,
            display_width: int,
            **kwargs
            ):
        super().__init__(
            master,
            display_width=display_width,
            **kwargs
        )
    
    def __create_display_label(self, turn_player_name: str):
        return f"{turn_player_name}のターン"
    
    def update_player_name(self, player_name: str):
        self.set_text(self.__create_display_label(player_name))


class SaveButton(SceneTransitionButton):
    """対戦を中断し、途中経過を保存するボタン"""

    def __init__(self, master, game_manager: GameManager):
        super().__init__(master, SAVE_BUTTON_TEXT, Display.HOME, game_manager.save_progress)


class ManagerDisplay(Frame):
    """ゲーム画面の右側に表示するディスプレイ
    
    ターンプレイヤーの表示や現在の石の数を表示する.
    試合の決着時、画面遷移のボタンや新しいゲームを始めるボタンを追加する.
    
    Args:
        master(Misc): マスター
        display_size(Sequence[int]): 画面上で表示される際の表示サイズ
        redo_command(Callable([[], None])): 待ったボタンで実行される処理
        game_reset_func(Callable[[], None]): game_resetメソッドが呼ばれたときに実行される処理"""
    
    def __init__(
            self,
            master: Misc,
            display_size: tuple[int],
            redo_command: Callable[[], None],
            game_reset_func: Callable[[], None],
            game_manager: GameManager
    ):
        super().__init__(
            master,
            width=display_size[0],
            height=display_size[1],
        )
        self.display_size = Coordinate(display_size)
        self.turn_player_display = TurnPlayerDisplay(self, display_size[0])
        self.black_stone_counter = CounterDisplay(self, Color.BLACK, self.display_size.x // 2)
        self.white_stone_counter = CounterDisplay(self, Color.WHITE, self.display_size.x // 2)
        self.redo_button = Button(self, text=REDO_BUTTON_TEXT, command=redo_command)
        self.save_button = SceneTransitionButton(self, SAVE_BUTTON_TEXT, Display.HOME, lambda: (game_manager.save_progress(), self.reset_game()))
        self.home_button = SceneTransitionButton(self, "ホーム画面へ", Display.HOME, self.reset_game)

        self.game_reset_func: Callable = game_reset_func

        # 配置
        self.turn_player_display.grid(row=0, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        self.black_stone_counter.grid(row=1, column=0, sticky=tkinter.W+tkinter.E)
        self.white_stone_counter.grid(row=1, column=1, sticky=tkinter.W+tkinter.E)
        self.redo_button.grid(row=2, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        self.save_button.grid(row=3, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        self.home_button.grid(row=4, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        

    def update_display(
            self,
            player_name: str,
            black_stone_count: int,
            white_stone_count: int
    ):
        """ディスプレイの情報を更新するメソッド
        
        ターンプレイヤーの名前と石の数を同時に更新する
        
        Args:
            player_name(str): ターンプレイヤー名
            black_stone_amount(int): 黒の石の数
            white_stone_count(int): 白の石の数
        """
        self.turn_player_display.update_player_name(player_name)
        self.black_stone_counter.update_counter(black_stone_count)
        self.white_stone_counter.update_counter(white_stone_count)
    
    def indicate_victory_scene(self, winner: OthelloPlayer | None):
        """勝利者とホームボタン及びニューゲームボタンを表示させるメソッド
        
        Args:
            winner(OthelloPlayer | None): 勝者. 引き分けなら`None`をいれる."""
        if winner is None:
            text = "引き分け！"
        else:
            text = winner.name + "の勝利！"
        self.winner_label = AutoFontLabel(
            self,
            text,
        )
        self.winner_label.grid(row=3, column=0, columnspan=2, sticky="ew")


        self.new_game_button = Button(
            self, text="新しいゲーム", command=self.reset_game
        )
        self.new_game_button.grid(row=4, column=1, sticky="ew")
    
    def reset_game(self):
        self.game_reset_func()

        if hasattr(self, "new_game_button"):
            self.new_game_button.destroy()
        
        if hasattr(self, "winner_label"):
            self.winner_label.destroy()


class SpectatingManager:
    """観戦モードの進行を担うクラス
    
    Attributes:
        othello_board(OthelloBoard): 管理するオセロボード
        history(History | None): 管理するゲームの履歴
        turn_index(int): 現在描画しているターンの番号
        turn_player(OthelloPlayer | None): 現在のターンプレイヤー"""

    def __init__(
            self,
            othello_board: OthelloBoard,
    ):
        self.othello_board = othello_board
        self.__manager_display: SpectatingManagerDisplay | None = None
        self.history: History | None = None
        self.turn_index: int = 0
        self.turn_player: OthelloPlayer | None = None
    
    @property
    def manager_display(self) -> SpectatingManager:
        """`manager_display` のゲッター
        
        `create_manager_display` メソッドが呼ばれる前に参照された時、エラーを生じる
        
        Returns:
            NotExistsManagerDisplayError: サブディスプレイが生成される前に参照されたとき生じる"""
        if self.__manager_display is None:
            raise NotExistsManagerDisplayError()
        return self.__manager_display
    
    def create_manager_display(
            self,
            master: Misc,
            display_size: tuple[int, int] | Coordinate
    ) -> SpectatingManagerDisplay:
        """サブディスプレイを生成して返すメソッド
        
        自身に記録処理も同時に行う
        
        Args:
            master(Misc): マスター
            display_size(tuple[int, int] | Coordinate): サブディスプレイの大きさ"""
        self.__manager_display = SpectatingManagerDisplay(
            master,
            display_size,
            self.undo,
            self.redo,
            self.reset,
        )
        return self.__manager_display

    def create_game(self, history: History) -> None:
        """観戦ゲームを作成するメソッド
        
        Args:
            history(History): 観戦したいゲームの履歴"""
        self.history = history
        self.restore_scene(self.turn_index)
    
    def restore_scene(self, turn_index: int) -> None:
        """指定ターンの `Scene` を復元して、盤面とサブディスプレイを更新するメソッド
        
        Args:
            turn_index(int): 反映するターンの番号"""
        self.othello_board.take_all_pieces()
        scene: Scene = self.history[turn_index]
        black_stone_count = 0
        white_stone_count = 0
        for y in range(len(scene.board)):
            for x in range(len(scene.board[0])):
                stone: Stone | None = scene.board[y][x]
                if stone is not None:
                    self.othello_board.put(stone, (x, y))
                    match stone.color:
                        case Color.BLACK: black_stone_count += 1
                        case Color.WHITE: white_stone_count += 1
        self.turn_player = scene.turn_player
        self.__manager_display.update_display(
            self.turn_player.name,
            black_stone_count,
            white_stone_count,
        )
        
    def undo(self):
        """一手戻すメソッド"""
        if self.turn_index > 0:
            self.turn_index -= 1
            self.restore_scene(self.turn_index)

    def redo(self):
        """一手進めるメソッド"""
        if self.turn_index < len(self.history) - 1:
            self.turn_index += 1
            self.restore_scene(self.turn_index)

    def reset(self):
        """観戦状態をリセットするメソッド"""
        self.othello_board.take_all_pieces
        self.turn_index = 0
        self.turn_player = 0
        self.history = None


class SpectatingManagerDisplay(Frame):
    
    def __init__(
            self,
            master: Misc,
            display_size: tuple[int, int],
            undo_command: Callable[[], None],
            redo_command: Callable[[], None],
            reset_func: Callable[[], None],
    ):
        super().__init__(
            master,
            width=display_size[0],
            height=display_size[1]
        )
        self.display_size = Coordinate(display_size)
        self.turn_player_display = TurnPlayerDisplay(self, display_size[0])
        self.black_stone_counter = CounterDisplay(
            self,
            Color.BLACK,
            self.display_size.x // 2
        )
        self.white_stone_counter = CounterDisplay(
            self,
            Color.WHITE,
            self.display_size.x // 2,
        )
        self.undo_button = Button(
            self,
            text=SM_UNDO_BUTTON_TEXT,
            command=undo_command,
        )
        self.redo_button = Button(
            self,
            text=SM_REDO_BUTTON_TEXT,
            command=redo_command,
        )
        self.home_button = SceneTransitionButton(
            self,
            SM_HOME_BUTTON_TEXT,
            Display.HOME,
            reset_func,
        )

        # 配置
        self.turn_player_display.grid(row=0, column=0, columnspan=2, sticky=tkinter.W+tkinter.E)
        self.black_stone_counter.grid(row=1, column=0, sticky=tkinter.W+tkinter.E)
        self.white_stone_counter.grid(row=1, column=1, sticky=tkinter.W+tkinter.E)
        self.redo_button.grid(row=2, column=0, sticky="we")
        self.undo_button.grid(row=2, column=1, sticky="we")
        self.home_button.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="we"
        )

    def update_display(
            self,
            player_name: str,
            black_stone_count: int,
            white_stone_count: int,
    ):
        self.turn_player_display.update_player_name(player_name)
        self.black_stone_counter.update_counter(black_stone_count)
        self.white_stone_counter.update_counter(white_stone_count)