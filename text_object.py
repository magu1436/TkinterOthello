
from typing import Literal

from tkinter.font import Font
from tkinter import Label, Misc, StringVar


DEFAULT_MARGIN_RATIO = .9


class AutoFontLabel(Label):
    """自身の横幅に合うように自動的にフォントサイズを調節するラベルクラス.
    
    
    コンストラクタで指定された横幅に合うようにテキストのフォントサイズを調整する.  
    横幅をあとから変更したい場合は `set_font_size_fit_to_width` メソッドを使用する.  
    文字列をあとから変更したい場合は `set_text` を使用することで自動的にフォントサイズ  
    を調整してくれる.
    
    Attributes:
        text(str): 表示されているテキスト
        width(int): このウィジェットの横幅"""

    def __init__(
            self, 
            master: Misc, 
            text: str = "",
            display_width: int | None = None,
            margin_ratio: float = DEFAULT_MARGIN_RATIO,
            font_family: str = "メイリオ",
            **kwargs
        ):
        """コンストラクタ
        
        Args:
            master(Misc): 親ウィジェット
            text(str): 文字列
            display_width(str, optional): 文字列の表示サイズ(横幅). default to None
            margin_ratio(float, optional): 実際の横幅と表示文字列とのパディングの割合. default to 0.9
            font_family(str, optional): 文字列のフォント. default to 'メイリオ'
            **kwargs: tkinter.Labelに使用可能な任意のキーワード引数
        """
        
        self.__margin_ratio: float = margin_ratio

        self.__text_var: StringVar = StringVar()
        self.__text_var.set(text)

        if display_width is None:
            display_width = master.winfo_width()
        
        self.__width = display_width

        self.__font: Font = Font(family=font_family)
        super().__init__(master, font=self.__font, textvariable=self.__text_var, **kwargs)
        self.set_font_size_fit_to_width(display_width)
        
    @property
    def text(self) -> str:
        return self["text"]
    
    @property
    def width(self) -> int:
        return self.__width
    
    def set_font_size_fit_to_width(self, display_width: int):
        """自身のフォントサイズを指定の横幅に合うように変更するメソッド"""

        display_width *= self.__margin_ratio

        min_size, max_size = 1, 200
        best_size = min_size
        test_font = self.__font.copy()

        while min_size < max_size:
            mid = (min_size + max_size) // 2
            test_font.configure(size=mid)
            text_width = test_font.measure(self.__text_var.get())

            if text_width <= display_width:
                best_size = mid
                min_size = mid + 1
            else:
                max_size = mid - 1
    
        self.__font.configure(size=best_size)
        self.configure(font=self.__font)
    
    def set_text(self, text: str):
        """自身のテキスト変更するためのメソッド.  

        
        自動的にフォントサイズも変更される.    
        新しい文字列と元の文字列の長さがほぼ変わらない場合(割合が0.9以上)は  
        フォントサイズの調整を行わない.
        
        Args:
            text(str): 変更後の文字列
        """
        pre_text = self.text
        self.__text_var.set(text)

        # 文字列の長さがほぼ同じ場合はフォントサイズを変更しない
        if not(.9 < (float(len(pre_text)) / len(self.__text_var.get())) < 1.1):
            self.set_font_size_fit_to_width(self.__width)