from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game.board import Board
    from ..game.utils import Color, Pos


class Bot:
    def __init__(self) -> None:
        pass

    def giveNextMove(self, board: "Board", color: "Color") -> "tuple[Pos,Pos]":
        return None  # type: ignore
