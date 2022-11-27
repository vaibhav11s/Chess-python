from typing import TYPE_CHECKING

from .utils import Pos, Color, UNICODE_PIECE_SYMBOLS as UP
from .pieces import Pawn, Knight, Bishop, Rook, Queen, King

if TYPE_CHECKING:
    from .pieces import Piece


class Board:
    def __init__(self) -> None:
        self.board: "list[list[Piece|None]]" = [
            [None for _ in range(8)] for _ in range(8)
        ]
        self.deaths: "list[Piece]" = []

        pass

    def resetBoard(self) -> None:
        # empty spaces
        for j in range(2, 5):
            for i in range(8):
                self.board[j][i] = None
        # pawns
        for i in range(8):
            self.createPiece(Pawn, Color.BLACK, i, 1)
            self.createPiece(Pawn, Color.WHITE, i, 6)

        # knites
        self.createPiece(Knight, Color.BLACK, 1, 0)
        self.createPiece(Knight, Color.BLACK, 6, 0)
        self.createPiece(Knight, Color.WHITE, 1, 7)
        self.createPiece(Knight, Color.WHITE, 6, 7)

        # bishops
        self.createPiece(Bishop, Color.BLACK, 2, 0)
        self.createPiece(Bishop, Color.BLACK, 5, 0)
        self.createPiece(Bishop, Color.WHITE, 2, 7)
        self.createPiece(Bishop, Color.WHITE, 5, 7)

        # rook
        self.createPiece(Rook, Color.BLACK, 0, 0)
        self.createPiece(Rook, Color.BLACK, 7, 0)
        self.createPiece(Rook, Color.WHITE, 0, 7)
        self.createPiece(Rook, Color.WHITE, 7, 7)

        # queen
        self.createPiece(Queen, Color.BLACK, 3, 0)
        self.createPiece(Queen, Color.WHITE, 3, 7)

        # king
        self.createPiece(King, Color.BLACK, 4, 0)
        self.createPiece(King, Color.WHITE, 4, 7)
        self.deaths.clear()

    def movePieceFromTo(self, src: Pos, dest: Pos) -> 'tuple[bool, bool]':
        srcPiece = self.getPiece(src)
        # check in possible moves
        if srcPiece == None:
            return False, False
        possibleMoves = srcPiece.possibleMoves(self)
        if dest not in possibleMoves:
            return False, False
        destPiece = self.getPiece(dest)
        if destPiece == None:
            self.setPiece(srcPiece, dest)
            self.removePiece(src)
            srcPiece.moveTo(dest)
            return True, False
        if destPiece.color != srcPiece.color:
            isKing = isinstance(destPiece,King)
            self.killPiece(dest)
            self.setPiece(srcPiece, dest)
            self.removePiece(src)
            srcPiece.moveTo(dest)
            return True, isKing
        return False, False

    def killPiece(self, pos: Pos):
        piece = self.getPiece(pos)
        if piece != None:
            self.deaths.append(piece)
        self.setPiece(None, pos)

    def getPiece(self, pos: Pos) -> "Piece|None":
        return self.board[pos.Y][pos.X]

    def createPiece(self, Piec, color: Color, i, j) -> None:
        piece = Piec(i, j, color)
        self.board[j][i] = piece
        pass

    def setPiece(self, piece: "Piece|None", pos: Pos):
        self.board[pos.Y][pos.X] = piece

    def removePiece(self, pos: Pos):
        self.board[pos.Y][pos.X] = None

    def __repr__(self) -> str:
        repr = ""

        repr += "    " + "    ".join(["a", "b", "c", "d", "e", "f", "g", "h"]) + "   \n"

        repr += "  " + "╔" + "═" * 39 + "╗\n"
        repr += ("\n  ║" + "─" * 39 + "║\n").join(
            [
                (
                    str(i + 1)
                    + " "
                    + "║ "
                    + "  | ".join(
                        [str(UP.get(self.getPosRep(i, j), " ")) for j in range(8)]
                    )
                    + "  ║"
                )
                for i in range(8)
            ]
        )
        repr += "\n  ╚" + "═" * 39 + "╝"
        return repr

    def getPosRep(self, i, j):
        if self.board[i][j] == None:
            return "  "
        return str(self.board[i][j])

    # for pieces classes
    def canMove(self, pos: Pos) -> bool:
        if pos.X < 0 or pos.X > 7 or pos.Y < 0 or pos.Y > 7:
            return False
        piece = self.getPiece(pos)
        if piece == None:
            return True
        return False

    def canKill(self, pos: Pos, color: Color) -> bool:
        if pos.X < 0 or pos.X > 7 or pos.Y < 0 or pos.Y > 7:
            return False
        piece = self.getPiece(pos)
        if piece == None:
            return False
        if piece.color != color:
            return True
        return False

    def getDirection(self, color: Color):
        if color == Color.BLACK:
            return 1
        return -1
