from enum import Enum
from dataclasses import dataclass

UNICODE_PIECE_SYMBOLS = {
    "bR": "♖",
    "wR": "♜",
    "bN": "♘",
    "wN": "♞",
    "bB": "♗",
    "wB": "♝",
    "bQ": "♕",
    "wQ": "♛",
    "bK": "♔",
    "wK": "♚",
    "bP": "♙",
    "wP": "♟",
}


class Color(Enum):
    BLACK = 0
    WHITE = 1

    def GetOpp(self) -> "Color":
        if self == Color.BLACK:
            return Color.WHITE
        return Color.BLACK


@dataclass
class Pos:
    X: int
    Y: int

    def move(self, x, y) -> "Pos":
        return Pos(self.X + x, self.Y + y)


CharToInt = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
IntToChar = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}


def posFromEncoding(pos: str) -> "Pos|None":
    if len(pos) != 2:
        return None
    i = CharToInt.get(pos[0])
    if i == None:
        return None
    j = None
    try:
        j = 8 - int(pos[1])
    except:
        return None
    if j > 7 or j < 0:
        return None
    return Pos(i, j)


def endcodingFromPos(pos: Pos) -> "str":
    if pos.X < 0 or pos.X > 7 or pos.Y < 0 or pos.Y > 7:
        return ""
    return IntToChar[pos.X] + str(8 - pos.Y)
