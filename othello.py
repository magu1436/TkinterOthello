from __future__ import annotations

import tkinter

from systems import CONFIG
from game_display import GameDisplay
from history_display import HistoryDisplay
from home_display import HomeDisplay
from spectator_display import SpectatorDisplay


ICON_IMAGE_PATH = CONFIG["ICON_IMAGE_PATH"]

def main():

    root = tkinter.Tk()
    root.state("zoomed")
    root.title("othello game")
    root.iconbitmap(default=ICON_IMAGE_PATH)
    root.update_idletasks()

    game_display = GameDisplay(root, 5)
    game_display.grid(row=0, column=0, sticky="nsew")

    history_display = HistoryDisplay(root)
    history_display.grid(row=0, column=0, sticky="nsew")

    home_display = HomeDisplay(root, game_display, history_display)
    home_display.grid(row=0, column=0, sticky="nsew")

    spectator_display = SpectatorDisplay(root, 5)
    spectator_display.grid(row=0, column=0, sticky="nsew")

    home_display.tkraise()

    root.mainloop()

if __name__ == "__main__":
    main()