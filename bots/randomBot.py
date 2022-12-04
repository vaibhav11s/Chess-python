from typing import TYPE_CHECKING
from random import choice
from .bot import Bot
from time import sleep

if TYPE_CHECKING:
    from ..game.board import Board
    from ..game.utils import Pos, Color


class RandomBot(Bot):
    def giveMove(self, board: "Board", color: "Color") -> "tuple[Pos,Pos]":
        sleep(1)
        allMoves = board.getAllPossibleMoves(color)
        pieceMoves = choice(allMoves)
        move = choice(pieceMoves.to)
        return pieceMoves.piece.pos, move
