from typing import TYPE_CHECKING
from copy import deepcopy
from .utils import Pos, Color

if TYPE_CHECKING:
    from .board import Board


class Piece:
    def __init__(self, x: int, y: int, color: Color) -> None:
        self.pos = Pos(x, y)
        self.color = color

    def __repr__(self) -> str:
        return "xX"

    def possibleMoves(self, board: "Board", depth=1) -> "tuple[list[Pos],list[Pos]]":
        possMoves = self.childPossibleMoves(board)
        if depth == 0:
            return possMoves, []
        illegalMoves = []
        legalMoves = []
        for move in possMoves:
            newBoard = deepcopy(board)
            newBoard.overrideMove(self.pos, move)
            if newBoard.checked == self.color:
                legalMoves.append(move)
            else:
                illegalMoves.append(move)
        return illegalMoves, legalMoves

    def childPossibleMoves(self, board: "Board") -> "list[Pos]":
        return []

    def moveTo(self, pos: Pos):
        self.pos = pos


class Pawn(Piece):
    def __repr__(self) -> str:
        return "bP" if self.color == Color.BLACK else "wP"

    def childPossibleMoves(self, board: "Board"):
        dir = board.getDirection(self.color)
        moves: "list[Pos]" = []

        front = self.pos.move(0, dir)
        if board.canMove(front):
            moves.append(front)
            if (dir == 1 and self.pos.Y == 1) or (dir == -1 and self.pos.Y == 6):
                front2 = self.pos.move(0, dir * 2)
                if board.canMove(front2):
                    moves.append(front2)

        diagLeft = self.pos.move(-1, dir)
        if board.canKill(diagLeft, self.color):
            moves.append(diagLeft)
        diagRight = self.pos.move(+1, dir)
        if board.canKill(diagRight, self.color):
            moves.append(diagRight)
        return moves


KnightsMoves = [
    (+2, +1),
    (+2, -1),
    (-2, +1),
    (-2, -1),
    (+1, +2),
    (+1, -2),
    (-1, +2),
    (-1, -2),
]


class Knight(Piece):
    def __repr__(self) -> str:
        return "bN" if self.color == Color.BLACK else "wN"

    def childPossibleMoves(self, board: "Board"):
        moves: "list[Pos]" = []
        for mv in KnightsMoves:
            pos = self.pos.move(mv[0], mv[1])
            if board.canMove(pos) or board.canKill(pos, self.color):
                moves.append(pos)
        return moves


BishopDirection = [
    (+1, +1),
    (+1, -1),
    (-1, +1),
    (-1, -1),
]


class Bishop(Piece):
    def __repr__(self) -> str:
        return "bB" if self.color == Color.BLACK else "wB"

    def childPossibleMoves(self, board: "Board"):
        moves: "list[Pos]" = []
        for dir in BishopDirection:
            for i in range(1, 8):
                posN = self.pos.move(dir[0] * i, dir[1] * i)
                if board.canMove(posN):
                    moves.append(posN)
                elif board.canKill(posN, self.color):
                    moves.append(posN)
                    break
                else:
                    break
        return moves


RookDirections = [
    (+1, 0),
    (-1, 0),
    (0, +1),
    (0, -1),
]


class Rook(Piece):
    def __init__(self, x: int, y: int, color: Color) -> None:
        super().__init__(x, y, color)
        self.hasMoved = False

    def __repr__(self) -> str:
        return "bR" if self.color == Color.BLACK else "wR"

    def moveTo(self, pos: Pos):
        self.hasMoved = True
        return super().moveTo(pos)

    def childPossibleMoves(self, board: "Board"):
        moves: "list[Pos]" = []
        for dir in RookDirections:
            for i in range(1, 8):
                posN = self.pos.move(dir[0] * i, dir[1] * i)
                if board.canMove(posN):
                    moves.append(posN)
                elif board.canKill(posN, self.color):
                    moves.append(posN)
                    break
                else:
                    break
        return moves


class Queen(Piece):
    def __repr__(self) -> str:
        return "bQ" if self.color == Color.BLACK else "wQ"

    def childPossibleMoves(self, board: "Board"):
        moves: "list[Pos]" = []
        for dir in RookDirections + BishopDirection:
            for i in range(1, 8):
                posN = self.pos.move(dir[0] * i, dir[1] * i)
                if board.canMove(posN):
                    moves.append(posN)
                elif board.canKill(posN, self.color):
                    moves.append(posN)
                    break
                else:
                    break
        return moves


class King(Piece):
    def __init__(self, x: int, y: int, color: Color) -> None:
        super().__init__(x, y, color)
        self.hasMoved = False

    def __repr__(self) -> str:
        return "bK" if self.color == Color.BLACK else "wK"

    def moveTo(self, pos: Pos):
        self.hasMoved = True
        return super().moveTo(pos)

    def childPossibleMoves(self, board: "Board"):
        moves: "list[Pos]" = []
        for dir in RookDirections + BishopDirection:
            posN = self.pos.move(dir[0], dir[1])
            if board.canMove(posN):
                moves.append(posN)
            elif board.canKill(posN, self.color):
                moves.append(posN)
        moves = moves + self.getCastlingMoves(board)
        return moves

    def getCastlingMoves(self, board: "Board") -> "list[Pos]":
        if self.hasMoved:
            return []

        # check if currently in check
        if board.checked == self.color:
            return []
        moves = []

        def checkNonQueenSide():
            if (
                board.getPiece(self.pos.move(1, 0)) != None
                or board.getPiece(self.pos.move(2, 0)) != None
            ):
                return
            rookPos = board.getPiece(self.pos.move(3, 0))
            if not isinstance(rookPos, Rook):
                return
            if rookPos.hasMoved:
                return
            newBoard = deepcopy(board)
            newBoard.overrideMove(self.pos, self.pos.move(1, 0))
            if newBoard.checked == self.color:
                return
            newBoard.overrideMove(self.pos.move(1, 0), self.pos.move(2, 0))
            if newBoard.checked == self.color:
                return
            moves.append(self.pos.move(2, 0))

        def checkQueenSide():
            if (
                board.getPiece(self.pos.move(-1, 0)) != None
                or board.getPiece(self.pos.move(-2, 0)) != None
                or board.getPiece(self.pos.move(-3, 0)) != None
            ):
                return
            rookPos = board.getPiece(self.pos.move(-4, 0))
            if not isinstance(rookPos, Rook):
                return
            if rookPos.hasMoved:
                return
            newBoard = deepcopy(board)
            newBoard.overrideMove(self.pos, self.pos.move(-1, 0))
            if newBoard.checked == self.color:
                return
            newBoard.overrideMove(self.pos.move(-1, 0), self.pos.move(-2, 0))
            if newBoard.checked == self.color:
                return
            moves.append(self.pos.move(-2, 0))

        checkNonQueenSide()
        checkQueenSide()

        return moves
