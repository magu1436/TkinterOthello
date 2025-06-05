
from typing import Literal

from tkinter.font import Font
from tkinter import Label, Misc, StringVar


DEFAULT_MARGIN_RATIO = .9


class AutoFontLabel(Label):

    def __init__(
            self, 
            master: Misc, 
            text: str = "",
            display_width: int | None = None,
            margin_ratio: float = DEFAULT_MARGIN_RATIO,
            font_family: str = "メイリオ",
            **kwargs
        ):
        
        self.margin_ratio: float = margin_ratio

        self.text: StringVar = StringVar()
        self.text.set(text)

        self.font: Font = Font(family=font_family)
        super().__init__(master, font=self.font, textvariable=self.text, **kwargs)

        if display_width is None:
            display_width = master.winfo_width()
        self.set_font_size_fit_to_width(display_width)
    
    def set_font_size_fit_to_width(self, display_width: int):
        """自身のフォントサイズを指定の横幅に合うように変更するメソッド"""

        display_width *= self.margin_ratio

        min_size, max_size = 1, 200
        best_size = min_size

        while min_size < max_size:
            mid = (min_size + max_size) // 2
            self.font.configure(size=mid)
            text_width = self.font.measure(self.text.get())

            if text_width <= display_width:
                best_size = mid
                min_size = mid + 1
            else:
                max_size = mid - 1
    
        self.font.configure(size=best_size)
        self.configure(font=self.font)
    
    def set_text(self, text: str):
        """自身のテキスト変更するためのメソッド.
        
        自動的にフォントサイズも変更される
        
        Args:
            text(str): 変更後の文字列
        """
        width = self.winfo_width()
        self.text.set(text)
        self.set_font_size_fit_to_width(width)